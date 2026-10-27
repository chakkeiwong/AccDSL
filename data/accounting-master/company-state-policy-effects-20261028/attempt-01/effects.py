"""Audit-only policy effects on one exact native owner; no financial postings here."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'data/accounting-master/company-state-population-admission-20261028'))
import admission
rel = admission.rel
spec = importlib.util.spec_from_file_location(
    'policy_effects_existing_generator',
    ROOT / 'data/accounting-master/company-policy-20261023/policy.py')
policy_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy_module)
OWNER = 'CompanyOperationPathDraft/1'


def schema():
    def closed(fields):
        return dict(type='object', properties=fields, required=list(fields), additionalProperties=False)
    text = dict(type='string', minLength=1)
    digest = dict(type='string', pattern='^[0-9a-f]{64}$')
    return closed(dict(
        profile=dict(const='CompanyPolicyEffectRequest/1'),
        owner=text, role=text, path_sha256=digest, source_sha256=digest,
        context=closed(dict(entity=text, book=text, currency=text)),
        information=closed(dict(use=text, view=text)),
        policy=policy_module.schema()))


def answer(status, **fields):
    return dict(status=status, source_admission=False, actor_information_admission=False,
                legal_authority_admission=False, real_behavior_evidence=False,
                forecast_admission=False, full_company_constructor=False, **fields)


def inspect(request, path, source):
    errors = list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(request))
    if errors:
        return answer('invalid', reason='request_schema', field=list(errors[0].path))
    if request['owner'] != OWNER:
        return answer('unsupported', reason='native_owner')
    if request['role'] not in {'generate_inputs', 'validate_equalities', 'compare_targets'}:
        return answer('unsupported', reason='policy_effect')
    if request['information'] != dict(use='audit_only', view='archival_exogenous_stress'):
        return answer('unsupported', reason='actor_information_request')
    if not isinstance(path, dict) or path.get('profile') != OWNER:
        return answer('invalid', reason='path_profile')
    if request['path_sha256'] != rel.native.digest(path):
        return answer('invalid', reason='path_digest')
    if request['source_sha256'] != sha256(source).hexdigest():
        return answer('invalid', reason='source_digest')
    if path.get('initial_year', {}).get('context') != request['context']:
        return answer('invalid', reason='context_mismatch')
    proposed = policy_module.generate(path, request['policy'])
    if proposed['status'] != 'materialized_conditional_path':
        return answer(proposed['status'], reason='native_policy_refusal', native_policy_result=proposed,
                      native_result=None, native_execution_attempted=False)
    generating = request['role'] == 'generate_inputs'
    selected_path = proposed['path'] if generating else path
    checked = admission.inspect(selected_path, source, rel.native.digest(selected_path))
    native = checked['native_result']
    result = answer('generated_inputs' if generating else 'inspected',
        profile='CompanyPolicyEffectResult/1', request=deepcopy(request),
        request_sha256=rel.native.digest(request), input_path_sha256=request['path_sha256'],
        evaluated_path_sha256=rel.native.digest(selected_path), role=request['role'],
        native_result=native, population_inspection=checked, native_execution_attempted=True,
        native_execution_complete=native['status']=='complete_conditional',
        financial_effect_owner=OWNER, history_rewritten=generating,
        information_admission=deepcopy(proposed['information_admission']))
    if generating:
        result['materialization'] = proposed
        result['materialization_verification'] = policy_module.verify_materialization(path, request['policy'], proposed)
        return result
    population = checked['population_inspection']
    relationship = population['relationship_result'] if population is not None else None
    events = {} if relationship is None else {e['id']:e for e in relationship['event_nodes']}
    edges = {} if relationship is None else {(e['event'],e['claim_id']):e for e in relationship['relation_edges'] if e['kind']=='settles_claim'}
    rows = []
    for expected in proposed['allocation_trace']:
        event = rel.event_key(request['policy']['year_index'], expected['operation_id'])
        row = dict(event=event, claim_id=expected['claim_id'], target=expected['generated_amount'])
        edge = edges.get((event, expected['claim_id']))
        if edge is None:
            row.update(status='unresolved', actual=None, actual_minus_target=None,
                       reason='opening_not_inspected' if relationship is None else 'allocation_not_executed',
                       event_status=events.get(event, {}).get('status'))
        else:
            difference = Fraction(edge['amount']) - Fraction(expected['generated_amount'])
            row.update(status='known_conditional', actual=edge['amount'], actual_minus_target=rel.wire(difference))
            if request['role'] == 'validate_equalities':
                row['satisfies_equality'] = difference == 0
        rows.append(row)
    complete = all(row['status']=='known_conditional' for row in rows)
    result.update(comparisons=rows, comparison_evidence_complete=complete,
                  comparison_scope='specified claim allocations in the supplied executed path',
                  equality_constraint_result=None)
    if request['role'] == 'validate_equalities':
        violations = [dict(event=r['event'], claim_id=r['claim_id']) for r in rows if r.get('satisfies_equality') is False]
        result.update(known_violations=violations, equality_constraint_result=
                      ('violated' if violations else 'satisfied') if complete else 'unresolved')
        result['status'] = ('violates_equalities' if violations else 'satisfies_equalities') if complete else 'unresolved'
    else:
        result['status'] = 'compared_targets' if complete else 'unresolved'
    return result
