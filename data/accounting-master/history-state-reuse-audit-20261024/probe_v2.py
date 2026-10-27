"""Bounded engineering probes of inherited finite-history semantics."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import reconstruction_v1 as reconstruction
from rational_solver_v1 import Budget,solve


def run():
    start=time.monotonic();checks=[];observations={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    fixture=ROOT/'docs/design/fixtures/p04-reconstruction-cases-v1.json'
    spec=json.loads(fixture.read_text())['input_fixture']
    budget=Budget(2,10000,20,20,5000,1000,1000000)
    p=reconstruction.construct(deepcopy(spec));r=solve(p,budget)
    check('fixed_opening_fixture_supported',r['status']=='ExactWithinScope' and r['feasibility']=='Feasible')
    check('sixteen_declared_integer_cells',r['coverage']['total']==16 and r['coverage']['completed']==16)
    observations['fixed_opening']={k:r[k] for k in ['status','feasibility','coverage']}
    symbolic=deepcopy(spec);symbolic['symbols']=[{'id':'opening_cash','kind':'Real','domain':{
        'lower':'9','upper':'11','lower_closed':True,'upper_closed':True}}]
    symbolic['opening']['Cash']='opening_cash'
    try:
        reconstruction.construct(symbolic);error=None
    except (ValueError,TypeError) as exc:error={'type':type(exc).__name__,'reason':str(exc)[:250]}
    check('symbolic_opening_not_supported',error is not None)
    observations['symbolic_opening']=error
    dates=deepcopy(spec);dates['dates']=['2024-12-31','2024-01-01']
    dates['slots'][0]['date']='2024-12-31';dates['slots'][1]['date']='2024-01-01'
    dates['mappings']={'earlier_calendar_day':'balance:2024-01-01:Cash'}
    dated=reconstruction.construct(dates)
    expression=dated.outputs['earlier_calendar_day']
    value=reconstruction.z3.simplify(reconstruction.z3.substitute(expression,
        (dated.variables['a'],reconstruction.z3.IntVal(2)),
        (dated.variables['b'],reconstruction.z3.IntVal(3))))
    check('supplied_order_not_calendar_order',str(value)=='15')
    observations['date_order']={'supplied_dates':dates['dates'],'evaluated_earlier_day_cash':str(value),
        'meaning':'Later-calendar event is included because the prototype follows supplied date order.'}
    rows=json.loads((ROOT/'data/accounting-master/statement-network-contexts-20261024/cases.json').read_text())
    network=next(x for x in rows if x['case']=='explicit_numeric_subset')['result']
    requirements=network['preserved_report']['requirements']
    check('fifteen_state_dependencies_retained',len(requirements)==15)
    check('measurement_witness_not_opening',network['status']=='conditionally_feasible' and network['executable_opening'] is None)
    observations['state_dependencies']=[{'id':x['id'],'unavailable_state':x['unavailable_state'],
        'required_for_selected_execution':x['required_for_selected_execution'],'affects':x['affects']}
        for x in requirements]
    by_id={x['id']:x for x in requirements}
    check('known_fiscal_period_retained',by_id['period']['unavailable_state'] is None)
    check('required_execution_state_still_missing',all(by_id[k]['unavailable_state'] for k in ['opening','cash','claims','inventory','assets','debt','funding','tax']))
    paths=['scripts/reconstruction_v1.py','scripts/rational_solver_v1.py','tests/test_accounting_p04.py',
        'docs/design/fixtures/p04-reconstruction-cases-v1.json',
        'docs/design/proposal/architecture/history-families-contract-v1.md',
        'docs/design/proposal/architecture/history-families-result-v1.md',
        'docs/design/proposal/architecture/company-inputs-draft-20261023.md',
        'data/accounting-master/source-constrained-state-20261024/partial_state.py',
        'data/accounting-master/statement-network-contexts-20261024/cases.json',
        'data/accounting-master/statement-network-contexts-20261024/manifest.json']
    locks={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'observations':observations,
        'source_lock':locks,'manifest':{'started_utc':datetime.now(timezone.utc).isoformat(),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'python3 -B '+str(HERE.relative_to(ROOT)/'probe_v2.py')+' --record',
        'environment':'Python '+platform.python_version()+'; Z3 '+reconstruction.z3.get_version_string(),
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact bounded engineering probes',
        'budget':budget.__dict__,'wall_seconds':time.monotonic()-start,
        'plan':'docs/plans/accounting-history-state-reuse-audit-20261024.md',
        'result':str(HERE.relative_to(ROOT)/'result.md')}}


if __name__=='__main__':
    result=run()
    if '--record' in sys.argv:
        assert not (HERE/'audit-v2.json').exists(),'audit already recorded'
        (HERE/'audit-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':len(result['checks']),
        'failed':[c['name'] for c in result['checks'] if not c['passed']],
        'symbolic_opening':result['observations']['symbolic_opening'],
        'calendar_probe':result['observations']['date_order'],'sources':len(result['source_lock'])}))
    raise SystemExit(not result['passed'])
