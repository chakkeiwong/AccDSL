"""Selected complete internal claims; retained evaluators own every condition."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'admitted-program-binding-20261026'))
import binding
a=binding.admission;c=binding.c;core=binding.core;guards=binding.composer.guards
PROFILE='CompleteClaimsOpening/1'
POPULATION='SuppliedClaimPopulation/1'
CALL='CompleteClaimsOpeningCall/1'
PROGRAM='AdmittedCompleteClaimsProgram/1'
FLAGS=dict(executed=False,source_admission=False,accounting_admission=False,production_ready=False,
           actual_population_completeness=False,durable=False)
EXCLUDED=['empty_claims','claim_total']

def make_contract(template,invariant):
    return dict(profile=PROFILE,empty_template=deepcopy(template),empty_template_sha256=core.digest(template),
                state_invariant=deepcopy(invariant),invariant_sha256=core.digest(invariant),excluded_stages=deepcopy(EXCLUDED),
                residuals=['Complete supplied internal claim state only; actual-source completeness unadmitted'])

def population(book,provenance):
    return dict(profile=POPULATION,status='complete',map_pointer='/claims',book_sha256=core.digest(book),provenance=provenance)

def make_call(selection,contract,body,population):
    result=dict(profile=CALL,input_order_sha256=a.order_digest(body))
    for name,value in [('selection',selection),('contract',contract),('input',body),('population',population)]:
        result[name+'_sha256']=core.digest(value)
    return result

def derive(selection,contract):
    c.closed(contract,['profile','empty_template','empty_template_sha256','state_invariant','invariant_sha256','excluded_stages','residuals'],'contract_fields')
    c.need(contract['profile']==PROFILE,'contract_profile')
    core.identifiers(contract['residuals'],'contract_residuals',True)
    c.need(contract['excluded_stages']==EXCLUDED,'exact_excluded_stages')
    template=contract['empty_template'];invariant=contract['state_invariant']
    a.compile_template(template);guards.validate(invariant)
    c.need(core.digest(template)==contract['empty_template_sha256']==selection['template_sha256'],'selected_empty_template')
    c.need(core.digest(invariant)==contract['invariant_sha256']==selection['invariant_sha256'],'selected_full_invariant')
    c.need(invariant['context']==template['context']==selection['context'],'selected_context')
    stages={s['id']:s for s in template['stages']}
    c.need(stages.get('empty_claims')==dict(id='empty_claims',op='equals',reason='empty_opening_claim_population_required',
                                         path=['opening','memory','claims'],value={}),'empty_population_stage')
    total=stages.get('claim_total');c.need(type(total) is dict and total['op']=='predicate' and total['reason']=='claim_receivable_sum','empty_total_stage')
    manifest=total['manifest'];c.need(set(manifest['inputs'])=={'receivable'},'empty_total_input')
    typ=manifest['inputs']['receivable']['type']
    c.need(typ.get('kind')=='rational','empty_total_type')
    c.need(total['bindings']=={'receivable':dict(kind='role_balance',role='receivables',type=typ)},'empty_total_binding')
    expected=dict(id='claim_total',guard=dict(op='const',type=core.BOOL,value=True),guard_requires=[],
        predicate=dict(op='eq',left=dict(op='const',type=typ,value='0/1'),right=dict(op='ref',id='receivable')),
        requires=['receivable'],admission_refs=[],on_false='invalid',on_unknown='unresolved')
    c.need(manifest['requirements']==[expected],'empty_total_predicate')
    derived=deepcopy(template);derived['stages']=[s for s in derived['stages'] if s['id'] not in EXCLUDED]
    a.compile_template(derived)
    return derived

def assess(selection,contract,body,completeness,call):
    result=dict(profile=PROFILE,**FLAGS);stage='selection'
    try:
        c.closed(call,['profile','selection_sha256','contract_sha256','input_sha256','population_sha256','input_order_sha256'],'call_fields')
        c.need(call['profile']==CALL,'call_profile')
        for name,value in [('selection',selection),('contract',contract),('input',body),('population',completeness)]:
            c.need(call[name+'_sha256']==core.digest(value),'stale_'+name)
        c.need(call['input_order_sha256']==a.order_digest(body),'stale_input_order')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='contract';derived=derive(selection,contract)
        stage='completeness'
        c.closed(completeness,['profile','status','map_pointer','book_sha256','provenance'],'population_fields')
        c.need(completeness['profile']==POPULATION and completeness['map_pointer']=='/claims','population_profile_or_scope')
        c.need(completeness['status'] in ('complete','partial','unknown'),'population_status')
        c.base.text(completeness['provenance'],'population_provenance')
        c.need(completeness['book_sha256']==core.digest(body['opening']),'stale_population_book')
        if completeness['status']!='complete':
            return dict(result,status='unresolved',reason='complete_supplied_population_required',failed_stage=stage)
        stage='structural_admission'
        structural=a.assess(derived,body,a.make_call(derived,body))
        result.update(derived_template_sha256=core.digest(derived),structural=structural)
        if structural['status']!='opening_admitted':
            return dict(result,status=structural['status'],reason=structural['reason'],failed_stage=stage)
        stage='full_invariant'
        invariant=guards.assess(contract['state_invariant'],body['opening'],body['memory_definition'],body['schemas'])
        result['invariant']=invariant
        if invariant['status']!='collection_total_requirements_satisfied':
            status=invariant['status'] if invariant['status'] in ('invalid','unsupported','unresolved') else 'invalid'
            return dict(result,status=status,reason='complete_claim_invariant:'+invariant['status'],failed_stage=stage)
        return dict(result,status='opening_admitted',failed_stage=None,
            scope='Explicit complete supplied internal claim state; no actual-source completeness or accounting admission')
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status=getattr(exc,'status','invalid'),reason=str(exc)[:300],failed_stage=stage)

def make_program_call(selection,contract,body,completeness,program):
    call=make_call(selection,contract,body,completeness);call['profile']=PROGRAM
    call.update(program_sha256=core.digest(program),program_order_sha256=a.order_digest(program))
    return call

def execute(selection,contract,body,completeness,program,call):
    result=dict(profile=PROGRAM,**FLAGS,admission=None,delegated=None);stage='selection'
    try:
        expected=make_program_call(selection,contract,body,completeness,program)
        c.need(call==expected,'stale_or_incomplete_program_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='complete_opening'
        admitted=assess(selection,contract,body,completeness,make_call(selection,contract,body,completeness))
        result['admission']=admitted
        if admitted['status']!='opening_admitted':
            return dict(result,status=admitted['status'],reason=admitted['reason'],failed_stage=stage)
        # The original adapter still checks all selected facts/rules/commands.
        # Its structural admission is evaluated again; no caller success flag is used.
        stage='bound_execution';derived=derive(selection,contract);selected=deepcopy(selection)
        selected['template_sha256']=core.digest(derived)
        delegated=binding.execute(selected,derived,body,program,binding.make_call(selected,derived,body,program))
        result.update(delegated=delegated,executed=bool(delegated['executed']))
        if delegated.get('execution') is None:
            return dict(result,status=delegated['status'],reason=delegated.get('reason','bound_program_refused'),failed_stage=stage)
        return dict(result,status=delegated['status'],failed_stage=None,
            scope='Selected complete internal claims admitted before unchanged bound program execution')
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status=getattr(exc,'status','invalid'),reason=str(exc)[:300],failed_stage=stage)
