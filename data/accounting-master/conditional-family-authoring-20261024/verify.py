"""Retained source equality, semantic replay, regressions and frozen dependencies."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
spec=importlib.util.spec_from_file_location('conditional_authoring_cases',HERE/'cases.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
authoring=examples.authoring;core=authoring.core
PLAN='docs/plans/accounting-conditional-family-authoring-20261024.md'
EXPECTED=['conditionally_feasible','conditionally_feasible','conditional_family_witness',
          'conditional_family_witness','conditional_attachment_witness',
          'conditionally_infeasible','unresolved','unknown']

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def replay(row):
    e=row['exchange'];source=ROOT/row['source_path']
    return (sha(source)==row['source_sha256'] and authoring.lower(source.read_bytes())==e
        and e==row['expected_exchange']
        and examples.equivalent_result(e['definition'],e['budget'],row['result']))

def summary(rows):
    return [{'case':r['case'],'source_sha256':r['source_sha256'],
             'exchange_sha256':core.digest(r['exchange']),'status':r['result']['status']} for r in rows]

def conformance():
    checks=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    rows=examples.cases()
    for row,expected in zip(rows,EXPECTED):
        prefix=row['case']+'.';e=row['exchange']
        check(prefix+'expected_status',row['result']['status']==expected)
        check(prefix+'exact_expected_exchange',e==row['expected_exchange'])
        check(prefix+'source_semantic_replay',replay(row))
        check(prefix+'strict_json_exchange',authoring.decode_exchange(core.canonical(e))==e)
        check(prefix+'repeatable_render',authoring.lower(authoring.render(e))==e)
        check(prefix+'no_admission',all(row['result'][k] is False for k in
              ['executed','source_admission','accounting_admission']))
    check('all_expected_cases',len(rows)==len(EXPECTED))
    suite=unittest.TestSuite()
    for name in ['test_conditional_family_text_v1','test_typed_affine_history_v1',
                 'test_history_measurement_attachment_v1','test_conditional_history_family_v1',
                 'test_joint_measurement_constraints_v1','test_temporal_measurement_constraints_v1']:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    from test_accounting_p04 import ReconstructionTests
    for name in ['test_rounded_strict_and_unbounded','test_incomplete_unsupported_unknown',
                 'test_limits_and_unknown_bound_stages','test_exact_input_boundaries']:
        suite.addTest(ReconstructionTests(name))
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture).run(suite)
    check('94_targeted_authoring_and_preserved_methods',result.wasSuccessful() and result.testsRun==94)
    if not result.wasSuccessful():print(capture.getvalue(),file=sys.stderr)
    locks=json.loads((HERE/'dependency-lock.json').read_text())
    for n,h in locks.items():check('protected:'+n,sha(ROOT/n)==h)
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'unit_tests':result.testsRun},rows,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already recorded'
    clock=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for n,h in m[group].items():assert sha(ROOT/n)==h,n
        for row in json.loads((HERE/'cases.json').read_text()):assert replay(row),row['case']
    result,rows,locks=conformance()
    assert result['passed'],[x['name'] for x in result['checks'] if not x['passed']]
    observation={'mode':mode,'passed':True,'checks':len(result['checks']),
        'unit_tests':result['unit_tests'],'cases':len(rows),'protected_inputs':len(locks),
        'wall_seconds':time.monotonic()-clock}
    if mode=='--record':
        for n,x in [('checks.json',result),('cases.json',rows),('semantic-summary.json',summary(rows))]:dump(HERE/n,x)
        files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]+[HERE/'dependency-lock.json']
        files+=list((HERE/'examples').glob('*.accdsl'))
        files += [ROOT/'scripts/conditional_family_text_v1.py',ROOT/'tests/test_conditional_family_text_v1.py']
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; Z3 '+authoring.typed.z3.get_version_string(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic authoring conformance',
            'data_version':'dependency-lock.json and eight retained authored sources',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','semantic-summary.json']}})
    if mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert summary(rows)==json.loads((HERE/'semantic-summary.json').read_text())
    print(json.dumps(observation))

if __name__=='__main__':main()
