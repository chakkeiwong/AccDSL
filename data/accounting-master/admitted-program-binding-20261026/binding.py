"""Finite selected-contract binding; no native lifecycle dependency."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'declared-opening-admission-20261026'))
import admission
sys.path.insert(0,str(HERE.parent/'declarative-event-program-20261026'))
import composer
core=admission.core;c=admission.c
PROFILE='AdmittedDeclarativeProgram/1'
SELECTION='DeclaredProgramSelection/1'
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,durable=False)

def make_call(selection,template,native_input,program):
    return dict(profile=PROFILE,selection_sha256=core.digest(selection),template_sha256=core.digest(template),
                input_sha256=core.digest(native_input),program_sha256=core.digest(program),
                input_order_sha256=admission.order_digest(native_input),program_order_sha256=admission.order_digest(program))

def project_commands(program):
    commands=[]
    for cmd in program['commands']:
        item=deepcopy(cmd)
        if item['kind']=='event':item.pop('order')
        elif item['kind']=='carry':item.pop('memory_policies')
        commands.append(item)
    return commands

def execute(selection,template,native_input,program,call):
    result=dict(profile=PROFILE,**FLAGS,executed=False);stage='selection'
    try:
        c.closed(call,['profile','selection_sha256','template_sha256','input_sha256','program_sha256',
                       'input_order_sha256','program_order_sha256'],'call_fields')
        c.need(call['profile']==PROFILE,'call_profile')
        for name,value in [('selection',selection),('template',template),('input',native_input),('program',program)]:
            c.need(call[name+'_sha256']==core.digest(value),'stale_'+name)
        c.need(call['input_order_sha256']==admission.order_digest(native_input),'stale_input_order')
        c.need(call['program_order_sha256']==admission.order_digest(program),'stale_program_order')
        result.update(call)
        c.closed(selection,['profile','context','native_profile','program_profile','roles','unit_cost_pointer',
                            'policy','invariant_sha256','rules_sha256','template_sha256','residuals'],'selection_fields')
        c.need(selection['profile']==SELECTION,'selection_profile')
        core.identifiers(selection['residuals'],'selection_residuals',True)
        c.need(selection['template_sha256']==core.digest(template),'selected_template')
        c.need(selection['context']==template['context'],'selected_context')
        stage='opening_admission'
        admitted=admission.assess(template,native_input,admission.make_call(template,native_input))
        result['admission']=admitted
        if admitted['status']!='opening_admitted':
            return dict(result,status=admitted['status'],reason=admitted['reason'],failed_stage=stage,execution=None)
        stage='program_binding'
        c.need(native_input['profile']==selection['native_profile'] and program['profile']==selection['program_profile'],'selected_profiles')
        c.need(native_input['roles']==selection['roles'],'selected_roles')
        c.need(native_input['unit_cost_pointer']==selection['unit_cost_pointer'],'selected_unit_cost_pointer')
        c.need(native_input['policy']==selection['policy'],'selected_policy')
        for key in ['name','opening','schemas','mapping','memory_definition']:
            c.need(core.canonical(native_input[key])==core.canonical(program[key]),'shared_field:'+key)
        c.need(program['opening']['context']==selection['context'],'program_context')
        c.need(core.digest(program['state_invariant'])==program['invariant_sha256']==selection['invariant_sha256'],'selected_invariant')
        c.need(core.digest(program['rules'])==selection['rules_sha256'],'selected_rules')
        c.need(program['carry_policy']=={'mode':native_input['policy']['carry'],'provenance':native_input['policy']['provenance']},'selected_carry_policy')
        projected=project_commands(program)
        c.need(core.canonical(projected)==core.canonical(native_input['commands']),'complete_commands')
        for left,right in zip(projected,native_input['commands']):
            if left['kind']=='event':
                c.need(list(left['event']['inputs'])==list(right['event']['inputs']),'event_input_order')
        stage='execution';executed=composer.run(program,composer.make_call(program))
        return dict(result,status=executed['status'],executed=True,execution=executed,
                    scope='Selected finite opening and event-program correspondence; no generic rule-equivalence proof')
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status=getattr(exc,'status','invalid'),reason=str(exc)[:300] or type(exc).__name__,failed_stage=stage,execution=None)
