"""Freeze the exact current candidate and original obligations for a fresh audit."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-production-cost-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'baseline.json').exists()
assert sha(BASE/'accounting-product-proposal.pdf')=='46d17f8440c325353f6a7e250897a1629e5f08b60107d7104ec7bf30c04bd17c'
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
obligations=ROOT/'data/accounting-master/remaining-phases-audit-20261014/coverage-map.json'
assessment=ROOT/'data/accounting-master/post-certainty-readiness-20261013/assessment.json'
records=json.loads(obligations.read_text())['records'];assert len(records)==53
sources=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark','.pdf'])
contract_paths=[ROOT/'docs/design/proposal/architecture/initial-profile-v1.md']
sources+=contract_paths
result={'candidate_version':'2.93','pdf':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),'pdf_sha256':sha(BASE/'accounting-product-proposal.pdf'),'readiness':'not_ready','scope':'current evidence audit; no historical assessment rewritten','source_manifest':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sources],'original_obligations':{'path':str(obligations.relative_to(ROOT)),'sha256':sha(obligations),'records':records},'prior_assessment':{'path':str(assessment.relative_to(ROOT)),'sha256':sha(assessment),'version':'2.72'},'unrelated_index_sha256':hashlib.sha256(index).hexdigest(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
(OUT/'baseline.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({'version':'2.93','obligations':len(records),'protected_files':len(sources),'index_preserved':True}))
