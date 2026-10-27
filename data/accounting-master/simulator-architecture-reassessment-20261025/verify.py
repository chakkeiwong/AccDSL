from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,platform,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def main():
    record=sys.argv[1:]==['--record'];assert sys.argv[1:] in ([],['--record'])
    assert not record or not (HERE/'manifest.json').exists(),'already recorded'
    start=time.monotonic();checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    original=json.loads((HERE/'original-obligations.json').read_text())
    for entry in original['source_chain']:check('chain:'+entry['path'],sha(ROOT/entry['path'])==entry['sha256'])
    baseline=json.loads((ROOT/original['source_chain'][-1]['path']).read_text())
    for group,count in [('obligations',53),('interactions',6),('operations',46)]:
        expected=[]
        for row in baseline[group]:
            depth=0
            while 'prior_entry' in row or 'prior_record' in row:
                row=row['prior_entry'] if 'prior_entry' in row else row['prior_record'];depth+=1
            expected.append({'id':row['id'],'original_record':row,'nested_depth':depth,'original_sha256':digest(row)})
        check(group+':count',len(original[group])==count)
        check(group+':unique',len({x['id'] for x in original[group]})==count)
        check(group+':exact_originals',original[group]==expected)
    sources=json.loads((HERE/'inspected-sources.json').read_text())
    for name,h in sources.items():check('source:'+name,sha(ROOT/name)==h)
    check('fixed_context_present',"need(state['context']==CONTEXT" in (ROOT/'scripts/shared_tax_continuation_v1.py').read_text())
    check('generic_monetary_contract',"'cash_account'" in (ROOT/'scripts/method_monetary_effects_v1.py').read_text())
    check('generic_memory_contract','def stage(' in (ROOT/'scripts/method_memory_effects_v1.py').read_text())
    for name in ['docs/plans/accounting-current-program-20261025.md','docs/plans/accounting-company-book-transition-20261025.md']:
        check('next_document:'+name,(ROOT/name).is_file());sources[name]=sha(ROOT/name)
    for p in HERE.iterdir():
        if p.is_file() and p.name not in ['manifest.json','checks.json','source-lock.json','finish.py','control-refresh.json','progress.md']:
            sources[p.relative_to(ROOT).as_posix()]=sha(p)
    if record:dump(HERE/'source-lock.json',sources)
    else:check('source_lock_exact',sources==json.loads((HERE/'source-lock.json').read_text()))
    assert all(x['passed'] for x in checks),[x['name'] for x in checks if not x['passed']]
    summary={'passed':True,'checks':len(checks),'coverage':[53,6,46],'inspected_sources':22,'protected_files':len(sources),'whole_rows_closed':0}
    if record:
        dump(HERE/'checks.json',dict(summary,named_checks=checks))
        dump(HERE/'manifest.json',{'date_utc':datetime.now(timezone.utc).isoformat(),'git_commit_recorded':'03fea070f089821f4759e49a4466a3399b7fc078','command':'python3 -B '+str(HERE.relative_to(ROOT))+'/verify.py --record','environment':platform.python_version(),'cpu_gpu':'CPU file and contract inspection only','random_seeds':'N/A: deterministic documentary review','data_version':'source-lock.json and immutable original reference chain','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-simulator-architecture-reassessment-20261025.md','result':str(HERE.relative_to(ROOT))+'/result.md','source_lock_sha256':sha(HERE/'source-lock.json'),'summary':summary})
    print(json.dumps(summary))
if __name__=='__main__':main()
