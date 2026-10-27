from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    record = sys.argv[1:] == ['--record']
    assert sys.argv[1:] in ([], ['--record'])
    started = datetime.now(timezone.utc).isoformat()
    began = time.monotonic()
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
               '-p', 'test_declared_financing_schedule_evidence_v1.py']
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (HERE / 'focused-tests.log').write_text(run.stdout + '\n' + run.stderr)
    match = re.search(r'Ran (\d+) tests', run.stderr)
    focused = int(match[1]) if match else 0
    checks = [{'name': 'focused_tests',
               'passed': run.returncode == 0 and focused == 15 and run.stderr.rstrip().endswith('OK')}]

    examples = load(REL + '/examples.py', 'schedule_validation_examples')
    comparison = examples.compare()
    checks.extend(comparison['checks'])
    assert len(comparison['checks']) == 123
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']][:5]

    compact_cases = []
    for case in comparison['cases']:
        item = {'case': case['case'], 'checks': case['checks']}
        if 'schedule' in case:
            schedule = case['schedule']
            item['summary'] = {
                'interest_expense': schedule['interest_expense'],
                'interest_coverage': schedule['interest_coverage'],
                'financing_cash': schedule['financing_cash']['by_activity'],
                'schedules': {key: {
                    field: schedule['schedules'][key][field]
                    for field in ['opening', 'increases', 'decreases', 'closing',
                                  'categories', 'reconciliation']}
                    for key in ['debt', 'interest_payable', 'capital',
                                'retained', 'dividend_payable']}}
        else:
            item['summary'] = {'v1_v2': True}
        compact_cases.append(item)

    protected = {}
    paths = [
        Path('scripts/declared_financing_schedules_v1.py'),
        Path('scripts/declared_working_capital_v2.py'),
        Path('scripts/declared_company_program_v2.py'),
        Path('scripts/declared_financing_methods_v1.py'),
        Path('tests/test_declared_financing_schedule_evidence_v1.py'),
        Path(REL + '/examples.py'), Path(REL + '/audit.md'),
        Path(REL + '/design.md'), Path(REL + '/focused-tests.log'),
        Path('docs/plans/accounting-declared-financing-schedules-validation-20261025.md'),
        Path('data/accounting-master/declared-financing-schedules-repair-20261025/checks.json'),
        Path('data/accounting-master/declared-financing-schedules-repair-20261025/source-lock.json'),
        Path('data/accounting-master/declared-financing-schedules-20261025/checks.json'),
        Path('docs/design/proposal/manuscript-financing-clock-20261025/accounting-product-proposal.pdf'),
    ]
    for path in paths:
        protected[path.as_posix()] = digest(ROOT / path)

    summary = {'passed': True, 'checks': len(checks), 'focused_tests': focused,
               'comparison_checks': len(comparison['checks']), 'cases': len(comparison['cases']),
               'protected_files': len(protected), 'previous_claim_rejected': True}
    if record:
        dump(HERE / 'checks.json', {**summary, 'named_checks': checks})
        dump(HERE / 'comparison.json', {'cases': compact_cases, 'checks': comparison['checks'],
                                        'summary': summary})
        dump(HERE / 'source-lock.json', protected)
        dump(HERE / 'manifest.json', {
            'started_utc': started, 'wall_seconds': time.monotonic() - began,
            'git_commit_recorded': '03fea070f089821f4759e49a4466a3399b7fc078',
            'command': 'python3 -B ' + REL + '/verify.py --record',
            'environment': platform.python_version(),
            'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds': 'N/A: deterministic exact checks',
            'plan': 'docs/plans/accounting-declared-financing-schedules-validation-20261025.md',
            'result': REL + '/result.md', 'source_lock_sha256': digest(HERE / 'source-lock.json'),
            'summary': summary})
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
