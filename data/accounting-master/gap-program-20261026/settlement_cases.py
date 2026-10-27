"""E01: synthetic maturity and missed-payment memory in the existing typed runtime.
Expected financial paths below are authored independently of method expressions.
No actual issuer, legal-default, accounting-admission or equilibrium claim.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'scripts'))
import declared_company_program_v2 as runtime
import declared_financing_methods_v1 as h
import company_execution_v1 as native
spec = importlib.util.spec_from_file_location('operating_fixture', ROOT/'data/accounting-master/declared-operating-cycle-20261025/examples.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
ref, binary, const = h.ref, h.binary, h.constant
DATE = {'kind':'date', 'context':{}}
BOOL = runtime.core.BOOL
SCOPE = 'Supplied synthetic zero-coupon promise, one explicit accretion interval, no fees/tax/penalty/acceleration, no legal-default or accounting admission.'
checks = []

def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def check(name, actual, expected):
    ok = actual == expected
    checks.append({'id':name, 'passed':ok, 'actual':actual, 'expected':expected})
    if not ok:
        save('settlement-failed-checks.json', checks)
        raise AssertionError(name)

def scalar(typ):
    return {'type':'boolean'} if typ['kind']=='boolean' else h.scalar(typ['kind'])

def make(path, owner='alpha'):
    body, _, _, mapping = fixture.fixture(owner)
    book = body['opening']
    money = runtime.engine.money_type(book)
    share = {**deepcopy(money), 'dimensions':{'equity:share':1}}
    price = {**deepcopy(money), 'dimensions':{'currency:USD':1,'equity:share':-1}}
    types = {'original_face':money, 'outstanding':money, 'arrears':money,
             'missed_amount':money, 'due':DATE, 'matured':BOOL, 'missed':BOOL,
             'old_shares':share, 'new_shares':share}
    initial = {'original_face':'100/1','outstanding':'100/1','arrears':'0/1',
               'missed_amount':'0/1','due':'2027-06-30','matured':False,'missed':False,
               'old_shares':'100/1','new_shares':'0/1'}
    shape = deepcopy(body['schemas'][book['memory_schema']])
    shape['properties']['debt_terms'] = h.record({k:scalar(t) for k,t in types.items()})
    shape['required'].append('debt_terms')
    book['memory']['debt_terms'] = initial
    book['memory_schema'] = runtime.digest(shape)
    book['memory_types'].update({'/debt_terms/'+k:t for k,t in types.items()})
    book['balances'] = {a:'0/1' for a in mapping.values()}
    book['balances'].update({mapping[k]:h.fmt(v) for k,v in {'cash':60,'inventory':100,'debt':-80,'capital':-80}.items()})
    schemas = {runtime.digest(shape):shape}
    entries = {}
    zero = const(money,'0/1')
    neg = lambda expression: binary('sub',deepcopy(zero),expression)

    def method(key, extra, postings, flows, changes, inputs=None, numeric=None):
        inputs = {'approved':BOOL, **(inputs or {})}
        bindings = {'cash':(money,h.account('cash')), 'debt':(money,h.account('debt')),
                    'event_date':(DATE,h.event('event_date')),
                    **{k:(t,h.memory('/debt_terms/'+k)) for k,t in types.items()},
                    **{k:(t,h.event(k)) for k,t in inputs.items()}}
        base = [('approved',ref('approved'),['approved'],'unsupported'),
                ('cash_nonnegative',binary('le',deepcopy(zero),ref('cash')),['cash'],'invalid'),
                ('remaining_nonnegative',binary('le',deepcopy(zero),ref('outstanding')),['outstanding'],'invalid')]
        pre_rows = base + extra
        pre_keys = {x for _,_,deps,_ in pre_rows for x in deps}
        post_rows = [('cash_nonnegative',binary('le',deepcopy(zero),ref('cash')),['cash'],'invalid'),
                     ('remaining_nonnegative',binary('le',deepcopy(zero),ref('outstanding')),['outstanding'],'invalid')]
        if key in ['mature','settle_due','observe_missed','settle_late']:
            post_rows.append(('carrying_matches_remaining_at_maturity',binary('eq',ref('debt'),neg(ref('outstanding'))),['debt','outstanding'],'invalid'))
        post_keys = {x for _,_,deps,_ in post_rows for x in deps}
        identity = 'synthetic.dated-settlement.'+key
        operations=[]; fields={}; input_bindings={}; calculations=[]
        for name, expression, deps in changes:
            if isinstance(expression, dict):
                calc='next_'+name
                calculations.append({'id':calc,'type':types[name],'expression':expression,'requires':deps})
                fields[calc]=scalar(types[name]); input_bindings[calc]={'kind':'calculation','name':calc}
                value={'kind':'read','source':'inputs','pointer':'/'+calc}
            else:
                value={'kind':'literal','value':expression}
            operations.append({'id':'write.'+name,'op':'replace','path':['debt_terms',name],'value':value})
        numeric_keys = set(numeric or []) | {x for _,_,deps in postings+flows for x in deps} | {x for _,e,deps in changes if isinstance(e,dict) for x in deps}
        input_shape=h.record(fields); ss={**schemas,runtime.digest(input_shape):input_shape}
        roles={'cash'}|{r for r,_,_ in postings}|{bindings[k][1]['role'] for k in pre_keys|post_keys|numeric_keys if bindings[k][1]['kind']=='account'}
        definition={'profile':runtime.engine.METHOD,'id':identity,'version':'1','context':deepcopy(book['context']),
          'account_map':{r:mapping[r] for r in sorted(roles)},
          'preconditions':{'manifest':h.conditions(identity,{k:bindings[k][0] for k in sorted(pre_keys)},pre_rows),'bindings':{k:bindings[k][1] for k in sorted(pre_keys)}},
          'postconditions':{'manifest':h.conditions(identity,{k:bindings[k][0] for k in sorted(post_keys)},post_rows),'bindings':{k:bindings[k][1] for k in sorted(post_keys)}},
          'monetary':{'definition':{'profile':runtime.engine.monetary.PROFILE,'method_id':identity,'version':'1',
            'inputs':{k:h.declaration(bindings[k][0],k) for k in sorted(numeric_keys)},'calculations':calculations,
            'accounts':{r:money for r in sorted(roles)},'cash_account':'cash',
            'postings':[{'id':r,'account':r,'expression':e,'requires':deps} for r,e,deps in postings],
            'flows':[{'id':key,'activity':activity,'origin':key,'expression':e,'requires':deps} for activity,e,deps in flows]},
            'bindings':{k:bindings[k][1] for k in sorted(numeric_keys)}},
          'memory':{'definition':{'profile':runtime.engine.memory.PROFILE,'state_schema':book['memory_schema'],
            'input_schema':runtime.digest(input_shape),'operations':operations},'input_bindings':input_bindings},
          'residual_prerequisites':[SCOPE]}
        entries[key]={'method_sha256':runtime.digest(definition),'method':definition,'schemas':ss,
          'account_classes':{r:book['accounts'][mapping[r]]['classification'] for r in roles},
          'event_inputs':inputs,'metadata_bindings':{'event_date':'date'} if 'event_date' in pre_keys else {},
          'clock':{'kind':'direct_event_date'}}
        schemas.update(ss)

    eq=lambda name,value,typ:binary('eq',ref(name),const(typ,value))
    require_due=[('on_due_date',binary('eq',ref('event_date'),ref('due')),['event_date','due'],'invalid')]
    require_mature=[('matured',eq('matured',True,BOOL),['matured'],'invalid')]
    late=[('after_due_date',binary('lt',ref('due'),ref('event_date')),['due','event_date'],'invalid')]
    discount=binary('add',ref('original_face'),ref('debt'))
    method('mature',require_due+[('not_yet_mature',eq('matured',False,BOOL),['matured'],'invalid'),
      ('unpaid_original_face',binary('eq',ref('outstanding'),ref('original_face')),['outstanding','original_face'],'invalid'),
      ('discount_nonnegative',binary('le',zero,deepcopy(discount)),['original_face','debt'],'invalid')],
      [('interest',discount,['original_face','debt']),('debt',neg(deepcopy(discount)),['original_face','debt'])],[],[('matured',True,[])])
    amount=binary('mul',ref('shares'),ref('price'))
    method('equity', [('positive_shares',binary('lt',const(share,'0/1'),ref('shares')),['shares'],'invalid'),
      ('positive_price',binary('lt',const(price,'0/1'),ref('price')),['price'],'invalid')],
      [('cash',amount,['shares','price']),('capital',neg(deepcopy(amount)),['shares','price'])],
      [('financing',deepcopy(amount),['shares','price'])],
      [('new_shares',binary('add',ref('new_shares'),ref('shares')),['new_shares','shares'])],{'shares':share,'price':price})
    pay_checks=[('positive_payment',binary('lt',zero,ref('amount')),['amount'],'invalid'),
      ('cash_available',binary('le',ref('amount'),ref('cash')),['amount','cash'],'invalid'),
      ('claim_available',binary('le',ref('amount'),ref('outstanding')),['amount','outstanding'],'invalid'),
      ('carrying_equals_outstanding',binary('eq',ref('debt'),neg(ref('outstanding'))),['debt','outstanding'],'invalid')]
    postings=[('debt',ref('amount'),['amount']),('cash',neg(ref('amount')),['amount'])]
    flows=[('financing',neg(ref('amount')),['amount'])]
    reduction=('outstanding',binary('sub',ref('outstanding'),ref('amount')),['outstanding','amount'])
    method('settle_due',require_due+require_mature+pay_checks,postings,flows,[reduction],{'amount':money})
    method('observe_missed',require_mature+late+[('not_observed',eq('missed',False,BOOL),['missed'],'invalid'),
      ('unpaid_amount',binary('lt',zero,ref('outstanding')),['outstanding'],'invalid')],[],[],
      [('missed',True,[]),('missed_amount',ref('outstanding'),['outstanding']),('arrears',ref('outstanding'),['outstanding'])])
    method('settle_late',require_mature+late+pay_checks+[('observed_missed',eq('missed',True,BOOL),['missed'],'invalid'),
      ('arrears_available',binary('le',ref('amount'),ref('arrears')),['amount','arrears'],'invalid')],postings,flows,
      [reduction,('arrears',binary('sub',ref('arrears'),ref('amount')),['arrears','amount'])],{'amount':money})
    body.update(profile=runtime.PROFILE,name='dated-settlement-'+path+'-'+owner,schemas=schemas,
      registry={'profile':runtime.methods.REGISTRY,'context':deepcopy(book['context']),'entries':entries},commands=[])
    if path=='early':
        rows=[('equity','2027-06-29',{'shares':'40/1','price':'1/1'}),('mature','2027-06-30',{}),('settle_due','2027-06-30',{'amount':'100/1'})]
    else:
        rows=[('mature','2027-06-30',{}),('settle_due','2027-06-30',{'amount':'60/1'}),('observe_missed','2027-07-01',{}),
              ('equity','2027-07-02',{'shares':'40/1','price':'1/1'}),('settle_late','2027-07-03',{'amount':'40/1'})]
    for i,(kind,date,values) in enumerate(rows):
        body['commands'].append({'kind':'event','method_key':kind,'event':{'id':kind+'.'+str(i),'date':date,
          'inputs':{k:{'type':deepcopy(entries[kind]['event_inputs'][k]),'value':runtime.engine.known(v),'provenance':SCOPE} for k,v in {'approved':True,**values}.items()}}})
    equity=next(c['event'] for c in body['commands'] if c['method_key']=='equity')
    body['commands'].append({'kind':'report','id':'closing','cutoff':'2027-07-04',
      'equity_movements':[{'id':'subscription','event_id':equity['id'],'date':equity['date'],'account':mapping['capital'],'amount':'40/1','description':'Supplied subscription settles on the event date'}],
      'notes':[{'id':'scope','label':'Conditional contract history','status':'unresolved','reason':SCOPE}]})
    return body,mapping

def expected_path(body, mapping, path):
    # Explicit independent economic table: cash, signed debt, capital, expense,
    # outstanding claim, arrears, historical missed amount, matured, missed, new shares.
    states = ([[100,-80,-120,0,100,0,0,False,False,40],
               [100,-100,-120,20,100,0,0,True,False,40],
               [0,0,-120,20,0,0,0,True,False,40]] if path=='early' else
              [[60,-100,-80,20,100,0,0,True,False,0],
               [0,-40,-80,20,40,0,0,True,False,0],
               [0,-40,-80,20,40,40,40,True,True,0],
               [40,-40,-120,20,40,40,40,True,True,40],
               [0,0,-120,20,0,0,40,True,True,40]])
    expected=deepcopy(body['opening']); out=[]
    for command,row in zip(body['commands'],states):
        before=deepcopy(expected);cash,debt,capital,expense,outstanding,arrears,missed_amount,matured,missed,shares=row
        expected['balances']={a:'0/1' for a in mapping.values()}
        expected['balances'].update({mapping[k]:h.fmt(v) for k,v in {'cash':cash,'inventory':100,'debt':debt,'capital':capital,'interest':expense}.items()})
        expected['memory']['debt_terms'].update(outstanding=h.fmt(outstanding),arrears=h.fmt(arrears),missed_amount=h.fmt(missed_amount),matured=matured,missed=missed,new_shares=h.fmt(shares))
        event=command['event'];expected['date']=event['date'];expected['seen'].append(event['id'])
        delta=Q(expected['balances'][mapping['cash']])-Q(before['balances'][mapping['cash']])
        flows=[]
        if delta:
            flows=[{'id':runtime.digest([event['id'],command['method_key']]),'entity':expected['context']['entity'],'book':expected['context']['book'],
              'currency':'USD','event_id':event['id'],'date':event['date'],'activity':'financing','origin':command['method_key'],'amount':h.fmt(delta)}]
            expected['flows'].extend(flows)
        journal={a:h.fmt(Q(expected['balances'][a])-Q(before['balances'][a])) for a in expected['balances']}
        out.append({'after':deepcopy(expected),'journal':journal,'flows':flows})
    return out

def run():
    started=time.monotonic()
    source_paths=[ROOT/'scripts'/name for name in ['declared_company_program_v2.py','declared_financing_methods_v1.py','declared_operating_methods_v1.py','company_method_clock_v1.py','company_method_clock_v2.py','company_book_transition_v1.py','company_book_reports_v1.py','company_book_carry_v1.py','company_execution_v1.py']]
    source_paths.append(Path(fixture.__file__))
    pins={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths}
    save('settlement-source-lock.json',pins)
    original=native.Engine.apply
    native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('native fallback forbidden'))
    outputs=[]; controls=[]
    try:
        for owner in ['alpha','beta']:
            for path in ['early','late']:
                body,mapping=make(path,owner); before=deepcopy(body); result=runtime.run(body);tag=owner+'.'+path
                save('settlement-last-attempt.json',{'case':tag,'result':result})
                check(tag+'.status',result['status'],'complete_provisional')
                check(tag+'.input_unchanged',body,before)
                expected=expected_path(body,mapping,path)
                check(tag+'.event_count',len(result['trace'])-1,len(expected))
                for i,(row,want) in enumerate(zip(result['trace'],expected)):
                    transition=row['result']['transition']
                    for part in ['after','journal','flows']:check(tag+'.'+str(i)+'.'+part,transition[part],want[part])
                closing=deepcopy(expected[-1]['after']);closing['date']='2027-07-04'
                check(tag+'.complete_current',result['current'],closing)
                check(tag+'.report_index',len(result['reports']),1)
                report=result['trace'][-1]['result']
                for name,actual,want in [('assets',report['balance_sheet']['total_assets'],'100/1'),('liabilities',report['balance_sheet']['total_liabilities'],'0/1'),
                  ('equity',report['equity']['closing'],'100/1'),('profit',report['income']['profit'],'-20/1'),('cashflow',report['cash_flows']['activities']['financing']['net'],'-60/1')]:check(tag+'.report.'+name,actual,want)
                check(tag+'.replay',runtime.verify(body,result),True)
                check(tag+'.admission_flags',all(result[k] is False for k in runtime.FLAGS),True)
                outputs.append({'case':tag,'program':body,'result':result,'independent_prefixes':expected})
        early=outputs[0]['result']['current']; late=outputs[1]['result']['current']
        check('same_terminal_balances',early['balances'],late['balances'])
        check('different_missed_history',(early['memory']['debt_terms']['missed'],late['memory']['debt_terms']['missed']),(False,True))
        check('historical_missed_amount_survives',late['memory']['debt_terms']['missed_amount'],'40/1')
        check('face_is_not_carrying_at_open',outputs[0]['program']['opening']['memory']['debt_terms']['outstanding'],'100/1')
        mutations=[]
        body,mapping=make('late')
        def mutate(name,change,index):
            candidate=deepcopy(body);change(candidate);mutations.append((name,candidate,index))
        mutate('future_cash_not_spendable',lambda b:b['commands'][1]['event']['inputs']['amount']['value'].update(value='100/1'),1)
        mutate('overpayment',lambda b:b['commands'][4]['event']['inputs']['amount']['value'].update(value='41/1'),4)
        mutate('negative_payment',lambda b:b['commands'][1]['event']['inputs']['amount']['value'].update(value='-1/1'),1)
        mutate('unknown_amount',lambda b:b['commands'][1]['event']['inputs']['amount'].update(value={'status':'unknown','reason':'No settlement instruction'}),1)
        mutate('false_eligibility',lambda b:b['commands'][0]['event']['inputs']['approved']['value'].update(value=False),0)
        mutate('assessment_on_due_date',lambda b:b['commands'][2]['event'].update(date='2027-06-30'),2)
        mutate('duplicate_event',lambda b:b['commands'][2]['event'].update(id=b['commands'][1]['event']['id']),2)
        mutate('late_equity_after_payment',lambda b:b['commands'][3]['event'].update(date='2027-07-04'),4)
        mutate('payment_before_maturity',lambda b:b['commands'].__setitem__(slice(0,2),[b['commands'][1],b['commands'][0]]),0)
        def repeat_maturity(b):
            c=deepcopy(b['commands'][0]);c['event']['id']='repeated-maturity';b['commands'].insert(1,c)
        mutate('repeat_accretion',repeat_maturity,1)
        for name,candidate,index in mutations:
            untouched=deepcopy(candidate);r=runtime.run(candidate)
            check(name+'.stopped',r['status'],'stopped_provisional')
            check(name+'.index',r['stop']['index'],index)
            check(name+'.refusal_class',r['stop']['status'],
                  {'unknown_amount':'unresolved','false_eligibility':'unsupported'}.get(name,'invalid'))
            expected=candidate['opening'] if index==0 else r['trace'][-1]['result']['transition']['after']
            check(name+'.atomic_prefix',r['current'],expected)
            check(name+'.commands_preserved',r['remaining_commands'],candidate['commands'][index:])
            check(name+'.input_unchanged',candidate,untouched)
            controls.append({'case':name,'program':candidate,'result':r})
        candidate=deepcopy(body)
        del candidate['commands'][1]['event']['inputs']['amount']
        r=runtime.run(candidate)
        check('omitted_amount.static_refusal',r['status'],'invalid')
        controls.append({'case':'omitted_amount','program':candidate,'result':r})
        candidate=deepcopy(body)
        entry=candidate['registry']['entries']['settle_due']
        entry['method']['memory']['definition']['operations']=[]
        entry['method_sha256']=runtime.digest(entry['method'])
        r=runtime.run(candidate)
        check('lost_principal_reduction.stopped',r['status'],'stopped_provisional')
        check('lost_principal_reduction.index',r['stop']['index'],1)
        check('lost_principal_reduction.postcondition',r['stop']['reason'],'postconditions')
        check('lost_principal_reduction.atomic',r['current'],r['trace'][0]['result']['transition']['after'])
        controls.append({'case':'lost_principal_reduction','program':candidate,'result':r})
        # A balanced journal can still omit contract-history state: independent
        # state oracle, not runtime replay, must detect these domain mutations.
        for name,key,field in [('lost_missed_history','observe_missed','missed_amount'),('lost_share_memory','equity','new_shares')]:
            candidate=deepcopy(body);entry=candidate['registry']['entries'][key]
            ops=entry['method']['memory']['definition']['operations']
            entry['method']['memory']['definition']['operations']=[op for op in ops if op['path'][-1]!=field]
            entry['method_sha256']=runtime.digest(entry['method']);r=runtime.run(candidate)
            check(name+'.accounting_can_complete',r['status'],'complete_provisional')
            check(name+'.oracle_detects_missing_memory',r['current']['memory']!=outputs[1]['result']['current']['memory'],True)
            controls.append({'case':name,'program':candidate,'result':r,'disposition':'Domain comparator rejects despite balanced complete runtime'})
        for path,pin in pins.items():check('protected.'+path,sha256((ROOT/path).read_bytes()).hexdigest(),pin)
    finally:
        native.Engine.apply=original
    save('settlement-cases.json',outputs);save('settlement-controls.json',controls);save('settlement-checks.json',checks)
    manifest={'status':'PASS','plan':'docs/plans/accounting-gap-program-20261026.md','result':'data/accounting-master/gap-program-20261026/settlement-result.md',
      'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/gap-program-20261026/settlement_cases.py',
      'git':'unusable repository marker; no commit invented','environment':{'python':platform.python_version(),'platform':platform.platform(),'CUDA_VISIBLE_DEVICES':os.getenv('CUDA_VISIBLE_DEVICES'),'gpu':'intentionally hidden; no GPU framework imported'},
      'data_version':'E01 explicit authored contract and independent rational path table; source-lock retained','seeds':'N/A deterministic exact arithmetic',
      'wall_seconds':time.monotonic()-started,'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'cases':len(outputs),'controls':len(controls),'checks':len(checks),
      'artifacts':['settlement-cases.json','settlement-controls.json','settlement-checks.json','settlement-source-lock.json'],'scope':SCOPE}
    save('settlement-run-manifest.json',manifest)
    print(json.dumps({k:manifest[k] for k in ['status','cases','controls','checks','wall_seconds']}))

if __name__=='__main__':
    run()
