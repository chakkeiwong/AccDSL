"""Refresh active annotations once, preserving historical controls byte-for-byte."""
from pathlib import Path
from hashlib import sha256
import json, subprocess, sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-company-source-integration-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    run=subprocess.run([sys.executable,'-B',str(HERE/'verify.py'),'--replay'],cwd=ROOT,text=True,capture_output=True,check=True)
    observation=json.loads(run.stdout);assert observation['passed']
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=('## Fiscal source-state interface checked — 24 October 2026

'
        'The source-constrained state draft passes 509 checks and replay;
'
        '93 protected inputs remain unchanged. Matched typed/text authoring
'
        'preserves 54 balance captions across the 364-day fiscal year and
'
        '91-day quarter. Display-only remains the baseline; explicit rounding
'
        'hypotheses supply conditional intervals without resolving missing state.
'
        'Result: '+REL+'/result.md.

'
        'Next: '+NEXT+'.
'
        'Integrate complete company composition, actual-source readiness and
'
        'partial-state semantics into protected manuscript Version 3.57.
'
        'Version 3.56 remains 421 pages, not_ready until that work passes.
'
        'S1–S5 partial; S6 held; S7 deferred. No whole requirement closes.

')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Preserve predecessor artifacts and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=NEXT,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Fiscal partial state:54 snapshots;364/91-day periods;509 checks/replay;93 protected inputs')
            a['next'][0]='Integrate company composition and source-constrained state into Version 3.57'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',observation)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'requirements':'MC02/04/05/06/10/11/16/24/28','remaining':'actual source state, general adapters and whole-company acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':observation['checks'],'next':NEXT}))
if __name__=='__main__':main()
