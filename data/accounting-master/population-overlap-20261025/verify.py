"""Bounded full exchanges, pinned sources and semantic replay."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import importlib
import json
import os
import platform
import subprocess
import sys
import time
import unittest
import examples as ex

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'data/accounting-master/cash-population-reconciliation-20261025'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def rel(p):return p.resolve().relative_to(ROOT).as_posix()

def run_tests(patterns):
    suite=unittest.TestSuite()
    for name in patterns:suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=name))
    with (HERE/'tests.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=1).run(suite)
    assert result.wasSuccessful(), 'Inspect tests.log'
    return result.testsRun

def record():
    assert not (HERE/'manifest.json').exists()
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    checked=subprocess.run([sys.executable,'-B',str(SOURCE/'inspect_sources.py')],
        capture_output=True,text=True,check=True)
    assert json.loads(checked.stdout)['passed']
    tests=run_tests(['test_population_overlap_v1.py','test_joint_measurement_constraints_v1.py',
                    'test_accounting_p06.py','test_retained_network_history_v1.py'])
    rows=[]
    for name,(body,budget,expected) in ex.cases().items():
        result=ex.overlap.assess(body,budget)
        assert result['status']==expected,(name,result.get('reason'))
        assert ex.overlap.verify_result(body,budget,result),name
        rows.append({'name':name,'request':body,'budget':budget,'expected':expected,'response':result})
    witnesses=ex.explicit_witnesses()
    for name,items in witnesses.items():
        row=next(r for r in rows if r['name']==name)
        for witness in items:ex.overlap.joint.check_witness(row['response']['definition'],witness)
    dump(HERE/'exchanges.json',rows);dump(HERE/'explicit-witnesses.json',witnesses)
    paths={HERE/'examples.py',HERE/'verify.py',ROOT/'scripts/population_overlap_v1.py',
           ROOT/'tests/test_population_overlap_v1.py',ROOT/'docs/plans/accounting-population-overlap-20261025.md',
           ROOT/'docs/plans/accounting-cash-population-reconciliation-20261025.md'}
    paths.update(p for p in SOURCE.iterdir() if p.is_file())
    paths.update(ROOT/p for p in json.loads((SOURCE/'source-ledger.json').read_text())['source_sha256'])
    prior=ROOT/'data/accounting-master/retained-network-history-20261025/manifest.json'
    paths.add(prior);paths.update(ROOT/p for p in json.loads(prior.read_text())['inputs'])
    paths.update(ROOT/p for p in json.loads(prior.read_text())['outputs'])
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p:
            p=Path(p).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix=='.py':paths.add(p)
    inputs={rel(p):sha(p) for p in sorted(paths)}
    manifest={'started_utc':started,'wall_seconds':time.monotonic()-start,
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/population-overlap-20261025/verify.py --record',
        'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                       'z3':ex.overlap.z3.get_version_string()},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPU; no TensorFlow import',
        'data_version':'Exact retained PDFs and XBRL archive pinned in source-ledger.json',
        'random_seeds':'N/A: deterministic rational conformance; no stochastic ranking',
        'plan':'docs/plans/accounting-population-overlap-20261025.md',
        'result':'data/accounting-master/population-overlap-20261025/result.md',
        'tests':tests,'focused_tests':11,'regressions':tests-11,'exchanges':len(rows),
        'inputs':inputs,'outputs':{rel(HERE/p):sha(HERE/p) for p in
                                  ['tests.log','exchanges.json','explicit-witnesses.json']}}
    dump(HERE/'manifest.json',manifest)
    return {'passed':True,'tests':tests,'cases':len(rows),'inputs':len(inputs),'explicit_witnesses':4}

def replay():
    m=json.loads((HERE/'manifest.json').read_text())
    for p,h in {**m['inputs'],**m['outputs']}.items():assert sha(ROOT/p)==h,p
    for row in json.loads((HERE/'exchanges.json').read_text()):
        assert ex.overlap.verify_result(row['request'],row['budget'],row['response']),row['name']
    for name,ws in json.loads((HERE/'explicit-witnesses.json').read_text()).items():
        body,_,_=ex.cases()[name];definition,_=ex.overlap.lower(body)
        for w in ws:ex.overlap.joint.check_witness(definition,w)
    return {'passed':True,'cases':m['exchanges'],'inputs':len(m['inputs']),'tests_recorded':m['tests']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    if args.record:print(json.dumps(record()))
    else:print(json.dumps(replay()))
