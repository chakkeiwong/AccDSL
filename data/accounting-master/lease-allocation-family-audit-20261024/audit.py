"""Conditional lease allocations: exact deductions and original native replay."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json, os, platform, subprocess, sys, time

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'tests'))
import test_lease_shared_book_v1 as fixtures
import rational_solver_v1 as solver
import z3

PLAN = 'docs/plans/accounting-lease-allocation-family-audit-20261024.md'
BUDGET = solver.Budget(4, 10000, 1, 1, 3000, 1000, 1000000)

def sha(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def audit():
    checks, probes = [], []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def exact_result(result):
        # Wall time is diagnostic, not part of deterministic saved evidence.
        result.pop('wall_seconds', None)
        return result
    x = z3.Real('lease_B_opening_rou')
    def problem(complete=False):
        p = solver.Problem('conditional_two_right_lease_allocation',
                           'supplied_exact_synthetic_aggregates', variables={'x':x}, slots=4)
        p.add('nonnegative_B', x >= 0)
        p.add('nonnegative_A', x <= 120)
        if complete:
            p.add('second_reduction_supported', x <= 111)
            p.add('supplied_depreciation_81_supported', x <= 30)
        return p
    all_allocations = problem()
    complete = problem(True)
    formulas = {'first_gain':50-x, 'first_rou':130-x, 'second_rou':111-x,
                'final_rou':30-x, 'profit':-39-x, 'joint_difference':(-39-x)-(30-x)}
    expected_bounds = {'first_gain':(-70,50), 'final_rou':(0,30),
                       'profit':(-69,-39), 'joint_difference':(-69,-69)}
    for name, limits in expected_bounds.items():
        p = all_allocations if name == 'first_gain' else complete
        result = exact_result(solver.solve(p, BUDGET, formulas[name]))
        check(name+'_complete_scope', result['status']=='ExactWithinScope' and
              result['coverage']['complete'] and result['feasibility']=='Feasible')
        check(name+'_certified_bounds', all(result['bounds'][side]['certified'] and
              result['bounds'][side]['attained'] and
              Q(result['bounds'][side]['value'])==value
              for side,value in zip(('lower','upper'),limits)))
        probes.append({'probe':name+'_bounds', 'result':result})
    # These propositions follow over the entire continuous interval, not a grid.
    for name, conditions, expected in [
        ('second_support_forward',[111-x>=0,x>111],'Infeasible'),
        ('second_support_reverse',[x<=111,111-x<0],'Infeasible'),
        ('complete_support_forward',[111-x>=0,81<=111-x,x>30],'Infeasible'),
        ('complete_support_reverse',[x<=30,81>111-x],'Infeasible'),
        ('marginal_endpoint_pair_impossible',[30-x==30,-39-x==-69],'Infeasible'),
        ('reported_final_asset10',[30-x==10],'ExactWithinScope')]:
        p = all_allocations if '_support_' in name else complete
        result = exact_result(solver.solve(p,BUDGET, x if name=='reported_final_asset10' else None,
                                           extra=conditions))
        check(name, result['status']==expected)
        if name=='reported_final_asset10':
            check('final_asset10_selects_x20', all(Q(result['bounds'][s]['value'])==20 and
                  result['bounds'][s]['certified'] for s in ['lower','upper']))
        # Unsat-core order/choice is not a scientific result; retain the checked
        # status, full formulas, and exact bounds without incidental core order.
        probes.append({'probe':name,'status':result['status'],
                       'query':result['query'],'bounds':result['bounds'],
                       'coverage':result['coverage'],
                       'conflict_rechecked':all(c.get('conflict',{}).get('rechecked')=='unsat'
                         for c in result['cells'] if c['feasibility']=='unsat')})
    replay = {}
    for allocation in [0,20,30,40,100,111,112,120]:
        state, events = fixtures.fixture()
        rights = state['leases'][0]['component']['rights']
        rights[0]['rou']=fixtures.lease.fmt(Q(120-allocation))
        rights[1]['rou']=fixtures.lease.fmt(Q(allocation))
        events[0]['parameters']['rights'][1]['removed_rou']=fixtures.lease.fmt(Q(allocation))
        before=deepcopy(state)
        result=fixtures.lease.run_prefix(state,events)
        expected_status=('hypothetical_sequence_complete' if allocation<=30 else
                         'rejected' if allocation<=111 else 'unsupported')
        expected_prefix=4 if allocation<=30 else 3 if allocation<=111 else 1
        check(f'x{allocation}_status',result['status']==expected_status)
        check(f'x{allocation}_prefix',len(result['proposals'])==expected_prefix)
        check(f'x{allocation}_opening_unchanged',state==before)
        first=result['proposals'][0]
        check(f'x{allocation}_first_gain',-Q(first['journal']['other_gains'])==50-allocation)
        check(f'x{allocation}_first_rou',Q(first['after']['balances']['rou'])==130-allocation)
        if allocation<=111:
            check(f'x{allocation}_second_rou',Q(result['proposals'][1]['after']['balances']['rou'])==111-allocation)
            check(f'x{allocation}_payment_cash',Q(result['state']['balances']['cash'])==101)
        if allocation<=30:
            b=result['state']['balances']
            check(f'x{allocation}_final_joint',Q(b['rou'])==30-allocation and
                  -sum(Q(b[k]) for k in fixtures.lease.types.PROFIT)==-39-allocation)
        else:
            check(f'x{allocation}_failed_event_atomic',result['failed_event_index']==expected_prefix and
                  result['state']==result['proposals'][-1]['after'])
        for i,p in enumerate(result['proposals']):
            check(f'x{allocation}_original_replay_{i}',fixtures.lease.apply(
                  state if i==0 else result['proposals'][i-1]['after'],events[i],p)==p['after'])
        replay[str(allocation)]={'opening':before,'events':events,'result':result}
    a,b=replay['20'],replay['30']
    check('identical_aggregate_opening',a['opening']['balances']==b['opening']['balances'])
    check('different_complete_outcomes',a['result']['state']['balances']['rou']=='10/1' and
          b['result']['state']['balances']['rou']=='0/1')
    # A tiny budget cannot certify even this declared family.
    limited=exact_result(solver.solve(complete,solver.Budget(4,10000,1,0,3000,1000,1000000),formulas['profit']))
    check('partial_budget_no_global_bounds',limited['status']=='PartialSearch' and limited['bounds'] is None)
    probes.append({'probe':'partial_budget','result':limited})
    unknown,events=fixtures.fixture();unknown['collection_complete']='unknown'
    check('unknown_membership_not_admitted',fixtures.lease.propose(unknown,events[0])['status']=='unresolved')
    locks=json.loads((HERE/'source-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'probes':probes,
            'native_replays':replay,'budget':BUDGET.__dict__,
            'flags':{k:False for k in ['actual_state_identified','source_admission','accounting_admission',
                                      'method_eligible','production_committed']}},locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for n,h in manifest[group].items():assert sha(ROOT/n)==h,n
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    result,locks=audit()
    assert result==json.loads(json.dumps(result)),'JSON round-trip changed evidence'
    assert result['passed'],[c['name'] for c in result['checks'] if not c['passed']]
    obs={'mode':mode,'passed':True,'checks':len(result['checks']),'probes':len(result['probes']),
         'native_allocations':len(result['native_replays']),'protected_inputs':len(locks),
         'wall_seconds':time.monotonic()-clock}
    if mode=='--record':
        dump(HERE/'audit.json',result)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':obs['wall_seconds'],
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'python3 -B '+str(HERE.relative_to(ROOT)/'audit.py')+' --record',
          'environment':{'python':platform.python_version(),'z3':z3.get_version_string()},
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic audit',
          'data_version':'Original synthetic CorporateResiduals/1 rights and declared allocation premise',
          'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
          'outputs':{str((HERE/'audit.json').relative_to(ROOT)):sha(HERE/'audit.json')},
          'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':assert result==json.loads((HERE/'audit.json').read_text())
    print(json.dumps(obs))

if __name__=='__main__':main()
