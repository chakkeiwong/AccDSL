"""Dimension, known arithmetic and retained allocation conformance evidence."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
from equations import comparisons
PLAN='docs/plans/accounting-guarded-requirements-20261024.md'
NEXT='docs/plans/accounting-requirement-version-interoperability-20261024.md'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def dump(p,value):
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    rows,source=comparisons()
    checks=[]
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
    for row in rows:
        check(row['case']+'.legacy_equation',row['passed'])
        check(row['case']+'.eight_requirements_retained',len(row['result'].get('findings',[]))==8)
        check(row['case']+'.no_admission',all(row['result'][k] is False for k in
             ['executed','source_admission','accounting_admission','method_eligible']))
    suite=unittest.TestSuite()
    for pattern in ['test_method_requirements_v1.py','test_method_requirement_text_v1.py',
                    'test_method_input_binding_v1.py','test_method_requirements_v2.py','test_method_requirements_v3.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    captured=io.StringIO()
    tests=unittest.TextTestRunner(stream=captured,verbosity=1).run(suite)
    check('combined_46_unit_methods',tests.wasSuccessful() and tests.testsRun==46)
    if not tests.wasSuccessful():
        print(captured.getvalue(),file=sys.stderr)
    prior=HERE.parent/'dimensional-requirements-20261024'
    m=json.loads((prior/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        locks.update(m[group])
    for path in [ROOT/PLAN,ROOT/NEXT,prior/'manifest.json',ROOT/'scripts/core0_ir_v1.py']:
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('consistent_lock:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':tests.testsRun,
            'retained_equation_cases':len(rows),'upstream_sha256':source},rows,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    start=datetime.now(timezone.utc).isoformat()
    clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items():
                assert sha(ROOT/name)==h,name
    result,rows,locks=conformance()
    obs={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
         'unit_tests':result['unit_tests'],'retained_equation_cases':len(rows),
         'protected_inputs':len(locks),'failed':[c['name'] for c in result['checks'] if not c['passed']],
         'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('equation-cases.json',rows),('source-lock.json',locks)]:
            dump(HERE/name,value)
        files=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ['.py','.md']]
        files.extend([ROOT/'scripts/method_requirements_v3.py',ROOT/'tests/test_method_requirements_v3.py'])
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; protected v1/v2 and explicit guarded activation',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic conformance',
            'data_version':{'retained_source_sha256':result['upstream_sha256']},
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in
                       ['checks.json','equation-cases.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert rows==json.loads((HERE/'equation-cases.json').read_text())
        assert locks==json.loads((HERE/'source-lock.json').read_text())
    print(json.dumps(obs))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
