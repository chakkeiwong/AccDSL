from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone
import json,platform,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import conditional_tax_losses_v1 as m
import examples
def sha(p):return sha256(p.read_bytes()).hexdigest()
def same(a,b):return m.book.caller.canonical(a)==m.book.caller.canonical(b)
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    m.protected();checks=[]
    def check(n,ok):
        assert ok,n
        checks.append(n)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for n,h in locks.items():check('protected:'+n,sha(ROOT/n)==h)
    output=[]
    for row in examples.cases():
        n=row['case'];body=row['request'];before=m.book.digest(body);r=m.propose(body)
        check(n+':status',r['status']==row['expected_status'])
        check(n+':input_unchanged',m.book.digest(body)==before)
        check(n+':flags',all(r[k] is False for k in m.FLAGS))
        check(n+':recompute',same(r,m.propose(body)))
        if 'reconciliation_result' in r:
            check(n+':complete_native_reconciliation',same(r['reconciliation_result'],m.tax.calculate(body['reconciliation_request'])))
        if r['status']=='proposed':
            p=r['proposal'];q={k:Q(v) for k,v in p['totals'].items()}
            check(n+':conservation',q['opening']+q['generated']==q['used']+q['expired']+q['closing'])
            check(n+':nonnegative',all(v>=0 for v in q.values()))
            check(n+':per_lot',all(Q(l['original'])==sum(Q(l[k]) for k in ['remaining','used','expired']) for l in p['after']['lots']))
            check(n+':movement_totals',all(sum(Q(v[k]) for v in p['movements'].values())==q[k] for k in q))
            check(n+':apply',same(m.apply(body,r)['after'],p['after']))
            check(n+':no_negative_tax',Q(p['conditional_gross_current_tax'])>=0)
            check(n+':cursor',p['after']['cursor']==body['reconciliation_request']['information_request']['interval']['end_exclusive'])
            check(n+':step_retained',p['after']['seen']==body['state']['seen']+[body['step_id']])
        output.append({**row,'result':r})
    by={r['case']:r['result'] for r in output}
    check('independent_generation',by['generate_19']['proposal']['totals']['generated']=='19/1')
    check('independent_usage',by['consume_19_from_21']['proposal']['conditional_gross_current_tax']=='1/2')
    check('independent_partial',by['partial_use_7']['proposal']['totals']['closing']=='12/1')
    check('independent_expiry',by['expiry_at_endpoint_allows_use_then_expires']['proposal']['totals']['expired']=='12/1')
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    check('tested_hashes',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'cases':len(output),'protected_files':len(locks),
        'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],
        'whole_requirements_closed':0,'actual_tax_assessed':False,'native_financial_carry':False}
    if mode=='--record':
        dump('cases.json',output);dump('checks.json',report);dump('check-names.json',checks)
        files=[p for p in HERE.iterdir() if p.is_file()]+[ROOT/'scripts/conditional_tax_losses_v1.py',
            ROOT/'tests/test_conditional_tax_losses_v1.py',ROOT/'docs/plans/accounting-tax-loss-integration-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/conditional-tax-losses-20261024/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic conformance',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-conditional-tax-losses-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})
    elif mode=='--replay':
        assert same(report,json.loads((HERE/'checks.json').read_text()))
        assert same(output,json.loads((HERE/'cases.json').read_text()))
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    print(json.dumps(report))
if __name__=='__main__':main()
