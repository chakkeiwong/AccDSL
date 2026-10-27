from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-book-integration-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')


def main():
    assert not (HERE/'control-refresh.json').exists(),'already refreshed'
    manifest=json.loads((HERE/'manifest.json').read_text())
    assert manifest['source_lock_sha256']==sha(HERE/'source-lock.json')
    for name,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    note=f'''## Declared company-book transition checked — 25 October 2026

Two company owners, distinct charts and memory layouts share checked payment
semantics. 24 focused tests, 37 direct dependency regressions and 35 native
comparisons pass. Static memory dimensional checks and strict JSON replay repaired.
3128 recorded checks protect 1568 files. Complete native states and payment reports
match through explicit projections; general reporting/admission remain open.
Result: {REL}/result.md. Next: {PLAN}.
Version 4.04 remains 503 pages, not_ready until integration. S1–S5 partial,
S6 held, S7 deferred. No whole requirement closes; forecasting remains deferred.

'''
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'master-current' in name or 'simulator-session' in name:rest='No command running. Evidence and detailed history remain in linked result records.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;x=json.loads(p.read_text());legacy={k:v for k,v in x.items() if k!=key};a=x[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-25')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md');a['completed_increments'].append('CompanyBookTransition/1:24 focused,37 regression tests;35 native comparisons;3128 checks')
            a['next'][0]='Integrate checked company-book composition into Version 4.05, then refresh coverage and method/clock adapters'
        dump(p,x);assert legacy=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'next':PLAN}))


if __name__=='__main__':main()
