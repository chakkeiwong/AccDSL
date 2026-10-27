"""Complete documentary coverage through immutable predecessor references."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,platform,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PRIOR='data/accounting-master/company-function-text-coverage-20261025'
NEXT='docs/plans/accounting-state-decision-schedule-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))

def main():
    record=sys.argv[1:]==['--record'];assert sys.argv[1:] in ([],['--record'])
    assert not record or not (HERE/'manifest.json').exists(),'already recorded'
    started=datetime.now(timezone.utc).isoformat();t=time.monotonic();checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    baseline=json.loads((ROOT/PRIOR/'inventory.json').read_text())
    protected={PRIOR+'/inventory.json':sha(ROOT/PRIOR/'inventory.json')}
    parent=baseline['baseline'];protected[parent['path']]=parent['sha256']
    parent_data=json.loads((ROOT/parent['path']).read_text())
    for package in ['state-decision-events-20261025','state-decision-events-integration-20261025']:
        folder=HERE.parent/package
        for p in folder.iterdir():
            if p.is_file():protected[p.relative_to(ROOT).as_posix()]=sha(p)
        manifest=json.loads((folder/('manifest.json' if package=='state-decision-events-20261025' else 'run-manifest.json')).read_text())
        if 'output_artifacts' in manifest:
            for name,h in manifest['output_artifacts'].items():
                if name in protected:assert protected[name]==h
                protected[name]=h
        else:
            for name,h in json.loads((folder/'source-lock.json').read_text()).items():
                if name in protected:assert protected[name]==h
                protected[name]=h
    targeted={'MC13','MC14','MC15','MC18','MC23','MC24','MC25','MC26','MC28','MC32','MC34','MC35'}
    inventory={'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.02','readiness':'not_ready',
               'baseline':{'path':PRIOR+'/inventory.json','sha256':protected[PRIOR+'/inventory.json']},
               'next_plan':NEXT,'whole_rows_closed':0,'scope':'Additive state-dependent decision integration; no whole-row admission'}
    for group,count in [('obligations',53),('interactions',6),('operations',46)]:
        rows=baseline[group];check('count:'+group,len(rows)==count);check('unique:'+group,len({r['id'] for r in rows})==count)
        parent_by_id={r['id']:r for r in parent_data[group]}
        inventory[group]=[]
        for row in rows:
            oldref=row['prior_ref']
            check('prior_ref:'+group+':'+row['id'],oldref['path']==parent['path'] and oldref['collection']==group and oldref['id']==row['id'] and oldref['sha256']==digest(parent_by_id[row['id']]))
            updated=group=='obligations' and row['id'] in targeted
            inventory[group].append({'id':row['id'],'prior_ref':{'path':PRIOR+'/inventory.json','collection':group,'id':row['id'],'sha256':digest(row)},
               'assessment':'scoped_advance_remaining_open' if updated else 'prior_scope_retained_not_reaudited',
               'advance':'Current-state decisions generate native sale proposals with exact transition and financial checks.' if updated else 'No new evidence assigned in this bounded review.',
               'residual':'General decisions and event schedules, broader methods and actual-company admission remain open.' if updated else 'Retain exact predecessor obligations and next work.',
               'evidence':['data/accounting-master/state-decision-events-20261025/result.md','data/accounting-master/state-decision-events-integration-20261025/result.md'] if updated else [],
               'full_requirement_closed':False,'acceptance':'not_promoted'})
    for name,h in protected.items():check('input:'+name,sha(ROOT/name)==h)
    if record:dump(HERE/'inventory.json',inventory)
    check('inventory_exact',json.loads((HERE/'inventory.json').read_text())==inventory)
    for p in HERE.iterdir():
        if p.is_file() and p.name not in ['source-lock.json','manifest.json','checks.json','control-refresh.json','finish.py']:protected[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in [NEXT,'docs/plans/accounting-state-decision-events-coverage-20261025.md']:protected[name]=sha(ROOT/name)
    if record:dump(HERE/'source-lock.json',protected)
    else:check('source_lock_exact',protected==json.loads((HERE/'source-lock.json').read_text()))
    for name,h in protected.items():check('sealed:'+name,sha(ROOT/name)==h)
    assert all(x['passed'] for x in checks),[x['name'] for x in checks if not x['passed']]
    summary={'passed':True,'checks':len(checks),'protected_files':len(protected),'coverage':[53,6,46],'updated_obligations':len(targeted),'whole_rows_closed':0}
    if record:
        dump(HERE/'checks.json',dict(summary,named_checks=checks))
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-t,'git_commit_recorded':'03fea070f089821f4759e49a4466a3399b7fc078','command':'python3 -B '+REL+'/verify.py --record','environment':platform.python_version(),'cpu_gpu':'CPU file/hash validation only','random_seeds':'N/A: deterministic','data_version':'source-lock.json','plan':'docs/plans/accounting-state-decision-events-coverage-20261025.md','result':REL+'/result.md','source_lock_sha256':sha(HERE/'source-lock.json'),'summary':summary})
    print(json.dumps(summary))
if __name__=='__main__':main()
