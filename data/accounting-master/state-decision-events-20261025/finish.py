"""One-time control refresh after exact evidence validation."""
from pathlib import Path
from hashlib import sha256
import json
from compare import compare
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-state-decision-events-integration-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists(),'already refreshed'
    manifest=json.loads((HERE/'manifest.json').read_text())
    assert manifest['source_lock_sha256']==sha(HERE/'source-lock.json')
    for name,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    assert compare()==json.loads((HERE/'comparison.json').read_text())
    checks=json.loads((HERE/'checks.json').read_text());assert checks['passed'] and all(x['passed'] for x in checks['named_checks'])
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=f'''## State-dependent decisions checked — 25 October 2026

StateDecisionEvent/1 reads the current conditional book and generates a native
inventory sale.28 focused,14 native and23 function regression methods pass;
64 comparisons across8 cases preserve exact events,transitions and financial
fields.2603 recorded checks protect853 files. No behavior or admission claim.
Result: {REL}/result.md. Design: {REL}/design.md.
Next: {PLAN}. Integrate the checked decision mechanism into protected Version4.02.
Version4.01 remains500 pages,not_ready;S1–S5 partial,S6 held,S7 deferred.
No whole requirement closes. Forecasting remains deferred.

'''
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Preserve frozen packages and unrelated work. No commit, subagents, outreach or forecast run.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-25')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md');a['completed_increments'].append('Current-state decisions:28 focused,14 native,23 function tests;64 exact comparisons;2603 checks')
            a['next'][0]='Integrate checked state-dependent decisions into Version4.02'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':checks['checks'],'next':PLAN}))
if __name__=='__main__':main()
