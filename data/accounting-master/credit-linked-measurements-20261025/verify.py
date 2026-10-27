"""Record once, then replay exact expressions and all retained native refusals."""
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

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')


def main():
    record='--record' in sys.argv; started=time.monotonic()
    if record: assert not (HERE/'evidence.json').exists()
    reads=set(); transient={}; tracking={'active':True,'test':None}
    def capture(event,args):
        if event!='open' or not tracking['active'] or not isinstance(args[0],(str,bytes)): return
        name,mode,flags=args
        if mode is not None and 'r' not in mode and '+' not in mode: return
        if mode is None and flags & 3 == 1: return
        p=Path(name.decode() if isinstance(name,bytes) else name).resolve()
        if p.suffix=='.pyc':
            try: p=Path(importlib.util.source_from_cache(str(p)))
            except ValueError: return
        if p.is_relative_to(ROOT) and p.is_file():
            reads.add(p)
            relative=p.relative_to(ROOT)
            if len(relative.parts)>2 and relative.parts[0]=='data' and relative.parts[1].startswith('tmp'):
                tracking['active']=False
                try: raw=p.read_bytes()
                finally: tracking['active']=True
                assert len(raw)<=131072,'transient_fixture_budget'
                transient[p]={'test':tracking['test'],'name':p.name,
                    'sha256':sha256(raw).hexdigest(),'bytes_hex':raw.hex()}
    sys.addaudithook(capture)
    import credit_linked_schedule_v1 as schedule
    tracking['active']=False
    patterns=['test_credit_linked_schedule_v1.py','test_sector_reference_binding_v1.py',
              'test_company_book_transition_v1.py','test_company_book_transition_v2.py']
    tests=[]
    for pattern in patterns:
        tracking['test']=pattern; tracking['active']=True; stream=io.StringIO()
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        tracking['active']=False
        assert result.wasSuccessful() and result.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record: (HERE/(pattern+'.log')).write_text(stream.getvalue())
        print(json.dumps({'tests':pattern,'passed':result.testsRun}),flush=True)
    folder=HERE/'cases'
    if record: folder.mkdir(exist_ok=True)
    tracking['active']=True; native_rows=schedule.retained(); tracking['active']=False
    cases=[]
    for native_row in native_rows:
        tracking['active']=True
        req=schedule.request(native_row['id']); before=deepcopy(req); result=schedule.calculate(req)
        tracking['active']=False
        assert before==req and result['status']=='certified_read_only',result.get('reason')
        row={'id':native_row['id'],'request':req,'result':result}; path=folder/(row['id']+'.json')
        if record:
            if path.exists(): assert row==json.loads(path.read_text()),'changed_recovered_case:'+row['id']
            else: dump(path,row)
        else: assert row==json.loads(path.read_text()),row['id']
        cases.append({'id':row['id'],'path':str(path.relative_to(ROOT)),'sha256':sha(path),
            'stages':len(result['schedule']['stages']),'journals':len(result['schedule']['journals']),
            'identities':len(result['certificates']['identities']),
            'authored_targets':len(result['certificates']['authored_targets']),
            'containment_checks':len(result['certificates']['containment'])})
    tracking['active']=True
    adverse=json.loads((schedule.NATIVE/'attempt-01/adverse.json').read_text()); refusals=[]
    for old in adverse:
        req={'profile':schedule.PROFILE,'case_id':native_rows[0]['id'],'native_request':deepcopy(old['request']),
             'native_request_sha256':schedule.digest(old['request']),
             'expected_native_result_sha256':schedule.digest(old['result'])}
        before=deepcopy(req); result=schedule.calculate(req)
        assert before==req and result['reason']=='native_refusal' and result['native_refusal']==old['result'],old['id']
        assert not result['posts'] and result['mutations']==[] and 'schedule' not in result
        refusals.append({'id':old['id'],'request':req,'result':result})
    tracking['active']=False
    path=HERE/'native-refusals.json'
    if record: dump(path,refusals)
    else: assert refusals==json.loads(path.read_text())
    locks={}
    def lock(p,expected=None):
        p=p if isinstance(p,Path) else ROOT/p; actual=sha(p)
        if expected is not None: assert actual==expected,str(p)
        locks[str(p.relative_to(ROOT))]=actual
    prior=ROOT/'data/accounting-master/credit-posting-representation-20261025/source-lock.json'
    for n,h in json.loads(prior.read_text()).items(): lock(n,h)
    lock(prior)
    for p in sorted(reads):
        if p.exists(): lock(p)
        else: assert p in transient,'disappeared_nonfixture:'+str(p)
    fixture_rows=sorted(transient.values(),key=lambda r:(r['test'],r['name'],r['sha256']))
    fixture_path=HERE/'transient-fixtures.json'
    if record: dump(fixture_path,fixture_rows)
    else: assert fixture_rows==json.loads(fixture_path.read_text())
    lock(fixture_path)
    for p in [Path(__file__),HERE/'audit.md',ROOT/'docs/plans/accounting-credit-linked-measurements-20261025.md']:
        lock(p)
    for c in cases: lock(c['path'],c['sha256'])
    lock(path)
    evidence={'tests':tests,'cases':cases,'case_count':len(cases),'native_refusals':len(refusals),
        'transient_test_fixtures':len(fixture_rows),
        'totals':{k:sum(c[k] for c in cases) for k in ['stages','journals','identities','authored_targets','containment_checks']},
        'scope':'Exact read-only shared-factor schedules; no host posting or accounting admission',
        'primary_criterion':'All required identities, authored targets, complete native structure and enclosure containment'}
    if record:
        dump(HERE/'evidence.json',evidence); lock(HERE/'evidence.json')
        for pattern in patterns: lock(HERE/(pattern+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/credit-linked-measurements-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact rational algebra; no GPU framework imported',
            'seeds':'N/A deterministic','data_version':'Nine retained dated-credit attempt-01 exchanges and adverse cases',
            'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-credit-linked-measurements-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),'provenance':'Git base plus exact uncommitted source hashes',
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text())
        saved=json.loads((HERE/'source-lock.json').read_text())
        for n,h in saved.items(): assert sha(ROOT/n)==h,n
        for n,h in locks.items(): assert saved[n]==h,n
        for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items(): assert sha(ROOT/n)==h,n
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
        'focused':tests[0]['count'],'regressions':sum(r['count'] for r in tests[1:]),
        'cases':len(cases),'native_refusals':len(refusals),'totals':evidence['totals'],
        'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}),flush=True)


if __name__=='__main__': main()
