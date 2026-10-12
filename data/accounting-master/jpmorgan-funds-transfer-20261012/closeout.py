"""Bind reviewed source and manuscript evidence without rewriting old units."""
import json
import subprocess
import time
from pathlib import Path
from prepare import OUT, ROOT, PDF, BASE, sha, save
from build_candidate import CAND

start=time.monotonic();assert not (OUT/'completion.json').exists()
source=json.loads((OUT/'source-manifest.json').read_text())
checks=json.loads((OUT/'integration-checks.json').read_text())
sc=json.loads((OUT/'source-checks.json').read_text())
assert checks['passed']==136 and not checks['failed'] and sc['passed']==33 and not sc['failed']
assert sha(CAND/'accounting-product-proposal.pdf')==checks['pdf_sha256']
assert checks['pdf_sha256'] in (OUT/'author-review.md').read_text()
for x in json.loads((OUT/'controls-after.json').read_text()):
    assert sha(ROOT/x['live'])==x['sha256']==sha(ROOT/x['snapshot'])
for x in json.loads((OUT/'final-renders.json').read_text()):
    assert sha(ROOT/x['render'])==x['sha256'] and x['pdf_sha256']==checks['pdf_sha256']
plan=ROOT/'docs/plans/accounting-jpmorgan-funds-transfer-20261012.md'
nextplan=ROOT/'docs/plans/accounting-national-bank-dividend-authority-20261012.md'
files=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [p for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf','.log','.blg'}]
files += [nextplan]
build=json.loads((OUT/'build-run.json').read_text());render=json.loads((OUT/'render-run.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'date':'2026-10-12',
    'plan':str(plan.relative_to(ROOT)),'result':str((OUT/'result.md').relative_to(ROOT)),
    'commands':[source['command'],['python3',str(OUT.relative_to(ROOT))+'/annotate.py'],
        ['python3',str(OUT.relative_to(ROOT))+'/build_candidate.py'],build['command'],render['command'],
        ['python3',str(OUT.relative_to(ROOT))+'/verify_integration.py'],
        ['python3',str(OUT.relative_to(ROOT))+'/update_controls.py'],['python3',str(Path(__file__).relative_to(ROOT))]],
    'environment':source['environment'] | {'build_overrides':build['environment_overrides']},
    'cpu_gpu':'CPU-only document inspection; CUDA_VISIBLE_DEVICES=-1; no GPU use or scientific framework import',
    'data_version':'Retained issuer 2025 Form 10-K and protected Version 2.38 bound by hashes',
    'seeds':'N/A: deterministic documentary checks',
    'wall_time_seconds':{'source':source['wall_seconds'],'annotation':sc['wall_seconds'],'build':build['wall_seconds'],
        'render':render['wall_seconds'],'integration':checks['wall_seconds'],'closeout':time.monotonic()-start},
    'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [PDF,BASE/'accounting-product-proposal.pdf',plan]},
    'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(files)},
    'review':'Author review; independent/human/domain/legal acceptance pending','readiness':'not_ready','runtime':'held'}
save('run-manifest.json',manifest)
for rel,digest in manifest['input_hashes'].items():assert sha(ROOT/rel)==digest
for rel,digest in manifest['artifact_hashes'].items():assert sha(ROOT/rel)==digest
save('completion.json',{'status':'bounded source and integration unit complete','source_checks':33,'integration_checks':136,
    'failed':0,'pages':176,'pdf_sha256':checks['pdf_sha256'],'manifest_sha256':sha(OUT/'run-manifest.json'),
    'bound_artifacts':len(manifest['artifact_hashes']),'readiness':'not_ready','next_plan':str(nextplan.relative_to(ROOT))})
print(json.dumps({'source_checks':33,'integration_checks':136,'bound_artifacts':len(manifest['artifact_hashes']),'pages':176}))
