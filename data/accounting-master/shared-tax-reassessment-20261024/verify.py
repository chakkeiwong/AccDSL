"""Deterministic cumulative replacement evidence; actual state remains intact."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from fractions import Fraction as Q
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from examples import cases,m
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def canonical(x):return m.continuation.caller.canonical(x)

def conformance():
    checks=[];observations=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for path,h in lock.items():check('protected:'+path,sha(ROOT/path)==h)
    tests=json.loads((HERE/'test-observation.json').read_text())
    check('tests_pass',tests['exit_code']==0)
    for path,h in tests['files'].items():check('tested_bytes:'+path,sha(ROOT/path)==h)
    for row in cases():
        body=row['request'];before=canonical(body);r=m.propose(body);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(body)==before)
        check(name+':no_promotion',all(r[k] is False for k in m.FLAGS))
        if 'continuation_result' in r:
            expected=m.continuation.run(body['continuation_request'])
            check(name+':complete_upstream',canonical(r['continuation_result'])==canonical(expected))
        if r['status']=='proposed':
            a=r['after'];b=r['continuation_result']['after'];f=r['financial_calculation']
            check(name+':balanced_journal',sum(Q(v) for v in r['journal'].values())==0)
            check(name+':balanced_book',sum(Q(v) for v in a['balances'].values())==0)
            check(name+':four_statement_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':incremental_expense',Q(f['replacement_expense'])-Q(f['previous_expense'])==Q(r['journal']['current_tax']))
            check(name+':paid_cash_preserved',a['balances']['cash']==b['balances']['cash'] and a['flows']==b['flows'])
            check(name+':non_tax_balances',all(a['balances'][k]==v for k,v in b['balances'].items() if k not in ['current_tax','income_tax_payable']))
            check(name+':other_state_preserved',all(a[k]==v for k,v in b.items() if k not in ['balances','seen','date']))
            check(name+':payable_identity',Q(f['replacement_expense'])-Q(f['actual_paid'])==-Q(a['balances']['income_tax_payable'])>=0)
            totals=r['replacement_loss_result']['totals']
            check(name+':loss_conservation',Q(totals['opening'])+Q(totals['generated'])==Q(totals['used'])+Q(totals['expired'])+Q(totals['closing']))
            check(name+':assessment_endpoint',r['assessed_until']==body['interval']['end_exclusive'])
            applied=m.apply(body,r)
            check(name+':exact_apply',applied['status']=='applied' and canonical(applied['after'])==canonical(a))
        observations.append({**row,'result':r})
    by={r['case']:r['result'] for r in observations}
    check('positive_delta_19_over_4',by['positive_paid']['journal']['current_tax']=='19/4')
    check('unpaid_reversal_minus_quarter',by['unpaid_reversal']['journal']['current_tax']=='-1/4')
    check('refund_has_no_financial_state','after' not in by['paid_refund_route_refused'])
    check('loss_replaced_not_combined',sum(Q(l['remaining']) for l in by['replace_provisional_loss']['loss_state']['lots'])==7)
    check('original_usage_19_not_20',by['reuse_original_inventory']['loss_state']['lots'][0]['used']=='19/1')
    return checks,observations,tests,lock

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already frozen'
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','files']:
            for name,h in manifest[group].items():assert sha(ROOT/name)==h,name
    checks,rows,tests,lock=conformance();passed=all(c['passed'] for c in checks)
    observation={'passed':passed,'checks':len(checks),'cases':len(rows),'protected_files':len(lock),
        'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],
        'whole_requirements_closed':0,'actual_tax_assessed':False,'committed':False,'native_financial_carry':False}
    if not passed:dump(HERE/('failure-'+str(time.time_ns())+'.json'),checks)
    if passed and mode=='--record':
        dump(HERE/'checks.json',checks);dump(HERE/'cases.json',rows);dump(HERE/'check-names.json',[c['name'] for c in checks])
        selected=[p for p in HERE.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.txt']]
        selected += [ROOT/'scripts/shared_tax_reassessment_v1.py',ROOT/'tests/test_shared_tax_reassessment_v1.py',
                     ROOT/'docs/plans/accounting-tax-reassessment-integration-20261024.md']
        dump(HERE/'manifest.json',{'recorded_at':started,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/shared-tax-reassessment-20261024/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported','random_seeds':'N/A: deterministic conformance',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-shared-tax-reassessment-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md'),
            'observation':observation,'inputs':lock,'files':{str(p.relative_to(ROOT)):sha(p) for p in selected}})
    elif passed and mode=='--replay':
        assert canonical(checks)==canonical(json.loads((HERE/'checks.json').read_text()))
        assert canonical(rows)==canonical(json.loads((HERE/'cases.json').read_text()))
    print(json.dumps(observation));return not passed
if __name__=='__main__':raise SystemExit(main())
