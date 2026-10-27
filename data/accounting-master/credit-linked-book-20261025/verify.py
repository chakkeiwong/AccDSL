"""Record and replay complete exact book proposals and boundary refusals."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util
import io
import json
import platform
import subprocess
import sys
import time
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')

def main():
    record='--record' in sys.argv;started=time.monotonic()
    if record:assert not (HERE/'evidence.json').exists()
    reads=set();tracking={'active':True}
    def capture(event,args):
        if event!='open' or not tracking['active'] or not isinstance(args[0],(str,bytes)):return
        name,mode,flags=args
        if mode is not None and 'r' not in mode and '+' not in mode:return
        if mode is None and flags & 3 == 1:return
        p=Path(name.decode() if isinstance(name,bytes) else name).resolve()
        if p.suffix=='.pyc':
            try:p=Path(importlib.util.source_from_cache(str(p)))
            except ValueError:return
        if p.is_relative_to(ROOT) and p.is_file():reads.add(p)
    sys.addaudithook(capture)
    import examples as ex
    bridge=ex.bridge;tracking['active']=False
    patterns=['test_credit_linked_book_v1.py','test_credit_linked_schedule_v1.py',
              'test_company_book_transition_v1.py','test_company_book_transition_v2.py','test_company_book_reports_v1.py']
    tests=[]
    for pattern in patterns:
        stream=io.StringIO();tracking['active']=True
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);tracking['active']=False
        assert r.wasSuccessful() and r.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':r.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
        print(json.dumps({'tests':pattern,'passed':r.testsRun}),flush=True)
    folder=HERE/'cases'
    if record:folder.mkdir(exist_ok=False)
    tracking['active']=True;native=bridge.linked.retained();tracking['active']=False
    cases=[]
    for n in native:
        for chart in ['named','numbered']:
            for complement in [False,True]:
                tracking['active']=True;row=ex.checked_case(n['id'],chart,complement);tracking['active']=False
                p=folder/(row['id']+'.json')
                if record:dump(p,row)
                else:assert row==json.loads(p.read_text()),row['id']
                result=row['result'];cases.append({'id':row['id'],'path':str(p.relative_to(ROOT)),'sha256':sha(p),
                    'journals':len(result['trace']),'observations':len(result['observations']),
                    'identity_checks':len(result['identity_checks']),
                    'rational_host_observations':sum(r['status']=='rational_book_validated' for r in result['rational_host_checks'])})
    tracking['active']=True
    base=ex.fixture();refusals=[]
    changes=[('stale_result',lambda q:q.update(expected_linked_result_sha256='0'*64)),
             ('post',lambda q:q.update(operation='post')),('order',lambda q:q.update(operation='order')),
             ('multiple_roots',lambda q:q.update(operation='merge_roots')),
             ('role_alias',lambda q:q['roles'].update(gross=q['roles']['cash'])),
             ('allowance_liability',lambda q:q['opening']['accounts'][q['roles']['allowance']].update(classification='liability')),
             ('wrong_scale',lambda q:q['context_adapter'].update(unit_scale='1000/1')),
             ('foreign_root_context',lambda q:q['context_adapter'].update(native_context_sha256='0'*64)),
             ('missing_alias_premise',lambda q:q['context_adapter'].update(premise=' ')),
             ('truncated_period',lambda q:q['opening']['period'].update(end_exclusive='2027-01-01')),
             ('repeated_identity',lambda q:q['opening'].update(seen=['credit.partial-early-writeoff.acquisition']))]
    for name,change in changes:
        q=deepcopy(base);change(q);before=deepcopy(q);r=bridge.propose(q)
        assert q==before and r['status']!='proposed_exact_read_only' and 'trace' not in r
        assert r['mutations']==[] and not r['posts']
        refusals.append({'id':name,'request':q,'result':r})
    tracking['active']=False
    p=HERE/'refusals.json'
    if record:dump(p,refusals)
    else:assert refusals==json.loads(p.read_text())
    locks={}
    def lock(p,expected=None):
        p=p if isinstance(p,Path) else ROOT/p;h=sha(p)
        if expected is not None:assert h==expected,str(p)
        locks[str(p.relative_to(ROOT))]=h
    prior=ROOT/'data/accounting-master/credit-host-boundary-20261025'
    for n,h in json.loads((prior/'source-lock.json').read_text()).items():lock(n,h)
    for n,h in json.loads((prior/'acceptance-manifest.json').read_text())['artifacts'].items():lock(n,h)
    lock(prior/'acceptance-manifest.json')
    for p in sorted(reads):lock(p)
    for c in cases:lock(c['path'],c['sha256'])
    for p in [HERE/'refusals.json',Path(__file__),HERE/'examples.py',HERE/'audit.md',
              ROOT/'docs/plans/accounting-credit-linked-book-20261025.md']:lock(p)
    evidence={'tests':tests,'cases':cases,'case_count':len(cases),'native_cases':9,'charts':2,'complements':2,
        'refusals':len(refusals),'totals':{k:sum(c[k] for c in cases) for k in ['journals','observations','identity_checks','rational_host_observations']},
        'scope':'Optional single-root proposed trace, cumulative balances/profit and unclassified cash; no accounting or posting admission'}
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json')
        for pattern in patterns:lock(HERE/(pattern+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/credit-linked-book-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact rational-polynomial operations; no GPU framework imported',
            'seeds':'N/A deterministic','data_version':'Accepted nine native/linked schedules and constructed opening books',
            'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-credit-linked-book-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),'provenance':'Git base plus uncommitted source hashes',
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text())
        saved=json.loads((HERE/'source-lock.json').read_text())
        for n,h in saved.items():assert sha(ROOT/n)==h,n
        for n,h in locks.items():assert saved[n]==h,n
        for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/n)==h,n
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
        'focused':tests[0]['count'],'regressions':sum(t['count'] for t in tests[1:]),'cases':len(cases),
        'refusals':len(refusals),'totals':evidence['totals'],'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}),flush=True)
if __name__=='__main__':main()
