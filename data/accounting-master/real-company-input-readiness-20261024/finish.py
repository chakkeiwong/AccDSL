"""Refresh active annotations once, preserving historical controls byte-for-byte."""
from pathlib import Path
from hashlib import sha256
import json, subprocess, sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-source-constrained-state-20261024.md'
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
    note=('## Real-company input requirements checked — 24 October 2026\n\n'
        'The retained Apple readiness reference passes 2,113 checks and replay;\n'
        '79 protected inputs remain unchanged. All 139 inventory entries and\n'
        '102/100 annual/interim readings plus 27/27 comparison rows are retained.\n'
        'Fifteen dependencies cover both finite targets. Missing state and target\n'
        'scope remain separate; no executable opening is fabricated.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+NEXT+'.\n'
        'Specify source-constrained partial state and fiscal periods, preserving\n'
        'displayed evidence, uncertain underlying balances and missing memory.\n'
        'Then integrate composition and source-input design in the manuscript.\n'
        'Version 3.56 remains 421 pages, not_ready. S1–S5 partial; S6 held;\n'
        'S7 deferred. No whole requirement closes; no global blocker.\n\n')
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
            a['completed_increments'].append('Real-company readiness:15 dependencies;139 inventory and 256 readings preserved;2113 checks/replay;79 protected files')
            a['next'][0]='Fiscal periods and source-constrained partial company state, then coherent manuscript integration'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',observation)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'requirements':'MC01–07/10/11/15/16/18/24/27/28','remaining':'actual source state, general adapters and whole-company acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':observation['checks'],'next':NEXT}))
if __name__=='__main__':main()
