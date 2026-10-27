"""Close the bounded historical lead with the current reconciliation unresolved."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    report = json.loads((OUT / 'checks.json').read_text())
    evidence = json.loads((OUT / 'evidence.json').read_text())
    baseline = json.loads((OUT / 'baseline.json').read_text())
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('17 bounded source checks pass', report['passed'] == 17 and not report['failed'])
    for label in ['historical_source', 'current_source']:
        source = evidence[label]
        ck(label + ' identity', sha(ROOT / source['path']) == source['sha256'])
    hist = evidence['historical_source']
    ck('inspected selected 2018 render', sha(ROOT / hist['render']) == hist['render_sha256'])
    current_pdf = ROOT / 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
    ck('Version 2.37 unchanged', sha(current_pdf) == baseline['current_pdf_sha256'])
    for name in ['author-review.md', 'result.md', 'next-source-frontier.md', 'hit-index.json']:
        ck('record ' + name, (OUT / name).is_file())
    ck('current bridge remains unresolved', 'no source that identifies\nthe 2025 instruments' in (OUT / 'result.md').read_text())
    controls = {}
    for item in baseline['pointer_snapshots']:
        ck('prior pointer ' + item['live'], sha(ROOT / item['snapshot']) == item['sha256'])
        path = ROOT / item['live']
        content = path.read_text()
        ck('current source and readiness ' + item['live'],
           'jpmorgan-junior-reconciliation-20261012/result.md' in content and
           'not_ready' in content and baseline['current_pdf_sha256'] in content)
        controls[item['live']] = sha(path)
    failures = [x['name'] for x in checks if not x['passed']]
    if failures:
        print(json.dumps({'failed': failures}))
        raise SystemExit(1)
    plan = 'docs/plans/accounting-jpmorgan-junior-reconciliation-20261012.md'
    excluded = {'run-manifest.json', 'closeout-checks.json', 'completion.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*')
              if p.is_file() and p.name not in excluded and p.suffix != '.pyc'}
    for path in [ROOT / plan, ROOT / hist['path'], ROOT / evidence['current_source']['path']]:
        hashes[str(path.relative_to(ROOT))] = sha(path)
    manifest = {
        'recorded_at': '2026-10-12', 'unit': 'Bounded JPMorgan junior-debt reconciliation inquiry',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated dirty work preserved; .git read-only',
        'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
        'data_version': 'Selected corpus 2018 Form 10-K and retained complete 2025 Form 10-K',
        'environment': {'python': platform.python_version(), 'cpu_gpu': 'CPU-only; GPU intentionally hidden',
                        'random_seeds': 'N/A deterministic source/search checks'},
        'commands': ['CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-junior-reconciliation-20261012/' + f
                     for f in ['locate.py', 'analyze.py', 'prepare.py', 'update_controls.py', 'closeout.py']],
        'wall_time_seconds': {'analysis': report['wall_seconds'], 'closeout_before_manifest': time.monotonic()-START},
        'source_checks': report['passed'], 'closeout_checks': len(checks),
        'current_candidate_pdf': str(current_pdf.relative_to(ROOT)),
        'current_candidate_sha256': baseline['current_pdf_sha256'],
        'current_reconciliation': 'unverified', 'historical_lead': 'source_checked',
        'controls': controls, 'pointer_snapshots': baseline['pointer_snapshots'],
        'artifact_hashes': hashes, 'readiness': 'not_ready',
    }
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0,
                                  'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_bounded_inquiry_current_mapping_unresolved',
                              'source_checks': report['passed'], 'closeout_checks': len(checks),
                              'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'),
                              'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0}))


if __name__ == '__main__':
    main()
