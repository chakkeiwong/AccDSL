"""One-time schema checkpoint; preserve unrelated and historical controls."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-return-execution-20261024.md'
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
    note=('## Native return authoring checked — 24 October 2026\n\n'
        'The closed typed/text component profile passes 107 checks and read-only\n'
        'replay, with 23 protected inputs unchanged and six legacy round trips.\n'
        'Known contradictions no longer hide behind unknown inputs; original\n'
        'failed evidence is preserved. Static eligibility is not execution.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Execute the shared-book reference return, tax, annual report and carry\n'
        'against the complete retained P trace. Version 3.55 remains 419 pages,\n'
        'not_ready and unchanged; this increment awaits integration. S1–S5\n'
        'partial, S6 held, S7 deferred; no whole requirement closes.\n\n')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:
                rest=('No active command. Record/replay already complete; do not rerecord.\n'
                    'Read native-return-design/specification.md and the active plan.\n'
                    'Preserve dirty work; no commit, subagents, controller or forecast run.\n')
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Native return authoring:107 checks/replay;23 protected files;six legacy paths;classification repair preserved')
            a['next'][0]='Shared-book native reference return, lot, tax, annual report and carry before manuscript integration'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',{'passed':True,'checks':107,'protected_files':23,'wall_seconds':0.5426863780012354,'read_only':True})
    dump(HERE/'coverage-delta.json',{'advanced':['MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],'whole_rows_closed':0,'remaining':'native execution,broader methods,source admission,durability,manuscript integration and acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'next':PLAN,'checks':107}))
if __name__=='__main__':main()
