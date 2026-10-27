from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'docs/design/proposal/manuscript-debt-reading-v553-20261027';T=R/'docs/design/proposal/manuscript-release-v553r1-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (D/'package-record.json').exists()
v=json.loads((D/'verification.json').read_text());assert v['pass']
review=json.loads((D/'rendered-review.json').read_text());assert len(review['pages'])==19
for row in review['pages']:assert sha(T/(row['volume']+'.pdf'))==row['pdf_sha256']
manifest=json.loads((B/'package-manifest.json').read_text())
manifest.update(candidate='5.53-R1;not_ready',manifest_self_hash='Stored outside this package in release-pursuit-20261027/opening-repair/package-record.json')
manifest['files'].append({'path':'reading-guide.tex','role':'manuscript_source','redistribution':'unreviewed_internal_only'})
for row in manifest['files']:
 p=T/row['path'];assert p.is_file() and not p.is_symlink();row.update(sha256=sha(p),bytes=p.stat().st_size)
manifest['files'].sort(key=lambda x:x['path'])
(T/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=subprocess.run(['python3','-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stdout+p.stderr
record={'candidate':'5.53-R1;not_ready','manifest_sha256':sha(T/'package-manifest.json'),'predecessor_manifest_sha256':sha(B/'package-manifest.json'),'files':len(manifest['files']),'verification':json.loads(p.stdout),'source_verification_sha256':sha(D/'verification.json'),'rendered_review_sha256':sha(D/'rendered-review.json'),'timestamp_utc':datetime.now(timezone.utc).isoformat(),'full_evidence_closure':False,'rights':'Internal review only; existing dispositions preserved; no public redistribution clearance'}
(D/'package-record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
