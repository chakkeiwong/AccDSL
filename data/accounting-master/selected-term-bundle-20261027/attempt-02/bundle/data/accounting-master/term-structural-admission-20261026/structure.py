"""Finite selected state structure over preserved stages and scalar validators."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'term-semantic-composition-20261026'))
import bundle
sys.path.insert(0,str(HERE.parent/'declared-opening-admission-20261026'))
import admission
p=bundle.p;core=bundle.core
PROFILE='SelectedStateStructure/1';CALL='SelectedStateStructureCall/1'
CONTRACT='SelectedTermStateContract/1';CONTRACT_CALL='SelectedTermStateContractCall/1'
FLAGS=dict(p.FLAGS,method_eligible=False,opening_admitted=False,future_commands_validated=False)

def validate(spec,definition):
    p.base.memory.bounded(spec)
    core.closed(spec,['profile','normalization','template','projections','checks','residuals'],'state_structure')
    core.need(spec['profile']==PROFILE,'state_structure_profile')
    mapping=spec['normalization'];core.need(type(mapping) is dict and bool(mapping),'normalization_record')
    for target,source in mapping.items():p.base.text(target,'normalized_key');p.base.text(source,'source_key')
    core.need(len(set(mapping.values()))==len(mapping),'injective_normalization')
    core.need(mapping.get('opening')=='book' and mapping.get('memory_definition')=='memory_definition' and mapping.get('schemas')=='schemas','structure_core_fields')
    admission.compile_template(spec['template'])
    core.need(type(spec['projections']) is dict and len(spec['projections'])<=16,'structure_projections')
    for name,source in spec['projections'].items():
        p.base.text(name,'projection_name');p.compile_spec(source,definition)
        core.need(source['context']==spec['template']['context'],'structure_projection_context')
    core.need(type(spec['checks']) is list and 0<len(spec['checks'])<=64,'structure_check_limit')
    used=set();identities=set()
    for check in spec['checks']:
        core.need(type(check) is dict,'structure_check');kind=check.get('op')
        core.need(kind in ('sha256_format','projected_nonblank_text'),'structure_check_op')
        core.closed(check,['id','op','reason']+(['path'] if kind=='sha256_format' else ['projection','field']),'structure_check')
        for k in ('id','reason'):p.base.text(check[k],k)
        core.need(check['id'] not in identities,'duplicate_structure_check');identities.add(check['id'])
        if kind=='sha256_format':admission.path_valid(check['path'])
        else:
            name=check['projection'];p.base.text(name,'check_projection');core.need(name in spec['projections'],'structure_projection_missing')
            field=check['field'];p.base.text(field,'check_field');source=spec['projections'][name]
            core.need(field in source['fields'] and source['fields'][field]['type']==p.guards.TEXT,'structure_text_type')
            used.add(name)
    core.need(used==set(spec['projections']),'unused_structure_projection')
    core.identifiers(spec['residuals'],'structure_residuals',True)

def normalize(state,spec):
    core.need(type(state) is dict and set(state)==set(spec['normalization'].values()),'exact_original_state_fields')
    inverse={source:target for target,source in spec['normalization'].items()}
    return {inverse[name]:deepcopy(value) for name,value in state.items()}

def make_call(spec,state,coverages):
    return dict(profile=CALL,spec_sha256=core.digest(spec),state_sha256=core.digest(state),
      state_order_sha256=p.order_digest(state),spec_order_sha256=p.order_digest(spec),coverages_sha256=core.digest(coverages))

def assess(spec,state,coverages,call):
    result=dict(profile=PROFILE,**FLAGS);stage='call'
    try:
        core.need(call==make_call(spec,state,coverages),'stale_state_structure_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='definition';validate(spec,state['memory_definition'])
        stage='state';p.base.binding.bounded(state);p.base.memory.bounded(state)
        normalized=normalize(state,spec);result['normalized_input']=normalized
        result['normalized_order_sha256']=p.order_digest(normalized)
        stage='stages';evaluation=admission.assess(spec['template'],normalized,admission.make_call(spec['template'],normalized))
        result['stage_assessment']=evaluation
        if evaluation['status']!='opening_admitted':return dict(result,status=evaluation['status'],reason=evaluation['reason'],failed_stage=stage)
        stage='checks';core.need(type(coverages) is dict and set(coverages)==set(spec['projections']),'exact_structure_coverages')
        projections={};findings=[]
        for name,source in spec['projections'].items():
            args=(source,state['book'],state['memory_definition'],state['schemas'],coverages[name])
            projections[name]=p.project(*args,p.make_call(*args))
        result['projections']=projections
        for check in spec['checks']:
            finding=dict(id=check['id'],op=check['op'],status='satisfied',evidence=[])
            try:
                if check['op']=='sha256_format':
                    value=admission.at(normalized,check['path']);p.base.binding.hash_string(value)
                    finding['evidence'].append(dict(path=check['path'],value=value))
                else:
                    projected=projections[check['projection']]
                    if projected['status']!='projected':
                        finding.update(status=projected['status'],reason=projected['reason']);findings.append(finding);continue
                    for index,row in enumerate(projected['rows']):
                        value=row[check['field']]['value'];p.base.text(value,check['reason'])
                        finding['evidence'].append(dict(row=index,value=value,source=projected['lineage'][index]['fields'][check['field']]))
            except (ValueError,TypeError,KeyError,IndexError) as exc:finding.update(status='invalid',reason=str(exc))
            findings.append(finding)
        result['findings']=findings
        statuses=[r['status'] for r in findings]
        status=next((s for s in ('invalid','unsupported','unresolved') if s in statuses),'state_structure_satisfied')
        return dict(result,status=status,failed_stage=None,residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)

def validate_contract(contract,state):
    core.closed(contract,['profile','context','roles','unit_cost_pointer','structure','semantics','residuals'],'term_state_contract')
    core.need(contract['profile']==CONTRACT,'term_state_contract_profile')
    validate(contract['structure'],state['memory_definition']);bundle.validate(contract['semantics'],state['memory_definition'])
    core.need(contract['context']==contract['structure']['template']['context']==contract['semantics']['context'],'contract_context')
    core.need(type(contract['roles']) is dict,'selected_roles_record')
    for k,v in contract['roles'].items():p.base.text(k,'selected_role');p.base.text(v,'selected_account')
    p.exact_pointer(contract['unit_cost_pointer'])
    # Preserve the selected receivables account rather than accepting stale bundle linkage.
    core.need(contract['semantics']['common']['globals']['receivable']['account']==contract['roles']['receivables'],'selected_receivable_binding')
    core.identifiers(contract['residuals'],'contract_residuals',True)

def contract_call(contract,state,coverage,selection):
    return dict(profile=CONTRACT_CALL,contract_sha256=core.digest(contract),state_sha256=core.digest(state),
      state_order_sha256=p.order_digest(state),contract_order_sha256=p.order_digest(contract),
      population_sha256=core.digest(coverage),reviewed_selection=selection)

def admit(contract,state,coverage,selection,call):
    result=dict(profile=CONTRACT,**FLAGS);stage='call'
    try:
        core.need(call==contract_call(contract,state,coverage,selection),'stale_term_contract_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        core.need(selection==core.digest(contract),'reviewed_term_contract')
        stage='contract';validate_contract(contract,state)
        core.need(state['roles']==contract['roles'] and state['unit_cost_pointer']==contract['unit_cost_pointer'],'selected_role_cost_binding')
        core.need(state['book']['context']==contract['context'],'selected_state_context')
        core.closed(coverage,['claims','terms','assessments'],'contract_populations')
        structure_cov={name:bundle.nested_coverage(source,coverage) for name,source in contract['structure']['projections'].items()}
        stage='structure';structure=assess(contract['structure'],state,structure_cov,make_call(contract['structure'],state,structure_cov))
        result['structure']=structure
        if structure['status']!='state_structure_satisfied':
            return dict(result,status=structure['status'],reason=structure.get('reason','structure_conditions'),failed_stage=stage)
        stage='semantics';s=contract['semantics'];h=core.digest(s)
        args=(s,state['book'],state['memory_definition'],state['schemas'],coverage,h)
        semantics=bundle.assess(*args,bundle.make_call(*args));result['semantics']=semantics
        if semantics['status']!='term_semantic_requirements_satisfied':
            return dict(result,status=semantics['status'],reason=semantics.get('reason','semantic_conditions'),failed_stage=stage)
        return dict(result,status='selected_term_state_satisfied',failed_stage=None,
          scope='Selected complete supplied synthetic term snapshot; future commands and new-period opening remain unchecked',
          derived_selection_basis='Semantics derived from independently reviewed combined contract',residuals=deepcopy(contract['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
