"""Exact interoperable semantics, source identity and unchanged prior evidence."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
from comparisons import comparisons
PLAN='docs/plans/accounting-collection-reference-requirements-20261024.md'
NEXT='docs/plans/accounting-ordered-identity-requirements-20261024.md'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    checks=[]
    rows=comparisons()
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
    for row in rows:
        check(row['case']+'.expected_comparison',row['passed'])
        check(row['case']+'.all_seven_conditions',len(row['result'].get('findings',[]))==7)
        check(row['case']+'.no_admission',all(row['result'][k] is False for k in
              ['executed','source_admission','accounting_admission','method_eligible']))
        check(row['case']+'.scope_boundary',row['boundary_counterexample']==
              (row['native']['status']=='invalid' and row['result']['status']=='collection_requirements_satisfied'))
    suite=unittest.TestSuite()
    for pattern in ['test_method_requirements_v1.py','test_method_requirement_text_v1.py',
                    'test_method_input_binding_v1.py','test_method_requirements_v2.py',
                    'test_method_requirements_v3.py','test_method_requirement_interoperability.py','test_method_collections_v1.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    captured=io.StringIO()
    result=unittest.TextTestRunner(stream=captured,verbosity=1).run(suite)
    check('combined_69_unit_methods',result.wasSuccessful() and result.testsRun==69)
    if not result.wasSuccessful():
        print(captured.getvalue(),file=sys.stderr)
    prior=HERE.parent/'requirement-version-interoperability-20261024'
    old=json.loads((prior/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        locks.update(old[group])
    for path in [ROOT/PLAN,ROOT/NEXT,prior/'manifest.json',HERE.parent/'company-return-schema-20261023/fixture.json']:
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('consistent_lock:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':result.testsRun,
            'cases':len(rows),'retained_cases':len(rows), 'boundary_counterexamples':sum(r['boundary_counterexample'] for r in rows)},rows,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started=datetime.now(timezone.utc).isoformat()
    clock=time.monotonic()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in manifest[group].items():
                assert sha(ROOT/name)==h,name
    result,rows,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
                 'unit_tests':result['unit_tests'],'cases':result['cases'],
                 'retained_cases':result['retained_cases'],'protected_inputs':len(locks),
                 'failed':[c['name'] for c in result['checks'] if not c['passed']],
                 'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('cases.json',rows),('source-lock.json',locks)]:
            dump(HERE/name,value)
        files=[p for p in HERE.iterdir() if p.is_file() and p.suffix in ['.py','.md']]
        files.extend(ROOT/p for p in ['scripts/method_collections_v1.py','tests/test_method_collections_v1.py'])
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; preserved guarded evaluator and finite collection prerequisites',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic conformance',
            'data_version':'exact upstream identities in source-lock.json; constructed projections labeled separately',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert rows==json.loads((HERE/'cases.json').read_text())
        assert locks==json.loads((HERE/'source-lock.json').read_text())
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
