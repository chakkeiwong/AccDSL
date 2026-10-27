"""Record or exactly replay text-to-retained-term conformance evidence."""
from pathlib import Path
from hashlib import sha256
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import examples
import receivable_term_text_v1 as text


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    started = time.monotonic()
    record = '--record' in sys.argv
    if record:
        assert not (HERE / 'evidence.json').exists(), 'record exists'
    tests = []
    for pattern in ['test_receivable_term_text_v1.py', 'test_receivable_term_history_v1.py',
                    'test_declared_receivable_text_v1.py', 'test_declared_receivable_lifecycle_v1.py',
                    'test_company_book_carry_v1.py']:
        stream = io.StringIO()
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun, stream.getvalue()
        tests.append({'pattern': pattern, 'count': result.testsRun})
        if record:
            (HERE / (pattern + '.log')).write_text(stream.getvalue())
    cases = {chart: examples.check(case, chart) for chart, case in examples.retained().items()}
    evidence = {'tests': tests, 'cases': cases, 'comparator':
                'Exact retained typed term requests/results; independent of new authoring runner',
                'scope': 'Finite constructed prospective term commands; no broader admission'}
    locks = {}

    def lock(p, expected=None):
        p = p if isinstance(p, Path) else ROOT / p
        actual = sha(p)
        if expected is not None:
            assert actual == expected, str(p)
        locks[str(p.relative_to(ROOT))] = actual

    prior = ROOT / 'data/accounting-master/receivable-term-history-20261025/source-lock.json'
    lock(prior)
    for name, expected in json.loads(prior.read_text()).items():
        lock(name, expected)
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and Path(name).resolve().parent == ROOT / 'scripts' and Path(name).suffix == '.py':
            lock(Path(name).resolve())
    for p in [Path(__file__), HERE / 'examples.py', HERE / 'audit.md',
              ROOT / 'docs/plans/accounting-receivable-term-authoring-20261025.md']:
        lock(p)
    for test in tests:
        lock(ROOT / 'tests' / test['pattern'])
    if record:
        dump(HERE / 'evidence.json', evidence)
        lock(HERE / 'evidence.json')
        for chart, case in cases.items():
            path = HERE / (chart + '.accdsl')
            path.write_text(case['source'])
            lock(path)
        for test in tests:
            lock(HERE / (test['pattern'] + '.log'))
        dump(HERE / 'source-lock.json', locks)
        dump(HERE / 'run-manifest.json', {
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B data/accounting-master/receivable-term-authoring-20261025/verify.py --record',
            'environment': sys.version, 'platform': platform.platform(),
            'cpu_gpu': 'CPU deterministic text/state checks; no GPU framework imported',
            'seeds': 'N/A: deterministic', 'wall_seconds': time.monotonic() - started,
            'data_version': 'Locked prior two-chart term lifecycle; nine events and carry per chart',
            'plan': 'docs/plans/accounting-receivable-term-authoring-20261025.md',
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'provenance': 'Uncommitted work identified by source locks',
            'artifacts': {str((HERE / n).relative_to(ROOT)): sha(HERE / n)
                          for n in ['evidence.json', 'source-lock.json']}})
    else:
        assert evidence == json.loads((HERE / 'evidence.json').read_text()), 'exact authoring replay'
        saved = json.loads((HERE / 'source-lock.json').read_text())
        for name, expected in saved.items():
            assert sha(ROOT / name) == expected, name
        for name, expected in locks.items():
            assert saved[name] == expected, name
        for name, expected in json.loads((HERE / 'run-manifest.json').read_text())['artifacts'].items():
            assert sha(ROOT / name) == expected, name
    print(json.dumps({'passed': True, 'mode': 'record' if record else 'read_only_replay',
                      'focused': tests[0]['count'], 'regressions': sum(t['count'] for t in tests[1:]),
                      'cases': len(cases), 'commands_per_case': [c['result']['successful_commands'] for c in cases.values()],
                      'locked_files': len(json.loads((HERE / 'source-lock.json').read_text()))}))


if __name__ == '__main__':
    main()
