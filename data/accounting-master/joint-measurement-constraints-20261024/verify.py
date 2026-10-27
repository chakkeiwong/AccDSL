"""Exact source identities and mathematical replay, not solver-model byte equality."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from examples import comparisons,joint
PLAN='docs/plans/accounting-joint-measurement-constraints-20261024.md'
NEXT='docs/plans/accounting-joint-source-relation-binding-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,value):p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def summary(rows):
    return [{'case':r['case'],'definition_sha256':joint.core.digest(r['definition']),
             'budget':r['budget'],'expected':r['expected'],'status':r['result']['status'],
             'passed':r['passed']} for r in rows]


def conformance():
    rows=comparisons();checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    for row in rows:
        check(row['case']+'.exact_category_and_witness',row['passed'])
        check(row['case']+'.no_admission',row['result']['executed'] is False and row['result']['source_admission'] is False
              and row['result']['accounting_admission'] is False and row['result']['actual_history']=='unknown'
              and row['result']['executable_opening'] is None)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_joint_measurement_constraints_v1.py')
    from test_accounting_p04 import ReconstructionTests
    for name in ['test_rounded_strict_and_unbounded','test_incomplete_unsupported_unknown',
                 'test_limits_and_unknown_bound_stages','test_exact_input_boundaries']:
        suite.addTest(ReconstructionTests(name))
    captured=io.StringIO();result=unittest.TextTestRunner(stream=captured).run(suite)
    check('15_joint_and_scoped_solver_methods',result.wasSuccessful() and result.testsRun==15)
    if not result.wasSuccessful():print(captured.getvalue(),file=sys.stderr)
    prior=HERE.parent/'joint-source-constraints-audit-20261024/manifest.json'
    old=json.loads(prior.read_text());locks={}
    for group in ['inputs','implementation','outputs']:locks.update(old[group])
    for p in [ROOT/PLAN,ROOT/NEXT,prior,ROOT/'tests/test_accounting_p04.py',ROOT/'tests/test_accounting_p03.py']:
        name=str(p.relative_to(ROOT));h=sha(p)
        check('consistent_source:'+name,name not in locks or locks[name]==h);locks[name]=h
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':result.testsRun},rows,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists()
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    if mode=='--replay':
        saved=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in saved[group].items():assert sha(ROOT/name)==h,name
        for row in json.loads((HERE/'cases.json').read_text()):
            if 'witness' in row['result']:joint.check_witness(row['definition'],row['result']['witness'])
    result,rows,locks=conformance();assert result['passed'],[c['name'] for c in result['checks'] if not c['passed']]
    observation={'mode':mode,'passed':True,'checks':len(result['checks']),'unit_tests':result['unit_tests'],
                 'cases':len(rows),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
    if mode=='--record':
        for name,value in [('checks.json',result),('cases.json',rows),('semantic-summary.json',summary(rows)),('source-lock.json',locks)]:dump(HERE/name,value)
        files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]
        files.extend(ROOT/p for p in ['scripts/joint_measurement_constraints_v1.py','tests/test_joint_measurement_constraints_v1.py'])
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
             'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
             'environment':'Python '+platform.python_version()+'; Z3 '+joint.z3.get_version_string(),
             'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic feasibility; no stochastic ranking',
             'data_version':'source-lock.json; constructed conditional systems','plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
             'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
             'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','semantic-summary.json','source-lock.json']},
             'replay':'Exact input/implementation hashes; rechecked witness validity and same expected status. Model/core choices and wall time are not compared bytewise.'})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert summary(rows)==json.loads((HERE/'semantic-summary.json').read_text())
    print(json.dumps(observation))

if __name__=='__main__':main()
