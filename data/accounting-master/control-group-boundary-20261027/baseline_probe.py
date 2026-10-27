"""Small baseline validity check; no predecessor writer is executed."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import importlib.util,json,os,platform,subprocess,time
H=Path(__file__).resolve().parent;R=H.parents[2]
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
out=H/'baseline-attempt-01';out.mkdir(exist_ok=False);start=time.monotonic()
spec=importlib.util.spec_from_file_location('group_examples',R/'data/accounting-master/group-period-report-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
base=ex.fixture();before=deepcopy(base);good=ex.group.report(base)
assert good['status']=='period_reported' and base==before
assert good['cash_flows']['opening_cash']=='200/1' and good['cash_flows']['closing_cash']=='220/1'
assert good['equity']==dict(opening='200/1',direct_movements='0/1',profit='20/1',closing='220/1')
changed=deepcopy(base);changed['closing']['world']['control_edges'][0]['start']='2025-02-01'
bad=ex.group.report(changed);assert bad['status']=='invalid' and bad['reason']=='period_world:control_edges'
partial=deepcopy(base)
for side in ['opening','closing']:partial[side]['world']['control_edges'][0]['ownership_fraction']='3/4'
nci=ex.group.report(partial);assert nci['status']=='invalid' and nci['reason']=='opening_worksheet:full_ownership_only'
for result in [good,bad,nci]:assert all(result[key] is False for key in ex.group.FLAGS)
for name,request,result in [('unchanged',base,good),('changed-control',changed,bad),('partial-ownership',partial,nci)]:
    (out/(name+'.json')).write_text(json.dumps(dict(request=request,result=result),indent=2)+'\n')
files=[Path(__file__),H/'contract.md',R/'docs/plans/accounting-control-group-boundary-20261027.md',Path(ex.__file__),Path(ex.group.__file__),Path(ex.group.composition.__file__)]
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
(out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
manifest=dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R)),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-control-group-boundary-20261027.md',data_version='source-lock.json',result='baseline-attempt-01/verification.json')
(out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(status='PASS',cases=3,unchanged_report='period_reported',changed_control_refusal=bad['reason'],partial_ownership_refusal=nci['reason'],admission=False)
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
