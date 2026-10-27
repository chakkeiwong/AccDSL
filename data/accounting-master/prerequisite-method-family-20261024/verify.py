"""Exact dependency preservation and source/temporal semantic replay."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
spec=importlib.util.spec_from_file_location('prerequisite_method_cases',HERE/'cases.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
family=examples.joined;core=family.core
PLAN='docs/plans/accounting-prerequisite-method-family-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')


def replay(row):
    return family.verify_result(row['request'],row['budget'],row['result'])


def summary(rows):
    return [{'case':r['case'],'request_sha256':core.digest(r['request']),
             'budget':r['budget'],'expected':r['expected'],'status':r['result']['status']} for r in rows]


def conformance():
    checks=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    rows=examples.cases()
    for row in rows:
        r=row['result'];prefix=row['case']+'.'
        check(prefix+'category',r['status']==row['expected'])
        check(prefix+'semantic_replay',replay(row))
        check(prefix+'boundary',all(r[k] is False for k in ['executed','source_admission','accounting_admission'])
              and r['actual_history']=='unknown' and r['executable_opening'] is None)
        for branch in r.get('branches',[]):
            if branch['status']=='feasible':
                check(prefix+'independent_branch_'+str(branch['index']),branch['replay']==family.replay_witness(
                    row['request'],row['budget'],branch['index'],branch['witness']))
                check(prefix+'no_native_claim_'+str(branch['index']),branch['replay']['monetary']['native_preconditions_checked'] is False and branch['replay']['both_original_evaluators_checked'] is True and branch['replay']['prerequisites']['status'] in ['requirements_satisfied','no_active_requirements'])
    suite=unittest.TestSuite()
    for name in ['test_prerequisite_method_family_v1','test_piecewise_method_family_v1','test_method_requirements_v1','test_method_requirements_v2','test_method_requirements_v3','test_typed_return_transition_v1']:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    from test_accounting_p04 import ReconstructionTests
    for name in ['test_rounded_strict_and_unbounded','test_incomplete_unsupported_unknown',
                 'test_limits_and_unknown_bound_stages','test_exact_input_boundaries']:
        suite.addTest(ReconstructionTests(name))
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture).run(suite)
    check('80_targeted_join_parent_prerequisite_and_solver_regressions',result.wasSuccessful() and result.testsRun==80)
    if not result.wasSuccessful():print(capture.getvalue(),file=sys.stderr)
    locks=json.loads((HERE/'dependency-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':result.testsRun},rows,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already recorded'
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    if mode=='--replay':
        saved=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in saved[group].items():assert sha(ROOT/name)==h,name
        for row in json.loads((HERE/'cases.json').read_text()):assert replay(row),row['case']
    result,rows,locks=conformance();assert result['passed'],[c['name'] for c in result['checks'] if not c['passed']]
    observation={'mode':mode,'passed':True,'checks':len(result['checks']),'unit_tests':result['unit_tests'],
                 'cases':len(rows),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
    if mode=='--record':
        for name,value in [('checks.json',result),('cases.json',rows),('semantic-summary.json',summary(rows))]:dump(HERE/name,value)
        files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]+[HERE/'dependency-lock.json']
        files.extend(ROOT/name for name in ['scripts/prerequisite_method_family_v1.py',
            'tests/test_prerequisite_method_family_v1.py'])
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; Z3 '+family.z3.get_version_string(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact rational feasibility; no stochastic ranking',
            'data_version':'dependency-lock.json; authored complete monetary and prerequisite family intersections and protected comparator sources',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','semantic-summary.json']},
            'replay':'Exact source/definition/lowering identities and mathematical witness/core checks; solver choices and timing may differ.'})
    if mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert summary(rows)==json.loads((HERE/'semantic-summary.json').read_text())
    print(json.dumps(observation))


if __name__=='__main__':main()
