"""Finite synthetic return/lease book; original kernels, shared balances, pure apply."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as Q
import json
import module_invocation_v1 as caller
import typed_return_transition_v1 as returns
import lease_shared_book_v1 as lease

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-book-successor-20261024'
LOCK='915afa6bfe4462f7ec1c85b18f528f8aae032954bc5cf1c7fbf2811ebd5e25d0'
PROFILE='SyntheticReturnLeaseBook/1';EVENT='SyntheticReturnLeaseEvent/1'
ACCOUNTS=returns.structure.native.ACCOUNTS+['rou','lease_liability','other_gains']
FLAGS={'committed':False,'physical_durability':False,'source_admission':False,
       'accounting_admission':False,'method_eligible':False}
CONTEXT={'entity':'Synthetic-Return-Lease','book_role':'legal','currency':'USD','case_id':'shared_book_successor'}

class Refused(ValueError):
    def __init__(self,status,reason):self.status=status;self.reason=reason;super().__init__(reason)
def need(ok,why,status='invalid'):
    if not ok:raise Refused(status,why)
def protected():
    raw=(HERE/'source-lock.json').read_bytes();need(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'source_changed:'+name)
def digest(x):return caller.digest(x)
def fmt(x):return lease.fmt(x)
def amount(x):return lease.amount(x)

def schema():
    shape=returns.structure.schema();p=shape['properties'];record=returns.structure.author.closed
    text={'type':'string','minLength':1,'maxLength':4096};rat=deepcopy(p['other_inventory']);day=deepcopy(p['date'])
    p['profile']={'const':PROFILE}
    p['source']=record({'meaning':{'const':'declared_synthetic_book'},'premise':text,'numeric_lineage':text})
    p['balances']=record({k:deepcopy(rat) for k in ACCOUNTS})
    right=record({'right_id':text,'rou':rat,'liability':rat,'rate':rat,'last_measurement_date':day})
    member=record({'component':record({'lease_id':text,'rights':{'type':'array','items':right}}),'instantiation_premise':text})
    p['leases']={'type':'array','items':member}
    p['lease_membership']={'oneOf':[{'type':'boolean'},{'const':'unknown'}]}
    p['lease_membership_premise']=text
    shape['required']=list(p)
    return shape

def invariant(state):
    caller.bounded(state);returns.structure.validate(state,schema())
    need(state['context']==CONTEXT,'declared_context_only','unsupported')
    now=lease.day(state['date']);start=lease.day(state['period']['start']);end=lease.day(state['period']['end_exclusive'])
    need(start<=now<end,'state_date_outside_period')
    need(start<=lease.day(state['tax_closed_until'])<=now,'tax_close_date')
    b={k:amount(v) for k,v in state['balances'].items()}
    need(sum(b.values())==0,'shared_book_unbalanced')
    need(b['cash']>=0,'shared_cash_shortage','funding_failure')
    c=state['component'];lots=state['lots']
    need(amount(state['other_inventory'])>=0,'negative_other_inventory')
    need(b['inventory']==amount(state['other_inventory'])+sum(amount(l['carrying']) for l in lots.values()),'inventory_allocation')
    need(b['refund_liability']==-amount(c['refund']) and b['recovery_asset']==amount(c['recovery']),'return_allocation')
    if c['settled']:need(amount(c['refund'])==amount(c['recovery'])==0,'settled_rights_remain')
    for key,l in lots.items():
        need(key==l['id'] and l['component_id']==c['id'],'lot_identity')
        need(amount(l['units'])>=0 and amount(l['carrying'])>=0 and amount(l['tax_base'])==amount(l['carrying']),'lot_amount_or_tax_method')
        need(lease.day(l['acquired'])<=now,'future_lot')
        need((amount(l['units'])==amount(l['carrying'])==amount(l['tax_base'])==0) if l['disposed'] else amount(l['units'])>0,'lot_disposition')
    need(state['lease_membership'] is True,'lease_membership_unresolved','unresolved')
    ids=set();rou=Q(0);liability=Q(0)
    for item in state['leases']:
        comp=lease.typed(item['component'],lease.types.COMPONENTS['lease']);key=comp['lease_id']
        need(key not in ids and bool(comp['rights']),'lease_identity_or_empty_rights');ids.add(key)
        a=sum(r['rou'] for r in comp['rights']);l=sum(r['liability'] for r in comp['rights'])
        lease.financial.check_component('lease',comp,{'rou':a,'lease_liability':-l})
        need(all(lease.day(r['last_measurement_date'])<=now for r in comp['rights']),'future_lease_measurement')
        rou+=a;liability+=l
    need(b['rou']==rou and b['lease_liability']==-liability,'lease_allocation')
    need(len(state['seen'])==len(set(state['seen'])),'duplicate_event_history')
    taxids=[a['event_id'] for a in state['tax_adjustments']]
    need(len(taxids)==len(set(taxids)) and set(taxids)<=set(state['seen']),'tax_adjustment_history')
    for a in state['tax_adjustments']:need(start<=lease.day(a['date'])<=now,'tax_adjustment_date')
    for f in state['flows']:
        need(f['entity']==CONTEXT['entity'] and f['event_id'] in state['seen'],'flow_owner_or_event')
        need(start<=lease.day(f['date'])<=now,'flow_date')
    return state

def memory_program(kind):
    _,builder=returns.checked_builders();definition,schemas=builder.program(kind)
    shape=schema();inputs=deepcopy(schemas[definition['input_schema']]);inputs['properties']['balances']=deepcopy(shape['properties']['balances'])
    h,k=digest(shape),digest(inputs);definition['state_schema']=h;definition['input_schema']=k
    return definition,{h:shape,k:inputs}

def return_effect(state,event):
    returns.structure.validate(event,returns.event_schema())
    need(event['kind'] in ['settle','sell'],'selected_return_methods_only','unsupported')
    if event['kind']=='settle':need(event['lot_id'] not in state['lots'],'duplicate_lot')
    else:
        need(event['lot_id'] in state['lots'],'unknown_lot')
        need(not state['lots'][event['lot_id']]['disposed'],'lot_disposed')
    assessed,lineage=returns.prerequisite_manifest(state,event,digest(state),digest(event))
    need(assessed['status']=='requirements_satisfied','return_prerequisites:'+assessed['status'],assessed['status'])
    builder,_=returns.checked_builders()
    context={'entity':CONTEXT['entity'],'book_role':'legal','at':event['date']}
    definition=builder.program(event['kind'],context,ACCOUNTS)
    values=builder.project(state,event)
    if event['kind']=='settle':
        paths={'n':('event','/actual_units'),'p':('before','/component/unit_refund'),
          'c':('before','/component/unit_cost'),'d':('event','/unit_deterioration'),
          'h':('event','/unit_handling'),'nrv':('event','/inventory_nrv'),
          'refund_before':('before','/component/refund'),'recovery_before':('before','/component/recovery')}
    else:
        token=event['lot_id'].replace('~','~0').replace('/','~1')
        paths={'proceeds':('event','/proceeds'),'cost':('before','/lots/'+token+'/carrying')}
    monetary_lineage={}
    for key,(origin,pointer) in paths.items():
        h=digest(state if origin=='before' else event)
        definition['inputs'][key]['source_ref']='sha256:'+h+'#'+pointer
        monetary_lineage[key]={'source':origin,'sha256':h,'pointer':pointer}
    amounts=returns.monetary.derive({digest(definition):definition},digest(definition),values)
    need(amounts['status']=='derived','return_amounts:'+amounts['status'],amounts['status'])
    balances={k:fmt(amount(v)+amount(amounts['journal'][k])) for k,v in state['balances'].items()}
    _,memory_builder=returns.checked_builders();inputs=memory_builder.inputs_for(state,event,amounts);inputs['balances']=balances
    mem,schemas=memory_program(event['kind']);staged=returns.memory.stage({digest(mem):mem},digest(mem),schemas,state,inputs)
    need(staged['status']=='staged','return_memory:'+staged.get('reason',staged['status']))
    return staged['after'],amounts['journal'],inputs['flows'],{'prerequisites':assessed,'prerequisite_lineage':lineage,'monetary_definition':digest(definition),'monetary_lineage':monetary_lineage,'memory_definition':digest(mem)}

def lease_effect(state,event):
    caller.closed(event,['id','date','method','lease_id','parameters'])
    method=event['method'];need(method in lease.FOOTPRINT,'selected_lease_methods_only','unsupported')
    selected=[i for i,x in enumerate(state['leases']) if x['component']['lease_id']==event['lease_id']]
    need(len(selected)==1,'unknown_lease');index=selected[0]
    comp=lease.typed(state['leases'][index]['component'],lease.types.COMPONENTS['lease'])
    params=lease.typed(event['parameters'],lease.types.EVENTS[method][1])
    after,j,cash,oci,equity=lease.financial.derive('lease',comp,method,params,event['date'],lease.original_need)
    need(set(j)<=lease.FOOTPRINT[method] and all(v==0 for v in [*oci.values(),*equity.values()]),'kernel_footprint_changed','unsupported')
    journal={k:fmt(j.get(k,Q(0))) for k in ACCOUNTS}
    flows=[{'entity':CONTEXT['entity'],'activity':k,'origin':method+':'+event['lease_id'],'amount':fmt(v),'date':event['date'],'event_id':event['id']} for k,v in cash.items() if v]
    z=deepcopy(state);z['leases'][index]['component']=lease.encode(after)
    z['balances']={k:fmt(amount(v)+amount(journal[k])) for k,v in state['balances'].items()}
    z['date']=event['date'];z['seen'].append(event['id']);z['flows'].extend(flows)
    return z,journal,flows,{'kernel':'original_corporate_lease','method':method}

def propose(state,event):
    try:
        protected();invariant(state);caller.bounded(event);caller.closed(event,['profile','module','event'])
        need(event['profile']==EVENT,'event_profile');need(event['module'] in ['return','lease'],'unsupported_module','unsupported')
        e=event['event'];need(type(e) is dict and type(e.get('id')) is str and bool(e['id']),'event_identity')
        need(e['id'] not in state['seen'],'duplicate_event')
        need(lease.day(state['date'])<=lease.day(e['date'])<lease.day(state['period']['end_exclusive']),'event_chronology')
        after,journal,flows,details=(return_effect if event['module']=='return' else lease_effect)(state,e)
        writes={'balances','date','seen','flows'}|({'component','lots','tax_adjustments'} if event['module']=='return' else {'leases'})
        need(all(state[k]==after[k] for k in state if k not in writes),'module_write_boundary')
        need(after['seen']==state['seen']+[e['id']] and after['flows']==state['flows']+flows,'append_history_boundary')
        need(sum(amount(v) for v in journal.values())==0,'journal_unbalanced')
        need(amount(journal['cash'])==sum(amount(f['amount']) for f in flows),'cash_flow_mismatch')
        invariant(after)
        p={'profile':'SyntheticReturnLeaseProposal/1','before_sha256':digest(state),'event_sha256':digest(event),
           'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'source_bundle_sha256':LOCK,
           'journal':journal,'flows':flows,'after':after,'details':details,**FLAGS}
        p['write_fields']=sorted(writes)
        return {'status':'proposed','proposal':p,**FLAGS}
    except (Refused,lease.Refused) as exc:return {'status':exc.status,'reason':exc.reason,'proposal':None,**FLAGS}
    except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OSError,RecursionError,OverflowError) as exc:
        return {'status':'invalid','reason':str(exc)[:300],'proposal':None,**FLAGS}

def apply(state,event,proposal):
    r=propose(state,event)
    if r['status']!='proposed':return r
    try:
        caller.bounded(proposal)
        need(caller.canonical(proposal)==caller.canonical(r['proposal']),'full_recomputation_mismatch')
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError):
        return {'status':'invalid','reason':'full_recomputation_mismatch',**FLAGS}
    return {'status':'applied_diagnostic','after':deepcopy(proposal['after']),**FLAGS}

def run_prefix(state,events):
    current=deepcopy(state);trace=[]
    try:
        protected();invariant(current);caller.bounded(events)
        need(type(events) is list,'event_list_required')
    except (Refused,lease.Refused) as exc:
        return {'status':'stopped','stop_status':exc.status,'reason':exc.reason,'after':current,'trace':trace,**FLAGS}
    except (ValueError,TypeError,KeyError,AssertionError,OSError,RecursionError,OverflowError) as exc:
        return {'status':'stopped','stop_status':'invalid','reason':str(exc)[:300],'after':current,'trace':trace,**FLAGS}
    for event in events:
        r=propose(current,event);trace.append({'event':deepcopy(event),'result':r})
        if r['status']!='proposed':return {'status':'stopped','stop_status':r['status'],'after':current,'trace':trace,**FLAGS}
        a=apply(current,event,r['proposal']);need(a['status']=='applied_diagnostic','internal_apply_mismatch')
        current=a['after']
    return {'status':'complete','after':current,'trace':trace,**FLAGS}
