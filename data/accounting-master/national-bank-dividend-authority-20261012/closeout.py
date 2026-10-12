"""Freeze this completed source/integration unit; never rewrite it later."""
import datetime
import json
import platform
import subprocess
import sys
import time
from build_candidate import OUT, ROOT, BASE, CAND, sha, save

start = time.monotonic()
assert not (OUT / 'completion.json').exists()
source = json.loads((OUT / 'source-checks.json').read_text())
integration = json.loads((OUT / 'integration-checks.json').read_text())
assert not source['failed'] and not integration['failed']
assert sha(CAND / 'accounting-product-proposal.pdf') == integration['pdf_sha256']
assert integration['pdf_sha256'] in (OUT / 'author-review.md').read_text()
for row in json.loads((OUT / 'controls-after.json').read_text()):
    assert sha(ROOT / row['live']) == row['sha256'] == sha(ROOT / row['snapshot'])
for row in json.loads((OUT / 'final-renders.json').read_text()):
    assert sha(ROOT / row['render']) == row['sha256'] and row['pdf_sha256'] == integration['pdf_sha256']
plans = ['docs/plans/accounting-national-bank-dividend-authority-20261012.md',
         'docs/plans/accounting-dividend-timing-integration-20261012.md',
         'docs/plans/accounting-bank-capital-payout-dependencies-20261012.md']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark', '.pdf', '.log', '.blg'}]
paths += [ROOT / p for p in plans]
external = {ROOT / row['source'] for row in json.loads((OUT / 'renders.json').read_text())}
external.add(BASE / 'accounting-product-proposal.pdf')
build = json.loads((OUT / 'build-run.json').read_text())
manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'started_utc': json.loads((OUT / 'baseline.json').read_text())['started_utc'],
            'closed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
            'commands': [['python3', str((OUT / name).relative_to(ROOT))] for name in
                         ['record_sources.py', 'complete_sources.py', 'build_candidate.py', 'build_pdf.py',
                          'render_review.py', 'verify_integration.py', 'update_controls.py', 'closeout.py']],
            'build_command': build['command'],
            'source_access': str((OUT / 'access-receipts.json').relative_to(ROOT)),
            'environment': {'python': sys.executable, 'version': platform.python_version(),
                            'libraries': ['PyMuPDF', 'lxml'], 'build_overrides': build['environment_overrides']},
            'cpu_gpu': 'CPU document processing only; GPU intentionally hidden for build; no GPU framework import or device query.',
            'data_version': 'Hash-bound eCFR dated responses, 2024 US Code, 2025 CFR, 90 FR 55248 and issuer 2025 Form 10-K.',
            'seeds': 'N/A: deterministic documentary work',
            'wall_seconds': {'source_checks': source['wall_seconds'], 'final_build': build['wall_seconds'],
                             'integration_checks': integration['wall_seconds'], 'closeout': time.monotonic() - start},
            'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(external)},
            'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
            'readiness': 'not_ready', 'review': 'bounded author review; independent/human/domain/legal acceptance pending',
            'runtime': 'held', 'next_plan': plans[-1]}
save('run-manifest.json', manifest)
for rel, digest in (manifest['input_hashes'] | manifest['artifact_hashes']).items():
    assert sha(ROOT / rel) == digest
save('completion.json', {'status': 'bounded source and integration unit complete', 'source_checks': source['passed'],
                         'integration_checks': integration['passed'], 'failed': 0, 'pages': integration['pages'],
                         'pdf_sha256': integration['pdf_sha256'], 'manifest_sha256': sha(OUT / 'run-manifest.json'),
                         'bound_artifacts': len(manifest['artifact_hashes']), 'readiness': 'not_ready',
                         'next_plan': plans[-1]})
print(json.dumps({'source_checks': source['passed'], 'integration_checks': integration['passed'],
                  'bound_artifacts': len(manifest['artifact_hashes']), 'readiness': 'not_ready'}))
