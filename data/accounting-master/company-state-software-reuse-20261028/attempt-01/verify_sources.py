"""Verify retained software-source identity, not external runtime correctness."""
import argparse
import base64
from datetime import datetime,timezone
from hashlib import sha1,sha256
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
PLAN='docs/plans/company-state-software-reuse-review-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
 out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();checks=[];paths=[Path(__file__),ROOT/PLAN]
 def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
 tools=ROOT/'docs/design/research/tools.json';paths.append(tools)
 records=json.loads(tools.read_text())['records'];selected=[r for r in records if r['repository'] in ['Arelle/Arelle','lballabio/QuantLib','Z3Prover/z3']]
 ck('three retained repository records',len(selected),3)
 for r in selected:
  for name,expected in r['sha256'].items():
   p=ROOT/name;paths.append(p);ck('inherited snapshot/'+name,sha256(p.read_bytes()).hexdigest(),expected)
 folder=ROOT/'docs/design/proposal/methods/preparation-20261005-v1/03-adapters'
 register=folder/'source-register.json';paths.append(register)
 source=json.loads(register.read_text())['sources']
 selected_arelle=[]
 for r in source:
  if r['repository']=='Arelle/Arelle' and r['upstream_path'] in ['arelle/ModelInstanceObject.py','arelle/ValidateDuplicateFacts.py','arelle/ValidateXbrlCalcs.py','arelle/api/Session.py','arelle/RuntimeOptions.py','pyproject.toml','LICENSE.md']:
   p=folder/r['path'];paths.append(p);ck('commit-pinned/'+r['upstream_path'],sha256(p.read_bytes()).hexdigest(),r['sha256']);selected_arelle.append(r)
 ck('seven selected Arelle source dependencies',len(selected_arelle),7)
 ck('single retained Arelle commit',sorted({r['commit'] for r in selected_arelle}),['01f6a4656c2c6551d2f05f31c9d74366d133ee7e'])
 old=ROOT/'docs/design/research/software/Arelle_Arelle-arelle_ModelInstanceObject.py'
 pinned=folder/'sources/upstream/arelle/arelle__ModelInstanceObject.py'
 ck('old and commit-linked Arelle bodies identical',old.read_bytes()==pinned.read_bytes(),True)
 actus=ROOT/'docs/design/research/software/actus-interface-20261023';blobs=[]
 for filename,response in [('EventController.java','controller-blob.json'),('TimeSeries.java','timeseries-blob.json'),('Event.java','event-blob.json'),('build.gradle.kts','build-blob.json')]:
  p=actus/filename;j=actus/response;paths.extend([p,j]);data=p.read_bytes();meta=json.loads(j.read_text())
  expected=base64.b64decode(meta['content']);identity=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  ck('ACTUS blob bytes/'+filename,data==expected,True);ck('ACTUS Git blob/'+filename,identity,meta['sha'])
  blobs.append(dict(path=str(p.relative_to(ROOT)),git_blob=meta['sha']))
 tree=actus/'service-tree.json';paths.append(tree);tree_data=json.loads(tree.read_text())
 ck('ACTUS service tree identity',tree_data['sha'],'7293157a7f272925dbce68b5a037d2e23c585c9e')
 lookup={r['sha'] for r in tree_data['tree']}
 for row in blobs:ck('ACTUS tree contains/'+row['path'],row['git_blob'] in lookup,True)
 previous=[('company-state-context-failure-20261028/attempt-02/verification.json','pass'),('company-state-gross-equity-history-20261028/attempt-01/verification.json','pass'),('company-state-persistent-rate-failures-20261028/attempt-01/verification.json','pass')]
 for name,expected in previous:
  p=ROOT/'data/accounting-master'/name;paths.append(p);ck('retained local evidence/'+name,json.loads(p.read_text())['status'],expected)
 pam=ROOT/'data/accounting-master/literature-closure-20261026/actus-fixture-results.json';paths.append(pam);r=json.loads(pam.read_text());ck('PAM arithmetic retained',r['status'],'PASS');ck('PAM scope remains non-runtime','Not runtime conformance' in r['scope'],True)
 fixture=ROOT/'data/accounting-master/literature-closure-20261026/sources/actus-tests-tests_actus-tests-pam.json';paths.append(fixture);ck('PAM fixture source hash',sha256(fixture.read_bytes()).hexdigest(),r['source_sha256'])
 for n in ['scripts/rational_solver_v1.py','docs/design/research/actus-interface-boundary-20261023.md','docs/design/proposal/methods/selected-reuse-20261015.md','docs/design/proposal/methods/software-reuse-methods-v1.md','data/accounting-master/literature-closure-20261026/software-audit.md']:
  paths.append(ROOT/n)
 import z3
 runtime=dict(solver_version=z3.get_version_string(),distribution_version=importlib.metadata.version('z3-solver'),import_path=z3.__file__,environment_lock=False)
 hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
 failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),source_files=len(hashes),failed=failed,external_runtime_executed=False,source_review_only=True)
 manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only hashes/JSON; solver import for installed version; no accelerators',random_seeds='N/A deterministic source integrity',data_version='Retained02/05/23/26October source records; no current-version claim',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes)
 for name,obj in [('verification',v),('checks',checks),('run-manifest',manifest),('installed-solver',runtime),('actus-blobs',blobs),('arelle-selected-records',selected_arelle)]:dump(out/(name+'.json'),obj)
 (out/'verify_sources.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

