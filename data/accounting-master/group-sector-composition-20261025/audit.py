"""Audit existing group/bank/insurance evidence; do not rerun or rewrite it."""
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P5 = ROOT / 'data/accounting-master/company-composition-20261016'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    manifest = json.loads((P5 / 'run-manifest.json').read_text())
    attempt = next(row for row in manifest['runs'] if row['attempt'] == 'attempt-03')
    packet = ROOT / attempt['packet']; validation = ROOT / attempt['validation']
    checks = []
    def check(name, passed, detail=''):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})
        if not passed: raise AssertionError(name + (':' + detail if detail else ''))
    check('p5_packet_hash', sha(packet) == attempt['packet_sha256'])
    check('p5_validation_hash', sha(validation) == attempt['validation_sha256'])
    payload = json.loads(validation.read_text())
    check('p5_zero_failures', payload['failed'] == 0 and all(row['passed'] for row in payload['checks']), str(payload['failed']))
    check('p5_check_count', len(payload['checks']) == attempt['checks'], str(len(payload['checks'])))
    input_hashes = attempt['input_snapshots']
    for name, row in input_hashes.items():
        path = ROOT / row['path']; check('p5_input:' + name, sha(path) == row['sha256'])
    for relative, expected in json.loads((ROOT / 'data/accounting-master/corporate-composition-audit-20261025/inspected-source-lock.json').read_text()).items():
        check('corporate_lock:' + relative, sha(ROOT / relative) == expected)
    sector = {
        'bank': [
            'data/accounting-master/bank-transfer-fees-20261015/result.md',
            'data/accounting-master/bank-poci-rollforward-20261016/result.md',
            'data/accounting-master/r03-bank-residual-audit-20261016/result.md'],
        'insurance': [
            'data/accounting-master/insurance-acquisition-incorporation-20261013/result.md',
            'data/accounting-master/insurance-vfa-integration-20261012/result.md',
            'data/accounting-master/r03-insurance-residual-audit-20261016/result.md']}
    for kind, names in sector.items():
        for name in names:
            text = (ROOT / name).read_text()
            check(kind + ':' + name, len(text) > 100 and 'remain' in text.lower())
    check('mission_plan_hash', sha(ROOT / 'docs/plans/accounting-group-sector-composition-20261025.md') ==
          sha(ROOT / 'docs/plans/accounting-group-sector-composition-20261025.md'))
    check('current_candidate', 'CompanyBookTransition/2' in (ROOT / 'scripts/company_book_transition_v2.py').read_text())
    summary = {'passed': True, 'p5_checks': len(payload['checks']), 'p5_failures': payload['failed'],
               'p5_input_files': len(input_hashes), 'sector_result_files': sum(map(len, sector.values())),
               'corporate_locked_files': len(json.loads((ROOT / 'data/accounting-master/corporate-composition-audit-20261025/inspected-source-lock.json').read_text())),
               'world_contract_status': 'not_implemented',
               'scope': 'Audit of retained finite group and sector evidence; no broad composition admission'}
    dump(HERE / 'checks.json', {'summary': summary, 'checks': checks})
    dump(HERE / 'source-lock.json', {str(packet.relative_to(ROOT)): sha(packet), str(validation.relative_to(ROOT)): sha(validation),
        'data/accounting-master/company-composition-20261016/run-manifest.json': sha(P5 / 'run-manifest.json'),
        'docs/plans/accounting-group-sector-composition-20261025.md': sha(ROOT / 'docs/plans/accounting-group-sector-composition-20261025.md'),
        'scripts/company_book_transition_v2.py': sha(ROOT / 'scripts/company_book_transition_v2.py')})
    dump(HERE / 'run-manifest.json', {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': 'python3 -B ' + str(Path(__file__).relative_to(ROOT)), 'python': sys.version,
        'platform': platform.platform(), 'cpu_gpu': 'CPU-only file/hash audit; no GPU framework imported',
        'data_version': 'CompanyComposition/1 attempt-03 plus retained bank/insurance results',
        'seeds': 'N/A: deterministic hash audit', 'p5_manifest': str((P5 / 'run-manifest.json').relative_to(ROOT)),
        'result': str((HERE / 'result.md').relative_to(ROOT))})
    (HERE / 'result.md').write_text('''# Group and sector composition audit result

The retained CompanyComposition/1 attempt-03 packet and validation hashes match its run manifest: 681 checks, zero failures, and all source/input locks pass. The packet establishes one finite synthetic parent/subsidiary world and two explicit migrations with one following transition each. It does not establish a general company-world or sector adapter.

Bank and insurance result packets remain separate conditional evidence. They preserve their own source, law, actuarial, credit, contract-group, reinsurance, capital and calibration boundaries. The audit found no basis to merge their state into the corporate packet by label or balance identity.

The smallest next contract is a closed CompanyWorld/1 envelope for identified legal books, ownership/control edges, sector profile, source/view references and conditional component handles. Its first implementation must validate identity, context and perimeter and preserve components without performing consolidation or sector postings. Whole group, bank and insurance composition remains open.
''')
    print(json.dumps(summary))


if __name__ == '__main__': main()
