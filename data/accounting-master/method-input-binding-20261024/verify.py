"""Record-bound values, independent adversarial checks and prior-byte preservation."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,time,unittest

os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
from examples import retained,assess
PLAN='docs/plans/accounting-method-input-binding-20261024.md'
NEXT='docs/plans/accounting-complete-method-coverage-20261024.md'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    checks,outputs,records=[],{},{}
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
    for key,case in retained().items():
        p=case['packet']
        result=assess(p)
        outputs[key]=result
        check(key+'.bound',result['status']=='bound')
        check(key+'.exact_values',result.get('values')==case['expected_values'])
        check(key+'.selected_assessment',result.get('assessment',{}).get('status')=='requirements_satisfied')
        check(key+'.complete_lineage',set(result.get('lineage',{}))==set(case['expected_values']))
        for field,trace in result.get('lineage',{}).items():
            check(key+'.exact_source.'+field,trace['source_ref']=='sha256:'+trace['raw_sha256']+'#'+trace['pointer'])
        records[key]={**{k:v for k,v in p.items() if k!='blobs'},
                      'raw_utf8':{h:raw.decode('utf-8') for h,raw in p['blobs'].items()},
                      'provenance':case['provenance'],'upstream_raw_sha256':case['upstream_raw_sha256']}
    suite=unittest.TestSuite()
    for pattern in ['test_method_requirements_v1.py','test_method_requirement_text_v1.py','test_method_input_binding_v1.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    capture=io.StringIO()
    tests=unittest.TextTestRunner(stream=capture,verbosity=1).run(suite)
    check('combined_semantics_authoring_binding_suite',tests.wasSuccessful() and tests.testsRun==28)
    if not tests.wasSuccessful():
        print(capture.getvalue(),file=sys.stderr)
    prior=HERE.parent/'method-requirement-authoring-20261024'
    m=json.loads((prior/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        for name,h in m[group].items():
            if name in locks:
                check('consistent_lock:'+name,locks[name]==h)
            locks[name]=h
    paths=[ROOT/PLAN,ROOT/NEXT,prior/'manifest.json',
           HERE.parent/'company-portable-authoring-20261023/portable.py',
           HERE.parent/'company-path-admission-20261023/admission.py',
           ROOT/'docs/design/proposal/manuscript-method-requirements-20261024/accounting-product-proposal.pdf']
    for module in list(sys.modules.values()):
        if getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            if path.is_relative_to(ROOT) and not path.is_relative_to(HERE) and path not in [
                ROOT/'scripts/method_input_binding_v1.py',ROOT/'tests/test_method_input_binding_v1.py']:
                paths.append(path)
    for path in sorted(set(paths)):
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('preserved_known_hash:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':tests.testsRun,
            'records':len(records),'results':outputs},records,locks


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
    result,records,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
                 'unit_tests':result['unit_tests'],'records':result['records'],'protected_inputs':len(locks),
                 'failed':[c['name'] for c in result['checks'] if not c['passed']],
                 'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('binding-records.json',records),('source-lock.json',locks)]:
            dump(HERE/name,value)
        implementation=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]
        implementation.extend([ROOT/'scripts/method_input_binding_v1.py',ROOT/'tests/test_method_input_binding_v1.py'])
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; pinned portable decoder and protected predicate core',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no numerical framework imported',
            'random_seeds':'N/A: deterministic conformance','data_version':'Exact retained bytes and explicit derived return record',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in implementation},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in
                       ['checks.json','binding-records.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert records==json.loads((HERE/'binding-records.json').read_text())
        assert locks==json.loads((HERE/'source-lock.json').read_text())
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
