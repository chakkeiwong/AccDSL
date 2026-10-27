"""Closed audit caller; native owners retain all financial semantics."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
# Fixed, reviewed entry points only. Caller input cannot select code or a path.
ENTRIES = {
    'state_inspection': ('inspect', 'data/accounting-master/company-state-typed-request-20261028/request.py'),
    'policy_effect': ('inspect', 'data/accounting-master/company-state-policy-effects-20261028/effects.py'),
    'book_report': ('report', 'scripts/company_book_reports_v1.py'),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def registry():
    return json.loads((HERE / 'registry.json').read_text())


def schema():
    def closed(fields):
        return dict(type='object', properties=fields, required=list(fields), additionalProperties=False)
    text = dict(type='string', minLength=1, pattern=r'\S')
    hash_value = dict(type='string', pattern='^[0-9a-f]{64}$')
    time_value = dict(type='string', format='date-time')
    evidence = dict(type='array', minItems=1, uniqueItems=True, items=text)
    audit = closed(dict(use=dict(const='audit_only'), view=dict(const='archival_exogenous_stress')))
    actor = closed(dict(use=dict(enum=['actor_observation', 'actor_action']), actor_id=text,
                        economic_time=time_value, decision_cutoff=time_value, system_cutoff=time_value,
                        observation_or_action=text, receipt_evidence_refs=evidence, authority_evidence_refs=evidence))
    resource = closed(dict(id=text, sha256=hash_value, byte_length=dict(type='integer', minimum=0)))
    result = closed(dict(profile=dict(const='CompanyNativeRequest/1'), capability=text, operation=text,
        implementation_sha256=hash_value, payload=dict(type='object'), payload_sha256=hash_value,
        resources=dict(type='array', items=resource),
        population=closed(dict(scope=dict(const='supplied_native_input'), actual_company_coverage=dict(const='unknown'))),
        information=dict(oneOf=[audit, actor]), joins=dict(type='array', uniqueItems=True, items=text)))
    result['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    return result


def answer(status, **fields):
    return dict(profile='CompanyNativeResponse/1', dispatch_status=status, source_admission=False,
                actor_information_admission=False, legal_authority_admission=False,
                population_complete=False, full_company_constructor=False, financial_composition=False,
                physical_durability=False, **fields)


def native_module(capability):
    # Internal helper takes only a fixed registry key, never user-supplied code.
    _, relative = ENTRIES[capability]
    sys.path.insert(0, str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('common_native_' + capability, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dispatch(request, resources):
    errors = list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(request))
    if errors:
        return answer('invalid', reason='envelope_schema', field=list(errors[0].path))
    capability = request['capability']
    if capability not in ENTRIES:
        return answer('unsupported', reason='native_capability')
    operation, relative = ENTRIES[capability]
    if request['operation'] != operation:
        return answer('unsupported', reason='native_operation')
    pin = registry()[capability]['implementation_sha256']
    if request['implementation_sha256'] != pin:
        return answer('invalid', reason='implementation_digest')
    if sha256((ROOT / relative).read_bytes()).hexdigest() != pin:
        return answer('invalid', reason='implementation_changed')
    payload = request['payload']
    try:
        if digest(payload) != request['payload_sha256']:
            return answer('invalid', reason='payload_digest')
    except (TypeError, ValueError):
        return answer('invalid', reason='non_json_payload')
    required = {'request'} if capability == 'book_report' else {'request', 'path'}
    if set(payload) != required:
        return answer('invalid', reason='payload_fields')
    descriptors = request['resources']
    ids = [r['id'] for r in descriptors]
    expected_ids = set() if capability == 'book_report' else {'source'}
    if len(ids) != len(set(ids)) or set(ids) != expected_ids:
        return answer('invalid', reason='resource_descriptors')
    if type(resources) is not dict or set(resources) != expected_ids:
        return answer('invalid', reason='resource_set')
    for ref in descriptors:
        raw = resources[ref['id']]
        if type(raw) is not bytes:
            return answer('invalid', reason='resource_not_bytes')
        if len(raw) != ref['byte_length'] or sha256(raw).hexdigest() != ref['sha256']:
            return answer('invalid', reason='resource_digest')
    if request['joins']:
        return answer('unsupported', reason='cross_profile_join', requested_joins=deepcopy(request['joins']))
    if request['information']['use'] != 'audit_only':
        return answer('unsupported', reason='actor_operator_unimplemented',
                      actor_requirement=deepcopy(request['information']))
    module = native_module(capability)
    try:
        if capability == 'book_report':
            native = module.report(payload['request'])
        else:
            native = module.inspect(payload['request'], payload['path'], resources['source'])
    except Exception as exc:
        # An exception is not rewritten as a native financial refusal.
        return answer('native_exception', exception=dict(type=type(exc).__name__,
                      module=type(exc).__module__, message=str(exc)))
    return answer('returned', capability=capability, operation=operation,
        request_sha256=digest(request), implementation_sha256=pin,
        population=deepcopy(request['population']), information=deepcopy(request['information']),
        native_result=native)
