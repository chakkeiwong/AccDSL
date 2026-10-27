"""Explicitly ordered native events and current-state decisions; no admission."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import state_decision_schedule_v1 as scheduler

decision=scheduler.decision
runtime=decision.runtime
PROFILE='MixedEventTimeline/1'
SCHEDULER_SHA256='c4696564c39936f9e8ed27a736202c16b7c0dc479304d06073c34c275b6aed36'
MAX_OPERATIONS=32
MAX_ACTIONS=64
FLAGS=decision.FLAGS
need=decision.need
closed=decision.closed
digest=decision.digest


def protected():
    need(sha256(Path(scheduler.__file__).read_bytes()).hexdigest()==SCHEDULER_SHA256,'scheduler_dependency_hash')
    scheduler.protected()


def operation_shape(operation):
    closed(operation,['kind','event']);event=operation['event']
    if operation['kind']=='allocated_tax_payment':
        closed(event,['id','date','amount','authorization','allocations'])
        decision.text(event['id'],'event_id');decision.day(event['date'])
        total=runtime.annual.losses.tax.numeric(event['amount']);need(total>0,'positive_payment')
        runtime.annual.losses.declaration(event['authorization'],'boolean')
        need(type(event['allocations']) is list and bool(event['allocations']),'nonempty_allocations')
        seen=set();allocated=0
        for allocation in event['allocations']:
            closed(allocation,['vintage_id','amount']);key=allocation['vintage_id']
            decision.text(key,'vintage_id');need(key not in seen,'duplicate_allocation');seen.add(key)
            amount=runtime.annual.losses.tax.numeric(allocation['amount']);need(amount>0,'positive_allocation');allocated+=amount
        need(total==allocated,'allocation_sum_mismatch')
    elif operation['kind']=='partial_inventory_sale':
        closed(event,['profile','id','date','method','lot_id','sold_units','proceeds','findings'])
        need(event['profile']==runtime.partial.PROFILE,'sale_profile')
        need(event['method']==runtime.partial.MODEL,'selected_sale_method','unsupported')
        decision.text(event['id'],'event_id');decision.text(event['lot_id'],'lot_id');decision.day(event['date'])
        runtime.partial.number(event['sold_units']);runtime.partial.number(event['proceeds'])
        decision.findings_shape(event['findings'])
    else:raise decision.Refused('unsupported','native_operation_adapter')
    return event['id'],event['date']


def prepare(state,root):
    protected();runtime.annual.caller.bounded(root)
    closed(root,['profile','id','expected_state_sha256','context','scenario','schedules','operations'])
    need(root['profile']==PROFILE,'profile')
    schedule_root={k:deepcopy(v) for k,v in root.items() if k!='operations'}
    schedule_root['profile']=scheduler.PROFILE
    calendar=[dict(row,kind='decision') for row in scheduler.prepare(state,schedule_root)]
    need(type(root['operations']) is list and len(root['operations'])<=MAX_OPERATIONS,'native_operation_limit')
    ids=set()
    for entry in root['operations']:
        closed(entry,['id','priority','date','operation']);decision.text(entry['id'],'timeline_entry_id')
        need(entry['id'] not in ids,'duplicate_native_entry');ids.add(entry['id'])
        need(type(entry['priority']) is int and entry['priority']>=0,'explicit_nonnegative_priority')
        event_id,event_date=operation_shape(entry['operation'])
        need(entry['date']==event_date,'operation_date_mismatch')
        at=decision.day(entry['date'])
        need(decision.day(state['after']['date'])<=at<decision.day(state['after']['period']['end_exclusive']),'operation_outside_current_book')
        calendar.append({'kind':'native_operation','id':entry['id'],'priority':entry['priority'],
                         'date':entry['date'],'event_id':event_id,'operation':deepcopy(entry['operation'])})
    need(len(calendar)<=MAX_ACTIONS,'total_action_limit')
    seen=set();order=set()
    for row in calendar:
        need(row['event_id'] not in seen,'duplicate_timeline_event');seen.add(row['event_id'])
        key=(row['date'],row['priority'])
        need(key not in order,'ambiguous_same_day_priority','unresolved');order.add(key)
    return schedule_root,sorted(calendar,key=lambda row:(row['date'],row['priority']))


def run(state,root):
    try:
        schedule_root,calendar=prepare(state,root)
        current=deepcopy(state);trace=[];stop=None;cursor=state['after']['date']
        for index,entry in enumerate(calendar):
            request=None
            if entry['kind']=='decision':
                request=scheduler.materialize(current,schedule_root,entry)
                proposed=decision.propose(current,request);outcome=decision.apply(current,request,proposed)
            else:
                try:
                    native=runtime.transition(current,entry['operation'])
                    outcome={'profile':PROFILE,**FLAGS,'status':'applied_provisional','after':native['after'],'transition':native}
                except Exception as exc:outcome={**decision.failure(exc),'profile':PROFILE}
            if outcome['status'] not in ['applied_provisional','no_action']:
                stop={'index':index,'entry':deepcopy(entry),'request':request,'outcome':outcome};break
            trace.append({'entry':deepcopy(entry),'request':request,'result':outcome})
            current=outcome['after'];cursor=entry['date']
        report=runtime.annual.root.carry.statements(current['opening'],current['after'],current['account_classes'])
        report.update(scope='Recorded conditional state after an authored mixed-action prefix; not a complete fiscal event population',unresolved=deepcopy(runtime.annual.UNRESOLVED))
        return {'profile':PROFILE,**FLAGS,'status':'stopped_provisional' if stop else 'complete_mixed_timeline',
                'timeline_sha256':digest(root),'initial_state_sha256':digest(state),
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                'scheduler_sha256':SCHEDULER_SHA256,'calendar':calendar,'after':current,'trace':trace,'stop':stop,
                'timeline_cursor':cursor,'remaining_actions':deepcopy(calendar[len(trace):]),
                'recorded_statements':report,'fiscal_complete':False}
    except Exception as exc:return {**decision.failure(exc),'profile':PROFILE}
