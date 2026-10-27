"""Preservation audit with explicit evidence roles; no sector promotion."""
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P5 = ROOT / 'data/accounting-master/company-composition-20261016'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def inspect():
    locks = {}; checks = []
    def retain(path):
        locks[str(path.relative_to(ROOT))] = sha(path)
        return path
    def read(path): return json.loads(retain(path).read_text())
    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed), 'role': 'preservation_or_record_consistency'})
        if not passed: raise AssertionError(name)
    manifest = read(P5 / 'run-manifest.json')
    attempt = next(row for row in manifest['runs'] if row['attempt'] == 'attempt-03')
    for field in ['packet', 'validation']:
        path = retain(ROOT / attempt[field]); check('p5_' + field + '_hash', sha(path) == attempt[field + '_sha256'])
    validation = read(ROOT / attempt['validation'])
    check('p5_recorded_checks', len(validation['checks']) == attempt['checks'] == 681)
    check('p5_recorded_failures', validation['failed'] == 0 and all(row['passed'] for row in validation['checks']))
    for name, row in attempt['input_snapshots'].items():
        check('p5_input:' + name, sha(retain(ROOT / row['path'])) == row['sha256'])
    prior_lock = read(ROOT / 'data/accounting-master/corporate-composition-audit-20261025/inspected-source-lock.json')
    for name, expected in prior_lock.items(): check('corporate_lock:' + name, sha(retain(ROOT / name)) == expected)
    evidence = []
    for sector, expected_count in [('bank', 53), ('insurance', 2705)]:
        folder = ROOT / ('data/accounting-master/r03-' + sector + '-residual-audit-20261016')
        previous = read(folder / 'run-manifest.json'); note = read(folder / 'audit.json')
        check(sector + '_audit_hash', sha(folder / 'audit.json') == previous['audit_sha256'])
        observed = read(ROOT / previous['validation'])
        if sector == 'bank':
            check('bank_recorded_validation', observed['total'] == expected_count and observed['failures'] == 0
                  and len(observed['checks']) == expected_count and all(row['passed'] for row in observed['checks']))
        else:
            check('insurance_recorded_diagnostic', observed['passed'] is True and observed['checks'] == 92
                  and observed['failures'] == [])
            # The residual manifest points to the 92-check diagnostic, not the
            # 2,705-check exchange validation. Resolve the actual original run.
            original = ROOT / 'data/accounting-master/extended-method-exchanges-20261015/insurance-assessment'
            origin = read(original / 'run-manifest.json')
            run = next(row for row in origin['runs'] if row['attempt'] == 'attempt-02')
            check('insurance_exchange_record', run['verification']['checks'] == expected_count
                  and run['verification']['failures'] == 0 and run['verification']['status'] == 'passed')
            for filename in ['portable-exchanges.json', 'verification.json']:
                path = retain(original / 'attempt-02' / filename)
                record = next(row for row in origin['files'] if row['path'] == str(path.relative_to(ROOT)))
                check('insurance_original_hash:' + filename, sha(path) == record['sha256'])
            check('insurance_packet_hash', sha(original / 'attempt-02/portable-exchanges.json') == run['verification']['packet_sha256'])
            retain(original / 'result.md')
        retain(folder / 'result.md')
        evidence.append({'sector': sector, 'result': str((folder / 'result.md').relative_to(ROOT)),
                         'recorded_checks': expected_count, 'role': 'retained_report_not_fresh_sector_execution',
                         'scope': note['admitted_scope'], 'residuals_at_that_date': note['residuals'],
                         'limitations': note['nonclaims']})
    for name in ['bank-transfer-fees-20261015', 'bank-poci-rollforward-20261016',
                 'insurance-acquisition-incorporation-20261013', 'insurance-vfa-integration-20261012']:
        retain(ROOT / 'data/accounting-master' / name / 'result.md')
    for relative in ['data/accounting-master/company-module-boundary-20261023/design.md',
                     'data/accounting-master/group-sector-composition-20261025/audit.py',
                     'data/accounting-master/group-sector-composition-20261025/checks.json',
                     'data/accounting-master/group-sector-composition-20261025/source-lock.json',
                     'data/accounting-master/group-sector-composition-20261025/result.md',
                     'docs/plans/accounting-group-sector-composition-20261025.md']:
        retain(ROOT / relative)
    return {'checks': checks, 'evidence': evidence, 'source_lock': locks,
            'summary': {'passed': True, 'checks': len(checks), 'locked_files': len(locks),
                        'p5_recorded_checks': 681, 'p5_input_files': len(attempt['input_snapshots']),
                        'corporate_locked_files': len(prior_lock),
                        'sector_semantics_revalidated': False, 'references_resolved': False}}


def main():
    start = time.monotonic(); value = inspect()
    if '--verify' in sys.argv:
        expected = json.loads((HERE / 'audit.json').read_text())
        if value != expected: raise AssertionError('retained audit replay mismatch')
        print(json.dumps({'replayed': True, **value['summary']})); return
    if (HERE / 'audit.json').exists(): raise SystemExit('audit exists; use --verify')
    dump(HERE / 'audit.json', value)
    dump(HERE / 'audit-manifest.json', {
        'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'command': 'python3 -B data/accounting-master/company-world-envelope-20261025/audit.py',
        'environment': sys.version, 'platform': platform.platform(), 'wall_seconds': time.monotonic() - start,
        'cpu_gpu': 'CPU file/hash inspection; no GPU framework imported', 'random_seeds': 'N/A: deterministic',
        'data_version': 'Retained P5 attempt-03 and dated bank/insurance result files, per audit.json',
        'plan': 'docs/plans/accounting-world-envelope-repair-20261025.md',
        'artifacts': ['audit.json','audit-result.md'], 'script_sha256': sha(Path(__file__))})
    print(json.dumps(value['summary']))


if __name__ == '__main__': main()
