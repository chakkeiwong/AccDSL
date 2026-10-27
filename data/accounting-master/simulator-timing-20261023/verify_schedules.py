"""Validate proposed schedule bodies and their financial meaning against saved IR."""
from datetime import datetime, timezone
from copy import deepcopy
from fractions import Fraction as Q
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time

from jsonschema import Draft202012Validator, FormatChecker
from verify import OUT, ROOT, SOURCE, PLAN, rational, replay, digest


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def evaluate(body, source, validator):
    errors = list(validator.iter_errors(body))
    if errors:
        return {'status': 'invalid_schema', 'detail': errors[0].message}
    ref = body['projection_ref']
    record = source['record_registry'].get(ref['digest'])
    if not record or record['kind'] != ref['kind'] or record['schema'] != ref['schema']:
        return {'status': 'invalid_reference'}
    projection = record['body']
    expected = {x['event_kind'] for x in projection['event_plan']}
    names = [x['event_kind'] for x in body['events']]
    if set(names) != expected or len(names) != len(expected):
        return {'status': 'invalid_event_coverage'}
    events = {x['event_kind']: x for x in body['events']}
    parents = {k: set(e['after']) for k, e in events.items()}
    if any(not v <= expected for v in parents.values()):
        return {'status': 'invalid_dependency_reference'}
    parents['delivery'].add('purchase')
    parents['collection'].add('delivery')
    parents['supplier_payment'].add('purchase')
    parents['tax'].update(('delivery', 'payroll', 'depreciation', 'interest'))
    parents['close'].update(expected - {'close'})
    ordered = []
    remaining = set(expected)
    while remaining:
        ready = sorted(k for k in remaining if not (parents[k] & remaining))
        if not ready:
            return {'status': 'invalid_dependency_cycle'}
        ordered.extend(ready)
        remaining.difference_update(ready)
    ancestors = {}
    for k in ordered:
        ancestors[k] = set(parents[k])
        for parent in parents[k]:
            ancestors[k].update(ancestors[parent])
    start, end = (instant(body['horizon'][k]) for k in ('start', 'end_exclusive'))
    if start >= end:
        return {'status': 'invalid_horizon'}
    # This documentary profile annotates the retained one-year projection only.
    facts_ref = source['aliases']['economic-facts']
    forecast = source['record_registry'][facts_ref['digest']]['body']['forecast']
    expected_start = instant(forecast['start'] + 'T00:00:00Z')
    expected_end = instant(forecast['end_exclusive'] + 'T00:00:00Z')
    if (start, end) != (expected_start, expected_end):
        return {'status': 'invalid_horizon'}
    known = {k: instant(e['at']) for k, e in events.items() if isinstance(e['at'], str)}
    if any(not start <= t < end for t in known.values()):
        return {'status': 'invalid_horizon'}
    if any(known[p] > known[k] for k in known for p in parents[k] if p in known):
        return {'status': 'invalid_date_order'}
    if len(known) != len(events):
        return {'status': 'unresolved_timing', 'unknown_events': sorted(set(events) - set(known))}
    for i, left in enumerate(sorted(events)):
        for right in sorted(events)[i + 1:]:
            if known[left] == known[right] and left not in ancestors[right] and right not in ancestors[left]:
                return {'status': 'unresolved_timing', 'unordered_same_instant': [left, right]}
    # Dependency rank breaks only explicitly ordered ties; ambiguity was rejected above.
    rank = {k: i for i, k in enumerate(ordered)}
    execution_order = sorted(expected, key=lambda k: (known[k], rank[k]))
    journal = {x['event_kind']: x for x in projection['proposed_journals']}
    opening = {k: rational(v) for k, v in source['record_registry'][projection['opening_ref']['digest']]['body']['balances'].items()}
    event_plan = {x['event_kind']: x for x in projection['event_plan']}
    result = replay(opening, [journal[k] for k in execution_order], event_plan, Q(1, 2), True)
    if result['status'] == 'funding_failure' and body['funding_knowledge']['tag'] == 'unknown':
        result['status'] = 'unresolved_funding'
    result['execution_order'] = execution_order
    result['facility_required'] = result['status'] != 'complete'
    return result


def main():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.perf_counter()
    schema_path, cases_path = OUT / 'schedule.schema.json', OUT / 'schedule-cases.json'
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    source_hash = digest(SOURCE)
    source = json.loads(SOURCE.read_text())
    cases = json.loads(cases_path.read_text())['cases']
    checks = []
    outputs = {}
    for case in cases:
        result = evaluate(case['body'], source, validator)
        outputs[case['id']] = result
        checks.append({'name': case['id'], 'expected': case['expected'], 'observed': result['status'], 'passed': result['status'] == case['expected']})
    checks.append({'name': 'array_order_irrelevant', 'passed': outputs['collection_before_supplier'] == outputs['reversed_array_same_dates']})
    checks.append({'name': 'declared_same_instant_order_resolves', 'passed': outputs['same_instant_ordered']['balances'] == outputs['collection_before_supplier']['balances']})
    checks.append({'name': 'unknown_funding_does_not_post_payment', 'passed': outputs['unknown_facility']['balances'] == outputs['supplier_before_collection']['balances'] and outputs['unknown_facility']['shortfall'] == Q(427, 5)})
    baseline = next(c['body'] for c in cases if c['id'] == 'collection_before_supplier')
    for boundary in ('start', 'end_exclusive'):
        shifted = deepcopy(baseline)
        shifted['horizon'][boundary] = shifted['horizon'][boundary].replace('T00:', 'T01:')
        observed = evaluate(shifted, source, validator)['status']
        checks.append({'name': 'reject_hour_shifted_' + boundary,
                       'expected': 'invalid_horizon', 'observed': observed,
                       'passed': observed == 'invalid_horizon'})
    checks.append({'name': 'source_unchanged', 'passed': digest(SOURCE) == source_hash})
    result = {'passed': all(c['passed'] for c in checks), 'check_count': len(checks), 'cases': outputs, 'checks': checks,
              'scope': 'documentary schedule validation; not a registered product API or general policy engine',
              'floating_share': '1/2', 'input_sha256': source_hash}
    result_path = OUT / 'schedule-checks.json'
    result_path.write_text(json.dumps(result, indent=2, default=str) + chr(10))
    manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'commands': ['env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/simulator-timing-20261023/prepare_schedules.py', 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/simulator-timing-20261023/verify_schedules.py'],
                'environment': {'executable': sys.executable, 'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema')},
                'cpu_gpu': 'CPU only; GPU intentionally hidden; no ML framework imported',
                'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'random_seeds': 'N/A: deterministic fixtures', 'data_version': source_hash,
                'started_utc': started, 'wall_seconds_verification': time.perf_counter() - timer,
                'plan_file': str(PLAN.relative_to(ROOT)), 'result_file': str((OUT / 'result.md').relative_to(ROOT)),
                'artifacts': {str(p.relative_to(ROOT)): digest(p) for p in (schema_path, cases_path, result_path, OUT / 'prepare_schedules.py', OUT / 'verify.py', OUT / 'verify_schedules.py')}}
    (OUT / 'schedule-manifest.json').write_text(json.dumps(manifest, indent=2) + chr(10))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'cases': len(cases), 'failures': [x for x in checks if not x['passed']]}))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
