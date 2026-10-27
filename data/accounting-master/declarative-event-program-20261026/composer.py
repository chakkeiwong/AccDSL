"""Finite explicit event rules with retained typed/report/carry owners."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'ordered-event-eligibility-20261026'))
import gate
sys.path.insert(0,str(HERE.parent/'ordered-assessment-expansion-20261026'))
import expander
sys.path.insert(0,str(HERE.parent/'authored-state-invariants-20261026'))
import guards
import company_book_reports_v1 as reports
import company_book_carry_v1 as carry

c=gate.c;core=c.core;base=c.base;typed=c.frontend.v2
PROFILE='DeclarativeEventCompanyProgram/1'
MAX_COMMANDS=64;MAX_TRACE_BYTES=8*1024*1024
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,
           full_native_opening_contract_evaluated=False,durable=False)

def identity(command):return command['event']['id'] if command['kind']=='event' else command['id']

def input_order(body):
    return [list(cmd['event']['inputs']) if cmd['kind']=='event' else None for cmd in body['commands']]

def make_call(body):
    return dict(profile=PROFILE,program_sha256=core.digest(body),input_order_sha256=core.digest(input_order(body)))

def validate(body,call):
    c.need(len(core.canonical(body))<=core.MAX_BYTES,'program_size_limit');c.exact(body)
    c.closed(call,['profile','program_sha256','input_order_sha256'],'program_call_fields')
    c.need(call['profile']==PROFILE,'call_profile')
    c.need(call['program_sha256']==core.digest(body),'stale_program')
    c.need(call['input_order_sha256']==core.digest(input_order(body)),'stale_input_order')
    c.closed(body,['profile','name','opening','schemas','mapping','memory_definition','state_invariant',
                   'invariant_sha256','rules','commands','carry_policy','residuals'],'program_fields')
    c.need(body['profile']==PROFILE,'program_profile');base.text(body['name'],'program_name')
    for name,value in body.items():
        if name not in ('rules','commands'):base.memory.bounded(value)
    core.identifiers(body['residuals'],'program_residuals',True)
    guards.validate(body['state_invariant'])
    c.need(core.digest(body['state_invariant'])==body['invariant_sha256'],'invariant_digest')
    typed.typed_book(body['opening'],body['memory_definition'],body['schemas'])
    c.closed(body['carry_policy'],['mode','provenance'],'carry_policy_fields')
    c.need(body['carry_policy']['mode']=='preserve_all_memory','selected_carry_policy')
    base.text(body['carry_policy']['provenance'],'carry_provenance')
    c.need(type(body['rules']) is dict and 0<len(body['rules'])<=64,'rules_population')
    for key,rule in body['rules'].items():
        base.text(key,'rule_key')
        c.closed(rule,['eligibility','eligibility_sha256','construction','construction_sha256'],'rule_fields')
        for field in ('eligibility','construction'):
            base.memory.bounded(rule[field]);c.need(core.digest(rule[field])==rule[field+'_sha256'],'rule_digest:'+field)
        c.need(rule['eligibility']['operation']==key,'rule_operation')
        gate.compile_template(rule['eligibility'],body['opening'],body['memory_definition'])
        c.need(rule['construction'].get('profile') in (c.PROFILE,expander.PROFILE),'construction_profile')
    c.need(type(body['commands']) is list and 0<len(body['commands'])<=MAX_COMMANDS,'command_limit')
    for cmd in body['commands']:
        base.memory.bounded(cmd)
        c.need(type(cmd) is dict,'command_record');kind=cmd.get('kind')
        if kind=='event':
            c.closed(cmd,['kind','method_key','event','order'],'event_command_fields')
            c.need(cmd['method_key'] in body['rules'],'missing_rule')
            base.closed(cmd['event'],['id','date','inputs']);core.scalar(cmd['event']['date'],'date')
            c.need(type(cmd['event']['inputs']) is dict,'event_inputs')
            ordered=body['rules'][cmd['method_key']]['construction']['profile']==expander.PROFILE
            c.need(type(cmd['order']) is list if ordered else cmd['order'] is None,'construction_order_kind')
        else:
            c.need(kind in ('report','carry'),'command_kind')
            fields=['kind','id','cutoff','equity_movements','notes']
            if kind=='carry':fields+=['retained_account','next_end_exclusive','memory_policies']
            c.closed(cmd,fields,'report_command_fields');core.scalar(cmd['cutoff'],'date')
            c.need(type(cmd['equity_movements']) is list and type(cmd['notes']) is list,'report_lists')
        base.text(identity(cmd),'command_id')

class InvariantFailure(ValueError):
    def __init__(self,stage,result):
        self.stage=stage;self.result=result;self.status=result['status']
        super().__init__('state_invariant:'+stage+':'+result['status'])

def invariant(body,book,stage):
    checked=guards.assess(body['state_invariant'],book,body['memory_definition'],body['schemas'])
    if checked['status']!='collection_total_requirements_satisfied':raise InvariantFailure(stage,checked)
    return checked

def run(body,call):
    try:
        validate(body,call);opening_check=invariant(body,body['opening'],'opening')
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(profile=PROFILE,**FLAGS,status=getattr(exc,'status','invalid'),reason=str(exc)[:300],
                    stage=getattr(exc,'stage','validation'),executed_commands=0)
    current=deepcopy(body['opening']);opening=deepcopy(current);trace=[];output_reports=[]
    used=set(current['seen']);stop=None;trace_bytes=2
    for index,cmd in enumerate(body['commands']):
        request=result=eligibility=construction=after_check=None
        before=deepcopy(current);next_opening=opening
        try:
            key=identity(cmd);c.need(key not in used,'duplicate_command')
            typed.typed_book(current,body['memory_definition'],body['schemas'])
            before_check=invariant(body,current,'before')
            if cmd['kind']=='event':
                rule=body['rules'][cmd['method_key']];event=cmd['event'];template=rule['eligibility']
                eligibility=gate.assess(template,current,event,body['schemas'],body['memory_definition'],
                                       gate.make_call(template,current,event,body['schemas'],body['memory_definition']))
                if eligibility['status']!='eligible':
                    stop=dict(index=index,status=eligibility['status'],reason=eligibility['reason'],
                              failed_stage=eligibility['failed_stage'],eligibility=eligibility,
                              before_sha256=core.digest(current),request=None,result=None)
                    break
                template=rule['construction']
                if template['profile']==c.PROFILE:
                    construction=c.construct(template,current,event,body['schemas'],body['memory_definition'],c.make_call(template,current,event))
                    request=construction['request']
                else:
                    construction=expander.construct(template,current,event,body['schemas'],body['memory_definition'],
                                                    expander.make_call(template,current,event,cmd['order']))
                    request=construction['construction']['request']
                result=typed.propose(current,request);success=result['status']=='proposed'
                after=result['after'] if success else current
            else:
                cutoff=cmd['cutoff'];c.need(current['date']<=cutoff<current['period']['end_exclusive'],'report_chronology')
                observed=deepcopy(current);observed['date']=cutoff
                request=reports.request(opening,observed,body['schemas'],body['mapping'],cmd['equity_movements'],cmd['notes'])
                if cmd['kind']=='report':result=reports.report(request);success=result['status']=='reported';after=observed
                else:
                    expected={p:dict(kind='preserve',provenance=body['carry_policy']['provenance']) for p in current['memory_types']}
                    c.need(cmd['memory_policies']==expected,'selected_carry_policy')
                    request=carry.request(request,key,cmd['retained_account'],cmd['next_end_exclusive'],cmd['memory_policies'])
                    result=carry.propose(request);success=result['status']=='proposed'
                    after=result['next_opening'] if success else current
                    next_opening=after if success else opening
            if not success:
                stop=dict(index=index,status=result['status'],reason=result.get('reason','transition_refusal'),
                          before_sha256=core.digest(current),request=request,result=result,eligibility=eligibility)
                break
            typed.typed_book(after,body['memory_definition'],body['schemas']);after_check=invariant(body,after,'after')
            item=dict(index=index,command=deepcopy(cmd),request=request,result=result,
                      before_sha256=core.digest(before),after_sha256=core.digest(after),
                      opening_before_sha256=core.digest(opening),opening_after_sha256=core.digest(next_opening),
                      eligibility=eligibility,construction=construction,
                      invariant_before=before_check,invariant_after=after_check)
            size=len(core.canonical(item));c.need(trace_bytes+size<=MAX_TRACE_BYTES,'trace_size_limit')
            trace.append(item);trace_bytes+=size;used.add(key);current=deepcopy(after);opening=deepcopy(next_opening)
            if cmd['kind'] in ('report','carry'):
                output_reports.append(dict(id=key,result=deepcopy(result if cmd['kind']=='report' else result['report'])))
        except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
            stop=dict(index=index,status=getattr(exc,'status','invalid'),reason=str(exc)[:300],
                      before_sha256=core.digest(current),request=request,result=result,eligibility=eligibility)
            if isinstance(exc,InvariantFailure):stop.update(invariant=exc.result,failed_stage=exc.stage)
            break
    return dict(profile=PROFILE,**FLAGS,status='stopped_provisional' if stop else 'complete_provisional',
                program_sha256=call['program_sha256'],input_order_sha256=call['input_order_sha256'],
                current=current,opening=opening,successful_commands=len(trace),trace=trace,reports=output_reports,
                opening_invariant=opening_check,stop=stop,remaining_commands=deepcopy(body['commands'][len(trace):]),
                implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Explicit event execution after separately checked native opening admission; no durability or accounting admission')
