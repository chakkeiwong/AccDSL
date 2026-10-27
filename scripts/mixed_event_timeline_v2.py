"""Explicit current-assessment clocks with unchanged native financial effects."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
import mixed_event_timeline_v1 as prior
import annual_program_authoring_v1 as authoring

scheduler=prior.scheduler;decision=prior.decision;runtime=prior.runtime
PROFILE='MixedEventTimeline/2'
FLAGS=prior.FLAGS
need=prior.need;closed=prior.closed;digest=prior.digest
PINS={'mixed_event_timeline_v1.py':'2b103ab4413815a24aa431ab959cbfce51ae3560209a0590a62fd5cae10138b4',
      'annual_program_authoring_v1.py':'edd39fe682370b9a2a742c3a89e0c76007b434c51301182e6e0a4924faa72f72',
      'annual_period_book_v1.py':'e94dbbffb103c7fd67f316fb34b563defb5d87a9b2df1bd90606cec09865060b'}

def protected():
    for name,h in PINS.items():need(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==h,'dependency_hash:'+name)
    prior.protected();authoring.protected()

def assessment_clock(operation):
    need(operation['kind']=='current_assessment','current_assessment_only')
    identity=authoring.validate_operation(operation)
    interval=operation['event']['interval']
    start,end,through=(decision.day(interval[k]) for k in ['start','end_exclusive','activity_through'])
    need(start<end and through==end-timedelta(days=1),'assessment_clock_interval')
    return identity,interval['activity_through']

def prepare(state,root):
    protected();runtime.annual.caller.bounded(root)
    closed(root,['profile','id','expected_state_sha256','context','scenario','schedules','operations'])
    need(root['profile']==PROFILE,'profile')
    need(type(root['operations']) is list and len(root['operations'])<=prior.MAX_OPERATIONS,'native_operation_limit')
    legacy=deepcopy(root);legacy['profile']=prior.PROFILE;legacy['operations']=[]
    additions=[];native_ids=set()
    for entry in root['operations']:
        closed(entry,['id','priority','date','operation']);decision.text(entry['id'],'timeline_entry_id')
        need(entry['id'] not in native_ids,'duplicate_native_entry');native_ids.add(entry['id'])
        need(type(entry['priority']) is int and entry['priority']>=0,'explicit_nonnegative_priority')
        operation=entry['operation'];closed(operation,['kind','event'])
        if operation['kind']!='current_assessment':
            legacy['operations'].append(deepcopy(entry));continue
        identity,date=assessment_clock(operation)
        need(entry['date']==date,'assessment_date_mismatch')
        at=decision.day(date)
        need(decision.day(state['after']['date'])<=at<decision.day(state['after']['period']['end_exclusive']),
             'operation_outside_current_book')
        additions.append({'kind':'native_operation','id':entry['id'],'priority':entry['priority'],
            'date':date,'event_id':identity,'operation':deepcopy(operation),
            'clock':{'kind':'current_assessment_activity_through','interval':deepcopy(operation['event']['interval'])}})
    schedule_root,calendar=prior.prepare(state,legacy)
    calendar+=additions
    need(len(calendar)<=prior.MAX_ACTIONS,'total_action_limit')
    identities=set();order=set()
    for entry in calendar:
        need(entry['event_id'] not in identities,'duplicate_timeline_event');identities.add(entry['event_id'])
        key=(entry['date'],entry['priority'])
        need(key not in order,'ambiguous_same_day_priority','unresolved');order.add(key)
    return schedule_root,sorted(calendar,key=lambda x:(x['date'],x['priority']))

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
        report.update(scope='Recorded conditional mixed-action prefix including supplied current assessment; not complete fiscal events',
                      unresolved=deepcopy(runtime.annual.UNRESOLVED))
        return {'profile':PROFILE,**FLAGS,'status':'stopped_provisional' if stop else 'complete_mixed_timeline',
            'timeline_sha256':digest(root),'initial_state_sha256':digest(state),
            'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256':deepcopy(PINS),'calendar':calendar,'after':current,'trace':trace,'stop':stop,
            'timeline_cursor':cursor,'remaining_actions':deepcopy(calendar[len(trace):]),
            'recorded_statements':report,'fiscal_complete':False}
    except Exception as exc:return {**decision.failure(exc),'profile':PROFILE}
