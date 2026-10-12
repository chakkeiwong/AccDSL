"""Close a source-only unit with preserved controls and external inputs."""
import datetime
import json
import platform
import subprocess
import sys
import time
from record_conditions import OUT, ROOT, sha, save

start=time.monotonic();assert not (OUT/'completion.json').exists()
checks=json.loads((OUT/'source-checks.json').read_text());assert not checks['failed']
baseline=json.loads((OUT/'baseline.json').read_text())
for row in json.loads((OUT/'controls-after.json').read_text()):
    assert sha(ROOT/row['live'])==row['sha256']==sha(ROOT/row['snapshot'])
plans=['docs/plans/accounting-bank-method1-surcharge-20261012.md','docs/plans/accounting-bank-method1-reporting-20261012.md']
pdf=ROOT/'docs/design/proposal/manuscript-capital-recognition-20261012/accounting-product-proposal.pdf'
assert sha(pdf)==baseline['pdf_sha256']
external=[pdf, ROOT/'data/accounting-master/bank-capital-payout-dependencies-20261012/sources/ecfr-2026-04-01-3.11.xml']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans]
receipts=json.loads((OUT/'access-receipts.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'started_utc':baseline['started_utc'],'closed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'plans':plans,'scope_extension':str((OUT/'archive-definition-audit.md').relative_to(ROOT)),
 'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['record_conditions.py','update_controls.py','closeout.py']],
 'source_access':str((OUT/'access-receipts.json').relative_to(ROOT)),
 'normalization':'Inline Python/lxml itertext and whitespace collapse; complete paragraph inventories plus footnotes/CITA preserved in sections.json.',
 'environment':{'python':sys.executable,'version':platform.python_version(),'libraries':['lxml','PyMuPDF']},
 'cpu_gpu':'CPU document processing only; no GPU framework imports, queries or device use.',
 'data_version':'Five admitted eCFR responses, excluded 429, two annual-CFR editions and retained April 3.11; exact hashes bound.',
 'seeds':'N/A: deterministic documentary work',
 'wall_seconds':{'source_transfers':sum(r['transfer']['time_total'] for r in receipts)+sum(json.loads((OUT/n).read_text())['transfer']['time_total'] for n in ['archive-receipt.json','archive-2026-receipt.json']),'source_checks':checks['wall_seconds'],'closeout':time.monotonic()-start},
 'timing_note':'Transport timestamps mark batch submission; curl durations record individual transfers.',
 'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in external},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'manuscript':'Version 2.42 unchanged','readiness':'not_ready','runtime':'held','next_plan':plans[-1]}
save('run-manifest.json',manifest)
for rel,digest in (manifest['input_hashes']|manifest['artifact_hashes']).items():assert sha(ROOT/rel)==digest
save('completion.json',{'status':'bounded source-only unit complete','source_checks':checks['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(manifest['artifact_hashes']),
 'manuscript':'Version 2.42 unchanged','readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'source_checks':checks['passed'],'bound_artifacts':len(manifest['artifact_hashes']),'candidate':'2.42 unchanged'}))
