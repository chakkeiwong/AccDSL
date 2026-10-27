"""Bounded per-case record/replay, with protected v1 projection comparisons."""
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
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(HERE))
import examples
import declared_indirect_cash_v2 as bridge


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def v1_comparison(chart, variant, current):
    if variant in ['disposal_gain', 'disposal_loss']:
        return {'status': 'newly_supported', 'reason': 'v1 lacks explicit nonoperating profit classification'}
    request, expected = examples.prior.fixture(chart, variant)
    result = examples.prior.bridge.report(request)
    assert result['status'] == 'explained_provisional', result
    assert result['items'] == expected
    for key in ['financial_report', 'direct_operating_cash', 'opening_sha256', 'closing_sha256']:
        assert current[key] == result[key], key
    assert current['items']['profit'] == result['items']['profit']
    assert current['items']['working_capital'] == result['items']['working_capital']
    assert bridge.total(bridge.number(current['items'][k]) for k in
        ['noncash_profit', 'nonoperating_profit_adjustment']) == bridge.number(result['items']['noncash_profit'])
    assert current['items']['indirect_operating_cash'] == result['items']['indirect_operating_cash']
    return {'status': 'common_projection_equal', 'request': request, 'result': result,
            'category_change': 'Explicit nonoperating profit replaces prior noncash interest adjustment'
            if variant == 'financing_interest' else 'No numerical category change'}


def main():
    started = time.monotonic()
    record = '--record' in sys.argv
    if record:
        assert not (HERE / 'evidence.json').exists(), 'evidence exists'
    tests = []
    for pattern in ['test_declared_indirect_cash_v2.py', 'test_company_book_reports_v1.py']:
        stream = io.StringIO()
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun, stream.getvalue()
        tests.append({'pattern': pattern, 'count': result.testsRun})
        if record:
            (HERE / (pattern + '.log')).write_text(stream.getvalue())
        print(json.dumps({'tests': pattern, 'passed': result.testsRun}), flush=True)
    cases = []
    folder = HERE / 'cases'
    folder.mkdir(exist_ok=True)
    for chart in ['alpha', 'beta']:
        for variant in examples.VARIANTS:
            name = chart + '.' + variant
            p = folder / (name + '.json')
            if record:
                assert not p.exists(), p
                row = examples.checked_case(chart, variant)
                row['baseline'] = v1_comparison(chart, variant, row['result'])
                dump(p, row)
            else:
                saved = json.loads(p.read_text())
                request, expected = examples.fixture(chart, variant)
                assert request == saved['request'] and expected == saved['expected'], name + ':fixture'
                result = bridge.report(request)
                assert result == saved['result'], name + ':full_result'
                assert result['items'] == expected and all(result[k] is False for k in bridge.FLAGS)
                # v1 results were independently computed at record time and are
                # locked; do not rerun that unchanged comparator on every replay.
            cases.append({'name': name, 'path': str(p.relative_to(ROOT)), 'sha256': sha(p)})
            examples._fixtures.clear()
            print(json.dumps({'case': name, 'status': 'passed'}), flush=True)
    locks = {}

    def lock(p, expected=None):
        p = p if isinstance(p, Path) else ROOT / p
        actual = sha(p)
        if expected is not None:
            assert actual == expected, str(p)
        locks[str(p.relative_to(ROOT))] = actual

    baseline = ROOT / 'data/accounting-master/declared-indirect-cash-20261025/baseline-v1'
    for name, expected in json.loads((baseline / 'source-lock.json').read_text()).items():
        lock(name, expected)
    for p in baseline.rglob('*'):
        if p.is_file(): lock(p)
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and Path(name).resolve().parent == ROOT / 'scripts' and Path(name).suffix == '.py':
            lock(Path(name).resolve())
    for p in [Path(__file__), HERE / 'examples.py', HERE / 'audit.md',
              ROOT / 'docs/plans/accounting-indirect-profit-components-20261025.md',
              ROOT / 'data/accounting-master/declared-financing-clock-20261025/examples.py',
              ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py']:
        lock(p)
    for row in tests: lock(ROOT / 'tests' / row['pattern'])
    evidence = {'tests': tests, 'cases': cases, 'case_count': len(cases),
                'v1_projection_comparisons': 16, 'new_gain_loss_cases': 4,
                'scope': 'Conditional finite classification algebra; no source, accounting or fiscal completeness'}
    if record:
        dump(HERE / 'evidence.json', evidence)
        lock(HERE / 'evidence.json')
        for row in tests: lock(HERE / (row['pattern'] + '.log'))
        dump(HERE / 'source-lock.json', locks)
        dump(HERE / 'run-manifest.json', {
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B data/accounting-master/declared-indirect-profit-components-20261025/verify.py --record',
            'environment': sys.version, 'platform': platform.platform(),
            'cpu_gpu': 'CPU exact deterministic accounting-state algebra; no GPU frameworks imported',
            'seeds': 'N/A deterministic', 'data_version': 'Two constructed charts; preserved v1 baseline and locked method definitions',
            'wall_seconds': time.monotonic() - started,
            'plan': 'docs/plans/accounting-indirect-profit-components-20261025.md',
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'provenance': 'Uncommitted sources identified by hashes',
            'artifacts': {str((HERE / n).relative_to(ROOT)): sha(HERE / n)
                          for n in ['evidence.json', 'source-lock.json']}})
    else:
        assert evidence == json.loads((HERE / 'evidence.json').read_text()), 'evidence replay'
        saved = json.loads((HERE / 'source-lock.json').read_text())
        for name, expected in saved.items(): assert sha(ROOT / name) == expected, name
        for name, expected in locks.items(): assert saved[name] == expected, name
        for name, expected in json.loads((HERE / 'run-manifest.json').read_text())['artifacts'].items():
            assert sha(ROOT / name) == expected, name
    print(json.dumps({'passed': True, 'mode': 'record' if record else 'read_only_replay',
                      'focused': tests[0]['count'], 'regressions': tests[1]['count'],
                      'cases': len(cases), 'locked_sources': len(json.loads((HERE / 'source-lock.json').read_text()))}), flush=True)


if __name__ == '__main__':
    main()
