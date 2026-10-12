"""Bind the final candidate, source dependencies and reviewed live pointers."""
import datetime
import json
import platform
import subprocess
import sys
from build_candidate import OUT, ROOT, BASE, CAND, sha, save

assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'integration-checks.json').read_text());assert not c['failed']
for r in json.loads((OUT/'controls-after.json').read_text()):assert sha(ROOT/r['live'])==r['sha256']==sha(ROOT/r['snapshot'])
inputs=[BASE/'accounting-product-proposal.pdf']
for d in ['bank-method1-surcharge-20261012','bank-method1-reporting-20261012']:
    inputs.extend([ROOT/'data/accounting-master'/d/'run-manifest.json',ROOT/'data/accounting-master'/d/'completion.json'])
for rel in ['bank-capital-payout-dependencies-20261012/sources/ecfr-2026-04-01-3.11.xml',
            'bank-method1-surcharge-20261012/sources/ecfr-2026-01-01-217.403.xml',
            'bank-method1-surcharge-20261012/sources/ecfr-2026-01-01-217.404.xml',
            'bank-method1-reporting-20261012/sources/fr-y15-current-instructions.pdf',
            'bank-method1-reporting-20261012/sources/denominators-2024.pdf',
            'bank-method1-reporting-20261012/sources/denominators-2025.pdf']:
    inputs.append(ROOT/'data/accounting-master'/rel)
plans=['docs/plans/accounting-bank-reporting-integration-20261012.md','docs/plans/accounting-bank-method1-rule-history-20261012.md']
paths=[p for base in [OUT,CAND] for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/x for x in plans]
now=datetime.datetime.now(datetime.timezone.utc)
builds=[json.loads((OUT/'build-run.json').read_text())]+[json.loads(p.read_text()) for p in OUT.glob('intermediate/*/build-run.json')]
manifest={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
 'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['build_candidate.py','render_review.py','verify_integration.py','update_controls.py','closeout.py']],
 'builds':builds,'environment':{'python':sys.executable,'version':platform.python_version(),'libraries':['PyMuPDF'],'latex':'LuaLaTeX via latexmk'},
 'cpu_gpu':'CUDA_VISIBLE_DEVICES=-1 during builds; CPU document processing only; no GPU framework imports or device use.',
 'data_version':'Protected 2.42 source tree plus exact insertion and five references; six retained primary authority/report sources.',
 'seeds':'N/A: deterministic document work','wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),'builds':sum(r['wall_seconds'] for r in builds),'checks':c['wall_seconds']},
 'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in inputs},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'pdf':str((CAND/'accounting-product-proposal.pdf').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],
 'manuscript':'Version 2.43','pages':c['pages'],'readiness':'not_ready','runtime':'held','next_plan':plans[-1]}
assert sha(BASE/'accounting-product-proposal.pdf')==b['pdf_sha256']
save('run-manifest.json',manifest)
for rel,digest in (manifest['input_hashes']|manifest['artifact_hashes']).items():assert sha(ROOT/rel)==digest
save('completion.json',{'status':'bounded manuscript integration complete','integration_checks':c['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(manifest['artifact_hashes']),
 'manuscript':'Version 2.43','pdf_sha256':c['pdf_sha256'],'pages':c['pages'],'readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'integration_checks':c['passed'],'bound_artifacts':len(manifest['artifact_hashes']),'candidate':'2.43','pages':c['pages']}))
