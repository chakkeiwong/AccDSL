"""Record bounded source-network exchanges; replay without rewriting evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse
import json
import os
import platform
import subprocess
import sys
import time
import unittest
import examples as ex

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def record():
    assert not (HERE/'manifest.json').exists()
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    suite=unittest.TestSuite()
    patterns=['test_retained_population_overlap.py','test_population_overlap_v1.py',
              'test_temporal_measurement_constraints_v1.py','test_joint_measurement_constraints_v1.py']
    for p in patterns:suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=p))
    with (HERE/'tests.log').open('w') as stream:
        tests=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
    assert tests.wasSuccessful(),'Inspect tests.log'
    rows=[]
    for name,(s,g,b,expected) in ex.cases().items():
        result=ex.compose.assess(s,g,b)
        assert result['status']==expected,(name,result.get('reason'))
        assert ex.compose.verify(s,g,b,result),name
        rows.append({'name':name,'source_request':s,'groups':g,'budget':b,'expected':expected,'result':result})
    first=next(r for r in rows if r['name']=='both_instants')
    witnesses=[ex.alternative_witness(first['result'],extra) for extra in [0,100]]
    for w in witnesses:ex.compose.temporal.check_witness(first['result']['definition'],ex.BUDGET,w)
    dump(HERE/'exchanges.json',rows);dump(HERE/'explicit-witnesses.json',witnesses)
    prior=ROOT/'data/accounting-master/population-overlap-20261025/manifest.json'
    p=json.loads(prior.read_text());inputs={**p['inputs'],**p['outputs'],rel(prior):sha(prior)}
    for name in inputs:assert sha(ROOT/name)==inputs[name],name
    paths=[HERE/'compose.py',HERE/'examples.py',HERE/'verify.py',HERE/'audit.md',
           ROOT/'tests/test_retained_population_overlap.py',
           ROOT/'tests/test_temporal_measurement_constraints_v1.py',
           ROOT/'docs/plans/accounting-retained-population-overlap-20261025.md']
    for p in paths:inputs[rel(p)]=sha(p)
    outputs={rel(HERE/n):sha(HERE/n) for n in ['tests.log','exchanges.json','explicit-witnesses.json']}
    m={'started_utc':started,'wall_seconds':time.monotonic()-start,
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/retained-population-overlap-20261025/verify.py --record',
        'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                       'z3':ex.compose.overlap.z3.get_version_string()},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPUs; no TensorFlow import',
        'random_seeds':'N/A: exact rational conformance; no stochastic ranking',
        'data_version':'Pinned retained source network and source-ledger bytes',
        'plan':'docs/plans/accounting-retained-population-overlap-20261025.md',
        'result':'data/accounting-master/retained-population-overlap-20261025/result.md',
        'focused_tests':6,'tests':tests.testsRun,'regressions':tests.testsRun-6,
        'cases':len(rows),'inputs':inputs,'outputs':outputs}
    dump(HERE/'manifest.json',m)
    return {'passed':True,'tests':tests.testsRun,'cases':len(rows),'inputs':len(inputs),'explicit_witnesses':2}

def replay():
    m=json.loads((HERE/'manifest.json').read_text())
    for p,h in {**m['inputs'],**m['outputs']}.items():assert sha(ROOT/p)==h,p
    rows=json.loads((HERE/'exchanges.json').read_text())
    for row in rows:assert ex.compose.verify(row['source_request'],row['groups'],row['budget'],row['result']),row['name']
    first=next(r for r in rows if r['name']=='both_instants')
    for w in json.loads((HERE/'explicit-witnesses.json').read_text()):
        ex.compose.temporal.check_witness(first['result']['definition'],ex.BUDGET,w)
    return {'passed':True,'cases':len(rows),'tests_recorded':m['tests'],'inputs':len(m['inputs'])}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true')
    print(json.dumps(record() if parser.parse_args().record else replay()))
