"""Exact selected-state gaps; no new composition or source admission."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json,sys,time,os,platform,subprocess
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import typed_return_transition_v1 as native
from test_typed_return_transition_v1 import fixtures,raw_args
from test_prerequisite_method_family_v1 import fixture as joined_fixture
import prerequisite_method_family_v1 as joined
from test_piecewise_method_family_v1 import BUDGET
from test_typed_affine_history_v1 import stock_fixture
import typed_affine_history_v1 as history
from test_conditional_history_family_v1 import BUDGET as HISTORY_BUDGET

def run():
    checks=[];observations={}
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    _,state,event=next(x for x in fixtures.selected_cases() if x[2]['kind']=='settle')
    original=deepcopy((state,event));normal=native.propose(*raw_args(state,event))
    check('known_native_proposal',normal['status']=='proposed')
    d=joined_fixture(variable=False);r=joined.assess(d,BUDGET)
    check('known_join_candidate',r['status']=='conditional_family_witness')
    low=deepcopy(state);cash=Q(low['balances']['cash']);low['balances']['cash']='1/1'
    low['balances']['original_equity']=native.monetary.fmt(Q(low['balances']['original_equity'])+cash-1)
    native.structure.native.invariant(low)
    failed=native.propose(*raw_args(low,event))
    check('balanced_low_cash_state_still_valid',sum(Q(v) for v in low['balances'].values())==0)
    check('funding_rejected_after_effects',failed['status']=='funding_failure')
    check('cash_absent_from_family_input',not any(k in d['family']['method']['inputs'] for k in ['cash','opening_cash']))
    observations['cash']={'opening_before':state['balances']['cash'],'opening_modified':'1/1',
        'family_status':r['status'],'native_result':failed,'same_method_inputs':fixtures.project(low,event)==fixtures.project(state,event)}
    check('cash_change_invisible_to_selected_inputs',observations['cash']['same_method_inputs'])
    _,_,sale=next(x for x in fixtures.selected_cases() if x[2]['kind']=='sell')
    sale=deepcopy(sale);sale['date']=event['date']
    before=native.propose(*raw_args(state,sale));after=native.propose(*raw_args(normal['proposal']['after'],sale))
    check('sale_before_lot_rejects',before.get('reason')=='unknown_lot')
    check('sale_after_settlement_proposed',after['status']=='proposed')
    observations['ordering']={'before':before,'after_status':after['status'],
        'created_lot':normal['proposal']['after']['lots'][event['lot_id']]}
    zero=deepcopy(d);zero['family']['domains']['n']['interval'].update(lower='0/1',upper='0/1')
    for name in ['refund_cash','handling_cash']:zero['bindings'][name]['binding']['value']='0/1'
    monetary=joined.parent.assess(zero['family'],BUDGET);selected=joined.assess(zero,BUDGET)
    check('zero_monetary_balances',monetary['status']=='conditional_family_witness')
    check('zero_selected_quantity_excluded',selected['status']=='conditionally_infeasible')
    observations['zero_quantity']={'monetary_status':monetary['status'],'selected_status':selected['status'],
        'quantity_expression':next(x['predicate'] for x in d['requirements']['requirements'] if x['id']=='quantities')}
    temporal=stock_fixture();temporal['value_type']['context']['at']=event['date']
    # Give every type the same dated context so failure tests the time policy, not a mixed book.
    def date_types(x):
        if isinstance(x,dict):
            if x.get('kind')=='rational' and 'context' in x:x['context']['at']=event['date']
            for v in x.values():date_types(v)
        elif isinstance(x,list):
            for v in x:date_types(v)
    date_types(temporal);blocked=history.assess(temporal,HISTORY_BUDGET)
    check('dated_history_context_rejects',blocked.get('reason')=='time_declared_separately')
    observations['contexts']={'method':d['family']['method']['inputs']['n']['type']['context'],
        'history':stock_fixture()['value_type']['context'],'dated_history_result':blocked}
    check('original_fixture_unchanged',(state,event)==original)
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'observations':observations}

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else '--check';assert mode in ['--check','--record','--replay']
    started=time.monotonic();result=run();assert result['passed'],[x for x in result['checks'] if not x['passed']]
    names=['scripts/typed_return_transition_v1.py','scripts/native_return_state_structure_v1.py',
        'scripts/method_memory_effects_v1.py','scripts/method_monetary_effects_v1.py',
        'scripts/method_requirements_v3.py','scripts/typed_affine_history_v1.py',
        'scripts/conditional_history_family_v1.py','scripts/prerequisite_method_family_v1.py',
        'scripts/piecewise_method_family_v1.py','scripts/typed_history_measurement_attachment_v1.py',
        'data/accounting-master/typed-monetary-effects-20261024/examples.py',
        'data/accounting-master/typed-memory-effects-20261024/examples.py',
        'data/accounting-master/company-return-execution-20261024/native_returns.py',
        'tests/test_prerequisite_method_family_v1.py','tests/test_typed_return_transition_v1.py',
        'tests/test_typed_affine_history_v1.py',
        'docs/plans/accounting-method-history-composition-audit-20261024.md']
    lock={n:sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    if mode=='--record':
        assert not (HERE/'audit.json').exists()
        (HERE/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
        m={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           'command':'python3 -B '+str(HERE.relative_to(ROOT)/'probe.py')+' --record',
           'environment':platform.python_version()+'; Z3 '+joined.z3.get_version_string(),
           'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic probes',
           'wall_seconds':time.monotonic()-started,'data_version':lock,
           'plan':'docs/plans/accounting-method-history-composition-audit-20261024.md',
           'result':str(HERE.relative_to(ROOT)/'result.md'),
           'output':{'audit.json':sha256((HERE/'audit.json').read_bytes()).hexdigest(),
                     'probe.py':sha256(Path(__file__).read_bytes()).hexdigest()}}
        (HERE/'probe-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    if mode=='--replay':
        saved=json.loads((HERE/'probe-manifest.json').read_text());assert saved['data_version']==lock
        for name,digest in saved['output'].items():assert sha256((HERE/name).read_bytes()).hexdigest()==digest
        assert result==json.loads((HERE/'audit.json').read_text())
    print(json.dumps({'passed':True,'checks':len(result['checks']),'protected_sources':len(lock),'mode':mode}))
if __name__=='__main__':main()
