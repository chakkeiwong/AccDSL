"""Freeze the corrected source reading without rewriting the old unit."""
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
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    report = json.loads((OUT / 'checks.json').read_text())
    facts = json.loads((OUT / 'source-facts.json').read_text())
    ck('23 targeted checks pass', report['passed'] == 23 and not report['failed'])
    ck('source identity', sha(ROOT / facts['source_pdf']) == facts['sha256'])
    ck('separate table band recorded', facts['note20']['bands_in_display_order'] ==
       ['Parent company', 'Subsidiaries', 'Junior subordinated debt'])
    old = ROOT / 'data/accounting-master/jpmorgan-debt-perimeter-20261012'
    old_completion = json.loads((old / 'completion.json').read_text())
    ck('old unit preserved', old_completion['manifest_sha256'] == sha(old / 'run-manifest.json'))
    v236 = ROOT / 'data/accounting-master/accounting-proposal-v236-integration-20261012'
    v236_completion = json.loads((v236 / 'completion.json').read_text())
    ck('old integration preserved', v236_completion['manifest_sha256'] == sha(v236 / 'run-manifest.json'))
    for name in ['verify.py', 'author-review.md', 'result.md', 'source-facts.json', 'checks.json']:
        ck('present ' + name, (OUT / name).is_file())
    ck('error called source-fidelity error', 'source-fidelity error' in (OUT / 'author-review.md').read_text())
    ck('legal issuer left unresolved', 'does not explain the legal issuer' in (OUT / 'result.md').read_text())
    failures = [item['name'] for item in checks if not item['passed']]
    if failures:
        print(json.dumps({'failed': failures}))
        raise SystemExit(1)
    plan = ROOT / 'docs/plans/accounting-jpmorgan-junior-classification-repair-20261012.md'
    source = ROOT / facts['source_pdf']
    image = old / 'rendered/page-283.png'
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.iterdir()
              if p.is_file() and p.name not in {'run-manifest.json', 'closeout-checks.json', 'completion.json'}}
    for p in [plan, source, image, old / 'run-manifest.json', v236 / 'run-manifest.json']:
        hashes[str(p.relative_to(ROOT))] = sha(p)
    manifest = {
        'recorded_at': '2026-10-12',
        'unit': 'JPMorgan Note 20 junior-band source-classification correction',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated dirty work preserved; .git read-only',
        'plan': str(plan.relative_to(ROOT)),
        'result': str((OUT / 'result.md').relative_to(ROOT)),
        'source_pdf': facts['source_pdf'], 'data_version': 'Retained complete issuer-hosted 2025 Form 10-K',
        'environment': {'python': platform.python_version(), 'cpu_gpu': 'CPU-only; GPU intentionally hidden',
                        'random_seeds': 'N/A deterministic source and arithmetic checks'},
        'commands': [
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-junior-classification-repair-20261012/verify.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-junior-classification-repair-20261012/closeout.py',
        ],
        'wall_time_seconds': {'source_check': report['wall_seconds'], 'closeout_before_manifest': time.monotonic()-START},
        'source_checks': report['passed'], 'closeout_checks': len(checks),
        'artifact_hashes': hashes, 'legal_issuer_mapping': 'unverified', 'readiness': 'not_ready',
    }
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0,
                                  'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_source_classification_correction',
                              'source_checks': report['passed'], 'closeout_checks': len(checks),
                              'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'),
                              'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0}))


if __name__ == '__main__':
    main()
