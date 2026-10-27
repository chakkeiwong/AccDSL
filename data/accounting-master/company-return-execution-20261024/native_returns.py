"""Finite shared-book reference methods; no I/O, production storage or forecasts."""
from copy import deepcopy
from datetime import date,timedelta
from fractions import Fraction as Q
from hashlib import sha256
import json

ACCOUNTS=['cash','inventory','ppe','recovery_asset','investment','dta','dtl',
 'refund_liability','debt','receivable','payable','capital','retained',
 'original_equity','revenue','cogs','selling_expense','wages','depreciation',
 'finance_expense','current_tax','deferred_tax']
INCOME=['revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax']
ASSETS=['cash','inventory','ppe','recovery_asset','investment','dta','receivable']
LIABILITIES=['dtl','refund_liability','debt','payable']
EQUITY=['capital','retained','original_equity']
FINDINGS=['rate_enacted','recovery_supported','temporary_difference_inventory_complete',
 'outside_basis_timing_control','outside_basis_no_foreseeable_reversal']
PROFILE='NativeReturnBookReference/1'
METHOD='ReturnReferenceMethods/1'

class Rejected(ValueError):
    def __init__(self,status,reason):self.status=status;self.reason=reason;super().__init__(reason)
def need(ok,reason,status='invalid'):
    if not ok:raise Rejected(status,reason)
def q(x):
    if x=='unknown':raise Rejected('unresolved','required amount unknown')
    need(type(x) is str,'rational string required')
    try:v=Q(x)
    except (ValueError,ZeroDivisionError):raise Rejected('invalid','malformed rational')
    need(x==fmt(v),'canonical rational required');return v
def fmt(x):
    v=Q(x);return str(v.numerator)+'/'+str(v.denominator)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return sha256(canon(x)).hexdigest()
def yes(x,label):
    if x=='unknown':raise Rejected('unresolved',label)
    need(type(x) is bool,'Boolean finding required')
    need(x,label,'unsupported')
def profit(b):return -sum(q(b[k]) for k in INCOME)
def pretax(b):return -sum(q(b[k]) for k in INCOME if k not in ['current_tax','deferred_tax'])

def invariant(s):
    fields={'profile','context','source','period','date','balances','component','lots','other_inventory',
        'tax_premises','tax_adjustments','tax_closed_until','seen','flows','opening_interest_remaining',
        'opening_interest_paid','prior_years','conditional'}
    need(type(s) is dict and set(s)==fields,'closed state fields')
    need(s['profile']==PROFILE and s['conditional'] is True,'state profile');b=s['balances']
    need(set(b)==set(ACCOUNTS),'closed account registry')
    need(set(ASSETS+LIABILITIES+EQUITY+INCOME)==set(ACCOUNTS),'account classification coverage')
    need(len(ASSETS+LIABILITIES+EQUITY+INCOME)==len(ACCOUNTS),'account classification overlap')
    need(sum(q(v) for v in b.values())==0,'book balance')
    need(q(b['cash'])>=0,'cash shortfall','funding_failure')
    need(q(s['other_inventory'])>=0,'negative other inventory')
    need(q(b['inventory'])==q(s['other_inventory'])+sum(q(l['carrying']) for l in s['lots'].values()),'inventory allocation')
    c=s['component'];need(q(b['refund_liability'])==-q(c['refund']),'refund allocation')
    need(q(b['recovery_asset'])==q(c['recovery']),'recovery allocation')
    need(type(c['settled']) is bool,'unknown settlement memory','unresolved')
    if c['settled']:need(q(c['refund'])==q(c['recovery'])==0,'settled rights remain')
    for key,lot in s['lots'].items():
        need(key==lot['id'] and lot['component_id']==c['id'],'lot identity')
        need(q(lot['units'])>=0 and q(lot['carrying'])>=0,'lot amount domain')
        need(q(lot['tax_base'])==q(lot['carrying']),'lot tax method','unsupported')
        need(type(lot['disposed']) is bool,'lot disposition type')
        if lot['disposed']:need(q(lot['units'])==q(lot['carrying'])==q(lot['tax_base'])==0,'disposed stock remains')
        else:need(q(lot['units'])>0,'empty live lot')
    need(len(s['seen'])==len(set(s['seen'])),'duplicate lifetime event')
    ids=[x['event_id'] for x in s['tax_adjustments']]
    need(len(ids)==len(set(ids)) and set(ids)<=set(s['seen']),'tax adjustment identity')
    return s

