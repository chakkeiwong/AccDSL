from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime, timezone
import json, platform, subprocess, sys, time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import shared_tax_reconciliation_v1 as m
import examples
def sha(p):return sha256(p.read_bytes()).hexdigest()
def same(a,b):return m.book.caller.canonical(a)==m.book.caller.canonical(b)
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    m.protected();checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    rows=[]
    for row in examples.cases():
        name=row['case'];body=row['request'];before=m.book.digest(body);r=m.calculate(body)
        check(name+':status',r['status']==row['expected_status'])
        check(name+':input_preserved',m.book.digest(body)==before)
        check(name+':flags',all(r[k] is False for k in m.FLAGS))
        check(name+':replay',m.verify_result(body,r))
        if 'request' in r:check(name+':request_complete',same(r['request'],body))
        if 'information_result' in r:
            check(name+':information_complete',same(r['information_result'],m.information.assess(body['information_request'])))
        if 'calculation' in r:
            c=r['calculation'];check(name+':pretax',c['pretax_income']=='5/1')
            check(name+':signed_adjustments',Q(c['signed_adjustments'])==sum(Q(v) for v in c['adjustment_totals'].values()))
            check(name+':taxable',Q(c['taxable_profit'])==Q(c['pretax_income'])+Q(c['signed_adjustments']))
            check(name+':native_once',c['native_adjustment_ids']==['return_settlement'])
            check(name+':basis',all(v['rights_total']==v['account_basis'] for v in c['basis_reconciliations'].values()))
            if r['status']=='conditional_gross_current_tax':
                check(name+':gross',Q(c['gross_current_tax'])==Q(c['rate'])*Q(c['taxable_profit']))
                check(name+':nonnegative',Q(c['taxable_profit'])>=0)
            else:check(name+':no_negative_tax',Q(c['taxable_profit'])<0 and 'gross_current_tax' not in c)
            check(name+':native_annual_unresolved',r['information_result']['native_report']['coverage']['annual_completion']=='unresolved')
        rows.append({**row,'result':r})
    by={r['case']:r['result'] for r in rows}
    check('independent_loss',by['mixed_negative_expression']['calculation']['taxable_profit']=='-19/1')
    check('independent_positive',by['hypothetical_positive_expression']['calculation']['gross_current_tax']=='21/4')
    check('independent_zero',by['hypothetical_zero_expression']['calculation']['gross_current_tax']=='0/1')
    check('rejected_basis_preserves_report',by['opening_asset_basis_mismatch']['information_result']['native_report']['income_recorded']['recorded_profit']=='5/1')
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    check('tested_hashes',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'cases':len(rows),'protected_files':len(locks),
        'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],
        'whole_requirements_closed':0,'actual_tax_assessed':False,'posted':False}
    if mode=='--record':
        dump('cases.json',rows);dump('checks.json',report);dump('check-names.json',checks)
        files=[p for p in HERE.iterdir() if p.is_file()]+[ROOT/'scripts/shared_tax_reconciliation_v1.py',
            ROOT/'tests/test_shared_tax_reconciliation_v1.py',ROOT/'docs/plans/accounting-tax-reconciliation-integration-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/shared-tax-reconciliation-20261024/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic checks',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-shared-tax-reconciliation-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})
    elif mode=='--replay':
        assert same(report,json.loads((HERE/'checks.json').read_text()))
        assert same(rows,json.loads((HERE/'cases.json').read_text()))
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    print(json.dumps(report))
if __name__=='__main__':main()
