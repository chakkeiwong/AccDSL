from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from datetime import datetime,timezone
import json,platform,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import shared_book_successor_v1 as m
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
    rows=[]
    for row in examples.cases():
        name=row['case'];before=m.digest(row);result=m.run_prefix(row['opening'],row['events'])
        check(name+':status',result['status']==row['expected_status'])
        check(name+':stop',result.get('stop_status')==row['expected_stop'])
        check(name+':immutable',before==m.digest(row))
        check(name+':flags',all(result[k] is False for k in m.FLAGS))
        state=row['opening']
        for i,item in enumerate(result['trace']):
            r=item['result'];tag=name+':'+str(i)
            if r['status']!='proposed':
                check(tag+':prefix_preserved',result['after']==state);continue
            p=r['proposal'];a=p['after']
            check(tag+':journal_balance',sum(Q(v) for v in p['journal'].values())==0)
            check(tag+':cash_flow',Q(p['journal']['cash'])==sum(Q(f['amount']) for f in p['flows']))
            check(tag+':all_account_deltas',all(Q(a['balances'][k])-Q(v)==Q(p['journal'][k]) for k,v in state['balances'].items()))
            check(tag+':memory',all(state[k]==a[k] for k in state if k not in p['write_fields']))
            check(tag+':pure_apply',m.apply(state,item['event'],p).get('after')==a)
            state=a
        rows.append({**row,'result':result})
    comparators=examples.native_comparators()
    for i,row in enumerate(comparators):
        a=row['successor_result']['proposal'];b=row['original_result']['proposal'];name='native:'+str(i)
        check(name+':journal',all(Q(a['journal'].get(k,'0/1'))==Q(b['journal'].get(k,'0/1')) for k in set(a['journal'])|set(b['journal'])))
        check(name+':flows',[(f['activity'],f['amount']) for f in a['flows']]==[(f['activity'],f['amount']) for f in b['flows']])
        if row['module']=='lease':check(name+':memory',[x['component'] for x in a['after']['leases']]==[x['component'] for x in b['after']['leases']])
        else:
            check(name+':component',a['after']['component']==b['after']['component'])
            strip=lambda lots:{k:{x:y for x,y in v.items() if x!='acquired'} for k,v in lots.items()}
            check(name+':lots',strip(a['after']['lots'])==strip(b['after']['lots']))
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests',tests['exit_code']==0)
    check('test_hashes',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'cases':len(rows),'native_comparators':len(comparators),'protected_files':len(locks),'test_methods':tests['test_methods'],'regression_methods':tests['regression_methods'],'whole_requirements_closed':0}
    if mode=='--record':
        dump('cases.json',rows);dump('native-comparators.json',comparators);dump('schema.json',m.schema());dump('checks.json',report);dump('check-names.json',checks)
        paths=[p for p in HERE.glob('*') if p.is_file()]+[ROOT/'scripts/shared_book_successor_v1.py',ROOT/'tests/test_shared_book_successor_v1.py',ROOT/'docs/plans/accounting-shared-book-integration-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record','environment':{'python':platform.python_version(),'executable':sys.executable},'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic reference checks','wall_seconds':time.monotonic()-start,'data_version':'source-lock.json','plan':'docs/plans/accounting-shared-book-successor-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}})
    elif mode=='--replay':
        assert report==json.loads((HERE/'checks.json').read_text())
        assert rows==json.loads((HERE/'cases.json').read_text())
        assert comparators==json.loads((HERE/'native-comparators.json').read_text())
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    print(json.dumps(report))
if __name__=='__main__':main()
