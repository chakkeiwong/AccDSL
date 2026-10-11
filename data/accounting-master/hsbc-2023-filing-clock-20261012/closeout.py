"""Freeze the HSBC filing event and source-limited document comparison."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert not (OUT / 'completion.json').exists(), 'Closed evidence stays frozen'
    baseline = json.loads((OUT / 'baseline.json').read_text())
    event = json.loads((OUT / 'event.json').read_text())
    report = json.loads((OUT / 'checks.json').read_text())
    checks = []
    def ck(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
    ck('22 source checks', report['passed'] == 22 and not report['failed'] and all(c['passed'] for c in report['checks']))
    for label in ['official_source', 'issuer_filing_copy']:
        obj = event[label]
        ck(label, sha(ROOT / obj['path']) == obj['sha256'])
    selected = event['selected_report']
    ck('selected annual unchanged', sha(ROOT / selected['local_path']) == selected['sha256'])
    ck('filing event retained', event['event']['filingDate'] == '2024-02-22'
       and event['event']['accessionNumber'] == '0001089113-24-000004')
    ck('no selected-file date admission', event['selected_publication_date'] == 'not_verified' and event['selected_byte_admissions'] == 0)
    ck('candidate unchanged', sha(ROOT / baseline['current_pdf']) == baseline['current_pdf_sha256'])
    for rel, digest in baseline['frozen_sources'].items():
        ck('frozen source ' + rel, sha(ROOT / rel) == digest)
    for r in event['renders']:
        ck('render identity ' + r['path'], sha(ROOT / r['path']) == r['sha256'])
    for name in ['result.md', 'author-review.md', 'next-source-frontier.md']:
        ck(name, (OUT / name).is_file())
    controls = {}
    for old in baseline['pointer_snapshots']:
        ck('snapshot ' + old['live'], sha(ROOT / old['snapshot']) == old['sha256'])
        text = (ROOT / old['live']).read_text()
        ck('current pointer ' + old['live'], 'hsbc-2023-filing-clock-20261012/result.md' in text
           and baseline['current_pdf_sha256'] in text and 'not_ready' in text)
        controls[old['live']] = sha(ROOT / old['live'])
    failures = [c['name'] for c in checks if not c['passed']]
    if failures:
        print(json.dumps({'failed': failures}))
        raise SystemExit(1)
    plan = 'docs/plans/accounting-hsbc-2023-filing-clock-20261012.md'
    excluded = {'run-manifest.json', 'completion.json', 'closeout-checks.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*')
              if p.is_file() and p.name not in excluded and p.suffix != '.pyc'}
    for rel in [plan, selected['local_path'], *baseline['frozen_sources']]:
        hashes[rel] = sha(ROOT / rel)
    write('run-manifest.json', {
        'recorded_at': '2026-10-12', 'unit': 'HSBC 2023 original Form 20-F filing event and distinct annual PDF',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated work and preexisting staged changes preserved; .git currently read-only',
        'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
        'data_version': {'SEC': event['official_source']['sha256'], 'issuer_filing': event['issuer_filing_copy']['sha256'], 'selected_annual': selected['sha256']},
        'environment': {'python': platform.python_version(), 'cpu_gpu': 'CPU-only PDF/source inspection; no framework import or GPU detection', 'random_seeds': 'N/A deterministic documentary checks'},
        'commands': ['python3 data/accounting-master/hsbc-2023-filing-clock-20261012/build.py', 'python3 data/accounting-master/hsbc-2023-filing-clock-20261012/closeout.py'],
        'source_GETs': [{'url': event['official_source']['url'], 'bytes': (ROOT / event['official_source']['path']).stat().st_size, 'http_status': 200, 'max_time_seconds': 45, 'max_bytes': 5000000},
                        {'url': event['issuer_filing_copy']['url'], 'bytes': (ROOT / event['issuer_filing_copy']['path']).stat().st_size, 'http_status': 200, 'max_time_seconds': 45, 'max_bytes': 8000000}],
        'timing': {'source_check_seconds': report['wall_seconds'], 'closeout_before_manifest_seconds': time.monotonic() - start, 'download_wall_time': 'not retained for complete transfers; headers and tool responses preserved'},
        'scope': 'metadata plus cover/page-count comparison; full document and incorporation equivalence not checked',
        'source_checks': report['passed'], 'closeout_checks': len(checks), 'pointer_snapshots': baseline['pointer_snapshots'],
        'controls_at_closeout': controls, 'artifact_hashes': hashes, 'current_candidate_sha256': baseline['current_pdf_sha256'],
        'selected_byte_admissions': 0, 'readiness': 'not_ready'})
    digest = sha(OUT / 'run-manifest.json')
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'manifest_sha256': digest})
    write('completion.json', {'status': 'closed_bounded_filing_event_selected_annual_date_unverified', 'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'manifest_sha256': digest, 'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0}))

if __name__ == '__main__':
    main()
