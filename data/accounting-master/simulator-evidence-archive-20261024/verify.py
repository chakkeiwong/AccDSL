"""Exact byte retention, bounded recovery regressions and protected-source replay."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,tempfile,time,unittest

os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import simulator_evidence_archive_v1 as archive
from test_simulator_evidence_archive_v1 import ArchiveTests,LIMITS,bundle,record

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def cases():
    rows=json.loads((ROOT/'data/accounting-master/sequential-outcome-range-20261024/cases.json').read_text())
    candidate=next(r for r in rows if r['case']=='candidate_obligations')
    full=rows[0]
    def rec(name,role,value,deps=()):
        return {'name':name,'role':role,'profile':value['profile'],'json':json.dumps(value,ensure_ascii=False,indent=2),'dependencies':list(deps)}
    return [
      {'case':'scalar_exact','bundle':bundle(record())},
      {'case':'unicode_first','bundle':bundle(record(text='{"profile":"Example/1","label":"café"}'))},
      {'case':'unicode_distinct','bundle':bundle(record(text='{"profile":"Example/1","label":"cafe\u0301"}'))},
      {'case':'ordered_dependencies','bundle':bundle(record('a'),record('b'),record('c',dependencies=['b','a']))},
      {'case':'whole_range_evidence','bundle':bundle(rec('opening','state',full['request']['family']['first_family']['state']),rec('query','definition',full['request'],['opening']),rec('answer','result',full['result'],['query','opening']))},
      {'case':'candidate_obligations','bundle':bundle(rec('query','definition',candidate['request']),rec('answer','result',candidate['result'],['query']))},
    ]

def conformance(retained=None):
    checks=[];rows=cases() if retained is None else retained
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    outputs=[]
    with tempfile.TemporaryDirectory(prefix='accdsl-archive-verify-',dir='/tmp') as tmp:
        path=Path(tmp)/'archive.db'
        with archive.Archive(path,LIMITS) as db:
            for row in rows:
                result=db.archive(row['bundle']);read=db.read(result['receipt'])
                check(row['case']+'_bytes',read['bundle']==row['bundle'])
                check(row['case']+'_retry',db.archive(row['bundle'])==result)
                check(row['case']+'_boundary',all(read[k] is False and result[k] is False for k in archive.BOUNDARY))
                if 'result' in row:check(row['case']+'_saved_receipt',result==row['result'])
                outputs.append({'case':row['case'],'bundle':row['bundle'],'limits':LIMITS,'result':result})
        with archive.Archive(path,LIMITS) as db:
            for row in outputs:check(row['case']+'_reopen',db.read(row['result']['receipt'])['bundle']==row['bundle'])
            check('receipt_integrity_count',db.integrity()['receipts']==len(rows))
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ArchiveTests)
    from test_accounting_p07 import P07Tests
    for name in ['test_foreground_process_kill_before_and_after_commit','test_retry_conflict_locks_and_closed_period_no_mutation','test_migration_success_failure_repeat_and_replay']:
        suite.addTest(P07Tests(name))
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(suite)
    check('23_archive_and_original_p07_methods',result.wasSuccessful() and result.testsRun==23)
    if not result.wasSuccessful():print(stream.getvalue(),file=sys.stderr)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':result.testsRun},outputs,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for n,h in m[group].items():assert sha(ROOT/n)==h,n
        retained=json.loads((HERE/'cases.json').read_text())
        a,again,_=conformance(retained);assert a['passed'] and again==retained
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    result,rows,locks=conformance();assert result['passed'],[c for c in result['checks'] if not c['passed']]
    observation={'mode':mode,'passed':True,'checks':len(result['checks']),'unit_tests':result['unit_tests'],'cases':len(rows),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
    if mode=='--record':
        dump(HERE/'checks.json',result);dump(HERE/'cases.json',rows)
        files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]+[ROOT/'scripts/simulator_evidence_archive_v1.py',ROOT/'tests/test_simulator_evidence_archive_v1.py',HERE/'source-lock.json']
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
         'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
         'environment':'Python '+platform.python_version()+'; SQLite '+archive.sqlite3.sqlite_version,
         'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic exact-byte and interruption checks',
         'data_version':'complete retained native/query records and source-lock.json','inputs':locks,
         'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
         'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json']},
         'plan':'docs/plans/accounting-simulator-evidence-archive-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert rows==json.loads((HERE/'cases.json').read_text())
    print(json.dumps(observation))

if __name__=='__main__':main()
