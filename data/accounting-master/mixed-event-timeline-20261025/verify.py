"""Record once, then replay without changing protected evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import os
import platform
import re
import subprocess
import sys
import time
from compare import compare

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PRIOR=HERE.parent/'state-decision-schedule-coverage-20261025'
PLAN='docs/plans/accounting-mixed-event-timeline-20261025.md'
NEXT='docs/plans/accounting-mixed-event-timeline-integration-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,value):p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    record=sys.argv[1:]==['--record'];assert sys.argv[1:] in ([],['--record'])
    assert not record or not (HERE/'manifest.json').exists(),'already recorded'
    begin=time.monotonic();started=datetime.now(timezone.utc).isoformat();os.environ['CUDA_VISIBLE_DEVICES']='-1'
    lock=json.loads((PRIOR/'source-lock.json').read_text())
    for p in PRIOR.iterdir():
        if p.is_file():lock[p.relative_to(ROOT).as_posix()]=sha(p)
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    for name,h in lock.items():check('protected:'+name,sha(ROOT/name)==h)
    observations={};counts={}
    for key,pattern in [('focused','test_mixed_event_timeline_v1.py'),('scheduler_regression','test_state_decision_schedule_v1.py')]:
        command=[sys.executable,'-B','-m','unittest','discover','-s','tests','-p',pattern]
        t=time.monotonic();r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        observations[key]={'command':command,'returncode':r.returncode,'wall_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr}
        check(key+':returncode',r.returncode==0)
        match=re.search(r'Ran (\d+) tests',r.stderr);counts[key]=int(match[1]) if match else 0
        check(key+':methods',counts[key]=={'focused':17,'scheduler_regression':18}[key] and r.stderr.rstrip().endswith('OK'))
    comparison=compare();checks.extend(comparison['checks'])
    for name,h in lock.items():check('unchanged:'+name,sha(ROOT/name)==h)
    for name in ['scripts/mixed_event_timeline_v1.py','tests/test_mixed_event_timeline_v1.py',PLAN,NEXT]:lock[name]=sha(ROOT/name)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'control-before' not in p.parts and p.name not in ['manifest.json','source-lock.json','checks.json','comparison.json','test-observation.json','control-refresh.json','finish.py','progress.md']:
            lock[p.relative_to(ROOT).as_posix()]=sha(p)
    if record:dump(HERE/'source-lock.json',lock)
    else:
        check('source_lock_exact',lock==json.loads((HERE/'source-lock.json').read_text()))
        check('comparison_replayed',comparison==json.loads((HERE/'comparison.json').read_text()))
    for name,h in lock.items():check('sealed:'+name,sha(ROOT/name)==h)
    failures=[x['name'] for x in checks if not x['passed']]
    assert not failures,failures
    summary={'passed':True,'checks':len(checks),'methods':counts,'comparison_checks':len(comparison['checks']),'cases':len(comparison['cases']),'protected_files':len(lock)}
    if record:
        dump(HERE/'checks.json',dict(summary,named_checks=checks));dump(HERE/'comparison.json',comparison);dump(HERE/'test-observation.json',observations)
        commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-begin,'git_commit_recorded':commit,
            'worktree':'Contains inherited unrelated changes; exact candidate sources are bound by source-lock.json',
            'command':'python3 -B '+REL+'/verify.py --record','environment':platform.python_version(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no numerical GPU framework imported','random_seeds':'N/A: exact deterministic checks',
            'data_version':'source-lock.json and saved authored synthetic scenarios','plan':PLAN,'result':REL+'/result.md',
            'source_lock_sha256':sha(HERE/'source-lock.json'),'summary':summary,'outputs':['checks.json','comparison.json','test-observation.json']})
    print(json.dumps(summary))

if __name__=='__main__':main()
