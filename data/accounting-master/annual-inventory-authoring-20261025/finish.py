from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-annual-inventory-family-20261025.md'
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
    note=f'''## Matched annual inventory authoring checked — 25 October 2026

{replay['checks']} checks cover {replay['cases']} cases and protect {replay['protected_files']} inputs;
{replay['test_methods']} focused and {replay['regression_methods']} regression methods pass.
Named inventory declarations lower exactly to the complete optional annual program.
Compilation preserves provenance, unknowns, order, raw hashes and source spans
without executing financial methods. Text and typed execution results match.
Actual annual admission and whole-language completeness remain unestablished.
Result: {REL}/result.md. Contract: {REL}/design.md.
Next: {PLAN}. Extend named families through the checked compiler and evaluator,
then integrate both interfaces and refresh complete coverage.
Version 3.97 remains 496 pages, not_ready. S1–S5 partial; S6 held; S7 deferred.
No whole requirement closes.

'''
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Annual inventory authoring evidence is frozen. Begin audited family dispatch.\nNo commit, agents, outreach or forecasting. Preserve unrelated work.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());other={k:v for k,v in d.items() if k!=key}
        a=d[key];a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-25')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append(f"Annual inventory authoring: {replay['checks']} checks, {replay['cases']} cases, 15 focused and 26 regression methods; annual readiness false")
            a['next'][0]='Check named annual inventory scenario-family dispatch'
        dump(p,d);assert other=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',replay)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'mc_scope':['MC05','MC11','MC13','MC16','MC24','MC26','MC28','MC33','MC35'],'latest_full_inventory':'data/accounting-master/annual-inventory-coverage-20261025/inventory.json','full_inventory_refresh_pending':True})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':replay['checks'],'next':PLAN}))
if __name__=='__main__':main()
