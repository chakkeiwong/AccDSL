from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from datetime import datetime,timezone
import json,platform,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import shared_state_compatibility_v1 as m
import module_invocation_v1 as caller
import examples
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    m.protected();checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for n,h in locks.items():check('protected:'+n,sha(ROOT/n)==h)
    rows=examples.cases();saved=json.loads((HERE/'cases.json').read_text()) if mode=='--replay' else None
    result=[];effects={}
    for i,row in enumerate(rows):
        before=caller.digest(row['request']);r=m.assess(row['request'])
        check(row['case']+':status',r['status']==row['expected_status'])
        check(row['case']+':immutable',before==caller.digest(row['request']))
        check(row['case']+':flags',all(r[k] is False for k in m.FLAGS))
        check(row['case']+':replay',m.verify_result(row['request'],r))
        check(row['case']+':saved',saved is None or saved[i]=={**row,'result':r})
        result.append({**row,'result':r})
    for key,row in examples.originals().items():
        r=caller.invoke(row['request']);check(key+':original',r==row['result'])
        b=examples.states()[key];p=r['native_result']['proposal'];a=p['after']
        check(key+':journal_balance',sum(Q(v) for v in p['journal'].values())==0)
        check(key+':cash_flows',Q(p['journal']['cash'])==sum(Q(x['amount']) for x in p['flows']))
        for k,v in b['balances'].items():check(key+':delta:'+k,Q(a['balances'][k])-Q(v)==Q(p['journal'][k]))
        changed=[k for k in b if b[k]!=a[k]]
        expected={'balances','component','date','flows','lots','seen','tax_adjustments'} if key=='typed_return' else {'balances','leases','seen'}
        check(key+':memory_writes',set(changed)==expected)
        effects[key]={'before':b,'event':row['request']['payload'].get('event',json.loads(row['request']['payload'].get('event_text','{}'))),'native_result':r['native_result'],'changed_top_fields':changed,'unchanged_top_fields':sorted(set(b)-set(changed))}
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests',tests['exit_code']==0)
    check('test_hashes',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'cases':len(rows),'protected_files':len(locks),'test_methods':tests['test_methods'],'native_controls':2,'whole_requirements_closed':0}
    if mode=='--record':
        dump('cases.json',result);dump('native-effects.json',effects);dump('checks.json',report);dump('check-names.json',checks)
        paths=[p for p in HERE.glob('*') if p.is_file()]+[ROOT/'scripts/shared_state_compatibility_v1.py',ROOT/'tests/test_shared_state_compatibility_v1.py',ROOT/'docs/plans/accounting-shared-book-successor-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record','environment':{'python':platform.python_version(),'executable':sys.executable},'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic reference checks','wall_seconds':time.monotonic()-start,'data_version':'source-lock.json','plan':'docs/plans/accounting-shared-state-compatibility-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}})
    elif mode=='--replay':
        assert report==json.loads((HERE/'checks.json').read_text())
        assert effects==json.loads((HERE/'native-effects.json').read_text())
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    print(json.dumps(report))
if __name__=='__main__':main()
