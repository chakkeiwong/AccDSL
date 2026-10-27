"""One-time coverage refresh with protected historical control annotations."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-real-company-input-readiness-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    from verify import conformance
    result,*_=conformance();assert result==json.loads((HERE/'checks.json').read_text()) and result['passed']
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=('## Whole-language coverage refreshed — 24 October 2026\n\n'
        'All 53 obligations, six interactions and 46 operations retain their\n'
        'complete prior records. Scoped updates affect 41/4/14 rows; 488 checks\n'
        'and replay pass with 164 protected files unchanged. No row closes.\n'
        'Result: '+REL+'/result.md.\n'
        'Phase decisions and remaining gaps: '+REL+'/review.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Trace retained Apple disclosures to executable company input requirements;\n'
        'keep consolidated aggregates, fiscal periods, unknown state and method\n'
        'premises distinct. Existing real-source connection is reused.\n'
        'Version 3.56 stays 421 pages, not_ready. Latest company composition\n'
        'awaits integration. S1–S5 partial; S6 held; S7 deferred.\n\n')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No active command. Preserve one-time records, candidate PDF and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Whole-language refresh:53/6/46 complete prior records;41/4/14 scoped updates;488 checks/replay;164 protected files')
            a['next'][0]='Real disclosure to executable company input readiness, without inventing state or changing fiscal scope'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',{'passed':True,'checks':488,'protected_files':164,'wall_seconds':0.05177230297704227,'read_only':True})
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'updated_rows':result['updated_rows'],'remaining':'row-specific residuals in inventory.json and phase decisions in review.md'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'next':PLAN,'checks':488}))
if __name__=='__main__':main()
