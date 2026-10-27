"""Record once; subsequent verification only reads sealed evidence."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import platform
import re
import subprocess
import sys
import time
from examples import compare

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PLAN='docs/plans/accounting-declared-operating-cycle-20261025.md'
NEXT='docs/plans/accounting-declared-operating-cycle-integration-20261025.md'
REL=HERE.relative_to(ROOT).as_posix()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')


def main():
    record=sys.argv[1:]==['--record'];assert sys.argv[1:] in ([],['--record'])
    assert not record or not (HERE/'manifest.json').exists(),'already recorded'
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat();os.environ['CUDA_VISIBLE_DEVICES']='-1'
    prior=HERE.parent/'declared-company-text-coverage-20261025'
    lock=json.loads((prior/'source-lock.json').read_text())
    for p in prior.iterdir():
        if p.is_file():lock[p.relative_to(ROOT).as_posix()]=sha(p)
    checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    for name,h in lock.items():check('predecessor:'+name,sha(ROOT/name)==h)
    observations={};counts={}
    for name,pattern,want in [('focused','test_declared_operating_methods_v1.py',17),('program_regression','test_declared_company_program_v1.py',19),('text_regression','test_declared_company_text_v1.py',19)]:
        cmd=[sys.executable,'-B','-m','unittest','discover','-s','tests','-p',pattern]
        t=time.monotonic();run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        observations[name]={'command':cmd,'returncode':run.returncode,'wall_seconds':time.monotonic()-t,'stdout':run.stdout,'stderr':run.stderr}
        found=re.search(r'Ran (\d+) tests',run.stderr);counts[name]=int(found[1]) if found else 0
        check(name+':tests',run.returncode==0 and counts[name]==want and run.stderr.rstrip().endswith('OK'))
    comparison=compare();rows=comparison['cases']
    for row in rows:
        for key,value in row['checks'].items():check(row['case']+':'+key,value)
    # Includes loaded test/comparator transitive sources, not only six core imports.
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            p=Path(path).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix=='.py':lock[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ['scripts/declared_operating_methods_v1.py','tests/test_declared_operating_methods_v1.py',PLAN,NEXT]:lock[name]=sha(ROOT/name)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.name not in ['manifest.json','source-lock.json','checks.json','comparison.json','test-observation.json','progress.md','control-refresh.json','finish.py']:
            lock[p.relative_to(ROOT).as_posix()]=sha(p)
    if not record:
        check('source_lock_exact',lock==json.loads((HERE/'source-lock.json').read_text()))
        check('native_comparison_replay',comparison==json.loads((HERE/'comparison.json').read_text()))
    for name,h in lock.items():check('sealed:'+name,sha(ROOT/name)==h)
    failures=[x['name'] for x in checks if not x['passed']];assert not failures,failures[:10]
    summary={'passed':True,'checks':len(checks),'methods':counts,'cases':len(rows),
             'comparison_checks':sum(len(x['checks']) for x in rows),'protected_files':len(lock)}
    if record:
        dump(HERE/'source-lock.json',lock);dump(HERE/'comparison.json',comparison)
        dump(HERE/'checks.json',{**summary,'named_checks':checks});dump(HERE/'test-observation.json',observations)
        commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        import importlib.metadata
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-start,'git_commit_recorded':commit,
             'command':'python3 -B '+REL+'/verify.py --record','environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema')},
             'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported','random_seeds':'N/A: deterministic exact checks',
             'data_version':'source-lock.json and authored synthetic examples','plan':PLAN,'result':REL+'/result.md',
             'source_lock_sha256':sha(HERE/'source-lock.json'),'summary':summary,
             'worktree':'Inherited unrelated changes preserved; exact candidate identities in source lock',
             'outputs':['checks.json','comparison.json','test-observation.json','source-lock.json']})
    print(json.dumps(summary))


if __name__=='__main__':main()
