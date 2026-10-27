"""Read-only exact shared-factor reconstruction of nine retained schedules."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

from credit_linked_algebra_v1 import Expr, Root, Refusal, need, canonical, digest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'data/accounting-master/dated-credit-schedules-20261016'
PROFILE = 'CreditLinkedSchedule/1'
PINS = {
    'reference.py':'839b0cb57e4b024adf75a4d47607e63b686e62e17c87d4b4f1b2ab35a2120800',
    'bounds.py':'95f370079a53315492d412c9b4ef3b1ef846118b596accfb2c7afcb7b5057185',
    'attempt-01/exchanges.json':'ea580e3474e2df16045e2c5501002bbebfe19be783f19d4620a2d20b2e79657b',
    'input-lock.json':'56aadac51b589e57ecccf60d6cb5518e7509165084d51b9fce588a8c9572e6c6',
    'authored-cases.json':'ac95fb3fda2e303dad851d2191c6706a1fb1be1e5147f394a7f1872b041bfb10',
}
FLAGS = {'posts':False, 'mutations':[], 'native_accounting_admission':False,
         'source_complete':False, 'host_book_admission':False}


def protected():
    for name, h in PINS.items():
        need(sha256((NATIVE/name).read_bytes()).hexdigest() == h, 'dependency_hash:'+name)


def load_native():
    protected()
    if 'bounds' in sys.modules:
        need(Path(sys.modules['bounds'].__file__).resolve() == NATIVE/'bounds.py', 'bounds_module_collision')
    else:
        spec = importlib.util.spec_from_file_location('bounds', NATIVE/'bounds.py')
        module = importlib.util.module_from_spec(spec); sys.modules['bounds'] = module
        spec.loader.exec_module(module)
    spec = importlib.util.spec_from_file_location('credit_linked_native', NATIVE/'reference.py')
    native = importlib.util.module_from_spec(spec); spec.loader.exec_module(native)
    return native, sys.modules['bounds']


def retained():
    protected()
    return json.loads((NATIVE/'attempt-01/exchanges.json').read_text())


def request(case_id):
    selected = next((r for r in retained() if r['id'] == case_id), None)
    need(selected is not None, 'unsupported_retained_case', 'unsupported')
    return {'profile':PROFILE, 'case_id':case_id, 'native_request':deepcopy(selected['request']),
            'native_request_sha256':digest(selected['request']),
            'expected_native_result_sha256':digest(selected['result'])}


def encode(value):
    if isinstance(value, Expr): return value.wire()
    if isinstance(value, Q): return str(value)
    if isinstance(value, list): return [encode(v) for v in value]
    if isinstance(value, dict): return {k:encode(v) for k,v in value.items()}
    return value


def reconstruct(req, bounds):
    a = req['acquisition']; root = Root.create(req['context'], a['rate'])
    zero = root.value(0); one = root.value(1)
    certificates = []
    def prove(name, left, right):
        remainder = left-right
        need(remainder.zero, 'identity_not_certified:'+name, 'not_certified')
        certificates.append({'identity':name,'status':'certified_equal','remainder':remainder.wire()})
    def factor(start, end):
        return root.power((bounds.day(end)-bounds.day(start)).days)
    def pv(flows, at):
        return sum((root.power(-(bounds.day(d)-bounds.day(at)).days)*Q(v) for d,v in flows.items()), zero)
    start = t = a['date']; initial = Q(a['price'])+Q(a['cost'])-Q(a['fee_received'])
    opening = Q(req['opening_cash']); contract = {d:Q(v) for d,v in a['contract'].items()}
    expected = {d:Q(v) for d,v in a['expected'].items()}
    residual = pv(expected,t)-initial; prove('initial_present_value',residual,zero)
    shortfall = pv(contract,t)-initial if req['wire']=='POCIDatedSchedule/1' else zero
    G=root.value(initial); L=zero; cash=opening-initial
    interest=impairment=catchup=zero; closed=False
    stages=[]; journals=[]; origins=[{'date':t,'kind':'initial','amount':G}]
    cash_flows=[{'date':t,'kind':'price','amount':-Q(a['price'])},
                {'date':t,'kind':'integral_cost','amount':-Q(a['cost'])},
                {'date':t,'kind':'integral_fee','amount':Q(a['fee_received'])}]
    uncollected=[]; written_off=[]; totals={}
    def journal(identity, entries):
        prove('journal:'+identity,sum(entries.values(),zero),zero)
        journals.append({'id':identity,'date':t,'entries':entries})
        for name, value in entries.items(): totals[name]=totals.get(name,zero)+value
    def stage(identity, kind):
        N=G-L; profit=interest+impairment+catchup
        direct_g=sum((o['amount']*factor(o['date'],t) for o in origins),zero)
        direct_n=pv(expected,t) if not closed else zero
        checks={'net_equals_gross_less_allowance':(N,G-L),'gross_origins':(G,direct_g),
                'remaining_cash_present_value':(N,direct_n),'financial_identity':(cash+N,opening+profit),
                'journal_gross':(totals.get('gross',zero),G),
                'journal_allowance':(totals.get('allowance',zero),-L),
                'journal_cash':(totals.get('cash',zero),root.value(cash-opening)),
                'journal_interest':(totals.get('interest',zero),-interest),
                'journal_impairment':(totals.get('impairment',zero),-impairment),
                'journal_catchup':(totals.get('catchup',zero),-catchup)}
        for name,(left,right) in checks.items(): prove(identity+':'+name,left,right)
        stages.append({'id':identity,'kind':kind,'date':t,'gross':G,'allowance':L,'net':N,
            'cash':root.value(cash),'interest':interest,'impairment':impairment,'catchup':catchup,
            'profit':profit,'equity':opening+profit,'direct_gross':direct_g,'direct_net':direct_n,
            'remaining_contract':contract.copy(),'expected':expected.copy()})
    journal('acquisition',{'gross':G,'cash':root.value(-initial)}); stage('acquisition','initial')
    for e in req['events']:
        identity=e['id']; kind=e['operation']; nt=e['date']; f=factor(t,nt)
        dG=G*(f-one); dL=L*(f-one); earned=(G-L)*(f-one)
        G=G*f; L=L*f; interest=interest+earned; t=nt
        journal(identity+'_accrual',{'gross':dG,'allowance':-dL,'interest':-earned})
        stage(identity+'_accrual','accrual')
        if kind=='credit_revision':
            new={d:Q(v) for d,v in e['expected'].items()}; newN=pv(new,t); gain=newN-(G-L)
            L=G-newN; impairment=impairment+gain; expected=new
            journal(identity+'_credit',{'allowance':gain,'impairment':-gain})
            w=e['writeoff']; fraction=Q(w['fraction'])
            if fraction:
                written_off.append({'date':t,'portion_id':w['portion_id'],
                                    'contractual_cash':{d:v*fraction for d,v in contract.items()}})
                contract={d:v*(1-fraction) for d,v in contract.items()}
                W=G*fraction; G=G-W; L=L-W
                origins.append({'date':t,'kind':'writeoff','amount':-W})
                journal(identity+'_writeoff',{'gross':-W,'allowance':W})
                if fraction==1:
                    prove(identity+':full_writeoff_gross',G,zero)
                    prove(identity+':full_writeoff_allowance',L,zero)
                    G=L=zero; closed=True
        elif kind=='estimate_revision':
            new={d:Q(v) for d,v in e['expected'].items()}; newG=pv(new,t); gain=newG-G
            G=newG; catchup=catchup+gain
            origins.append({'date':t,'kind':'noncredit_catchup','amount':gain})
            expected=new; contract=new.copy()
            journal(identity+'_estimate',{'gross':gain,'catchup':-gain})
        elif kind=='collect':
            amount=Q(e['amount']); cash+=amount; G=G-amount
            origins.append({'date':t,'kind':'collection','amount':root.value(-amount)})
            cash_flows.append({'date':t,'kind':'collection','amount':amount})
            journal(identity+'_cash',{'cash':root.value(amount),'gross':root.value(-amount)})
            expected.pop(t)
            uncollected.append({'due_date':t,'amount':contract.pop(t,Q(0))-amount,'legal_forgiveness':'not_assessed'})
            if e['close']:
                prove(identity+':settlement_net',G-L,zero)
                origins.append({'date':t,'kind':'settlement_allowance_clear','amount':-L})
                journal(identity+'_clear',{'gross':-L,'allowance':L})
                G=L=zero; closed=True
        else:
            need(kind=='advance','unsupported_event','unsupported')
        stage(identity,kind)
    result={'status':'conditional_complete','reason':'finite_dated_profile','context':req['context'],'wire':req['wire'],
            'initial_pv_residual':residual,'initial_credit_shortfall':shortfall,'numerical':req['numerical'],
            'closing':stages[-1],'stages':stages,'journals':journals,'cash_flows':cash_flows,'origins':origins,
            'factor_bounds':[{'start':start,'end':s['date'],'factor':factor(start,s['date'])} for s in stages],
            'financial_derecognized':closed,'uncollected_contract':uncollected,'writeoff_contract':written_off,
            'legal_forgiveness':'not_assessed','posts':False,'mutations':[]}
    return root,result,certificates


def crosscheck(exact, native, bounds):
    certificates=[]
    def walk(x,y,path):
        if isinstance(x,Expr):
            need(type(y) is dict and set(y)=={'lower','upper','width','exact'}, 'native_amount_shape:'+path)
            interval=sum((bounds.factor(x.root.rate,p,24)*c for p,c in x.terms),bounds.I.point(0))
            contained=Q(y['lower'])<=interval.lo<=interval.hi<=Q(y['upper'])
            need(contained, 'enclosure_not_contained:'+path, 'not_certified')
            certificates.append({'path':path,'exact_expression':x.wire(),'enclosure':interval.wire(),
                                 'native_enclosure':y,'contained':True})
        elif isinstance(x,dict):
            need(type(y) is dict and set(x)==set(y),'structure_mismatch:'+path)
            for k,v in x.items(): walk(v,y[k],path+'/'+str(k))
        elif isinstance(x,list):
            need(type(y) is list and len(x)==len(y),'list_mismatch:'+path)
            for i,(a,b) in enumerate(zip(x,y)): walk(a,b,path+'/'+str(i))
        else:
            need(encode(x)==y,'metadata_mismatch:'+path)
    walk(exact,native,'')
    return certificates


def authored_targets(case_id, root, exact):
    rows=json.loads((NATIVE/'authored-cases.json').read_text())['cases']
    target=next(r['expected'] for r in rows if r['id']==case_id)
    pairs=[('final_cash',exact['closing']['cash'],target['final_cash']),
           ('final_profit',exact['closing']['profit'],target['final_profit']),
           ('initial_shortfall',exact['initial_credit_shortfall'],target['initial_shortfall'])]
    stages={s['id']:s for s in exact['stages']}
    for identity,values in target['stages'].items():
        for name,v in values.items(): pairs.append((identity+':'+name,stages[identity][name],v))
    results=[]
    for name,actual,v in pairs:
        expected=root.power(181)*Q(v['f_coefficient'])+Q(v['constant']) if type(v) is dict else root.value(v)
        need((actual-expected).zero,'authored_target_not_certified:'+name,'not_certified')
        results.append({'target':name,'expected':expected.wire(),'actual':actual.wire(),'certified_equal':True})
    return results


def calculate(body):
    try:
        need(type(body) is dict,'request_shape')
        need(len(canonical(body))<=131072,'request_size','unsupported')
        need(set(body)=={'profile','case_id','native_request','native_request_sha256','expected_native_result_sha256'},'request_shape')
        need(body['profile']==PROFILE,'profile')
        native,bounds=load_native(); req=body['native_request']
        need(digest(req)==body['native_request_sha256'],'native_request_hash')
        actual=native.calculate(deepcopy(req))
        if actual['status']!='conditional_complete':
            return {'profile':PROFILE,'status':actual['status'],'reason':'native_refusal',
                    'native_refusal':actual,**deepcopy(FLAGS)}
        selected=next((r for r in retained() if r['id']==body['case_id']),None)
        need(selected is not None,'unsupported_retained_case','unsupported')
        need(canonical(req)==canonical(selected['request']),'outside_retained_native_request')
        need(actual==selected['result'] and digest(actual)==body['expected_native_result_sha256'],'native_result_binding')
        root,exact,identities=reconstruct(req,bounds)
        targets=authored_targets(body['case_id'],root,exact)
        containment=crosscheck(exact,actual,bounds)
        return {'profile':PROFILE,'status':'certified_read_only','case_id':body['case_id'],
                'native_request_sha256':digest(req),'native_result_sha256':digest(actual),
                'root':root.wire(),'root_sha256':root.identity,
                'amount_meaning':{'context_sha256':digest(req['context']),'monetary_unit':req['context']['unit'],
                    'factor_bounds':'dimensionless exact factors; retained field name for native comparison'},
                'schedule':encode(exact),'certificates':{'identities':identities,'authored_targets':targets,'containment':containment},
                'equality_limit':'Nonzero reduced polynomial means not_certified, not unequal',**deepcopy(FLAGS)}
    except Refusal as exc:
        return {'profile':PROFILE,'status':exc.status,'reason':exc.reason,**deepcopy(FLAGS)}
    except (TypeError,ValueError,KeyError,OverflowError,RecursionError,ZeroDivisionError) as exc:
        return {'profile':PROFILE,'status':'rejected','reason':'malformed_input:'+type(exc).__name__,**deepcopy(FLAGS)}
