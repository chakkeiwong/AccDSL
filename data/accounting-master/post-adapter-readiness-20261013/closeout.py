"""Close an author assessment without promoting readiness or changing frozen state."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
assert not (U/'completion.json').exists(),'Completed assessment'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());a=json.loads((U/'assessment.json').read_text());checks={}
checks['assessment_checks']=not json.loads((U/'integrity-checks.json').read_text())['failed']
checks['not_ready']=a['status']=='not_ready' and not a['ready'] and not a['implementation_enabled']
x=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['unrelated_index']=x==(U/'unrelated-index-before.txt').read_bytes();checks['100_entries']=len(x.splitlines())==100
for p in b['controls']:
    checks['snapshot:'+p['live']]=sha(R/p['snapshot'])==p['sha256'];t=(R/p['live']).read_text()
    checks['current:'+p['live']]='2.69' in t and 'not_ready' in t and 'accounting-apple-inline-occurrences-20261013.md' in t
for p,h in b['frozen'].items():checks['frozen:'+p]=sha(R/p)==h
checks['next_plan']=(R/a['next_plan']).is_file()
failed=[k for k,v in checks.items() if not v];save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed});assert not failed,failed
now=datetime.now(timezone.utc)
manifest={'git_commit':b['git_commit'],'command':['CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/post-adapter-readiness-20261013/build_assessment.py','CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/post-adapter-readiness-20261013/closeout.py'],'environment':sys.executable,'cpu_gpu':'CPU metadata processing; GPU intentionally hidden; no framework import','data_version':'post-awards53-row assessment plus source-bound2.68/2.69 evidence','random_seeds':'N/A deterministic metadata review','started_at':b['started_at'],'finished_at':now.isoformat(),'wall_seconds':(now-datetime.fromisoformat(b['started_at'])).total_seconds(),'wall_scope':'elapsed review work, not benchmark','plan':'docs/plans/accounting-post-adapter-readiness-20261013.md','result':str((U/'result.md').relative_to(R)),'outputs':{str(p.relative_to(R)):sha(p) for p in U.rglob('*') if p.is_file() and p.name not in {'completion.json','run-manifest.json'}},'controls':{p['live']:sha(R/p['live']) for p in b['controls']}}
save('run-manifest.json',manifest);save('completion.json',{'status':'complete_author_delta_assessment','readiness':'not_ready','manifest_sha256':sha(U/'run-manifest.json'),'next_plan':a['next_plan']});print(json.dumps({'passed':sum(checks.values()),'failed':failed,'staged_entries':100}))
