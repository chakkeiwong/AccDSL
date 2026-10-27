"""Read frozen inputs; write only this successor's diagnostic artifacts."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from identity_index import (Refusal, canonical, lookup, migrate_legacy,
                            pair_key)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'data/accounting-master/extended-method-exchanges-20261015/insurance'


def main():
    started = time.monotonic()
    protected = [OLD / p for p in ('build_exchanges.py', 'verify_exchanges.py',
                 'schema_design.py', 'semantic-contract.md',
                 'attempt-01/portable-exchanges.json', 'attempt-01/record-schemas.json')]
    protected += [ROOT / 'docs/design/proposal/manuscript-authoring-scope-20261026/accounting-product-proposal.pdf']
    hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in protected}
    data = json.loads((OLD / 'attempt-01/portable-exchanges.json').read_text())
    registry = data['record_registry']
    profile = data['aliases']['profile']
    checks = []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def refused(name, expected, action):
        try:
            action()
        except Refusal as exc:
            check(name, str(exc) == expected)
        else:
            check(name, False)

    source = (OLD / 'build_exchanges.py').read_text()
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == 'ident')
    env = {'body': lambda value: value}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'retained-ident', 'exec'), env)
    pattern = json.loads((OLD / 'attempt-01/record-schemas.json').read_text())['$defs']['OperationRequest']['properties']['client_id']['pattern']
    witness = [('a/b', 'c'), ('a', 'b/c')]
    old_keys = [env['ident']({'client_id': a, 'request_id': b}) for a, b in witness]
    check('collision witness permitted by retained schema',
          all(re.fullmatch(pattern, v) for pair in witness for v in pair))
    check('actual retained builder collides', old_keys[0] == old_keys[1])
    check('successor separates collision', pair_key(*witness[0]) != pair_key(*witness[1]))
    ids = ['a', 'b', '/', '//', 'a/b', 'b/c', 'a/', '/a', 'a.b', 'a:b', 'a@b', 'a-b', 'a_b', '0']
    keys = [pair_key(a, b) for a in ids for b in ids]
    check('finite separator matrix is injective', len(set(keys)) == len(keys))
    check('finite matrix round trips', all(json.loads(pair_key(a, b)) == [a, b] for a in ids for b in ids))
    for bad in (None, True, 1, '', 'a\nb', 'a b', 'é', 'a"b'):
        refused('invalid ID ' + repr(bad), 'invalid_identity_field', lambda bad=bad: pair_key(bad, 'ok'))

    seen = set()
    for exchange in data['exchanges']:
        for world_name in ('world_before', 'world_after'):
            old_index = exchange[world_name]['decisions']
            signature = sha256(canonical(old_index)).hexdigest()
            if signature in seen:
                continue
            seen.add(signature)
            original = deepcopy(old_index)
            result = migrate_legacy(old_index, list(old_index.values()), registry, profile)
            check('world unchanged ' + signature[:12], original == old_index)
            check('entries preserved ' + signature[:12],
                  sorted(canonical(v) for v in old_index.values()) ==
                  sorted(canonical(v) for v in result['entries'].values()))
            for decision in old_index.values():
                check('retained replay ' + decision['request_ref']['digest'][:12],
                      lookup(result, decision['request_ref'], registry) ==
                      {'disposition': 'replay', 'decision': decision})

    publication = next(e for e in data['exchanges'] if e.get('role') == 'publication')
    original_entry = next(iter(publication['world_after']['decisions'].values()))
    reg = deepcopy(registry)

    def references(value):
        if isinstance(value, dict):
            if set(value) == {'kind', 'schema', 'digest'}:
                yield value
            else:
                for child in value.values():
                    yield from references(child)
        elif isinstance(value, list):
            for child in value:
                yield from references(child)

    def clone(ref, suffix, updates):
        rec = deepcopy(reg[ref['digest']])
        rec['key'] += suffix
        rec['body'].update(updates)
        rec['dependencies'] = list({canonical(r): r for r in references(rec['body'])}.values())
        rec['dependencies'].sort(key=canonical)
        digest = sha256(('accdsl.portable.v1/' + rec['schema']).encode() + b'\x00' + canonical(rec)).hexdigest()
        reg[digest] = rec
        return {'kind': rec['kind'], 'schema': rec['schema'], 'digest': digest}

    def decision(client, request, suffix):
        rq = clone(original_entry['request_ref'], suffix,
                   {'client_id': client, 'request_id': request})
        receipt = clone(original_entry['receipt_ref'], suffix, {'request_ref': rq})
        response = clone(original_entry['response_ref'], suffix,
                         {'request_ref': rq, 'receipt_ref': receipt})
        return dict(original_entry, request_ref=rq, receipt_ref=receipt, response_ref=response)

    first, second = decision('a/b', 'c', '.one'), decision('a', 'b/c', '.two')
    legacy = {'a/b/c': first}
    reg_before, legacy_before = deepcopy(reg), deepcopy(legacy)
    refused('colliding retained history cannot silently overwrite', 'ambiguous_legacy_key',
            lambda: migrate_legacy(legacy, [first, second], reg, profile))
    index = migrate_legacy(legacy, [first], reg, profile)
    check('other pair is absent, not conflicted', lookup(index, second['request_ref'], reg)['disposition'] == 'absent')
    changed = clone(first['request_ref'], '.changed', {'require_current': False})
    check('changed request under same pair conflicts', lookup(index, changed, reg)['disposition'] == 'identity_conflict')
    competing = decision('a/b', 'c', '.competing')
    refused('conflicting decisions under one pair', 'conflicting_decision_history',
            lambda: migrate_legacy(legacy, [first, competing], reg, profile))
    bad_entry = dict(first, response_ref=second['response_ref'])
    refused('response for another request', 'response_binding',
            lambda: migrate_legacy({'a/b/c': bad_entry}, [bad_entry], reg, profile))
    bad_receipt = clone(first['receipt_ref'], '.bad-binding', {'request_ref': second['request_ref']})
    bad_response = clone(first['response_ref'], '.bad-receipt', {'receipt_ref': bad_receipt})
    bad_entry = dict(first, receipt_ref=bad_receipt, response_ref=bad_response)
    refused('receipt for another request', 'receipt_binding',
            lambda: migrate_legacy({'a/b/c': bad_entry}, [bad_entry], reg, profile))
    refused('missing receipt field', 'incomplete_decision',
            lambda: migrate_legacy(legacy, [{k: v for k, v in first.items() if k != 'receipt_ref'}], reg, profile))
    refusal_snapshot = deepcopy(reg)
    duplicate = migrate_legacy(legacy, [first, deepcopy(first)], reg, profile)
    check('identical history duplicates retain one decision', duplicate == index)
    refused('missing history', 'incomplete_index_history', lambda: migrate_legacy(legacy, [], reg, profile))
    refused('corrupt legacy key', 'incomplete_index_history', lambda: migrate_legacy({'wrong': first}, [first], reg, profile))
    broken = deepcopy(reg)
    del broken[first['request_ref']['digest']]
    refused('missing request body', 'missing_record', lambda: migrate_legacy(legacy, [first], broken, profile))
    corrupt = deepcopy(reg)
    corrupt[first['request_ref']['digest']]['body']['client_id'] = 'changed'
    refused('changed bytes under old digest', 'record_digest_mismatch', lambda: migrate_legacy(legacy, [first], corrupt, profile))
    moved = deepcopy(index)
    moved['entries'][pair_key('a', 'b/c')] = moved['entries'].pop(pair_key('a/b', 'c'))
    refused('misbound successor index', 'index_key_binding', lambda: lookup(moved, second['request_ref'], reg))
    check('refusals preserve caller inputs', reg == refusal_snapshot)
    check('synthetic additions preserve retained records', all(reg[k] == v for k, v in reg_before.items()))
    check('legacy index never changed', legacy == legacy_before)
    check('all frozen inputs unchanged', all(sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items()))
    output = {'judgment': 'bounded_successor_checks_pass', 'checks': checks,
              'unique_retained_indexes': len(seen), 'collision_witness': witness,
              'legacy_keys': old_keys, 'successor_keys': [pair_key(*p) for p in witness],
              'limitations': ['metadata-only helper', 'history completeness assumed',
                             'no runtime durability or financial re-admission'],
              'protected_files': hashes}
    (HERE / 'checks.json').write_text(json.dumps(output, indent=2) + '\n')
    manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'command': 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/component-identity-repair-20261026/verify.py',
                'python': sys.executable, 'python_version': platform.python_version(),
                'conda_environment': os.environ.get('CONDA_DEFAULT_ENV', 'not_named'),
                'cpu_gpu': 'CPU-only; GPU intentionally hidden; no framework imported',
                'data_version': hashes, 'random_seeds': 'N/A: deterministic finite checks',
                'wall_seconds': time.monotonic() - started,
                'plan': 'docs/plans/accounting-component-identity-repair-20261026.md',
                'result': str((HERE / 'result.md').relative_to(ROOT)),
                'outputs': [str((HERE / 'checks.json').relative_to(ROOT))]}
    (HERE / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'checks_passed': len(checks), 'retained_indexes': len(seen),
                      'frozen_inputs_unchanged': True}))


if __name__ == '__main__':
    main()
