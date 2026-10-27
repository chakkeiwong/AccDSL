"""Hypothetical shared-book lease transitions; original finite method scope only."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
from jsonschema import Draft202012Validator,FormatChecker

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/lease-shared-book-20261024'
SOURCE=ROOT/'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals'
PROFILE='SharedLeaseBook/1'
EVENT='LeaseBookEvent/1'
PROPOSAL='LeaseBookProposal/1'
FLAGS={'committed':False,'source_admission':False,'accounting_admission':False,'method_eligible':False}
FOOTPRINT={'lease.reduce':{'rou','lease_liability','other_gains'},
           'lease.pay':{'cash','finance_expense','lease_liability'},
           'lease.depreciate':{'rou','depreciation'}}

class Refused(ValueError):
    def __init__(self,status,reason):self.status=status;self.reason=reason;super().__init__(reason)

def need(ok,reason,status='invalid'):
    if not ok:raise Refused(status,reason)

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return sha256(canon(x)).hexdigest()
def fmt(x):
    q=Q(x);return str(q.numerator)+'/'+str(q.denominator)
def amount(x):
    if x=='unknown':raise Refused('unresolved','required amount unknown')
    need(type(x) is str,'canonical rational string required')
    try:q=Q(x)
    except (ValueError,ZeroDivisionError):raise Refused('invalid','malformed rational')
    need(fmt(q)==x,'canonical rational required');return q
def day(x):
    if x=='unknown':raise Refused('unresolved','required date unknown')
    need(type(x) is str,'date string required')
    try:d=date.fromisoformat(x)
    except ValueError:raise Refused('invalid','malformed date')
    need(d.isoformat()==x,'canonical date required');return d
def encode(x):
    if isinstance(x,Q) or type(x) is int:return fmt(x)
    if type(x) is dict:return {k:encode(v) for k,v in x.items()}
    if type(x) is list:return [encode(v) for v in x]
    return x

def protected():
    locks=json.loads((HERE/'source-lock.json').read_text())
    scope_path=HERE/'original-scope.json'
    need(sha256(scope_path.read_bytes()).hexdigest()==locks[str(scope_path.relative_to(ROOT))],'original scope bytes changed','unsupported')
    for n in ['financial_checks.py','type_design.py','source_policy.py','semantic-contract.md']:
        p=SOURCE/n
        need(sha256(p.read_bytes()).hexdigest()==locks[str(p.relative_to(ROOT))],'original method bytes changed','unsupported')

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

protected()
financial=load('shared_lease_original_financial',SOURCE/'financial_checks.py')
types=load('shared_lease_original_types',SOURCE/'type_design.py')
SCOPE=json.loads((HERE/'original-scope.json').read_text())
SCOPE_HASH=digest(SCOPE)

def wire(value,schema):
    """Convert only fields identified as rationals by the original schema."""
    if 'anyOf' in schema:
        if value is None:return None
        return wire(value,schema['anyOf'][0])
    if schema.get('type')=='object' and set(schema.get('properties',{}))=={'n','d'}:
        q=amount(value);return {'n':str(q.numerator),'d':str(q.denominator)}
    if type(value) is dict and schema.get('type')=='object':
        return {k:wire(v,schema['properties'][k]) if k in schema['properties'] else v for k,v in value.items()}
    if type(value) is list and schema.get('type')=='array':return [wire(v,schema['items']) for v in value]
    return value

def exact(value):
    if type(value) is dict:
        if set(value)=={'n','d'}:return Q(int(value['n']),int(value['d']))
        return {k:exact(v) for k,v in value.items()}
    if type(value) is list:return [exact(v) for v in value]
    return value

def typed(value,schema):
    converted=wire(value,schema)
    need(not list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(converted)),'original closed type mismatch')
    return exact(converted)

def scope_check(state):
    protected()
    need(state['context']==SCOPE['context'],'original owner/context mismatch','unsupported')
    need(state['original_scope_sha256']==SCOPE_HASH,'original scope mismatch','unsupported')

def invariant(state):
    fields={'profile','context','original_scope_sha256','period','date','balances','leases',
      'collection_complete','membership_premise','funding_policy','seen','flows','conditional'}
    need(type(state) is dict and set(state)==fields,'closed shared-book fields')
    need(state['profile']==PROFILE and state['conditional'] is True,'conditional book profile')
    scope_check(state)
    need(state['funding_policy']=='no_overdraft','unsupported funding policy','unsupported')
    if state['collection_complete'] is not True:
        need(state['collection_complete'] is False or state['collection_complete'] is None or (type(state['collection_complete']) is str and state['collection_complete']=='unknown'),'collection coverage type')
        raise Refused('unresolved','lease collection incomplete')
    need(type(state['membership_premise']) is str and bool(state['membership_premise'].strip()),'missing membership premise','unresolved')
    period=state['period'];need(type(period) is dict and set(period)=={'start','end_exclusive'},'closed execution period')
    start,end=day(period['start']),day(period['end_exclusive']);now=day(state['date'])
    need(day(SCOPE['source_period_start'])<=start<end<=day(SCOPE['source_period_end_exclusive']),'outside retained source period','unsupported')
    need(start<=now<end,'state outside execution period')
    balances=state['balances'];need(type(balances) is dict and set(balances)==set(types.ACCOUNTS),'complete original account registry')
    values={k:amount(v) for k,v in balances.items()}
    need(sum(values.values())==0,'shared book unbalanced')
    need(values['cash']>=0,'shared cash shortage','funding_failure')
    leases=state['leases'];need(type(leases) is list,'lease collection required')
    ids=set();rou=Q(0);liability=Q(0)
    for item in leases:
        need(type(item) is dict and set(item)=={'component','instantiation_premise'},'closed lease membership')
        need(type(item['instantiation_premise']) is str and item['instantiation_premise'].strip(),'lease instantiation premise missing','unresolved')
        component=typed(item['component'],types.COMPONENTS['lease'])
        ident=component['lease_id'];need(ident not in ids,'duplicate lease identity');ids.add(ident)
        local_rou=sum(r['rou'] for r in component['rights']);local_liability=sum(r['liability'] for r in component['rights'])
        try:financial.check_component('lease',component,{'rou':local_rou,'lease_liability':-local_liability})
        except AssertionError:raise Refused('invalid','lease rights/allocation invalid')
        for right in component['rights']:need(day(right['last_measurement_date'])<=now,'right measurement follows book date')
        rou+=local_rou;liability+=local_liability
    need(values['rou']==rou and values['lease_liability']==-liability,'complete lease allocation mismatch')
    seen=state['seen'];need(type(seen) is list and all(type(x) is str and x for x in seen) and len(seen)==len(set(seen)),'lifetime event identities')
    flows=state['flows'];need(type(flows) is list,'flow collection')
    for flow in flows:
        need(type(flow) is dict and set(flow)=={'event_id','date','activity','amount','origin','lease_id'},'closed gross flow fields')
        need(flow['event_id'] in seen and flow['lease_id'] in ids,'flow identity')
        need(flow['activity'] in types.CASH and type(flow['origin']) is str and flow['origin'],'flow classification')
        need(start<=day(flow['date'])<=now,'flow date outside prefix')
        amount(flow['amount'])
    return state

def original_need(ok,reason,status='rejected'):
    if not ok:raise Refused('unresolved' if status=='partial' else status,reason)

def _proposal(state,event):
    invariant(state)
    need(type(event) is dict and set(event)=={'profile','id','kind','method','lease_id','date','parameters','original_scope_sha256'},'closed lease event')
    need(event['profile']==EVENT and event['kind']=='lease','lease event profile')
    need(event['original_scope_sha256']==SCOPE_HASH,'event source/method scope mismatch','unsupported')
    need(type(event['id']) is str and event['id'] and event['id'] not in state['seen'],'new event identity required')
    method=event['method'];need(type(method) is str and method in FOOTPRINT,'method outside lease reference','unsupported')
    now=day(event['date']);need(day(state['date'])<=now<day(state['period']['end_exclusive']),'event outside ordered execution period')
    need(type(event['lease_id']) is str,'lease identifier')
    selected=[i for i,x in enumerate(state['leases']) if x['component']['lease_id']==event['lease_id']]
    need(len(selected)==1,'lease identity absent');index=selected[0]
    component=typed(state['leases'][index]['component'],types.COMPONENTS['lease'])
    need(all(day(r['last_measurement_date'])<=now for r in component['rights']),'event precedes right measurement')
    parameters=typed(event['parameters'],types.EVENTS[method][1])
    after,journal,cash,oci,equity=financial.derive('lease',component,method,parameters,event['date'],original_need)
    need(set(journal)<=FOOTPRINT[method],'original method footprint changed','unsupported')
    need(all(v==0 for v in [*oci.values(),*equity.values()]),'unexpected reserve effect','unsupported')
    need(sum(journal.values())==0 and journal.get('cash',Q(0))==sum(cash.values()),'invalid original monetary effects')
    z=deepcopy(state);z['date']=event['date'];z['seen'].append(event['id'])
    z['leases'][index]['component']=encode(after)
    z['balances']={k:fmt(amount(v)+journal.get(k,Q(0))) for k,v in state['balances'].items()}
    flows=[{'event_id':event['id'],'date':event['date'],'activity':k,'amount':fmt(v),'origin':method,'lease_id':event['lease_id']} for k,v in cash.items() if v]
    z['flows'].extend(flows);invariant(z)
    return {'profile':PROPOSAL,'before_sha256':digest(state),'event_sha256':digest(event),
      'original_scope_sha256':SCOPE_HASH,'method_ref':deepcopy(SCOPE['methods'][method]),
      'journal':{k:fmt(journal.get(k,Q(0))) for k in types.ACCOUNTS},'flows':flows,'after':z,**deepcopy(FLAGS)}

def propose(state,event):
    try:return {'status':'proposed','proposal':_proposal(state,event),**deepcopy(FLAGS)}
    except Refused as exc:return {'status':exc.status,'reason':exc.reason,'proposal':None,**deepcopy(FLAGS)}
    except (KeyError,TypeError,ValueError,RecursionError) as exc:
        return {'status':'invalid','reason':'malformed closed input: '+type(exc).__name__,'proposal':None,**deepcopy(FLAGS)}

def apply(state,event,proposal):
    expected=_proposal(state,event)
    need(type(proposal) is dict and canon(proposal)==canon(expected),'proposal differs from original complete replay')
    return deepcopy(expected['after'])

def run_prefix(opening,events):
    need(type(events) is list,'ordered event list required')
    state=deepcopy(opening);proposals=[]
    for index,event in enumerate(events):
        result=propose(state,event)
        if result['status']!='proposed':
            return {'status':result['status'],'reason':result['reason'],'failed_event_index':index,
              'state':state,'proposals':proposals,'complete':False,**deepcopy(FLAGS)}
        proposal=result['proposal'];state=apply(state,event,proposal);proposals.append(proposal)
    invariant(state)
    return {'status':'hypothetical_sequence_complete','state':state,'proposals':proposals,'complete':True,**deepcopy(FLAGS)}
