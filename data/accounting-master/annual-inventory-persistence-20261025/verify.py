"""Deterministic unweighted annual scenario-family evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from fractions import Fraction as Q
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from examples import m
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def canonical(x):return m.annual.caller.canonical(x)

from checks import conformance

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already frozen'
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','files']:
            for name,h in manifest[group].items():assert sha(ROOT/name)==h,name
    checks,rows,tests,lock=conformance();passed=all(c['passed'] for c in checks)
    observation={'passed':passed,'checks':len(checks),'cases':len(rows),'protected_files':len(lock),
        'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],
        'whole_requirements_closed':0,'actual_tax_assessed':False,'committed':False,'native_annual_persistence':True,'general_annual_execution':False}
    if not passed:dump(HERE/('failure-'+str(time.time_ns())+'.json'),checks)
    if passed and mode=='--record':
        dump(HERE/'checks.json',checks);dump(HERE/'cases.json',rows);dump(HERE/'check-names.json',[c['name'] for c in checks])
        selected=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.txt']]
        selected += [ROOT/'scripts/annual_inventory_store_v1.py',ROOT/'tests/test_annual_inventory_store_v1.py',
                     ROOT/'docs/plans/accounting-annual-inventory-persistence-integration-20261025.md']
        dump(HERE/'manifest.json',{'recorded_at':started,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/annual-inventory-persistence-20261025/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported','random_seeds':'N/A: deterministic conformance',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-annual-inventory-persistence-20261025.md','result':str(HERE.relative_to(ROOT)/'result.md'),
            'observation':observation,'inputs':lock,'files':{str(p.relative_to(ROOT)):sha(p) for p in selected}})
    elif passed and mode=='--replay':
        assert canonical(checks)==canonical(json.loads((HERE/'checks.json').read_text()))
        assert canonical(rows)==canonical(json.loads((HERE/'cases.json').read_text()))
    print(json.dumps(observation));return not passed
if __name__=='__main__':raise SystemExit(main())
