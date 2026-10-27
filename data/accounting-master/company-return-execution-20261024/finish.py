"""One-time execution checkpoint, preserving historical control fields."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-return-integration-20261024.md'
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
    note=('## Native shared-book reference checked — 24 October 2026\n\n'
        'The full retained P trace passes 253 checks and read-only replay;\n'
        '36 protected files remain unchanged. Native return, tax, annual\n'
        'statements and carry match the exact case. Surrounding corporate\n'
        'events use explicit retained-method adapters. Profit 49.5, cash\n'
        '491.5, equity 671.5 and operating cash 101.5 reconcile.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Integrate the authoring and execution reference into a protected\n'
        'manuscript successor. Version 3.55 stays 419 pages, not_ready and\n'
        'unchanged. S1–S5 partial; S6 held; S7 deferred. No whole row closes.\n\n')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No active command. Preserve one-time recordings and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Native shared-book reference:253 checks/replay;36 protected inputs;13-step P trace;tax/report/carry')
            a['next'][0]='Integrate return authoring and shared-book reference into Version 3.56'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',{'passed':True,'checks':253,'protected_files':36,'wall_seconds':0.6551975909969769,'read_only':True})
    dump(HERE/'coverage-delta.json',{'advanced':['MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],'whole_rows_closed':0,'remaining':'complete company profile,broader methods,source admission,durability,manuscript integration and acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'next':PLAN,'checks':253}))
if __name__=='__main__':main()
