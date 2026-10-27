from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from datetime import datetime,timezone
import json,platform,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import shared_book_statements_v1 as m
import examples
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check';assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    m.protected();checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for n,h in locks.items():check('protected:'+n,sha(ROOT/n)==h)
    out=[]
    for row in examples.cases():
        name=row['case'];body=row['request'];before=m.book.digest(body);r=m.calculate(body)
        check(name+':status',r['status']==row['expected_status'])
        check(name+':immutable',before==m.book.digest(body))
        check(name+':replay',m.verify_result(body,r))
        check(name+':flags',all(r[k] is False for k in m.FLAGS))
        if r['status']=='recorded_prefix':
            bs=r['balance_sheet_recorded'];eq=r['equity_recorded'];cf=r['cash_flows_recorded'];ind=r['indirect_operating_recorded']
            check(name+':balance_sheet',Q(bs['total_assets'])-Q(bs['total_liabilities'])==Q(bs['equity_including_recorded_profit']))
            check(name+':equity',Q(eq['opening'])+Q(eq['recorded_profit'])+Q(eq['owner_movement'])==Q(eq['closing']))
            check(name+':direct_cash',Q(cf['closing_cash'])-Q(cf['opening_cash'])==sum(Q(v['net']) for v in cf['activities'].values()))
            check(name+':indirect_cash',sum(Q(v) for v in ind['items'].values())==Q(cf['activities']['operating']['net']))
            check(name+':gross_flows',cf['gross_origins']==r['execution']['after']['flows'])
            check(name+':tax_unknown',r['coverage']['tax_assessment']=='unresolved' and r['income_recorded']['tax_assessment']=='unresolved')
            check(name+':period_unknown',r['coverage']['period_completion']==r['coverage']['annual_completion']=='unresolved')
            check(name+':prefix_count',r['coverage']['completed_events']==len(r['execution']['after']['seen']))
            check(name+':classification',sorted(x for v in r['account_classes'].values() for x in v)==sorted(m.book.ACCOUNTS))
        out.append({**row,'result':r})
    mixed=out[0]['result'];check('mixed_expected',mixed['income_recorded']['recorded_profit']=='5/1' and mixed['cash_flows_recorded']['closing_cash']=='361/1')
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests',tests['exit_code']==0)
    check('test_hashes',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'cases':len(out),'protected_files':len(locks),'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],'whole_requirements_closed':0}
    if mode=='--record':
        dump('cases.json',out);dump('checks.json',report);dump('check-names.json',checks)
        files=[p for p in HERE.glob('*') if p.is_file()]+[ROOT/'scripts/shared_book_statements_v1.py',ROOT/'tests/test_shared_book_statements_v1.py',ROOT/'docs/plans/accounting-shared-statement-integration-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record','environment':{'python':platform.python_version(),'executable':sys.executable},'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic reference checks','wall_seconds':time.monotonic()-start,'data_version':'source-lock.json','plan':'docs/plans/accounting-shared-book-statements-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})
    elif mode=='--replay':
        assert report==json.loads((HERE/'checks.json').read_text())
        assert out==json.loads((HERE/'cases.json').read_text())
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    print(json.dumps(report))
if __name__=='__main__':main()
