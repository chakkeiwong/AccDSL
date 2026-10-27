"""Freeze the bounded Note 20/33 source comparison."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, data): (OUT / name).write_text(json.dumps(data, indent=2) + '\n')

def main():
    assert not (OUT / 'completion.json').exists(), 'Closed source work stays frozen'
    source = json.loads((OUT / 'source-manifest.json').read_text())
    ledger = json.loads((OUT / 'source-ledger.json').read_text())
    report = json.loads((OUT / 'checks.json').read_text())
    checks = []
    def ck(name, value): checks.append({'check': name, 'passed': bool(value)})
    ck('50 source checks', report['passed'] == 50 and report['failed'] == 0 and all(x['passed'] for x in report['checks']))
    ck('source PDF intact', sha(ROOT / source['source_pdf']) == source['source_pdf_sha256'])
    ck('Note 33 comparator intact', sha(ROOT / source['comparator']) == source['comparator_sha256'])
    ck('Version 2.35 intact', sha(ROOT / source['candidate_pdf']) == source['candidate_pdf_sha256'])
    ck('two page source', [p['pdf_page'] for p in source['pages']] == [283, 284])
    for p in source['pages']:
        for field in ['reading', 'layout', 'render']:
            ck(f'{field} page {p["pdf_page"]}', sha(ROOT / p[field]) == p[field + '_sha256'])
    ck('14 selected rows', len(ledger['rows']) == 14)
    ck('eight qualifications', len(ledger['qualifiers']) == 8)
    for row in ledger['rows'] + ledger['qualifiers']:
        text = (ROOT / row['source_text']).read_text()
        ck('source span ' + row['id'], text[row['start']:row['end']] == row['quote'] and hashlib.sha256(row['quote'].encode()).hexdigest() == row['span_sha256'])
    for row in source['pointer_snapshots']:
        ck('prior control ' + row['live'], sha(ROOT / row['snapshot']) == row['sha256'])
        ck('live 2.35 still current ' + row['live'], source['candidate_pdf_sha256'] in (ROOT / row['live']).read_text())
    for name in ['result.md', 'author-review.md', 'next-source-frontier.md']:
        ck('review artifact ' + name, (OUT / name).is_file())
    ck('causal boundary retained', '**not** a verified legal-issuer' in (OUT / 'result.md').read_text())
    failed = [x['check'] for x in checks if not x['passed']]
    if failed:
        print(json.dumps({'failures': failed}))
        raise SystemExit(1)
    excluded = {'run-manifest.json', 'closeout-checks.json', 'completion.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in excluded}
    plan = 'docs/plans/accounting-jpmorgan-debt-perimeter-20261012.md'
    hashes[plan] = sha(ROOT / plan)
    manifest = {
        'recorded_at': '2026-10-12', 'unit': 'JPMorgan 2025 Note 20 debt perimeter and Note 33 comparator',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated dirty work preserved; .git read-only',
        'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
        'source_pdf': {'path': source['source_pdf'], 'sha256': source['source_pdf_sha256']},
        'data_version': 'Issuer-hosted complete 2025 Form 10-K candidate; selected-byte historical availability not established',
        'environment': {'python': platform.python_version(), 'pdf': 'PyMuPDF and pdftotext; no ML framework', 'cpu_gpu': 'CPU-only; GPU intentionally hidden', 'random_seeds': 'N/A deterministic documentary checks'},
        'commands': [
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-debt-perimeter-20261012/prepare.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-debt-perimeter-20261012/analyze.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-debt-perimeter-20261012/closeout.py',
        ],
        'wall_time_seconds': {'source_preparation': source['wall_seconds'], 'analysis': report['wall_seconds'], 'closeout_before_manifest': time.monotonic() - START},
        'source_checks': report['passed'], 'closeout_checks': len(checks),
        'artifact_hashes': hashes, 'readiness': 'not_ready',
        'instrument_classification': 'unverified', 'current_codification': 'not_verified',
        'historical_byte_availability': 'not_verified', 'independent_accounting': 'pending', 'human_acceptance': 'pending',
    }
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_bounded_source_reading', 'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'), 'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'artifact_hashes': len(hashes)}))

if __name__ == '__main__': main()
