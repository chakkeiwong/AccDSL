"""Record exact continuation cases without promoting synthetic accounting claims."""
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
def canonical(x):return m.caller.canonical(x)

def conformance():
    checks=[];observations=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for path,h in lock.items():check('protected:'+path,sha(ROOT/path)==h)
    tests=json.loads((HERE/'test-observation.json').read_text())
    check('focused_regression_pass',tests['exit_code']==0)
    for path,h in tests['files'].items():check('tested_bytes:'+path,sha(ROOT/path)==h)
    for row in cases():
        body=row['request'];before=canonical(body);r=m.run(body);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(body)==before)
        check(name+':no_promotion',all(r[k] is False for k in m.FLAGS))
        if r['status'] in ['complete','stopped']:
            after=r['after'];origin=body['origin'];native=r['native_report']
            check(name+':exact_origin',canonical(r['origin'])==canonical(origin))
            check(name+':loss_unchanged',canonical(r['loss_state'])==canonical(origin['loss_state']))
            check(name+':full_native_report',canonical(native)==canonical(r['loss_result']['reconciliation_result']['information_result']['native_report']))
            check(name+':all_accounts',set(after['balances'])==set(m.ACCOUNTS))
            check(name+':balanced',sum(Q(v) for v in after['balances'].values())==0)
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':fixed_tax_and_deferred',all(after['balances'][k]==origin['balances'][k] for k in ['current_tax','dta','dtl','deferred_tax']))
            check(name+':native_close_preserved',after['tax_closed_until']==origin['native_tax_closed_until'])
            check(name+':assessment_preserved',r['assessed_until']==origin['assessed_until'])
            check(name+':complete_partition',len(r['trace'])+len(r['remaining_operations'])==len(body['operations']))
            if r['status']=='stopped':check(name+':expected_stop',r['stop']['status']==row['expected_stop'])
            else:check(name+':no_stop',r['stop'] is None and not r['remaining_operations'])
            applied=m.apply(body,r)
            check(name+':exact_apply',applied['status']=='applied_prefix' and canonical(applied['after'])==canonical(after))
        observations.append({**row,'result':r})
    by={r['case']:r['result'] for r in observations}
    check('mixed_cash_arithmetic',by['mixed_paid']['after']['balances']['cash']=='721/2')
    check('mixed_profit_arithmetic',by['mixed_paid']['recorded_statements']['recorded_profit']=='9/2')
    check('unpaid_preserves_cash_and_liability',by['mixed_unpaid']['after']['balances']['cash']=='361/1' and by['mixed_unpaid']['after']['balances']['income_tax_payable']=='-1/2')
    check('tax_first_prefix_cash',by['tax_first_funding_failure']['after']['balances']['cash']=='483/4')
    check('lease_first_prefix_cash',by['lease_first_funding_failure']['after']['balances']['cash']=='1/4')
    check('post_assessment_return_adjustment',by['mixed_paid']['after']['tax_adjustments'][-1]['amount']=='-24/1')
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
        selected += [ROOT/'scripts/shared_tax_continuation_v1.py',ROOT/'tests/test_shared_tax_continuation_v1.py',
                     ROOT/'docs/plans/accounting-tax-continuation-integration-20261024.md']
        dump(HERE/'manifest.json',{'recorded_at':started,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/shared-tax-continuation-20261024/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported','random_seeds':'N/A: deterministic conformance',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-shared-tax-continuation-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'observation':observation,'inputs':lock,'files':{str(p.relative_to(ROOT)):sha(p) for p in selected}})
    elif passed and mode=='--replay':
        assert canonical(checks)==canonical(json.loads((HERE/'checks.json').read_text()))
        assert canonical(rows)==canonical(json.loads((HERE/'cases.json').read_text()))
    print(json.dumps(observation));return not passed
if __name__=='__main__':raise SystemExit(main())
