"""Record/replay the bounded envelope checks without rewriting predecessors."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import io
import json
import platform
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import company_world_envelope_v1 as world
from test_company_world_envelope_v1 import fixture
spec = importlib.util.spec_from_file_location('world_evidence_audit', HERE / 'audit.py')
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def run():
    record = '--record' in sys.argv
    if record and (HERE / 'evidence.json').exists(): raise SystemExit('record exists; replay without --record')
    start = time.monotonic()
    preserved = audit.inspect()
    assert preserved == json.loads((HERE / 'audit.json').read_text()), 'preservation replay'
    tests = []
    for pattern in ['test_company_world_envelope_v1.py', 'test_method_requirements_v1.py',
                    'test_company_book_transition_v1.py', 'test_company_book_transition_v2.py']:
        log = io.StringIO()
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        if not result.wasSuccessful() or not result.testsRun: raise AssertionError(log.getvalue())
        tests.append({'pattern': pattern, 'tests': result.testsRun})
        if record: (HERE / (pattern + '.log')).write_text(log.getvalue())
    cases = {}
    for name in ['mixed', 'empty', 'mismatch_source', 'mismatch_sector']:
        request = fixture()
        if name == 'empty': request['components'] = {}; request['obligations'] = []
        if name == 'mismatch_source': request['components']['bank.B']['source_ref'] = '0' * 64
        if name == 'mismatch_sector': request['components']['corporate.P']['owner'] = 'bank'
        before = deepcopy(request); response = world.propose(request)
        assert request == before and world.verify(request, response)
        assert all(response[flag] is False for flag in world.FLAGS)
        cases[name] = {'request': request, 'response': response}
    assert cases['mixed']['response']['status'] == cases['empty']['response']['status'] == 'proposed'
    assert cases['mismatch_source']['response']['reason'] == 'component_source_ref_binding'
    assert cases['mismatch_sector']['response']['reason'] == 'component_owner_sector'
    evidence = {'tests': tests, 'cases': cases, 'audit_checks': len(preserved['checks'])}
    if record:
        dump(HERE / 'evidence.json', evidence)
        names = ['scripts/company_world_envelope_v1.py', 'tests/test_company_world_envelope_v1.py',
                 'scripts/method_requirements_v1.py', 'scripts/company_book_transition_v1.py',
                 'scripts/company_book_transition_v2.py', 'tests/test_method_requirements_v1.py',
                 'tests/test_company_book_transition_v1.py', 'tests/test_company_book_transition_v2.py',
                 'docs/plans/accounting-world-envelope-repair-20261025.md']
        names += [str((HERE / name).relative_to(ROOT)) for name in
                  ['verify.py','audit.py','audit.json','audit-manifest.json','audit-result.md','recovery.md','evidence.json']]
        locks = dict(preserved['source_lock'])
        locks.update({name: sha(ROOT / name) for name in names})
        dump(HERE / 'source-lock.json', locks)
        dump(HERE / 'run-manifest.json', {
            'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
            'worktree': 'Pre-existing uncommitted work; source-lock.json identifies checked bytes',
            'command': 'python3 -B data/accounting-master/company-world-envelope-20261025/verify.py --record',
            'environment': sys.version, 'platform': platform.platform(),
            'cpu_gpu': 'CPU-only stdlib checks; no GPU framework imported', 'seeds': 'N/A: deterministic',
            'data_version': 'Synthetic opaque-handle fixture and retained evidence per source-lock.json',
            'wall_seconds': time.monotonic() - start,
            'plan': 'docs/plans/accounting-world-envelope-repair-20261025.md',
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'artifacts': [str((HERE / n).relative_to(ROOT)) for n in ['evidence.json','source-lock.json','audit.json']]})
    else:
        assert evidence == json.loads((HERE / 'evidence.json').read_text()), 'evidence replay'
        for name, expected in json.loads((HERE / 'source-lock.json').read_text()).items():
            assert sha(ROOT / name) == expected, 'source changed:' + name
    print(json.dumps({'passed': True, 'mode': 'record' if record else 'read_only_replay',
                      'focused': tests[0]['tests'], 'regressions': sum(row['tests'] for row in tests[1:]),
                      'cases': len(cases), 'audit_checks': len(preserved['checks'])}))


if __name__ == '__main__': run()
