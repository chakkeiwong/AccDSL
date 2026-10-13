"""Freeze scoped evidence and current controls before the explicit-path commit."""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
CAND=ROOT/'docs/design/proposal/manuscript-munich-new-contracts-20261013'
PLAN='docs/plans/accounting-munich-new-contracts-20261013.md'
NEXT='docs/plans/accounting-munich-measurement-bridge-20261013.md'
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda name,data:(UNIT/name).write_text(json.dumps(data,indent=2)+'\n')
base=json.loads((UNIT/'baseline.json').read_text())
digest=sha(CAND/'accounting-product-proposal.pdf')
checks={};counts={};controls=[]
for name in ['source-calculation-checks.json','manuscript-checks.json']:
    r=json.loads((UNIT/name).read_text());checks[name]=not r['failed'];counts[name]=r['passed']
for item in base['controls']:
    p=ROOT/item['live'];q=UNIT/'after'/item['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    controls.append({'live':item['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
    checks['control:'+item['live']]=digest in p.read_text() and Path(NEXT).name in p.read_text()
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT,text=True)
checks['unrelated_index_unchanged']=index==(UNIT/'unrelated-index-before.txt').read_text()
checks['next_plan_exists']=(ROOT/NEXT).is_file()
checks['authored_whitespace']=all(line==line.rstrip() for name in ['derivation-and-review.md','result.md','munich-addition.tex'] for line in (UNIT/name).read_text().splitlines())
assert all(checks.values()),[k for k,v in checks.items() if not v]
end=datetime.datetime.now(datetime.timezone.utc)
files={str(p.relative_to(ROOT)):sha(p) for p in sorted(UNIT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['run-manifest.json','completion.json','closeout-checks.json']}
manifest={'unit':UNIT.name,'plan':PLAN,'plan_sha256':sha(ROOT/PLAN),'next_plan':NEXT,'next_plan_sha256':sha(ROOT/NEXT),'result':str((UNIT/'result.md').relative_to(ROOT)),
          'git_commit_at_start':base['git_commit'],'started_at':base['started_at'],'finished_at':end.isoformat(),'elapsed_wall_seconds':(end-datetime.datetime.fromisoformat(base['started_at'])).total_seconds(),
          'environment':{'interpreter':sys.executable,'python_version':sys.version,'conda_environment':'tfgpu (arithmetic/document libraries only)','CPU':'CPU-only','GPU':'Intentionally hidden for all LuaLaTeX builds with CUDA_VISIBLE_DEVICES=-1; no GPU framework imported or initialized','random_seeds':'N/A: deterministic authored calculations','data_version':'Retained Munich Re 2023 report identified by baseline hash; reported values and hypothetical rounding witness distinguished'},
          'commands':['python3 '+str((UNIT/'check_calculations.py').relative_to(ROOT)),'python3 '+str((UNIT/'build_candidate.py').relative_to(ROOT)),'python3 '+str((UNIT/'check_manuscript.py').relative_to(ROOT)),'python3 '+str((UNIT/'closeout.py').relative_to(ROOT))],
          'build_runs':[json.loads((UNIT/f).read_text()) for f in ['initial-build/build-run.json','build-run.json'] if (UNIT/f).exists()],
          'baseline':base,'controls_after':controls,'candidate_files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(CAND.rglob('*')) if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf'}},'artifact_hashes':files,'readiness':'not_ready','human_acceptance':'pending'}
save('run-manifest.json',manifest)
save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':[]})
save('completion.json',{'completed_at':end.isoformat(),'scope':'Munich Re actual acquisition disclosures and Version 2.58 integration complete','readiness':'not_ready','check_counts':{**counts,'closeout':sum(checks.values())},'manifest_sha256':sha(UNIT/'run-manifest.json'),'pdf_sha256':digest,'next_plan':NEXT})
print(json.dumps({'closeout_passed':sum(checks.values()),'unrelated_staged_entries':len(index.splitlines()),'pdf_sha256':digest}))
