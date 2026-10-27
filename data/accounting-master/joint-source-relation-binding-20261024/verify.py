"""Record exact dependencies and semantically replay retained source results."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import io
import json
import os
import platform
import subprocess
import sys
import time
import unittest
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests')]
spec = importlib.util.spec_from_file_location('joint_source_binding_cases', HERE/'cases.py')
examples = importlib.util.module_from_spec(spec); spec.loader.exec_module(examples)
adapter = examples.adapter
PLAN = 'docs/plans/accounting-joint-source-relation-binding-20261024.md'
NEXT = 'docs/plans/accounting-joint-measurements-integration-20261024.md'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
def summary(rows):
    return [{'case':r['case'], 'request_sha256':adapter.core.digest(r['request']),
             'budget':r['budget'], 'expected':r['expected'], 'status':r['result']['status'],
             'definition_sha256':adapter.core.digest(r['result']['definition']),
             'preserved_report_sha256':r['result']['preserved_report_sha256']}
            for r in rows]


def conformance():
    checks = []
    def check(name, value): checks.append({'name':name, 'passed':bool(value)})
    rows = examples.cases()
    for row in rows:
        r = row['result']; prefix = row['case']+'.'
        check(prefix+'category', r['status'] == row['expected'])
        check(prefix+'complete_source', len(r['preserved_report']['observations']) == 256
              and len(r['preserved_report']['relations']) == len(r['relation_dispositions']) == 143)
        check(prefix+'semantic_replay', adapter.verify_result(row['request'], row['budget'], r))
        check(prefix+'boundaries', all(r[k] is False for k in ['executed','source_admission','accounting_admission'])
              and r['actual_history'] == 'unknown' and r['executable_opening'] is None)
        if 'witness' in r['joint_assessment']:
            check(prefix+'exact_witness', adapter.joint.check_witness(r['definition'],r['joint_assessment']['witness']))
    suite = unittest.TestSuite()
    for name in ['test_joint_source_relation_binding_v1','test_joint_measurement_constraints_v1']:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    from test_accounting_p04 import ReconstructionTests
    for name in ['test_rounded_strict_and_unbounded','test_incomplete_unsupported_unknown',
                 'test_limits_and_unknown_bound_stages','test_exact_input_boundaries']:
        suite.addTest(ReconstructionTests(name))
    captured = io.StringIO(); run = unittest.TextTestRunner(stream=captured).run(suite)
    check('33_targeted_source_joint_solver_methods', run.wasSuccessful() and run.testsRun == 33)
    if not run.wasSuccessful(): print(captured.getvalue(), file=sys.stderr)
    locks = adapter.verify_dependencies()
    for name in [PLAN, NEXT]: locks[name] = sha(ROOT/name)
    for name, digest in locks.items(): check('protected:'+name, sha(ROOT/name) == digest)
    return {'passed':all(c['passed'] for c in checks), 'checks':checks, 'unit_tests':run.testsRun}, rows, locks


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode != '--record' or not (HERE/'manifest.json').exists(), 'already recorded'
    start = time.monotonic(); started = datetime.now(timezone.utc).isoformat()
    if mode == '--replay':
        saved = json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,digest in saved[group].items(): assert sha(ROOT/name) == digest, name
        for row in json.loads((HERE/'cases.json').read_text()):
            assert adapter.verify_result(row['request'], row['budget'], row['result']), row['case']
    result, rows, locks = conformance()
    assert result['passed'], [c['name'] for c in result['checks'] if not c['passed']]
    observation = {'mode':mode,'passed':True,'checks':len(result['checks']),
                   'unit_tests':result['unit_tests'],'cases':len(rows),'protected_inputs':len(locks),
                   'wall_seconds':time.monotonic()-start}
    if mode == '--record':
        for name,value in [('checks.json',result),('cases.json',rows),('semantic-summary.json',summary(rows)),('source-lock.json',locks)]: dump(HERE/name,value)
        files = [p for p in HERE.iterdir() if p.suffix in ['.py','.md']]
        files.extend(ROOT/p for p in ['scripts/joint_source_relation_binding_v1.py','tests/test_joint_source_relation_binding_v1.py'])
        files.append(HERE/'dependency-lock.json')
        dump(HERE/'manifest.json', {'started_utc':started,'wall_seconds':observation['wall_seconds'],
             'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
             'environment':'Python '+platform.python_version()+'; Z3 '+adapter.joint.z3.get_version_string(),
             'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU libraries imported',
             'random_seeds':'N/A: exact conditional feasibility; no stochastic ranking',
             'data_version':'dependency-lock.json; frozen retained combined statement description',
             'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
             'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
             'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','semantic-summary.json','source-lock.json']},
             'replay':'Input/output hashes plus exact source fields, witness validity and rechecked core meaning. Solver model, core order and timing need not be identical.'})
    if mode == '--replay':
        assert result == json.loads((HERE/'checks.json').read_text())
        assert summary(rows) == json.loads((HERE/'semantic-summary.json').read_text())
    print(json.dumps(observation))


if __name__ == '__main__': main()