def initialize(authoring,opening,opening_interest):
    # Source correspondence is the caller's separately checked responsibility.
    from return_schema import validate,assess
    validate(authoring);a=assess(authoring)
    need(a['status']!='invalid','invalid authoring')
    b={k:fmt(v) for k,v in opening.items()};c=deepcopy(authoring['component'])
    need(set(b)==set(ACCOUNTS),'opening registry')
    need(all(q(b[k])==0 for k in INCOME),'nonzero opening income')
    need(q(b['dta'])==q(authoring['tax']['opening_dta']),'opening DTA allocation')
    need(-q(b['dtl'])==q(authoring['tax']['opening_dtl']),'opening DTL allocation')
    lots={l['id']:{**deepcopy(l),'disposed':False} for l in authoring['lots']}
    s={'profile':PROFILE,'context':deepcopy(authoring['context']),'source':deepcopy(authoring['source']),
       'period':deepcopy(authoring['period']),'date':authoring['period']['start'],
       'balances':b,'component':c,'lots':lots,'other_inventory':fmt(q(b['inventory'])-sum(q(l['carrying']) for l in lots.values())),
       'tax_premises':deepcopy(authoring['tax']),'tax_adjustments':[],'tax_closed_until':authoring['period']['start'],
       'seen':[],'flows':[],'opening_interest_remaining':fmt(opening_interest),'opening_interest_paid':'0/1',
       'prior_years':[],'conditional':True}
    need(q(s['opening_interest_remaining'])>=0,'opening interest domain')
    return invariant(s)

