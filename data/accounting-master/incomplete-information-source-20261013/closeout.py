"""Close source-specific discovery without claiming technical admission."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
assert not (U/'completion.json').exists(),'Completed inquiry'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());checks={}
checks['source_checks']=not json.loads((U/'checks.json').read_text())['failed']
x=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['index_preserved']=x==(U/'unrelated-index-before.txt').read_bytes();checks['100_entries']=len(x.splitlines())==100
nextplan='docs/plans/accounting-certain-answer-semantics-20261013.md'
for p in b['controls']:
    checks['snapshot:'+p['live']]=sha(R/p['snapshot'])==p['sha256']
    t=(R/p['live']).read_text();checks['current:'+p['live']]='2.70' in t and 'not_ready' in t and Path(nextplan).name in t
for group in ['candidate_files','frozen','dependencies']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
checks['next_plan']=(R/nextplan).is_file()
failed=[k for k,v in checks.items() if not v];save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed});assert not failed,failed
now=datetime.now(timezone.utc);manifest={'git_commit':b['git_commit'],'commands':['Four exact curl/subprocess commands in sources/*.receipt.json','CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/incomplete-information-source-20261013/check_inquiry.py','CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/incomplete-information-source-20261013/closeout.py'],'environment':sys.executable,'cpu_gpu':'CPU-only source/HTML/metadata inspection; GPU intentionally hidden; no framework import','data_version':'1984 target paper; four2026 discovery responses; no full text acquired','random_seeds':'N/A deterministic source inquiry','started_at':b['started_at'],'finished_at':now.isoformat(),'wall_seconds':(now-datetime.fromisoformat(b['started_at'])).total_seconds(),'wall_scope':'elapsed source investigation, not benchmark','plan':'docs/plans/accounting-incomplete-information-source-20261013.md','result':str((U/'result.md').relative_to(R)),'outputs':{str(p.relative_to(R)):sha(p) for p in U.rglob('*') if p.is_file() and p.name not in {'completion.json','run-manifest.json'}},'controls':{p['live']:sha(R/p['live']) for p in b['controls']}}
save('run-manifest.json',manifest);save('completion.json',{'status':'complete_bounded_discovery_source_blocked','readiness':'not_ready','manifest_sha256':sha(U/'run-manifest.json'),'next_plan':nextplan});print(json.dumps({'passed':sum(checks.values()),'failed':failed,'staged_entries':100}))
