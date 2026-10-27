"""One-time evidence recording and read-only deterministic replay."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import os
import platform
import subprocess
import sys
import time
from compare import compare

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL=HERE.relative_to(ROOT).as_posix()
PRIOR=HERE.parent/'company-functions-20261025'
PLAN='docs/plans/accounting-company-function-text-20261025.md'
NEXT='docs/plans/accounting-company-function-text-integration-20261025.md'

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))

def main():
    record=sys.argv[1:]==['--record']
    assert sys.argv[1:] in ([],['--record'])
    assert not record or not (HERE/'manifest.json').exists(),'already recorded'
    begin=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    lock=json.loads((PRIOR/'source-lock.json').read_text())
    for p in PRIOR.iterdir():
        if p.is_file():lock[p.relative_to(ROOT).as_posix()]=sha(p)
    source=HERE.parent/'company-functions-integration-20261025'
    for name,h in json.loads((source/'run-manifest.json').read_text())['output_artifacts'].items():
        assert name not in lock or lock[name]==h
        lock[name]=h
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    for name,h in lock.items():check('protected:'+name,sha(ROOT/name)==h)
    commands={
        'focused':[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_company_function_text_v1.py'],
        'typed_regression':[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_company_functions_v1.py'],
        'expression_regression':[sys.executable,'-B',str(HERE.parent/'company-expressions-20261023/verify.py')]
    }
    observations={}
    for key,cmd in commands.items():
        t=time.monotonic();r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        observations[key]={'command':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr}
        check(key+':returncode',r.returncode==0)
        if key in ['focused','typed_regression']:
            count=18 if key=='focused' else 23
            check(key+':methods','Ran '+str(count)+' tests' in r.stderr and r.stderr.rstrip().endswith('OK'))
        else:
            summary=json.loads(r.stdout)
            check('expression_regression:79_checks',summary['passed'] and summary['checks']==79 and not summary['recorded'])
    comparison=compare();checks.extend(comparison['checks'])
    for name,h in lock.items():check('unchanged:'+name,sha(ROOT/name)==h)
    for name in ['scripts/company_function_text_v1.py','tests/test_company_function_text_v1.py',PLAN,NEXT]:lock[name]=sha(ROOT/name)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'control-before' not in p.parts and p.name not in ['manifest.json','source-lock.json','checks.json','comparison.json','test-observation.json','control-refresh.json','finish.py']:
            lock[p.relative_to(ROOT).as_posix()]=sha(p)
    if record:dump(HERE/'source-lock.json',lock)
    else:
        recorded=json.loads((HERE/'source-lock.json').read_text())
        check('source_lock_exact',lock==recorded)
        check('comparison_replayed',comparison==json.loads((HERE/'comparison.json').read_text()))
    for name,h in lock.items():check('sealed:'+name,sha(ROOT/name)==h)
    failures=[x['name'] for x in checks if not x['passed']]
    if failures:
        dump(HERE/('failure-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json'),{'checks':checks,'observations':observations})
        raise AssertionError(failures)
    summary={'passed':True,'checks':len(checks),'focused_methods':18,'typed_regression_methods':23,'expression_regression_checks':79,'comparison_checks':285,'cases':6,'protected_files':len(lock)}
    if record:
        dump(HERE/'checks.json',dict(summary,named_checks=checks))
        dump(HERE/'comparison.json',comparison);dump(HERE/'test-observation.json',observations)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-begin,
            'git_commit_recorded':'03fea070f089821f4759e49a4466a3399b7fc078',
            'command':'python3 -B '+REL+'/verify.py --record','environment':platform.python_version(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no numerical GPU framework imported',
            'random_seeds':'N/A: exact deterministic checks','data_version':'source-lock.json plus saved authored synthetic paths',
            'plan':PLAN,'result':REL+'/result.md','source_lock_sha256':sha(HERE/'source-lock.json'),
            'summary':summary,'outputs':['checks.json','comparison.json','test-observation.json']})
    print(json.dumps(summary))

if __name__=='__main__':main()
