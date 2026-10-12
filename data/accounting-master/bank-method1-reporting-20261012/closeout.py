"""Bind the bounded reporting inquiry without regenerating closed work."""
import datetime
import json
import platform
import subprocess
import sys
from record_evidence import ROOT, OUT, sha, save

assert not (OUT/'completion.json').exists()
c=json.loads((OUT/'source-checks.json').read_text());assert not c['failed']
b=json.loads((OUT/'baseline.json').read_text())
for row in json.loads((OUT/'controls-after.json').read_text()):
    assert sha(ROOT/row['live'])==row['sha256']==sha(ROOT/row['snapshot'])
plans=['docs/plans/accounting-bank-method1-reporting-20261012.md','docs/plans/accounting-bank-reporting-integration-20261012.md']
pdf=ROOT/'docs/design/proposal/manuscript-capital-recognition-20261012/accounting-product-proposal.pdf'
assert sha(pdf)==b['pdf_sha256']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc)
transfers=json.loads((OUT/'access-receipts.json').read_text())+json.loads((OUT/'denominator-receipts.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
 'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['record_evidence.py','update_controls.py','closeout.py']],
 'source_commands':['access-receipts.json','denominator-receipts.json','search-access.json'],
 'reading':'Selected FR Y-15 pages and both complete denominator notices; raw source bytes, extracts, coordinates and ten inspected renders retained.',
 'environment':{'python':sys.executable,'version':platform.python_version(),'libraries':['PyMuPDF','BeautifulSoup']},
 'cpu_gpu':'CPU document processing only; no GPU framework imports, device queries or use.',
 'data_version':'Four official publications and discovery responses bound by exact hashes; no completeness or current-law claim.',
 'seeds':'N/A: deterministic documentary work',
 'wall_seconds':{'session_elapsed':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                 'source_checks':c['wall_seconds'],'recorded_curl_transfers':sum(r['transfer']['time_total'] for r in transfers)},
 'timing_note':'Elapsed time includes session recovery and review. Search transport records have separate durations; initial broad query duration preserved in search-access.json.',
 'input_hashes':{str(pdf.relative_to(ROOT)):sha(pdf)},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'manuscript':'Version 2.42 unchanged','readiness':'not_ready','runtime':'held','next_plan':plans[-1]}
save('run-manifest.json',manifest)
for rel,digest in (manifest['input_hashes']|manifest['artifact_hashes']).items():assert sha(ROOT/rel)==digest
save('completion.json',{'status':'bounded source inquiry complete','source_checks':c['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(manifest['artifact_hashes']),
 'manuscript':'Version 2.42 unchanged','readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'bound_artifacts':len(manifest['artifact_hashes']),'next':plans[-1]}))
