"""Version-explicit record binding; the v1 shadow validates bindings only."""
from copy import deepcopy
import method_requirements_v1 as core
import method_requirements_v2 as dimensional
import method_requirement_versions as versions
import method_input_binding_v1 as prior

PROFILE = 'MethodInputBinding/2'
SCHEMA = 'RequirementInputSchema/2'
BOUNDARY = {'executed': False, 'source_admission': False,
            'accounting_admission': False, 'method_eligible': False,
            'schema_meaning': 'caller_declared_selected_fields_only'}


def encoded(profile, value):
    versions.typed(profile, value)
    return deepcopy(value) if profile == core.PROFILE else dimensional.encoded(value)


def schema(value, profile):
    core.need(len(core.canonical(value)) <= core.MAX_BYTES, 'schema_size_limit')
    core.closed(value, ['profile', 'requirements_profile', 'schema_id', 'fields'], 'input_schema')
    core.need(value['profile'] == SCHEMA, 'input_schema_profile')
    core.need(value['requirements_profile'] == profile, 'schema_requirements_profile_mismatch')
    versions.module(profile)
    core.need(type(value['fields']) is dict, 'schema_fields')
    shadow = deepcopy(value)
    shadow.pop('requirements_profile')
    shadow['profile'] = prior.SCHEMA
    for pointer, field in value['fields'].items():
        core.closed(field, ['type', 'role', 'encoding', 'missing'], 'input_schema_field')
        shadow['fields'][pointer]['type'] = encoded(profile, field['type'])
    return prior.schema(shadow)


def binding_shadow(definition):
    """Cover input declarations without evaluating original method predicates."""
    inputs = deepcopy(definition['inputs'])
    predicates = []
    for key, declaration in inputs.items():
        declaration['type'] = encoded(definition['profile'], declaration['type'])
        predicates.append({'op': 'eq', 'left': {'op': 'ref', 'id': key},
                           'right': {'op': 'ref', 'id': key}})
    predicate = ({'op': 'all', 'args': predicates} if predicates else
                 {'op': 'const', 'type': core.BOOL, 'value': True})
    return {'profile': core.PROFILE, 'method_id': 'internal.binding-only-shadow',
            'version': '1', 'inputs': inputs, 'requirements': [{
                'id': 'binding-only', 'predicate': predicate, 'requires': sorted(inputs),
                'admission_refs': [], 'on_false': 'invalid', 'on_unknown': 'unresolved'}],
            'capabilities': [], 'residual_prerequisites': ['No semantic assessment of this shadow.']}


def bind(plan, manifests, schemas, blobs):
    try:
        core.need(len(core.canonical(plan)) <= core.MAX_BYTES, 'plan_size_limit')
        core.closed(plan, ['profile', 'manifest_digest', 'records', 'bindings'], 'binding_plan')
        core.need(plan['profile'] == PROFILE, 'binding_profile')
        definition = prior.record(manifests, plan['manifest_digest'], 'manifest')
        versions.validate(definition)
        core.need(type(plan['records']) is dict, 'records')
        shadow = binding_shadow(definition)
        shadow_key = core.digest(shadow)
        shadow_plan = deepcopy(plan)
        shadow_plan.update(profile=prior.PROFILE, manifest_digest=shadow_key)
        shadow_schemas = {}
        for name, reference in plan['records'].items():
            core.closed(reference, ['raw_sha256', 'schema_digest'], 'record_reference')
            original = prior.record(schemas, reference['schema_digest'], 'schema')
            converted = schema(original, definition['profile'])
            key = core.digest(converted)
            shadow_schemas[key] = converted
            shadow_plan['records'][name]['schema_digest'] = key
        result = prior.bind(shadow_plan, {shadow_key: shadow}, shadow_schemas, blobs)
        if result['status'] != 'bound':
            return result
        for key, item in result['lineage'].items():
            reference = plan['records'][item['record']]
            item['schema_digest'] = reference['schema_digest']
            item['type'] = deepcopy(definition['inputs'][key]['type'])
            item['requirements_profile'] = definition['profile']
        result.update(plan_digest=core.digest(plan), manifest_digest=plan['manifest_digest'],
                      requirements_profile=definition['profile'])
        result['binding_validation'] = {
            'meaning': 'internal binding-only v1 shadow; never semantically assessed',
            'manifest_digest': shadow_key, 'plan_digest': core.digest(shadow_plan),
            'schema_digests': {name: item['schema_digest']
                               for name, item in shadow_plan['records'].items()}}
        return result
    except prior.Unavailable as exc:
        return {**BOUNDARY, 'status': 'unsupported', 'reason': str(exc)}
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        return {**BOUNDARY, 'status': 'invalid', 'reason': str(exc)[:250]}


def assess_bound(plan, manifests, schemas, blobs, available_capabilities):
    result = bind(plan, manifests, schemas, blobs)
    if result['status'] == 'bound':
        result['assessment'] = versions.assess(
            manifests[plan['manifest_digest']], result['values'], available_capabilities)
    return result