def transition(s,event,adapter=None):
    invariant(s);z=deepcopy(s)
    base={'id','kind','method','date'}
    extra={'settle':{'source_pointer','component_id','lot_id','actual_units','unit_handling','unit_deterioration','refund_cash','handling_cash','inventory_nrv','all_rights_closed','handling_is_selling_cost'},
        'sell':{'source_pointer','lot_id','fraction','proceeds','performance_complete'},
        'tax':{'start','end_exclusive','rate',*FINDINGS},'surrounding':{'retained_event'}}
    need(type(event) is dict and base<=set(event),'event object and required fields')
    need(type(event['kind']) is str and event['kind'] in extra,'unknown event kind','unsupported')
    need(set(event)==base|extra[event['kind']],'closed event fields')
    need(type(event['id']) is str and event['id'],'event identity')
    need(event['id'] not in s['seen'],'duplicate event')
    try:day=date.fromisoformat(event['date'])
    except (ValueError,TypeError):raise Rejected('invalid','malformed event date')
    need(day.isoformat()==event['date'],'canonical event date')
    need(s['period']['start']<=event['date']<s['period']['end_exclusive'],'event outside period')
    need(event['date']>=s['date'] and event['date']>=s['tax_closed_until'],'event precedes close or state')
    j={k:Q(0) for k in ACCOUNTS};flows=[];b=s['balances'];c=z['component']
    def post(k,x):need(k in j,'unknown account');j[k]+=Q(x)
    def cash(amount,origin,activity='operating'):
        post('cash',amount);flows.append({'entity':s['context']['entity'],'activity':activity,'amount':fmt(amount),'origin':origin,'date':event['date'],'event_id':event['id']})
    if event['kind']=='settle':
        need(event['method']=='returns.settle','settlement method')
        need(event['component_id']==c['id'] and not c['settled'],'component already settled or changed')
        need(event['lot_id'] not in z['lots'],'duplicate lot')
        yes(event['all_rights_closed'],'return rights incomplete');yes(event['handling_is_selling_cost'],'handling classification')
        n,h,d=[q(event[k]) for k in ['actual_units','unit_handling','unit_deterioration']]
        need(0<n<=q(c['sold_units']) and h>=0 and 0<=d<=q(c['unit_cost']),'settlement quantities')
        nrv=q(event['inventory_nrv']);need(nrv>=0,'negative NRV')
        refund=n*q(c['unit_refund']);handling=n*h;v=min(n*(q(c['unit_cost'])-d),nrv)
        need(q(event['refund_cash'])==refund and q(event['handling_cash'])==handling,'cash facts disagree')
        f,r=q(c['refund']),q(c['recovery'])
        for k,x in [('refund_liability',f),('recovery_asset',-r),('inventory',v),('revenue',refund-f),('cogs',r-v),('selling_expense',handling)]:post(k,x)
        cash(-refund,'refund');cash(-handling,'handling')
        c.update(refund='0/1',recovery='0/1',settled=True)
        z['lots'][event['lot_id']]={'id':event['lot_id'],'component_id':c['id'],'units':fmt(n),'carrying':fmt(v),'tax_base':fmt(v),'acquired':event['date'],'disposed':False}
        z['tax_adjustments'].append({'event_id':event['id'],'date':event['date'],'amount':fmt(r-f)})
    elif event['kind']=='sell':
        need(event['method']=='inventory.sell','sale method');yes(event['performance_complete'],'sale performance')
        need(q(event['fraction'])==1,'whole lot method only','unsupported')
        need(event['lot_id'] in z['lots'],'unknown lot');lot=z['lots'][event['lot_id']]
        need(not lot['disposed'],'lot already disposed')
        v=q(event['proceeds']);cost=q(lot['carrying']);need(v>=0,'negative sale proceeds')
        cash(v,'external_sale');post('revenue',-v);post('inventory',-cost);post('cogs',cost)
        lot.update(units='0/1',carrying='0/1',tax_base='0/1',disposed=True)
    elif event['kind']=='tax':
        t=s['tax_premises']
        need(event['method']=='tax.close','tax method')
        for k in FINDINGS:yes(t[k],k);yes(event[k],k)
        need(t['method']=='refund_and_recovered_stock_on_settlement','tax timing method','unsupported')
        need(q(t['refund_tax_base'])==q(t['recovery_tax_base'])==0,'tax base method','unsupported')
        rate=q(t['rate']);need(rate==q(event['rate'])==Q(1,4),'retained tax rate only','unsupported')
        need(c['settled'],'return settlement needed before tax','unresolved')
        end=event['end_exclusive'];need(event['start']==s['tax_closed_until'],'noncontiguous tax period')
        need(event['start']<end<=s['period']['end_exclusive'],'tax end')
        need(day==date.fromisoformat(end)-timedelta(days=1),'tax cutoff date')
        adj=sum(q(x['amount']) for x in s['tax_adjustments'] if s['period']['start']<=x['date']<end)
        current=(pretax(b)+adj)*rate-q(b['current_tax'])
        need(current>=0,'tax refund route unsupported','unsupported')
        post('current_tax',current);cash(-current,'income_tax')
        post('dta',-q(b['dta']));post('dtl',-q(b['dtl']));post('deferred_tax',q(b['dta'])+q(b['dtl']))
        z['tax_closed_until']=end
    elif event['kind']=='surrounding':
        need(adapter is not None,'trusted surrounding method required','unsupported')
        delta=adapter(deepcopy(s),deepcopy(event))
        need(set(delta)=={'journal','flows','prior_interest'},'adapter fields')
        need(set(delta['journal'])==set(ACCOUNTS),'adapter registry')
        for k,x in delta['journal'].items():post(k,q(x))
        for f in delta['flows']:
            need(set(f)=={'entity','activity','amount','origin'},'adapter flow fields')
            need(f['entity']==s['context']['entity'],'adapter flow owner')
            flows.append({**f,'date':event['date'],'event_id':event['id']})
        need(all(j[k]==0 for k in ['refund_liability','recovery_asset','dta','dtl','current_tax','deferred_tax']),'adapter changed native allocation')
        z['other_inventory']=fmt(q(s['other_inventory'])+j['inventory'])
        interest=q(delta['prior_interest']);need(0<=interest<=q(s['opening_interest_remaining']),'opening interest allocation')
        need(interest<=-sum(q(f['amount']) for f in flows if f['origin']=='interest'),'interest exceeds payment')
        z['opening_interest_remaining']=fmt(q(s['opening_interest_remaining'])-interest)
        z['opening_interest_paid']=fmt(q(s['opening_interest_paid'])+interest)
    else:raise Rejected('unsupported','event method not selected')
    need(sum(j.values())==0,'unbalanced proposal')
    need(j['cash']==sum(q(f['amount']) for f in flows),'gross cash mismatch')
    need(all(f['activity'] in ['operating','investing','financing'] for f in flows),'cash classification')
    z['balances']={k:fmt(q(b[k])+j[k]) for k in ACCOUNTS}
    z['seen'].append(event['id']);z['date']=event['date'];z['flows'].extend(flows);invariant(z)
    return z,{k:fmt(v) for k,v in j.items()},flows

def propose(s,event,adapter=None):
    after,journal,flows=transition(s,event,adapter)
    return {'profile':'ReturnTransitionProposal/1','method_bundle':METHOD,'before_sha256':digest(s),
        'event_sha256':digest(event),'event':deepcopy(event),'journal':journal,'flows':flows,'after':after,'committed':False}

def apply(s,event,proposal,adapter=None):
    expected=propose(s,event,adapter)
    need(canon(proposal)==canon(expected),'proposal fails trusted semantic replay')
    return deepcopy(expected['after'])

def run_prefix(opening,events,adapters=None):
    """A rejected event returns its preceding state and explicit failure."""
    state=deepcopy(opening);proposals=[];adapters=adapters or {}
    for event in events:
        try:
            p=propose(state,event,adapters.get(event['id']))
            state=apply(state,event,p,adapters.get(event['id']));proposals.append(p)
        except Rejected as exc:
            return {'status':exc.status,'reason':exc.reason,'failed_event':event['id'],
                'state':state,'proposals':proposals,'complete_annual_opening':False}
    return {'status':'events_executed','state':state,'proposals':proposals,
        'complete_annual_opening':False}
