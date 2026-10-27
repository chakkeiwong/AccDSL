"""Preserve economic funding failures without relabeling malformed state."""
from copy import deepcopy
import method_requirements_v1 as core
import method_collection_totals_v1 as totals

PROFILE='MethodStateAssessment/1'
BOUNDARY={**totals.BOUNDARY,'scope':'selected_state_requirements_only'}


def validate(definition):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','method_id','version','totals','false_categories',
                           'residual_prerequisites'],'state_assessment_definition')
    core.need(definition['profile']==PROFILE,'state_assessment_profile')
    for key in ['method_id','version']:core.text(definition[key],key)
    totals.validate(definition['totals'])
    rules={r['id']:r for r in definition['totals']['assessment']['requirements']}
    mapping=definition['false_categories']
    core.need(type(mapping) is dict,'false_categories')
    for key,category in mapping.items():
        core.need(key in rules,'undeclared_category_requirement')
        core.need(category=='funding_failure','unsupported_false_category')
        core.need(rules[key]['on_false']=='invalid','category_requires_invalid_false')
    core.identifiers(definition['residual_prerequisites'],'residual_prerequisites',True)
    return definition


def assess(definition,values,available_capabilities):
    try:
        validate(definition)
        original=totals.assess(definition['totals'],values,available_capabilities)
        core.need('assessment' in original,'total_structure_invalid:'+original.get('reason',''))
        selected=original['assessment'];classified=[]
        statuses=[original['snapshot_assessment']['status']]
        if selected['missing_capabilities']:statuses.append('unsupported')
        statuses.extend(f['consequence'] for f in selected['required_known_findings'])
        for finding in selected['findings']:
            category=finding['consequence']
            if (finding['id'] in definition['false_categories'] and finding['activation']=='active'
                    and finding['body_truth']=='false' and category=='invalid'):
                category=definition['false_categories'][finding['id']]
            classified.append({'requirement':finding['id'],'original_consequence':finding['consequence'],
                               'category':category,'finding':deepcopy(finding)})
            statuses.append(category)
        status=next((s for s in ['invalid','funding_failure','unsupported','unresolved'] if s in statuses),
                    'state_requirements_satisfied')
        return {**BOUNDARY,'profile':PROFILE,'status':status,'definition_sha256':core.digest(definition),
                'values_sha256':core.digest(values),'original_assessment':original,'classified_findings':classified,
                'residual_prerequisites':deepcopy(definition['residual_prerequisites'])}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:250]}
