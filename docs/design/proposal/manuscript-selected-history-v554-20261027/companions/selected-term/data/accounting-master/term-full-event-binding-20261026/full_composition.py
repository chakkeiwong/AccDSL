"""Selected assessment/carry composition; no native lifecycle callbacks."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'term-structural-admission-20261026'))
import structure as s
sys.path.insert(0,str(HERE.parent/'nested-assessment-construction-20261026'))
import nested_expander as expander
sys.path.insert(0,str(HERE.parent/'ordered-event-eligibility-20261026'))
import nested_gate as gate
import company_book_carry_v1 as carry_engine
core=s.core;p=s.p
PROFILE='SelectedTermCommand/2'
FLAGS=dict(s.FLAGS,production_ready=False,durable=False)

def make_call(contract,rules,state,request,coverage,selection):
    return dict(profile=PROFILE,contract_sha256=core.digest(contract),rules_sha256=core.digest(rules),
      state_sha256=core.digest(state),request_sha256=core.digest(request),population_sha256=core.digest(coverage),
      state_order_sha256=p.order_digest(state),request_order_sha256=p.order_digest(request),
      rules_order_sha256=p.order_digest(rules),reviewed_selection=selection)

def selection_for(contract,rules):
    return core.digest(dict(contract=core.digest(contract),rules=core.digest(rules)))

def after_coverage(coverage,before,after):
    # Completeness is inherited only after exact declared transition from the
    # complete supplied before population, not manufactured for a new input.
    result=deepcopy(coverage)
    for value in result.values():
        if 'book_sha256' in value:value['book_sha256']=core.digest(after['book'])
    return result

def snapshot(contract,state,coverage):
    selected=core.digest(contract)
    return s.admit(contract,state,coverage,selected,s.contract_call(contract,state,coverage,selected))

def execute(contract,rules,state,request,coverage,selection,call):
    result=dict(profile=PROFILE,**FLAGS,provisional_transition=False);stage='call'
    try:
        core.need(call==make_call(contract,rules,state,request,coverage,selection),'stale_term_command_call')
        core.need(selection==selection_for(contract,rules),'reviewed_term_command')
        core.closed(rules,['assessment','amendment','collection','carry'],'term_rules')
        core.closed(rules['assessment'],['eligibility','construction'],'assessment_rule')
        core.need(rules['assessment']['eligibility']['operation']=='assess','assessment_operation')
        core.need(rules['carry']==dict(mode='preserve_terms_reset_cursor',cursor='/collection_clock/cursor',
          preserve_provenance='Preserve immutable terms and assessment basis',
          cursor_provenance='New period opens a contiguous assessment window'),'selected_carry_policy')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='before_state';checked=snapshot(contract,state,coverage);result['before_assessment']=checked
        if checked['status']!='selected_term_state_satisfied':return dict(result,status=checked['status'],failed_stage=stage)
        stage='request';p.base.binding.bounded(request);p.base.memory.bounded(request)
        book=state['book'];core.need(request['expected_state_sha256']==core.digest(state),'stale_term_state')
        if request['profile']=='ReceivableTermEvent/1':
            core.closed(request,['profile','expected_state_sha256','operation','event'],'term_event_request')
            core.need(request['operation'] in ('assess','amend','collect'),'unsupported_term_operation')
            selected={'assess':'assessment','amend':'amendment','collect':'collection'}[request['operation']]
            rule=rules[selected];core.closed(rule,['eligibility','construction'],'event_rule')
            core.need(rule['eligibility']['operation']==request['operation'],'event_operation_binding')
            event=request['event'];stage='eligibility'
            args=(rule['eligibility'],book,event,state['schemas'],state['memory_definition'])
            eligible=gate.assess(*args,gate.make_call(*args));result['eligibility']=eligible
            if eligible['status']!='eligible':return dict(result,status=eligible['status'],reason=eligible['reason'],failed_stage=stage)
            stage='construction';template=rule['construction'];order=list(book['memory']['claims'])
            args=(template,book,event,state['schemas'],state['memory_definition'])
            if request['operation']=='assess':
                construction=expander.construct(*args,expander.make_call(template,book,event,order))
                typed=construction['construction']['request']
            else:
                construction=expander.c.construct(*args,expander.c.make_call(template,book,event))
                typed=construction['request']
            result['construction']=construction;result['typed_request']=typed;stage='transition'
            transition=expander.c.frontend.v2.propose(book,typed);result['transition']=transition
            if transition['status']!='proposed':return dict(result,status=transition['status'],reason=transition.get('reason','typed_transition'),failed_stage=stage)
            after=deepcopy(state);after['book']=transition['after']
        else:
            core.need(request['profile']=='ReceivableTermCarry/1','unsupported_term_request')
            core.closed(request,['profile','expected_state_sha256','report_request','close_id','retained_account','next_end_exclusive'],'term_carry')
            core.need(core.canonical(request['report_request']['closing'])==core.canonical(book),'carry_closing_binding')
            policy=rules['carry'];policies={key:dict(kind='preserve',provenance=policy['preserve_provenance']) for key in book['memory_types']}
            core.need(policy['cursor'] in policies,'carry_cursor_leaf')
            policies[policy['cursor']]=dict(kind='next_period_start',provenance=policy['cursor_provenance'])
            typed=carry_engine.request(request['report_request'],request['close_id'],request['retained_account'],request['next_end_exclusive'],policies)
            result['carry_request']=typed;stage='carry';transition=carry_engine.propose(typed);result['carry']=transition
            if transition['status']!='proposed':return dict(result,status=transition['status'],reason=transition.get('reason','typed_carry'),failed_stage=stage)
            after=deepcopy(state);after['book']=transition['next_opening']
        stage='after_state';next_coverage=after_coverage(coverage,state,after)
        checked=snapshot(contract,after,next_coverage);result['after_assessment']=checked
        if checked['status']!='selected_term_state_satisfied':return dict(result,status=checked['status'],failed_stage=stage)
        return dict(result,status='proposed',failed_stage=None,after=after,after_sha256=core.digest(after),
          provisional_transition=True,coverage_after=next_coverage,
          scope='Selected synthetic term events/carry; supplied completeness inherited after exact transition')
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status=getattr(exc,'status','invalid'),reason=str(exc)[:300],failed_stage=stage)
