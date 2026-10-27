"""Matched text/typed semantics, independent parser cases and frozen-core replay."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import io
import json
import os
import platform
import subprocess
import sys
import time
import unittest

os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_text_v1 as front
from examples import examples
PLAN='docs/plans/accounting-method-requirement-authoring-20261024.md'
NEXT='docs/plans/accounting-method-requirement-integration-20261024.md'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    checks=[]
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
    expected={'operations.baseline':'requirements_satisfied','returns.baseline':'requirements_satisfied',
              'legal_cash':'requirements_satisfied','reported_cash':'unresolved','insurance_cohort':'unresolved'}
    records=examples()
    texts,results={},{}
    for key,value in records.items():
        before=core.canonical(value)
        text=front.render(value)
        lowered=front.lower(text)
        result=front.assess_exchange(lowered)
        texts[key]=text
        results[key]=result
        check(key+'.exact_roundtrip',core.canonical(lowered)==before)
        check(key+'.canonical_render',front.render(lowered)==text)
        check(key+'.strict_exchange',front.decode_exchange(before.decode())==value)
        check(key+'.same_evaluator',result==front.assess_exchange(value))
        check(key+'.expected_status',result['status']==expected[key])
        check(key+'.no_mutation',core.canonical(value)==before)
        check(key+'.no_admission',all(result[k] is False for k in
              ['executed','source_admission','accounting_admission','method_eligible']))
    suite=unittest.TestSuite()
    for pattern in ['test_method_requirements_v1.py','test_method_requirement_text_v1.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    capture=io.StringIO()
    units=unittest.TextTestRunner(stream=capture,verbosity=1).run(suite)
    check('independent_core_and_frontend_tests',units.wasSuccessful() and units.testsRun==19)
    if not units.wasSuccessful():
        print(capture.getvalue(),file=sys.stderr)
    prior=HERE.parent/'method-requirements-20261024'
    manifest=json.loads((prior/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        for name,h in manifest[group].items():
            if name in locks:
                check('consistent_lock:'+name,locks[name]==h)
            locks[name]=h
    for path in [prior/'manifest.json',ROOT/PLAN,ROOT/NEXT,
                 HERE.parent/'statement-context-coverage-20261024/statement_text.py',
                 HERE.parent/'company-return-schema-20261023/return_text.py']:
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('preserve_known_hash:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':units.testsRun,
            'examples':len(records),'results':results},records,texts,locks


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
    result,records,texts,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
                 'unit_tests':result['unit_tests'],'examples':result['examples'],
                 'protected_inputs':len(locks),'failed':[c['name'] for c in result['checks'] if not c['passed']],
                 'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('exchanges.json',records),('source-lock.json',locks)]:
            dump(HERE/name,value)
        for key,text in texts.items():
            (HERE/(key+'.accdsl')).write_text(text)
        files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]
        files.extend([ROOT/'scripts/method_requirement_text_v1.py',ROOT/'tests/test_method_requirement_text_v1.py'])
        output_names=['checks.json','exchanges.json','source-lock.json']+[key+'.accdsl' for key in texts]
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; standard-library parser and protected core',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no numerical framework imported',
            'random_seeds':'N/A: deterministic conformance','data_version':'Retained examples and constructed language cases',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
            'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in output_names}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert records==json.loads((HERE/'exchanges.json').read_text())
        for key,text in texts.items():
            assert text==(HERE/(key+'.accdsl')).read_text()
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
