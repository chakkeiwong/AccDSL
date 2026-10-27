"""Record the completed documentary run once, without rewriting evidence."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def main():
 target=HERE/'run-manifest.json'
 assert not target.exists(),'Do not replace a run manifest'
 attempt=HERE/'attempt-03'
 report=json.loads((attempt/'verification-01.json').read_text())
 assert report['failures']==0 and report['total']==1693
 packet=json.loads((attempt/'portable-exchanges.json').read_text())
 assert sha(attempt/'portable-exchanges.json')==report['packet_sha256']
 lock=json.loads((HERE/'predecessor-lock.json').read_text())
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
 assert commit==lock['git_commit'] and hashlib.sha256(index).hexdigest()==lock['index_sha256']
 assert len(index.splitlines())==lock['index_entries']==100
 for n,row in packet['input_snapshots'].items():
  assert sha(attempt/'inputs'/n)==row['sha256']==sha(ROOT/row['path'])
 validations=[]
 for a in (HERE/'attempt-02',attempt):
  p=a/'verification-01.json';v=json.loads(p.read_text())
  validations.append(dict(command='python3 '+rel(HERE/'verify_exchanges.py')+' '+a.name,artifact=rel(p),sha256=sha(p),checks=v['total'],failed=v['failures'],wall_seconds=v['wall_seconds'],packet_sha256=v['packet_sha256'],verifier_sha256=sha(a/'inputs/verify_exchanges.py')))
 files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=target]
 plan=ROOT/'docs/plans/accounting-bank-prudential-query-exchanges-20261015.md'
 sibling=HERE.parent/'p3b3-coverage-reconciliation.md'
 files.extend([plan,sibling])
 build=json.loads((attempt/'build-run.json').read_text())
 m=dict(date='2026-10-15',purpose='deterministic_documentary_specification_not_product_execution',git_commit=commit,index_sha256=lock['index_sha256'],staged_entries=100,
  environment=dict(python=platform.python_version(),jsonschema=importlib.metadata.version('jsonschema'),conda=os.environ.get('CONDA_DEFAULT_ENV','N/A: python3 on PATH'),cpu_only=True,CUDA_VISIBLE_DEVICES=os.environ.get('CUDA_VISIBLE_DEVICES','unset'),gpu='no GPU detection, framework or device use',random_seeds='N/A: exact deterministic rational examples',data_version='authored synthetic premises and hash-bound retained sources'),
  plan=rel(plan),result=rel(HERE/'result.md'),final_attempt=attempt.name,
  build=dict(command='python3 '+rel(HERE/'build_exchanges.py'),artifact=rel(attempt/'portable-exchanges.json'),wall_seconds=build['wall_seconds']),
  validations=validations,inputs=packet['input_snapshots'],outputs={rel(p):sha(p) for p in sorted(files)},
  preservation=dict(original_inputs=204,predecessor_files=len(lock['predecessor_files']),HEAD='unchanged',index='unchanged',lock_sha256=sha(HERE/'predecessor-lock.json')),
  limits=['Exact conditional documentary examples only','No actual-law/eligibility/calibration/payout/runtime acceptance','Original requirements and full not_ready assessment unchanged'])
 with target.open('x') as f:f.write(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=rel(target),sha256=sha(target),artifacts=len(files),checks=report['total'],failures=report['failures'])))
if __name__=='__main__':main()
