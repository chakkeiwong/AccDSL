"""Freeze the six older HSBC results-group links after author review."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    checks = []
    def ck(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
    baseline = json.loads((OUT / 'baseline.json').read_text())
    ledger = json.loads((OUT / 'dated-results-groups.json').read_text())
    report = json.loads((OUT / 'checks.json').read_text())
    ck('57 checks passed', report['passed'] == 57 and report['failed'] == 0
       and all(c['passed'] for c in report['checks']))
    source = ledger['source']
    ck('retained source identity', sha(ROOT / source['local_path']) == source['sha256'])
    ck('six group records', [r['report_year'] for r in ledger['records']] == list(range(2018, 2024)))
    ck('zero selected-byte admissions', ledger['selected_byte_admissions'] == 0)
    for r in ledger['records']:
        ck(str(r['report_year']) + ' report identity', sha(ROOT / r['selected_report']['local_path']) == r['selected_report']['sha256'])
        ck(str(r['report_year']) + ' publication unresolved', r['individual_file_publication_date'] == 'not_verified'
           and r['selected_byte_as_of_admission'] == 'none')
    ck('candidate unchanged', sha(ROOT / baseline['current_pdf']) == baseline['current_pdf_sha256'])
    for rel, digest in baseline['frozen_sources'].items():
        ck('frozen source ' + rel, sha(ROOT / rel) == digest)
    controls = {}
    for item in baseline['pointer_snapshots']:
        ck('snapshot ' + item['live'], sha(ROOT / item['snapshot']) == item['sha256'])
        current = ROOT / item['live']
        text = current.read_text()
        ck('live pointer ' + item['live'], 'hsbc-older-results-groups-20261012/result.md' in text
           and baseline['current_pdf_sha256'] in text and 'not_ready' in text)
        controls[item['live']] = sha(current)
    for name in ['result.md', 'author-review.md', 'next-source-frontier.md']:
        ck('record ' + name, (OUT / name).is_file())
    failed = [c['name'] for c in checks if not c['passed']]
    if failed:
        print(json.dumps({'failed': failed}))
        raise SystemExit(1)
    plan = 'docs/plans/accounting-hsbc-older-results-groups-20261012.md'
    excluded = {'run-manifest.json', 'completion.json', 'closeout-checks.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*')
              if p.is_file() and p.name not in excluded and p.suffix != '.pyc'}
    inputs = [plan, source['local_path'], 'data/financial-report-benchmark/source-access.json',
              *baseline['frozen_sources'], *[r['selected_report']['local_path'] for r in ledger['records']]]
    for rel in inputs:
        hashes[rel] = sha(ROOT / rel)
    manifest = {'recorded_at': '2026-10-12', 'unit': 'HSBC 2018-2023 results groups and selected links',
                'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
                'git_state': 'main; unrelated dirty work preserved; .git read-only',
                'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
                'data_version': 'Retained official paginated Group archive captured 2026-10-02T12:13:23+00:00',
                'environment': {'python': platform.python_version(),
                                'cpu_gpu': 'CPU-only standard-library parsing; no device detection or framework import',
                                'random_seeds': 'N/A deterministic source inspection'},
                'commands': ['python3 data/accounting-master/hsbc-older-results-groups-20261012/build.py',
                             'python3 data/accounting-master/hsbc-older-results-groups-20261012/closeout.py'],
                'wall_time_seconds': {'source_checks': report['wall_seconds'], 'closeout_before_manifest': time.monotonic() - start},
                'source_checks': report['passed'], 'closeout_checks': len(checks),
                'pointer_snapshots': baseline['pointer_snapshots'], 'controls_at_closeout': controls,
                'artifact_hashes': hashes, 'selected_byte_admissions': 0,
                'readiness': 'not_ready', 'current_candidate_sha256': baseline['current_pdf_sha256']}
    write('run-manifest.json', manifest)
    digest = sha(OUT / 'run-manifest.json')
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'manifest_sha256': digest})
    write('completion.json', {'status': 'closed_bounded_results_group_links_publication_unverified',
                              'source_checks': report['passed'], 'closeout_checks': len(checks),
                              'failed': 0, 'manifest_sha256': digest, 'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0}))

if __name__ == '__main__':
    main()
