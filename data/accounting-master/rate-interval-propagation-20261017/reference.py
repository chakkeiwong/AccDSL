"""Read-only documentary dated credit schedules; no production posting."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
from bounds import I,day,between,pv,solve_rate

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
COMMON={'amortised_cost','integral_cash_classified','complete_contract_and_expected_cash',
        'information_view_valid','no_modification_fx_tax','no_initial_writeoff_required'}
EVENT_FINDINGS={'information_view_valid','no_earlier_writeoff_required','complete_cash_since_previous',
                'unchanged_terms','no_writeoff_required_after_event'}

class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason

def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(obj,keys,reason):
    if not isinstance(obj,dict) or set(obj)!=set(keys):fail(reason)
def number(v,name):
    if v is None:fail('missing_'+name,'unresolved')
    if not isinstance(v,str) or len(v)>80:fail('number_encoding')
    try:q=Q(v)
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if str(q)!=v:fail('number_encoding')
    if abs(q)>10**12:fail('number_budget','unsupported')
    return q
def positive(v,name):
    q=number(v,name)
    if q<0:fail('negative_'+name)
    return q
def date_value(v):
    try:return day(v)
    except (TypeError,ValueError):fail('date_encoding')
def findings(f,keys):
    shape(f,keys,'finding_shape')
    for k,v in f.items():
        if v is None:fail('missing_'+k,'unresolved')
        if type(v)!=bool:fail('finding_encoding')
        if not v:fail('outside_'+k,'unsupported')
def flows(obj,at,allow_zero_date=False):
    if obj is None:fail('missing_schedule','unresolved')
    if not isinstance(obj,dict) or len(obj)>64:fail('schedule_shape')
    result={}
    for d,v in obj.items():
        if date_value(d)<date_value(at) or (d==at and not allow_zero_date):fail('schedule_chronology')
        if (date_value(d)-date_value(at)).days>7305:fail('schedule_horizon','unsupported')
        result[d]=positive(v,'cash')
    return result
def encoded(x):
    if isinstance(x,I):return x.wire()
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
    if isinstance(x,list):return [encoded(v) for v in x]
    return x

def calculate(req,reader=None):
    try:return _calculate(req,reader or (lambda p:(ROOT/p).read_bytes()))
    except Refusal as e:return dict(status=e.status,reason=e.reason,closing=None,stages=[],journals=[],cash_flows=[],mutations=[],posts=False)
    except (ValueError,ZeroDivisionError):return dict(status='rejected',reason='numeric_or_date_domain',closing=None,stages=[],journals=[],cash_flows=[],mutations=[],posts=False)

def _calculate(req,reader):
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        try:raw=reader(row['path'])
        except FileNotFoundError:fail('missing_protected_input','unresolved')
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:fail('changed_protected_input')
    shape(req,{'wire','operation','context','opening_cash','acquisition','numerical','events'},'request_shape')
    if req['wire'] not in ('POCIDatedIntervalSchedule/1','PerformingEIRIntervalSchedule/1'):fail('wire')
    poci=req['wire']=='POCIDatedIntervalSchedule/1'
    if req['operation']!='report':fail('report_only')
    context=req['context'];shape(context,{'entity','book','currency','unit','rule','contract','calendar'},'context_shape')
    if any(not isinstance(v,str) or not v for v in context.values()):fail('context_encoding')
    if context['unit']!='currency units' or context['calendar']!='ACT/365F-annual-compound' or context['rule']!='EU2023/1803-original-IFRS9':fail('context')
    num=req['numerical'];shape(num,{'scale','max_width','initial_pv_tolerance'},'numerical_shape')
    scale=num['scale'];limit=positive(num['max_width'],'max_width');tol=positive(num['initial_pv_tolerance'],'initial_pv_tolerance')
    if type(scale)!=int or not 12<=scale<=24 or not 0<limit<=Q(1,1000) or tol>Q(1,1000):fail('numerical_budget','unsupported')
    if tol!=0:fail('approximate_initial_rate_not_admitted','unsupported')
    a=req['acquisition'];shape(a,{'date','price','cost','fee_received','rate_search','contract','expected','findings'},'acquisition_shape')
    findings(a['findings'],COMMON|({'poci_at_origin','price_equals_fair_value'} if poci else {'zero_credit_loss_assessed','performing_at_origin'}))
    start=a['date'];date_value(start);t=start
    price=positive(a['price'],'price');cost=positive(a['cost'],'cost');fee=positive(a['fee_received'],'fee_received')
    initial=price+cost-fee;opening=positive(req['opening_cash'],'opening_cash')
    if initial<=0:fail('acquisition_domain')
    if opening<initial:fail('funding_required','unsupported')
    contract=flows(a['contract'],t);expected=flows(a['expected'],t)
    if not contract or not expected:fail('initial_cash_required')
    if any(v>contract.get(d,Q(0)) for d,v in expected.items()):fail('expected_exceeds_contract')
    if not poci and expected!=contract:fail('performing_expected_contract')
    search=a['rate_search'];shape(search,{'lower','upper','max_width'},'rate_search_shape')
    low=number(search['lower'],'rate_lower');high=number(search['upper'],'rate_upper')
    width=positive(search['max_width'],'rate_width')
    if low<=-1 or high>10 or low>=high or not 0<width<=Q(1,1000):fail('rate_search_domain','unsupported')
    try:certificate=solve_rate(expected,t,initial,low,high,width,scale)
    except ValueError as error:fail(str(error),'unsupported')
    r=I(Q(certificate['rate']['lower']),Q(certificate['rate']['upper']))
    residual=pv(expected,t,r,scale)-initial
    if not residual.contains(0):fail('initial_pv_certificate_mismatch')
    G=I.point(initial);L=I.point(0);cash=opening-initial;interest=I.point(0);impairment=I.point(0);catchup=I.point(0)
    stages=[];journals=[];cash_flows=[dict(date=t,kind='price',amount=-price),dict(date=t,kind='integral_cost',amount=-cost),dict(date=t,kind='integral_fee',amount=fee)]
    origins=[dict(date=t,kind='initial',amount=I.point(initial))];closed=False;uncollected=[];written_off=[]
    def journal(id,date,entries):journals.append(dict(id=id,date=date,entries=entries))
    journal('acquisition',t,dict(gross=G,cash=I.point(-initial)))
    def stage(id,kind):
        N=G-L;profit=interest+impairment+catchup
        direct_g=sum((x['amount']*between(r,x['date'],t,scale) for x in origins),I.point(0))
        direct_n=pv(expected,t,r,scale) if not closed else I.point(0)
        row=dict(id=id,kind=kind,date=t,gross=G,allowance=L,net=N,cash=I.point(cash),interest=interest,
                 impairment=impairment,catchup=catchup,profit=profit,equity=I.point(opening)+profit,
                 direct_gross=direct_g,direct_net=direct_n,remaining_contract=contract.copy(),expected=expected.copy())
        for x in row.values():
            if isinstance(x,I) and x.width>limit:fail('monetary_width_exceeded','unsupported')
        if not G.overlaps(direct_g):fail('gross_origin_identity')
        # Root equality is certified; interval widths include numerical dependence inflation.
        bound=I(-tol,tol)*between(r,start,t,scale)
        if not (N-direct_n).overlaps(bound):fail('net_pv_identity')
        if not (I.point(cash)+N-(I.point(opening)+profit)).contains(0):fail('financial_identity')
        stages.append(row)
    stage('acquisition','initial')
    if not isinstance(req['events'],list) or not 1<=len(req['events'])<=128:fail('events_shape')
    seen={'acquisition'}
    for e in req['events']:
        if not isinstance(e,dict):fail('event_shape')
        kind=e.get('operation');extras={'advance':set(),'credit_revision':{'expected','writeoff'},'estimate_revision':{'expected'},'collect':{'amount','close'}}
        if kind not in extras:fail('event_operation')
        shape(e,{'id','operation','date','information_date','context','findings'}|extras[kind],'event_shape')
        id=e['id']
        if not isinstance(id,str) or not id or id in seen or id.endswith('_accrual'):fail('event_id')
        seen.add(id)
        if closed:fail('event_after_close')
        if e['context']!=context:fail('event_context')
        findings(e['findings'],EVENT_FINDINGS)
        nt=e['date'];date_value(nt)
        if date_value(nt)<date_value(t):fail('event_chronology')
        if not date_value(start)<=date_value(e['information_date'])<=date_value(nt):fail('future_information')
        if (date_value(nt)-date_value(start)).days>7305:fail('event_horizon','unsupported')
        if any(date_value(d)<date_value(nt) and v for d,v in expected.items()):fail('missed_expected_cash')
        f=between(r,t,nt,scale);dG=G*(f-1);dL=L*(f-1);earned=(G-L)*(f-1)
        G=G*f;L=L*f;interest=interest+earned;t=nt
        journal(id+'_accrual',t,dict(gross=dG,allowance=-dL,interest=-earned))
        stage(id+'_accrual','accrual')
        if kind=='advance':
            if expected.get(t,0):fail('due_cash_must_be_resolved')
        elif kind=='credit_revision':
            if not poci:fail('credit_profile','unsupported')
            new=flows(e['expected'],t,True)
            if any(v>contract.get(d,0) for d,v in new.items()):fail('expected_exceeds_contract')
            oldN=G-L;newN=pv(new,t,r,scale);gain=newN-oldN;L=G-newN;impairment=impairment+gain;expected=new
            journal(id+'_credit',t,dict(allowance=gain,impairment=-gain))
            w=e['writeoff'];shape(w,{'fraction','portion_id','no_reasonable_recovery','portion_expected_cash'},'writeoff_shape')
            fraction=positive(w['fraction'],'writeoff_fraction')
            if fraction>1:fail('writeoff_fraction')
            if fraction:
                if w['no_reasonable_recovery'] is None:fail('missing_no_recovery','unresolved')
                if w['no_reasonable_recovery'] is not True:fail('no_recovery_finding_required','unsupported')
                if not isinstance(w['portion_id'],str) or not w['portion_id']:fail('writeoff_portion_identity')
                if positive(w['portion_expected_cash'],'portion_expected_cash')!=0:fail('writeoff_expected_cash_nonzero')
                written_off.append(dict(date=t,portion_id=w['portion_id'],contractual_cash={d:v*fraction for d,v in contract.items()}))
                contract={d:v*(1-fraction) for d,v in contract.items()}
                if any(v>contract.get(d,0) for d,v in expected.items()):fail('expected_exceeds_surviving_contract')
                W=G*fraction;G=G-W;L=L-W
                origins.append(dict(date=t,kind='writeoff',amount=-W))
                journal(id+'_writeoff',t,dict(gross=-W,allowance=W))
                if fraction==1:
                    if any(expected.values()):fail('full_writeoff_has_cash')
                    G=L=I.point(0);closed=True
            else:
                if w!={'fraction':'0','portion_id':None,'no_reasonable_recovery':None,'portion_expected_cash':'0'}:fail('zero_writeoff_shape')
                if not any(expected.values()):fail('earlier_writeoff_required','unsupported')
        elif kind=='estimate_revision':
            if poci:fail('noncredit_poci_revision_outside_profile','unsupported')
            new=flows(e['expected'],t)
            if not new:fail('estimate_cash_required')
            # Supplied unchanged-terms finding admits this prepayment option schedule.
            if any(d>max(contract) for d in new):fail('estimate_maturity_extension','unsupported')
            newG=pv(new,t,r,scale);gain=newG-G;G=newG;catchup=catchup+gain
            origins.append(dict(date=t,kind='noncredit_catchup',amount=gain));expected=new;contract=new.copy()
            journal(id+'_estimate',t,dict(gross=gain,catchup=-gain))
        else:
            amount=positive(e['amount'],'collection')
            if type(e['close'])!=bool:fail('close_encoding')
            if expected.get(t)!=amount:fail('cash_expectation_mismatch')
            if amount>contract.get(t,0):fail('cash_contract_mismatch')
            cash+=amount;G=G-amount
            origins.append(dict(date=t,kind='collection',amount=I.point(-amount)))
            cash_flows.append(dict(date=t,kind='collection',amount=amount))
            journal(id+'_cash',t,dict(cash=I.point(amount),gross=I.point(-amount)))
            expected.pop(t)
            uncollected.append(dict(due_date=t,amount=contract.pop(t,Q(0))-amount,legal_forgiveness='not_assessed'))
            if e['close']:
                if any(expected.values()):fail('close_has_expected_cash')
                if not (G-L).overlaps(I(-tol,tol)*between(r,start,t,scale)):fail('close_net_residual')
                origins.append(dict(date=t,kind='settlement_allowance_clear',amount=-L))
                journal(id+'_clear',t,dict(gross=-L,allowance=L))
                G=L=I.point(0);closed=True
            elif not any(expected.values()):fail('terminal_close_required')
        stage(id,kind)
    return encoded(dict(status='conditional_complete',reason='finite_dated_interval_profile',context=context,wire=req['wire'],
                        rate_certificate=certificate,shared_rate=r,interval_semantics='one immutable original root; marginal enclosures are not independently selectable amounts',
                        initial_pv_residual=residual,initial_credit_shortfall=pv(flows(a['contract'],start),start,r,scale)-initial if poci else I.point(0),
                        numerical=num,closing=stages[-1],stages=stages,journals=journals,cash_flows=cash_flows,origins=origins,
                        factor_bounds=[dict(start=start,end=s['date'],factor=between(r,start,s['date'],scale)) for s in stages],
                        financial_derecognized=closed,uncollected_contract=uncollected,writeoff_contract=written_off,
                        legal_forgiveness='not_assessed',posts=False,mutations=[]))
