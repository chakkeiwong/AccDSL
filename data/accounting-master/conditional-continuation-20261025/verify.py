"""Record exact conditional continuation evidence once; replay read-only."""
from hashlib import sha256
from pathlib import Path
import argparse
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
import conditional_company_continuation_v1 as continuation
import test_conditional_company_continuation_v1 as examples


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def tests(names):
    suites = [unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=name) for name in names]
    assert all(s.countTestCases() for s in suites)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(suites))
    return result, stream.getvalue()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--record', action='store_true'); args = parser.parse_args()
    if args.record: assert not (HERE / 'checks.json').exists()
    started = time.time()
    focal = ['test_conditional_company_continuation_v1.py']
    regression = ['test_conditional_company_opening_v1.py', 'test_company_book_transition_v1.py',
                  'test_company_book_reports_v1.py']
    paths = [Path(__file__), HERE / 'audit.md', ROOT / 'docs/plans/accounting-conditional-continuation-20261025.md']
    paths += [ROOT / 'tests' / n for n in focal + regression]
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and Path(name).suffix == '.py' and Path(name).is_relative_to(ROOT): paths.append(Path(name))
    previous = ROOT / 'data/accounting-master/history-to-opening-20261025/source-lock.json'
    for name, expected in json.loads(previous.read_text()).items(): assert sha(ROOT / name) == expected, name
    paths.append(previous)
    lock = {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))}
    if not args.record: assert lock == json.loads((HERE / 'source-lock.json').read_text())
    focused, flog = tests(focal); prior, rlog = tests(regression)
    if args.record:
        (HERE / 'focused.log').write_text(flog); (HERE / 'regression.log').write_text(rlog)
    assert focused.wasSuccessful(), flog[-3000:]
    assert prior.wasSuccessful(), rlog[-3000:]
    cases, checks = [], []
    for owner in ['alpha', 'beta']:
        for selected, expected in [((10, 2, 3), '5/1'), ((8, 3, 4), '7/1')]:
            request = examples.fixture(owner, selected); result = continuation.run(request)
            assert result['status'] == 'conditional_continuation', result
            book = request['opening_result']['opening']; current = result['current']
            cash = book['cash_account']; equity = next(k for k, v in book['accounts'].items() if v['classification'] == 'equity')
            direct = continuation.engine.propose(book, request['transition_request'])
            values = {'conditional': result['status'] == 'conditional_continuation',
                'direct_transition': result['transition'] == direct,
                'complete_journal': result['transition']['journal'] == {cash: '-1/1', equity: '1/1'},
                'complete_balances': current['balances'] == {cash: '14/1', equity: '-14/1'},
                'memory_preserved': current['memory'] == book['memory'],
                'selected_memory': current['memory']['history']['sales/a~1'] == expected,
                'provenance_retained': result['opening_result'] == request['opening_result'],
                'profit': result['report']['income']['profit'] == '0/1',
                'financing_flow': result['report']['cash_flows']['activities']['financing']['net'] == '-1/1',
                'equity': result['report']['equity']['closing'] == '14/1',
                'false_flags': all(result[k] is False for k in continuation.FLAGS),
                'replay': continuation.verify(request, result)}
            name = owner + ':' + str(selected)
            checks.extend({'name': name + ':' + k, 'passed': bool(v)} for k, v in values.items())
            cases.append({'case': name, 'request': request, 'result': result})
    assert all(r['passed'] for r in checks)
    assert all(sha(ROOT / name) == h for name, h in lock.items()), 'source_changed_during_run'
    summary = {'passed': True, 'focused_tests': focused.testsRun, 'regression_tests': prior.testsRun,
        'named_comparisons': len(checks), 'cases': len(cases), 'protected_files': len(lock)}
    comparison = {'checks': checks, 'cases': cases}
    if args.record:
        dump(HERE / 'source-lock.json', lock); dump(HERE / 'checks.json', summary); dump(HERE / 'comparison.json', comparison)
        dump(HERE / 'run-manifest.json', {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B ' + str(Path(__file__).relative_to(ROOT)) + ' --record',
            'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
            'solver_version': continuation.source.attachment.z3.get_version_string(),
            'cpu_gpu': 'CPU-only Python/Z3; no GPU import', 'seeds': 'N/A: exact selected witnesses',
            'data_version': 'Source-locked synthetic fixtures', 'wall_seconds': time.time() - started,
            'plan': 'docs/plans/accounting-conditional-continuation-20261025.md', 'result': str(HERE.relative_to(ROOT) / 'result.md'),
            'artifacts': ['checks.json', 'source-lock.json', 'comparison.json', 'focused.log', 'regression.log']})
    else:
        assert summary == json.loads((HERE / 'checks.json').read_text())
        assert continuation.core.canonical(comparison) == continuation.core.canonical(json.loads((HERE / 'comparison.json').read_text()))
    print(json.dumps({**summary, 'mode': 'record' if args.record else 'read_only_replay'}))


if __name__ == '__main__': main()
