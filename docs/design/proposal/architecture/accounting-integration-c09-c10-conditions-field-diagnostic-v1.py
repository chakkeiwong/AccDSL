"""Finite proposal-example diagnostic. Not a runtime API or accounting engine.

Derive findings solely from submitted C09/C10 values, then compare the saved
expectations. The fixture purposes, IDs and expected findings never select rules.
Run from the repository root with one fresh output JSON path.
"""
import copy
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

B = Path('docs/design/proposal/architecture')
P = 'accounting-integration-c09-c10-conditions-field-'
ABSENT = object()
BLANK = frozenset(chr(n) for n in (
    list(range(0x9, 0xE)) + [0x20, 0x85, 0xA0, 0x1680]
    + list(range(0x2000, 0x200B)) + [0x2028, 0x2029, 0x202F, 0x205F, 0x3000]))
A = 'identical_instrument_active_market_quote'
T = 'technique_only_observable_market_data'
REASON = ('Required null or nonblank string; with exact required=true and any '
          'typed null route, a nonblank string is required.')
CONTEXT = 'Required null or nonblank contextual string; no route or method inference.'
OBJECT = 'Required object; malformed parent suppresses descendants only.'
BOOL = 'Required exact Boolean.'
ROUTE = 'Required Boolean or null.'
TEXT = 'Required nonblank string.'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False)


def type_name(value):
    if value is None:
        return 'null'
    return {bool: 'boolean', int: 'number', float: 'number', str: 'string',
            dict: 'object', list: 'array'}[type(value)]


def derive(candidate):
    """Presence/type/content inspection; no access to expectations or labels."""
    findings = []

    def inspect(parent, key, path, kind, rule, require_text=False):
        value = parent.get(key, ABSENT)
        code = None
        if value is ABSENT:
            code = 'INVALID_CONDITION_PACKET'
        else:
            valid_type = {
                'object': type(value) is dict,
                'boolean': type(value) is bool,
                'route': value is None or type(value) is bool,
                'reason': value is None or type(value) is str,
                'text': type(value) is str,
            }[kind]
            if not valid_type:
                code = 'INVALID_FIELD_TYPE'
            elif type(value) is str and kind in ('reason', 'text') and not any(
                    c not in BLANK for c in value):
                code = 'INVALID_UNKNOWN_REPRESENTATION'
            elif kind == 'reason' and require_text and value is None:
                code = 'INVALID_UNKNOWN_REPRESENTATION'
        if code:
            observed = {'present': value is not ABSENT}
            if value is not ABSENT:
                observed.update(type=type_name(value), value=value)
            findings.append({'stage': 'shape', 'path': path, 'code': code,
                             'expected_rule': rule, 'observed': observed})
            return ABSENT
        return value

    for cid in ('C09', 'C10'):
        path = 'source/' + cid
        packet = inspect(candidate, cid, path, 'object', OBJECT)
        if packet is ABSENT:
            continue
        value = inspect(packet, 'value', path + '/value', 'object', OBJECT)
        obligation = False
        if value is not ABSENT:
            if cid == 'C09':
                required = inspect(value, 'required', path + '/value/required',
                                   'boolean', BOOL)
                first = inspect(value, A, path + '/value/' + A, 'route', ROUTE)
                second = inspect(value, T, path + '/value/' + T, 'route', ROUTE)
                # ABSENT is distinct from typed null. Exact identity excludes 1.
                obligation = required is True and (first is None or second is None)
                inspect(value, 'unknown_reason', path + '/value/unknown_reason',
                        'reason', REASON, obligation)
                inspect(value, 'branch', path + '/value/branch', 'text', TEXT)
            else:
                inspect(value, 'method', path + '/value/method', 'text', TEXT)
                for flag in ('unequal_price_a_method_available',
                             'unequal_price_b_method_available'):
                    inspect(value, flag, path + '/value/' + flag, 'boolean', BOOL)
        inspect(packet, 'unknown_reason', path + '/unknown_reason', 'reason',
                REASON if cid == 'C09' else CONTEXT, obligation)
    return sorted(findings, key=lambda item: (item['path'], item['code']))


