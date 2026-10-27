"""State-bound deferred assessment and a terminal, explicit fiscal carry."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import mixed_event_timeline_v2 as prior

scheduler=prior.scheduler;decision=prior.decision;runtime=prior.runtime
authoring=prior.authoring
PROFILE='MixedEventTimeline/3'
FLAGS=prior.FLAGS
need=prior.need;closed=prior.closed;digest=prior.digest
DEPENDENCY_SHA256='347f0c3e74c0f2368a363a209a38e42db52e23260a0d454f1f438f1b218b536c'

def protected():
    need(sha256(Path(prior.__file__).read_bytes()).hexdigest()==DEPENDENCY_SHA256,'timeline_dependency_hash')
    prior.protected()

def prepare(state,root):
    protected();runtime.annual.caller.bounded(root)
    closed(root,['profile','id','expected_state_sha256','context','scenario','schedules','operations'])
    need(root['profile']==PROFILE,'profile')
    need(type(root['operations']) is list and len(root['operations'])<=prior.prior.MAX_OPERATIONS,'native_operation_limit')
    legacy=deepcopy(root);legacy['profile']=prior.PROFILE;legacy['operations']=[]
    additions=[];ids=set();carry_count=0
    financial=state['after'];start=decision.day(financial['date']);end=decision.day(financial['period']['end_exclusive'])
    for entry in root['operations']:
        closed(entry,['id','priority','date','operation']);decision.text(entry['id'],'timeline_entry_id')
        need(entry['id'] not in ids,'duplicate_native_entry');ids.add(entry['id'])
        need(type(entry['priority']) is int and entry['priority']>=0,'explicit_nonnegative_priority')
        operation=entry['operation'];closed(operation,['kind','event']);kind=operation['kind']
        if kind not in ['deferred_assessment','provisional_carry']:
            legacy['operations'].append(deepcopy(entry));continue
        identity=authoring.validate_operation(operation);event=operation['event']
        if kind=='deferred_assessment':
            date=event['measurement']['at'];at=decision.day(date)
            need(start<=at<end,'measurement_outside_current_book')
            clock={'kind':'deferred_measurement_at','measurement':deepcopy(event['measurement'])}
        else:
            carry_count+=1;need(carry_count==1,'single_terminal_carry')
            date=event['next_period']['start'];at=decision.day(date)
            need(at==end,'carry_boundary_mismatch')
            need(at<decision.day(event['next_period']['end_exclusive']),'next_period_end')
            clock={'kind':'next_period_start','next_period':deepcopy(event['next_period'])}
        need(entry['date']==date,'operation_clock_mismatch')
        additions.append({'kind':'native_operation','id':entry['id'],'priority':entry['priority'],
            'date':date,'event_id':identity,'operation':deepcopy(operation),'clock':clock})
    schedule_root,calendar=prior.prepare(state,legacy)
    calendar+=additions
    need(len(calendar)<=prior.prior.MAX_ACTIONS,'total_action_limit')
    identities=set();order=set()
    for entry in calendar:
        need(entry['event_id'] not in identities,'duplicate_timeline_event');identities.add(entry['event_id'])
        key=(entry['date'],entry['priority'])
        need(key not in order,'ambiguous_same_day_priority','unresolved');order.add(key)
    calendar.sort(key=lambda x:(x['date'],x['priority']))
    for i,entry in enumerate(calendar):
        if entry.get('operation',{}).get('kind')=='provisional_carry':
            need(i==len(calendar)-1,'carry_must_end_timeline')
    return schedule_root,calendar

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
                    # Keep caller-supplied measurement bytes; native execution
                    # must check their original digest against this actual state.
                    native=runtime.transition(current,entry['operation'])
                    outcome={'profile':PROFILE,**FLAGS,'status':'applied_provisional','after':native['after'],'transition':native}
                except Exception as exc:outcome={**decision.failure(exc),'profile':PROFILE}
            if outcome['status'] not in ['applied_provisional','no_action']:
                stop={'index':index,'entry':deepcopy(entry),'request':request,'outcome':outcome};break
            trace.append({'entry':deepcopy(entry),'request':request,'result':outcome})
            current=outcome['after'];cursor=entry['date']
        report=runtime.annual.root.carry.statements(current['opening'],current['after'],current['account_classes'])
        report.update(scope='Recorded current-period prefix; any carried prior-period report remains in period_archive; not complete fiscal activity',
                      unresolved=deepcopy(runtime.annual.UNRESOLVED))
        return {'profile':PROFILE,**FLAGS,'status':'stopped_provisional' if stop else 'complete_mixed_timeline',
            'timeline_sha256':digest(root),'initial_state_sha256':digest(state),
            'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256':DEPENDENCY_SHA256,'calendar':calendar,'after':current,'trace':trace,'stop':stop,
            'timeline_cursor':cursor,'remaining_actions':deepcopy(calendar[len(trace):]),
            'recorded_statements':report,'fiscal_complete':False}
    except Exception as exc:return {**decision.failure(exc),'profile':PROFILE}
