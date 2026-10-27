"""Finite authored calendars; each decision binds to the book at execution."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
import state_decision_events_v1 as decision

PROFILE='StateDecisionSchedule/1'
DEPENDENCY_SHA256='b54c3d641773d25fdf1fa4d3efbf9efe79498e537867f95d17adfd63ae355da6'
MAX_SCHEDULES=32
MAX_OCCURRENCES=64
FLAGS=decision.FLAGS
need=decision.need
closed=decision.closed
day=decision.day
digest=decision.digest


def protected():
    need(sha256(Path(decision.__file__).read_bytes()).hexdigest()==DEPENDENCY_SHA256,'decision_dependency_hash')
    decision.protected()


def dates(calendar,financial):
    need(type(calendar) is dict,'calendar_record')
    if calendar.get('kind')=='explicit_dates':
        closed(calendar,['kind','dates'])
        values=calendar['dates']
        need(type(values) is list and 0<len(values)<=MAX_OCCURRENCES,'explicit_dates_limit')
        parsed=[day(value) for value in values]
        need(parsed==sorted(set(parsed)),'dates_unique_increasing')
    elif calendar.get('kind')=='every_days':
        closed(calendar,['kind','start','end_exclusive','step_days'])
        start,end=day(calendar['start']),day(calendar['end_exclusive']);step=calendar['step_days']
        need(type(step) is int and step>0,'positive_integer_step')
        need(start<end<=day(financial['period']['end_exclusive']),'calendar_interval')
        parsed=[];current=start
        while current<end:
            parsed.append(current);need(len(parsed)<=MAX_OCCURRENCES,'calendar_occurrence_limit')
            if step>=(end-current).days:break
            current+=timedelta(days=step)
    else:raise decision.Refused('unsupported','calendar_kind')
    need(all(day(financial['date'])<=value<day(financial['period']['end_exclusive']) for value in parsed),'calendar_outside_current_book')
    return [value.isoformat() for value in parsed]


def materialize(state,root,occurrence):
    schedule=next(row for row in root['schedules'] if row['id']==occurrence['schedule_id'])
    template=deepcopy(schedule['template'])
    template['event'].update(id=occurrence['event_id'],date=occurrence['date'])
    return {'profile':decision.PROFILE,'id':occurrence['decision_id'],
            'expected_state_sha256':digest(state),'context':deepcopy(root['context']),
            'decision_date':occurrence['date'],'scenario':deepcopy(root['scenario']),**template}


def prepare(state,root):
    protected();decision.runtime.annual.invariant(state);decision.runtime.annual.caller.bounded(root)
    closed(root,['profile','id','expected_state_sha256','context','scenario','schedules'])
    need(root['profile']==PROFILE,'profile');decision.text(root['id'],'schedule_root_id')
    need(root['expected_state_sha256']==digest(state),'stale_initial_state')
    need(root['context']==state['after']['context'],'context_mismatch')
    closed(root['scenario'],['kind','premise'])
    need(root['scenario']['kind']=='authored_closed_path','scenario_kind','unsupported')
    decision.text(root['scenario']['premise'],'closed_path_premise')
    need(type(root['schedules']) is list and len(root['schedules'])<=MAX_SCHEDULES,'schedule_limit')
    ids=set();occurrences=[];first=[]
    for schedule in root['schedules']:
        closed(schedule,['id','priority','calendar','template']);decision.text(schedule['id'],'schedule_id')
        need(schedule['id'] not in ids,'duplicate_schedule');ids.add(schedule['id'])
        priority=schedule['priority'];need(type(priority) is int and priority>=0,'explicit_nonnegative_priority')
        closed(schedule['template'],['model','bindings','output_map','event'])
        closed(schedule['template']['event'],['method','lot_id','findings'])
        calendar=dates(schedule['calendar'],state['after'])
        for index,value in enumerate(calendar):
            token=digest([root['id'],schedule['id'],index])
            occurrence={'schedule_id':schedule['id'],'index':index,'date':value,'priority':priority,
                        'decision_id':'scheduled-decision:'+token,'event_id':'scheduled-event:'+token}
            occurrences.append(occurrence)
            if index==0:first.append(occurrence)
            need(len(occurrences)<=MAX_OCCURRENCES,'total_occurrence_limit')
    # Static validation of every template precedes economic execution or ambiguity.
    for occurrence in first:decision.prepare(state,materialize(state,root,occurrence))
    seen=set()
    for occurrence in occurrences:
        key=(occurrence['date'],occurrence['priority'])
        need(key not in seen,'ambiguous_same_day_priority','unresolved');seen.add(key)
    return sorted(occurrences,key=lambda row:(row['date'],row['priority']))


def run(state,root):
    try:
        calendar=prepare(state,root);current=deepcopy(state);trace=[];stop=None;cursor=state['after']['date']
        for index,occurrence in enumerate(calendar):
            request=materialize(current,root,occurrence)
            proposed=decision.propose(current,request);outcome=decision.apply(current,request,proposed)
            if outcome['status'] not in ['applied_provisional','no_action']:
                stop={'index':index,'occurrence':deepcopy(occurrence),'request':request,'outcome':outcome};break
            trace.append({'occurrence':deepcopy(occurrence),'request':request,'result':outcome})
            current=outcome['after'];cursor=occurrence['date']
        report=decision.runtime.annual.root.carry.statements(current['opening'],current['after'],current['account_classes'])
        report.update(scope='Recorded conditional state after an authored decision prefix; not a complete fiscal event population',unresolved=deepcopy(decision.runtime.annual.UNRESOLVED))
        return {'profile':PROFILE,**FLAGS,'status':'stopped_provisional' if stop else 'complete_scheduled_decisions',
                'schedule_sha256':digest(root),'initial_state_sha256':digest(state),
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                'dependency_sha256':DEPENDENCY_SHA256,'calendar':calendar,'after':current,
                'trace':trace,'stop':stop,'decision_cursor':cursor,
                'remaining_occurrences':deepcopy(calendar[len(trace):]),'recorded_statements':report,'fiscal_complete':False}
    except Exception as exc:
        return {**decision.failure(exc),'profile':PROFILE}