def main():
    started = time.monotonic()
    target = Path(sys.argv[1])
    if target.exists():
        raise SystemExit('Refusing to overwrite existing diagnostic evidence: ' + str(target))
    checks, results, inputs = [], [], {}

    def check(label, passed):
        checks.append({'id': label, 'passed': bool(passed)})

    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def load(path):
        inputs[str(path)] = digest(path)
        return json.loads(Path(path).read_text())

    fixtures = load(B / (P + 'controls-v1.json'))
    inputs[str(Path(__file__))] = digest(__file__)
    for ref in fixtures['sources'] + [fixtures['specification'], fixtures['matrix']]:
        check('source pin ' + ref['path'], digest(ref['path']) == ref['sha256'])
        inputs[ref['path']] = digest(ref['path'])
    source_cases = {ref['path']: {c['id']: c for c in load(ref['path'])['cases']}
                    for ref in fixtures['sources']}
    check('explicit Unicode set', fixtures['blank_codepoints'] == [
        f'U+{ord(c):04X}' for c in sorted(BLANK)])
    ids = [c['id'] for c in fixtures['local_controls']]
    check('unique control IDs', len(ids) == len(set(ids)))
    pairs, null_controllers, preserved_strings = set(), 0, 0
    for control in fixtures['local_controls']:
        label = control['id']
        comparator = control['comparator']
        ref = comparator['file']
        check(label + ' comparator hash', digest(ref['path']) == ref['sha256'])
        original = source_cases[ref['path']][comparator['case_id']]['complete_inputs']
        rebuilt = {cid: copy.deepcopy(original[cid]) for cid in ('C09', 'C10')}
        check(label + ' comparator projection', comparator['projection'] == ['C09', 'C10'])
        mutated = []
        for mutation in control['mutations']:
            parts = mutation['path'].split('/')
            check(label + ' mutation root', parts[0] == 'source' and parts[1] in ('C09', 'C10'))
            parent = rebuilt
            for key in parts[1:-1]:
                parent = parent[key]
            key = parts[-1]
            check(label + ' exact prior value ' + mutation['path'],
                  key in parent and canonical(parent[key]) == canonical(mutation['before']))
            mutated.append(mutation['path'])
            if mutation['op'] == 'remove':
                del parent[key]
            elif mutation['op'] == 'replace':
                parent[key] = copy.deepcopy(mutation['after'])
            else:
                raise ValueError('Unsupported mutation operation')
        check(label + ' no repeated mutation paths', len(mutated) == len(set(mutated)))
        check(label + ' exact mutation reconstruction and unchanged fields',
              canonical(rebuilt) == canonical(control['candidate']))
        actual = derive(control['candidate'])
        check(label + ' complete findings including stage/path/rule/observation',
              canonical(actual) == canonical(control['expected_diagnostics']))
        check(label + ' path/code order', actual == sorted(actual, key=lambda x: (x['path'], x['code'])))
        reason_paths = [f['path'] for f in actual if f['path'].endswith('/unknown_reason')]
        check(label + ' at most one finding per reason', len(reason_paths) == len(set(reason_paths)))
        check(label + ' representation outcome', control['representation_valid'] is (not actual))
        check(label + ' accounting not assessed', control['accounting_outcome'] == 'not_assessed_representation_only')
        if not control['mutations']:
            v = rebuilt['C09']['value']
            if v['required'] is True:
                pairs.add((v[A], v[T]))
            elif v['required'] is False:
                null_controllers += 1
        for mutation in control['mutations']:
            if type(mutation.get('after')) is str:
                preserved_strings += 1
        results.append({'id': label, 'derived_diagnostics': actual,
                        'representation_valid': not actual,
                        'accounting_outcome': 'not_assessed_representation_only'})
    check('all nine retained required=true pairs', pairs == {(x,y) for x in (True,False,None) for y in (True,False,None)})
    check('retained equal-price control', null_controllers >= 1)
    failures = [c for c in checks if not c['passed']]
    report = {'schema_version': 'accdsl.proposal.c09-c10.field-verification.v1',
              'passed': not failures, 'control_count': len(results),
              'assertion_count': len(checks), 'failures': failures,
              'checks': checks, 'results': results, 'input_hashes': inputs,
              'manifest': {'command': ['python3', str(Path(__file__)), str(target)],
                  'environment': 'standard-library Python ' + platform.python_version(),
                  'git_commit': 'unavailable: pre-existing unusable .git marker; no initialization',
                  'cpu_gpu': 'CPU-only JSON diagnostic; no device/framework probing or imports',
                  'random_seeds': 'N/A: deterministic finite document diagnostic',
                  'data_version': inputs[str(B / (P + 'controls-v1.json'))],
                  'wall_seconds': round(time.monotonic()-started, 6),
                  'plan_file': 'data/accounting-master/runs/20261006T005135-d44c7a2e/P16/approved-plan.json',
                  'result_file': str(target), 'output_artifact_paths': [str(target)]},
              'limits': ['Representation-only finite controls.',
                        'No complete exchange, accounting assessment or runtime conformance evidence.']}
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'controls': len(results),
                      'assertions': len(checks), 'failures': failures[:8], 'output': str(target)}))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
