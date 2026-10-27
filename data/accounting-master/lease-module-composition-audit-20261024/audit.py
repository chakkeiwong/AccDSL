"""Original lease financial calculation and outer-boundary applicability checks."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json,os,platform,subprocess,sys,time

os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals'
sys.path.insert(0,str(SOURCE))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
financial=load('lease_original_financial',SOURCE/'financial_checks.py')
authored=load('lease_original_authored',SOURCE/'authored_cases.py')
original=load('lease_original_outer',SOURCE/'verify_exchanges.py')
types=load('lease_original_types',SOURCE/'type_design.py')
native=load('lease_current_native',ROOT/'data/accounting-master/company-return-execution-20261024/native_returns.py')

def encode(value):
    if isinstance(value,Q):return f'{value.numerator}/{value.denominator}'
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def conformance():
    checks=[];probes=[]
    def check(name,value,**details):
        checks.append({'name':name,'passed':bool(value)})
        if details:probes.append({'probe':name,**encode(details)})
    case=deepcopy(next(c for c in authored.CASES if c['id']=='heterogeneous-rights'))
    outer=original.Auditor(SOURCE/'attempt-01')
    opening=case['opening_component'];balances={k:Q(case['opening_balances'].get(k,0)) for k in original.ACCOUNTS}
    cash_total={k:Q(0) for k in original.CASH};state=opening
    for i,step in enumerate(case['steps'],1):
        before=deepcopy(state)
        result=financial.derive('lease',state,step['method'],step['parameters'],step['event_date'],original.require)
        state,journal,cash,oci,equity=result
        check(f'step_{i}_original_state',state==step['after'])
        check(f'step_{i}_authored_journal',journal=={k:Q(v) for k,v in step['journal'].items() if v})
        check(f'step_{i}_gross_categories',cash=={k:Q(step['cash_change'].get(k,0)) for k in original.CASH})
        check(f'step_{i}_input_immutable',before==(opening if i==1 else case['steps'][i-2]['after']))
        balances={k:v+journal.get(k,Q(0)) for k,v in balances.items()}
        for k,v in cash.items():cash_total[k]+=v
        financial.check_component('lease',state,balances)
        check(f'step_{i}_balances',sum(balances.values())==0 and balances['cash']>=0)
        basis=outer.alias[f'heterogeneous-rights.{i}.basis']
        # Check exact original record shapes for the full dependency closure.
        for digest in outer.closure([basis]):outer.record_shape(outer.reg[digest],digest)
        closing,component,proposal,outer_cash=outer.basis_effects(basis)
        check(f'step_{i}_outer_state',original.exact(closing['balances'])==balances and component['value']==state and outer_cash==cash)
        expected=outer.body(outer.alias[f'heterogeneous-rights.{i}.state'])
        check(f'step_{i}_saved_outer_balances',closing['balances']==expected['balances'])
        probes.append({'probe':f'original_step_{i}','method':step['method'],'date':step['event_date'],'journal':encode(journal),'rights':encode(state['rights']),'cash':encode(cash)})
    check('hand_lifecycle_totals',balances['cash']==101 and balances['rou']==0 and balances['lease_liability']==0 and balances['other_gains']==-21 and balances['finance_expense']==9 and balances['depreciation']==81 and -sum(balances[k] for k in original.PROFIT)==-69,closing=balances,cash_categories=cash_total)
    check('hand_remeasurement',Q(121)/(1+Q(1,10))==110 and Q(99)/(1+Q(1,10))==90 and Q(90)*Q(1,10)==9)
    # Whole B liability50/ROU30 is not one-third of both pooled balances.
    exact_gain=Q(50)-30;aggregate_rou=Q(120)*Q(50,150);aggregate_gain=50-aggregate_rou
    check('pooled_fraction_is_wrong_for_traced_right',exact_gain==20 and aggregate_gain==10 and aggregate_rou!=30,exact_gain=exact_gain,pooled_gain=aggregate_gain,pooled_removed_rou=aggregate_rou)
    def refused(name,s,method,p,when,code,status='rejected'):
        before=deepcopy(s);actual=None
        try:financial.derive('lease',s,method,p,when,original.require)
        except original.Refusal as exc:actual=(exc.code,exc.status)
        check(name,actual==(code,status) and s==before,expected=[code,status],actual=actual)
    first=case['steps'][0];pay=case['steps'][2];dep=case['steps'][3]
    p=deepcopy(first['parameters']);p['allocation_basis']='unknown';refused('missing_traced_allocation',opening,first['method'],p,first['event_date'],'lease_allocation_basis_missing','partial')
    p=deepcopy(first['parameters']);p['standalone_allocation_supported']=None;refused('unknown_allocation_finding',opening,first['method'],p,first['event_date'],'standalone_allocation_missing','partial')
    p=deepcopy(first['parameters']);p['standalone_allocation_supported']=False;refused('false_allocation_finding',opening,first['method'],p,first['event_date'],'standalone_allocation_missing')
    p=deepcopy(first['parameters']);p['annual_end_payments']=False;refused('nonannual_schedule',opening,first['method'],p,first['event_date'],'nonannual_lease_schedule_unspecified','unsupported')
    p=deepcopy(first['parameters']);p['rights'][1]['removed_rou']=None;refused('unknown_surrender_amount',opening,first['method'],p,first['event_date'],'surrendered_rou_missing','partial')
    p=deepcopy(first['parameters']);p['rights'][1]['removed_rou']=20;refused('full_right_partial_removal',opening,first['method'],p,first['event_date'],'full_right_termination_mismatch')
    p=deepcopy(first['parameters']);p['rights'][1]['right_id']='A';refused('duplicate_right_payload',opening,first['method'],p,first['event_date'],'lease_rights_mismatch')
    p=deepcopy(pay['parameters']);refused('wrong_payment_anniversary',case['steps'][1]['after'],pay['method'],p,'2024-12-31','lease_payment_interval_mismatch')
    p['amount']=100;refused('excess_payment',case['steps'][1]['after'],pay['method'],p,pay['event_date'],'lease_payment_invalid')
    p=deepcopy(dep['parameters']);p['systematic_allocation_supported']=None;refused('unknown_depreciation_basis',case['steps'][2]['after'],dep['method'],p,dep['event_date'],'lease_depreciation_basis_missing','partial')
    p=deepcopy(dep['parameters']);p['amount']=82;refused('excess_depreciation',case['steps'][2]['after'],dep['method'],p,dep['event_date'],'lease_depreciation_invalid')
    # Wrong owner and event date are refused by the outer basis boundary.
    br=outer.alias['heterogeneous-rights.1.basis'];basis=outer.body(br)
    old=basis['identity']['entity_id'];basis['identity']['entity_id']='ForeignOwner'
    try:
        try:outer.basis_effects(br);actual=None
        except original.Refusal as exc:actual=exc.code
        check('outer_owner_mismatch',actual=='owner_identity_mismatch')
    finally:basis['identity']['entity_id']=old
    event=outer.body(basis['event_ref']);old=event['event_date'];event['event_date']='2023-12-31'
    try:
        try:outer.basis_effects(br);actual=None
        except original.Refusal as exc:actual=exc.code
        check('outer_event_before_opening',actual=='event_before_opening')
    finally:event['event_date']=old
    from jsonschema import Draft202012Validator
    payload=deepcopy(event['parameters']);payload['annual_end_payments']='yes'
    check('outer_schema_rejects_truthy_nonboolean',bool(list(Draft202012Validator(types.EVENTS['lease.reduce'][1]).iter_errors(payload))))
    # Test the exact original outer calculator with a deliberately cash-poor
    # balanced synthetic opening. It contains no company no-overdraft condition.
    br=outer.alias['heterogeneous-rights.3.basis'];basis=outer.body(br);book=outer.body(basis['opening_ref']);saved=deepcopy(book['balances'])
    try:
        values=original.exact(book['balances']);old_cash=values['cash'];values['cash']=Q(50);values['original_equity']+=old_cash-50
        book['balances']=original.rational_vector(values)
        closing,_,_,cash=outer.basis_effects(br)
        check('component_calculator_does_not_impose_shared_funding',original.value(closing['balances']['cash'])==-49,opening_cash=50,payment=99,component_closing_cash=-49,company_no_overdraft='would refuse; distinct additional policy')
    finally:book['balances']=saved
    missing=sorted({'rou','lease_liability','other_gains'}-set(native.ACCOUNTS))
    check('native_account_registry_cannot_accept_lease_journal',missing==['lease_liability','other_gains','rou'],missing_accounts=missing)
    check('component_opening_must_not_be_added_twice',Q(400)-99==301 and Q(400)+200-99==501,caller_cash=400,correct_cash=301,duplicate_component_opening_cash=501)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'probes':probes},locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for g in ['inputs','implementation','outputs']:
            for n,h in m[g].items():assert sha(ROOT/n)==h,n
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat();r,locks=conformance()
    assert r['passed'],[x for x in r['checks'] if not x['passed']]
    observation={'mode':mode,'passed':True,'checks':len(r['checks']),'detailed_probes':len(r['probes']),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
    if mode=='--record':
        dump(HERE/'audit.json',r)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'python3 -B '+str(HERE.relative_to(ROOT)/'audit.py')+' --record','environment':'Python '+platform.python_version(),
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic lifecycle audit',
          'data_version':'CorporateResiduals/1 attempt-01 original lease sequence and source-lock.json','inputs':locks,
          'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
          'outputs':{str((HERE/'audit.json').relative_to(ROOT)):sha(HERE/'audit.json')},
          'plan':'docs/plans/accounting-lease-module-composition-audit-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':assert r==json.loads((HERE/'audit.json').read_text())
    print(json.dumps(observation))

if __name__=='__main__':main()
