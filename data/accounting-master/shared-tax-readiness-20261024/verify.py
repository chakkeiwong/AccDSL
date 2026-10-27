from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(HERE))
import shared_tax_readiness_v1 as m
import examples

def sha(path): return sha256(path.read_bytes()).hexdigest()
def same(a, b): return m.book.caller.canonical(a) == m.book.caller.canonical(b)
def dump(name, value): (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    start = time.monotonic(); mode = sys.argv[1] if len(sys.argv) > 1 else '--check'
    assert mode in ['--check', '--record', '--replay']
    if mode == '--record': assert not (HERE / 'manifest.json').exists(), 'already recorded'
    m.protected(); checks = []
    def check(name, condition):
        assert condition, name
        checks.append(name)
    locks = json.loads((HERE / 'source-lock.json').read_text())
    for name, expected in locks.items(): check('protected:' + name, sha(ROOT / name) == expected)
    output = []
    for row in examples.cases():
        name = row['case']; body = row['request']; before = m.book.digest(body)
        result = m.assess(body)
        check(name + ':status', result['status'] == row['expected_status'])
        check(name + ':input_unchanged', m.book.digest(body) == before)
        check(name + ':flags', all(result[k] is False for k in m.FLAGS))
        check(name + ':exact_replay', m.verify_result(body, result))
        if 'request' in result: check(name + ':full_request', same(result['request'], body))
        if 'native_report' in result:
            check(name + ':complete_native_report', same(result['native_report'], m.reports.calculate(body['report_request'])))
        if 'requirements_result' in result:
            check(name + ':evaluator_flags', all(result['requirements_result'][k] is False for k in
                  ['executed', 'source_admission', 'accounting_admission', 'method_eligible']))
        output.append({**row, 'result': result})
    mixed = output[0]['result']
    check('all_61_declarations_missing', len(mixed['unresolved_information']) == len(mixed['required_information']) == 61)
    check('terminated_B_retained', {'lease_id': 'lease1', 'right_id': 'B'} in mixed['population']['lease_rights'])
    check('lease_gain_treatment_required', 'income/other_gains/treatment' in mixed['required_information'])
    check('unknown_loss_not_refund', 'loss_route' in mixed['unresolved_information'])
    check('complete_original_report', same(mixed['native_report'], examples.originals()['mixed_lifecycle']['result']))
    for row in output:
        if row['result']['status'] == 'information_supplied':
            check(row['case'] + ':not_annual', row['result']['native_report']['coverage']['annual_completion'] == 'unresolved')
    tests = json.loads((HERE / 'test-observation.json').read_text())
    check('tests_pass', tests['exit_code'] == 0)
    check('tested_source_hashes', all(sha(ROOT / n) == h for n, h in tests['files'].items()))
    report = {'passed': True, 'checks': len(checks), 'cases': len(output), 'protected_files': len(locks),
              'test_methods': tests['test_methods'], 'regression_methods': tests['regression_methods'],
              'whole_requirements_closed': 0, 'tax_computed': False}
    if mode == '--record':
        dump('cases.json', output); dump('checks.json', report); dump('check-names.json', checks)
        files = [p for p in HERE.iterdir() if p.is_file()] + [ROOT / 'scripts/shared_tax_readiness_v1.py',
            ROOT / 'tests/test_shared_tax_readiness_v1.py', ROOT / 'docs/plans/accounting-tax-readiness-integration-20261024.md']
        dump('manifest.json', {'recorded_at': datetime.now(timezone.utc).isoformat(),
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B data/accounting-master/shared-tax-readiness-20261024/verify.py --record',
            'environment': {'python': platform.python_version(), 'executable': sys.executable},
            'cpu_gpu': 'CPU-only; no GPU framework imported', 'random_seeds': 'N/A: deterministic conformance',
            'wall_seconds': time.monotonic() - start, 'data_version': 'source-lock.json',
            'plan': 'docs/plans/accounting-shared-tax-readiness-20261024.md',
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'files': {str(p.relative_to(ROOT)): sha(p) for p in files}})
    elif mode == '--replay':
        assert same(report, json.loads((HERE / 'checks.json').read_text()))
        assert same(output, json.loads((HERE / 'cases.json').read_text()))
        for name, expected in json.loads((HERE / 'manifest.json').read_text())['files'].items():
            assert sha(ROOT / name) == expected, name
    print(json.dumps(report))


if __name__ == '__main__': main()
