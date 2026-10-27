from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-assessed-carry-integration-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists(),'already refreshed'
    replay=json.loads(subprocess.run([sys.executable,'-B',str(HERE/'verify.py'),'--replay'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    assert replay['passed'] and (HERE/'result.md').exists() and (ROOT/PLAN).exists()
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=f'''## Provisional assessed-state carry checked — 24 October 2026

{replay['checks']} checks cover {replay['cases']} cases and protect {replay['protected_files']} inputs;
{replay['test_methods']} focused and {replay['regression_methods']} regression methods pass.
The actual deferred-assessed closing book crosses the provisional boundary.
Recorded profit, deferred balances and recognition history survive; new-period
current and deferred tax remain unassessed. Annual readiness stays false.
Result: {REL}/result.md. Contract: {REL}/design.md.
Next: {PLAN}. Integrate in protected Version 3.86, refresh full coverage,
then audit new-period current tax with separate liability vintages.
Version 3.85 remains 486 pages, not_ready. S1–S5 partial; S6 held; S7 deferred.
No whole requirement closes.

'''
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Assessed-carry evidence and controls are frozen. Begin protected integration.\nNo commit, agents, outreach or forecasting. Preserve unrelated work.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());other={k:v for k,v in d.items() if k!=key}
        a=d[key];a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append(f"Assessed carry: {replay['checks']} checks, {replay['cases']} cases, 10 focused and 26 regression methods; annual readiness false")
            a['next'][0]='Integrate provisional assessed-state carry in protected Version 3.86'
        dump(p,d);assert other=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',replay)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'mc_scope':['MC05','MC11','MC13','MC16','MC24','MC26','MC28','MC33','MC35'],'latest_full_inventory':'data/accounting-master/deferred-assessment-coverage-20261024/inventory.json','full_inventory_refresh_pending':True})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':replay['checks'],'next':PLAN}))
if __name__=='__main__':main()
