"""Conditional joint measurements from the exact retained statement description.

This finite reference adapter admits neither accounting policies nor source facts.
Its optional hypotheses are a closed registry, not user-authored solver code.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

import joint_measurement_constraints_v1 as joint
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'data/accounting-master/joint-source-relation-binding-20261024'
LOCK_SHA256 = '88a2ad8a69e22a17e28b34d496b1a0bc2ab4ef3651fe579f271a2a86dbecf67e'
PROFILE = 'RetainedJointSourceRelations/1'
SUPPORTED = tuple(group + '.balance:' + key for group in ('annual', 'interim')
                  for key in ('current_assets', 'noncurrent_assets', 'assets',
                              'current_liabilities', 'noncurrent_liabilities',
                              'liabilities', 'equity', 'liabilities_equity', 'identity'))
BOUNDARY = {**joint.BOUNDARY, 'scope': 'selected_retained_balance_measurements_only'}
core = joint.core


def verify_dependencies():
    raw = (PACKAGE / 'dependency-lock.json').read_bytes()
    core.need(sha256(raw).hexdigest() == LOCK_SHA256, 'dependency_lock_changed')
    locks = json.loads(raw)
    for name, digest in locks.items():
        core.need(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                  'dependency_changed:' + name)
    return locks


verify_dependencies()
_path = ROOT / 'data/accounting-master/statement-context-coverage-20261024/statement_context.py'
_spec = importlib.util.spec_from_file_location('joint_source_frozen_statement_context', _path)
statement = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(statement)


def rounding_hypothesis():
    return {'id': 'displayed_million_nearest_ties_away_v1', 'status': 'proposed',
            'meaning': 'Each selected amount is rounded to the nearest displayed USD million; exact half ties round away from zero.',
            'mode': 'nearest_ties_away_from_zero', 'quantum': '1/1', 'unit': 'USD million'}


def identity_hypothesis(relation_id):
    core.need(relation_id in SUPPORTED, 'unsupported_identity')
    return {'id': 'latent_identity:' + relation_id, 'status': 'proposed',
            'meaning': 'The underlying unrounded measurements satisfy the exact retained terms of ' + relation_id + '.'}


def fixture(selected=None, assume=False):
    """Authoring convenience; assumptions stay off unless explicitly requested."""
    selected = list(SUPPORTED if selected is None else selected)
    return {'profile': PROFILE, 'statement_request': statement.fixture(),
            'selected_relations': selected,
            'rounding_hypothesis': rounding_hypothesis() if assume else None,
            'identity_hypotheses': {key: identity_hypothesis(key) if assume else None
                                    for key in selected}}


def _budget(budget):
    core.closed(budget, joint.BUDGET_FIELDS, 'budget')
    b = joint.solver.Budget(**budget)
    core.need(b.max_cells <= 1 and b.max_integer_assignments <= 1 and b.max_slots == 0,
              'single_conjunction_budget')
    core.need(b.elapsed_ms <= 60000 and b.solver_timeout_ms <= 10000 and b.solver_rlimit <= 10000000,
              'reference_runtime_limit')


def build(body, budget):
    """Recompute source report and derive terms; never consume a caller report."""
    verify_dependencies()
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'request_size_limit')
    core.closed(body, ['profile', 'statement_request', 'selected_relations',
                       'rounding_hypothesis', 'identity_hypotheses'], 'source_request')
    core.need(body['profile'] == PROFILE, 'profile')
    selected = body['selected_relations']
    core.identifiers(selected, 'selected_relations')
    core.need(len(selected) <= len(SUPPORTED) and set(selected) <= set(SUPPORTED),
              'unsupported_relation_selection')
    _budget(budget)
    rounding = body['rounding_hypothesis']
    core.need(rounding is None or rounding == rounding_hypothesis(), 'rounding_hypothesis_mismatch')
    identities = body['identity_hypotheses']
    core.need(type(identities) is dict and set(identities) == set(selected), 'identity_selection_mismatch')
    for key in selected:
        core.need(identities[key] is None or identities[key] == identity_hypothesis(key),
                  'identity_hypothesis_mismatch:' + key)
    request = body['statement_request']
    core.need(request['source']['target'] == statement.OPS and request['source']['view'] == 'combined',
              'complete_combined_statement_required')
    preserved = statement.evaluate(request)
    core.need(len(preserved['observations']) == 256 and len(preserved['relations']) == 143,
              'complete_statement_required')
    source_rows = {row['id']: row for row in request['relations']}
    source_dispositions = {row['id']: row for row in preserved['relations']}
    observations, equations, mappings, local = {}, [], {}, []
    for key in selected:
        row = source_rows[key]
        core.need(row['kind'] == 'snapshot_sum' and row['comparison'] == 'terms'
                  and not row['omitted_source_rows'], 'unsupported_relation_shape')
        core.need(source_dispositions[key]['context_check']['status'] ==
                  'compatible_for_declared_displayed_relation', 'unsupported_relation_context')
        terms, legacy_terms, equation_type = [], [], None
        for side, sign in [('lhs', Q(1)), ('rhs', Q(-1))]:
            for term in row[side]:
                alias = term['alias']; item = preserved['observations'][alias]
                declaration = item['declaration']; observation = item['observation']
                ref = declaration['observation_ref']; digest = ref['digest']
                context = observation['context']; when = declaration['measurement_time']
                core.need(ref == observation['ref'], 'observation_ref_mismatch')
                core.need(context['unit'] == declaration['unit'] == 'USD million'
                          and when['kind'] == 'instant', 'unsupported_observation_context')
                typed_context = {k: v for k, v in context.items() if k != 'unit'}
                core.need('instant' not in typed_context, 'reserved_instant_context')
                typed_context['instant'] = when['at']
                typ = {'kind': 'rational', 'context': typed_context,
                       'dimensions': {'currency:USD': 1}, 'scale': '1000000/1'}
                joint.types.typed(typ)
                if equation_type is None: equation_type = typ
                core.need(typ == equation_type, 'equation_context_mismatch')
                value = observation['record']['body']['value']; interval = None
                if rounding is not None and value['tag'] == 'known_displayed':
                    amount = value['amount']; displayed = Q(int(amount['n']), int(amount['d']))
                    interval = statement.state.rounding_interval(displayed, Q(rounding['quantum']))
                premise = None if rounding is None else {k: rounding[k] for k in ('id', 'status', 'meaning')}
                definition = {'type': typ, 'interval': interval, 'interval_premise': premise,
                              'source_ref': ref['schema'] + ':' + digest}
                core.need(digest not in observations or observations[digest] == definition,
                          'shared_observation_mapping_conflict')
                observations[digest] = definition
                mapping = {'observation_ref': deepcopy(ref), 'original_context': deepcopy(context),
                           'measurement_time': deepcopy(when), 'aliases': [],
                           'reading_file_ref': deepcopy(item['reading_file_ref']),
                           'reading_pointer': item['reading_pointer']}
                if digest not in mappings: mappings[digest] = mapping
                if alias not in mappings[digest]['aliases']: mappings[digest]['aliases'].append(alias)
                coefficient = sign * joint.rational(term['coefficient'])
                coefficient_text = f'{coefficient.numerator}/{coefficient.denominator}'
                terms.append({'observation': digest, 'coefficient': coefficient_text})
                legacy_terms.append({'observation_ref': deepcopy(ref), 'coefficient': coefficient_text})
        equation = {'id': key, 'type': equation_type, 'terms': terms, 'rhs': '0/1',
                    'identity_premise': deepcopy(identities[key])}
        equations.append(equation)
        missing = []
        if rounding is None: missing.append('rounding_hypothesis')
        if identities[key] is None: missing.append('identity_hypothesis:' + key)
        assessment = ({'status': 'unresolved', 'missing': missing} if missing else
                      statement.prior.interval_sum(legacy_terms, {k: v['interval'] for k, v in observations.items()}))
        local.append({'relation_id': key, 'identity_premise': deepcopy(identities[key]),
                      'interval_premise': deepcopy(rounding), 'assessment': assessment})
    definition = {'profile': joint.PROFILE, 'observations': observations, 'equations': equations}
    if selected: joint.validate(definition, budget)
    return {'profile': PROFILE, **BOUNDARY, 'request_sha256': core.digest(body),
            'dependency_lock_sha256': LOCK_SHA256, 'budget': deepcopy(budget),
            'preserved_report': preserved, 'preserved_report_sha256': core.digest(preserved),
            'selected_relations': deepcopy(selected), 'definition': definition,
            'source_mapping': mappings, 'local_assessments': local,
            'relation_dispositions': [{'id': row['id'],
                'status': 'selected_conditional_system' if row['id'] in selected else
                          'supported_unselected' if row['id'] in SUPPORTED else 'outside_adapter_scope',
                'reason': 'Selected terms and explicit optional premises are assessed jointly.' if row['id'] in selected else
                          'No identity is asserted here; full original disposition remains in preserved_report.',
                'original_disposition_sha256': core.digest(row)} for row in preserved['relations']]}


def assess(body, budget):
    try:
        result = build(body, budget)
        if result['selected_relations']:
            assessment = joint.assess(result['definition'], budget)
        else:
            assessment = {**joint.BOUNDARY, 'status': 'no_asserted_system'}
        return {**result, 'status': assessment['status'], 'joint_assessment': assessment}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError,
            OverflowError, ValidationError) as exc:
        return {'profile': PROFILE, **BOUNDARY, 'status': 'invalid', 'reason': str(exc)[:300]}


def _check_conflicts(definition, budget, conflicts):
    coefficients, missing, _, _ = joint.validate(definition, budget)
    core.need(not missing and type(conflicts) is list and len(conflicts) == 1, 'conflict_scope')
    variables = {key: joint.z3.Real('replay.' + str(i))
                 for i, key in enumerate(definition['observations'])}
    formulas = {}
    for key, item in definition['observations'].items():
        interval = item['interval']
        formulas['domain:' + key] = joint.solver.domain_formula(variables[key], {
            'lower': interval['lower'], 'upper': interval['upper'],
            'lower_closed': interval['lower_inclusive'], 'upper_closed': interval['upper_inclusive']})
    for row, terms in zip(definition['equations'], coefficients):
        formulas['equation:' + row['id']] = sum((joint.solver.q(a)*variables[k]
            for k, a in terms.items()), joint.solver.q(0)) == joint.solver.q(row['rhs'])
    for conflict in conflicts:
        core.closed(conflict, ['labels', 'rechecked', 'minimal'], 'conflict')
        core.identifiers(conflict['labels'], 'conflict_labels', nonempty=True)
        core.need(conflict['rechecked'] == 'unsat' and conflict['minimal'] is False, 'conflict_claim')
        core.need(set(conflict['labels']) <= set(formulas), 'unknown_conflict_label')
        core.need(budget['solver_timeout_ms'] > 0 and budget['solver_rlimit'] > 0, 'core_budget')
        engine = joint.z3.Solver()
        engine.set(timeout=budget['solver_timeout_ms'], rlimit=budget['solver_rlimit'])
        engine.add(*(formulas[label] for label in conflict['labels']))
        core.need(engine.check() == joint.z3.unsat, 'core_not_rechecked_unsat')
    return True


def verify_result(body, budget, result):
    """Check all deterministic fields and mathematical result, allowing solver choices."""
    try:
        replay = assess(body, budget)
        if replay['status'] == 'invalid': return result == replay
        core.need(type(result) is dict and set(result) == set(replay), 'result_fields')
        for key in replay:
            if key != 'joint_assessment': core.need(result[key] == replay[key], 'result_changed:' + key)
        saved, current = result['joint_assessment'], replay['joint_assessment']
        core.need(set(saved) == set(current), 'assessment_fields')
        variable = {'witness', 'conflicts', 'solver_wall_seconds'}
        for key in current:
            if key not in variable: core.need(saved[key] == current[key], 'assessment_changed:' + key)
        if 'witness' in saved: joint.check_witness(result['definition'], saved['witness'])
        if 'conflicts' in saved:
            _check_conflicts(result['definition'], budget, saved['conflicts'])
        if 'solver_wall_seconds' in saved:
            elapsed = saved['solver_wall_seconds']
            core.need(type(elapsed) in (int, float) and 0 <= elapsed < float('inf'), 'solver_timing_invalid')
        return True
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError, OverflowError):
        return False
