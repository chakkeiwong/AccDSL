"""Record once, then replay without rewriting accepted evidence."""
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.metadata
import importlib.util
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(HERE)]
import examples

FOCUSED = ['test_company_memory_types_v1.py', 'test_company_book_transition_v2.py',
           'test_declared_receivable_lifecycle_v1.py', 'test_declared_receivable_text_v1.py']
REGRESSION = ['test_company_book_transition_v1.py', 'test_method_memory_effects_v1.py',
              'test_declared_collection_clock_v1.py', 'test_declared_operating_methods_v1.py',
              'test_declared_company_program_v1.py', 'test_company_book_carry_v1.py']


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, data): path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def run_tests(names):
    stream = io.StringIO(); suites = []
    for name in names:
        assert (ROOT / 'tests' / name).is_file(), name
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=name)
        assert suite.countTestCases() > 0, name
        suites.append(suite)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(suites))
    return result, stream.getvalue()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--record', action='store_true'); args = parser.parse_args()
    if args.record: assert not (HERE / 'checks.json').exists(), 'record_once_only'
    started = time.time()
    paths = [HERE / name for name in ['verify.py', 'examples.py', 'audit.md', 'transition-audit.md', 'lifecycle-audit.md']]
    paths += [ROOT / 'scripts' / name for name in ['company_memory_types_v1.py', 'company_book_transition_v2.py',
        'declared_receivable_lifecycle_v1.py', 'declared_receivable_text_v1.py']]
    paths += [ROOT / 'tests' / name for name in FOCUSED + REGRESSION]
    prior = ROOT / 'data/accounting-master/declared-dynamic-collection-clock-20261025/source-lock.json'
    prior_pins = json.loads(prior.read_text())
    for name, expected in prior_pins.items(): assert sha(ROOT / name) == expected, 'prior_changed:' + name
    paths += [ROOT / name for name in prior_pins]
    paths += [prior, ROOT / 'docs/plans/accounting-declared-collection-state-growth-20261025.md']
    paths = sorted(set(paths)); lock = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    if not args.record: assert lock == json.loads((HERE / 'source-lock.json').read_text()), 'recorded_source_mismatch'
    focused, focus_log = run_tests(FOCUSED)
    regression, regression_log = run_tests(REGRESSION)
    if args.record:
        (HERE / 'focused.log').write_text(focus_log); (HERE / 'regression.log').write_text(regression_log)
    if not focused.wasSuccessful() or not regression.wasSuccessful():
        print(focus_log[-4000:] + regression_log[-4000:]); raise AssertionError('test_failure')
    comparison = examples.compare()
    assert comparison['checks'] and all(row['passed'] for row in comparison['checks'])
    assert len({r['name'] for r in comparison['checks']}) == len(comparison['checks']), 'duplicate_check_name'
    assert all(sha(ROOT / name) == h for name, h in lock.items()), 'source_changed_during_run'
    summary = {'passed': True, 'focused_tests': focused.testsRun, 'regression_tests': regression.testsRun,
        'comparison_checks': len(comparison['checks']), 'cases': len(comparison['cases']), 'protected_files': len(lock),
        'scope': 'Typed finite claim growth and declared lifecycle only; no whole requirement closure'}
    if args.record:
        dump(HERE / 'source-lock.json', lock); dump(HERE / 'comparison.json', comparison)
        dump(HERE / 'checks.json', summary)
        manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B ' + str(Path(__file__).relative_to(ROOT)) + ' --record',
            'environment': {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
                            'jsonschema': importlib.metadata.version('jsonschema')},
            'cpu_gpu': 'CPU-only ordinary Python; no GPU framework imported', 'seeds': 'N/A: exact deterministic fixtures',
            'data_version': 'Synthetic fixtures in recorded source lock', 'wall_seconds': time.time() - started,
            'plan': 'docs/plans/accounting-declared-collection-state-growth-20261025.md',
            'result': str(HERE.relative_to(ROOT) / 'result.md'),
            'outputs': [str(HERE.relative_to(ROOT) / n) for n in ['checks.json', 'comparison.json', 'source-lock.json', 'focused.log', 'regression.log']]}
        dump(HERE / 'run-manifest.json', manifest)
    else:
        assert summary == json.loads((HERE / 'checks.json').read_text())
        assert examples.core.canonical(comparison) == examples.core.canonical(json.loads((HERE / 'comparison.json').read_text())), 'comparison_replay'
    print(json.dumps({**summary, 'mode': 'record' if args.record else 'read_only_replay'}))


if __name__ == '__main__': main()
