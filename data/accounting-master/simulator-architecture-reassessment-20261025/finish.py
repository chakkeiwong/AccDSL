from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-book-transition-20261025.md'
PROGRAM='docs/plans/accounting-current-program-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def main():
    assert not (HERE/'control-refresh.json').exists()
    replay=subprocess.run([sys.executable,'-B',str(HERE/'verify.py')],cwd=ROOT,capture_output=True,text=True,check=True)
    summary=json.loads(replay.stdout)
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=f'''## Architecture reassessed — 25 October2026

Current program: {PROGRAM}. Version4.04,503 pages,not_ready.
Current-state scheduling is checked, but its annual book still binds a fixed
synthetic context/chart. Existing typed monetary/memory engines are reusable.
Next: {PLAN}. Define an explicit company-book transition boundary with declared
accounts,context and typed memory; preserve all existing native profiles.
Review: {REL}/result.md. All53/6/46 original requirements retained;22 inspected
contracts/documents;43 recorded checks. No whole requirement closes.
S1–S5 partial,S6 held,S7 deferred. Forecasting remains deferred.

'''
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Preserve frozen packages and unrelated dirty work. No commit,subagents,outreach or forecasting.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',current_program=PROGRAM,updated='2026-10-25')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md');a['completed_increments'].append('Full architecture reassessment:53/6/46 retained;fixed annual-book context identified;general transition boundary selected')
            a['next'][0]='Specify and check a declared company-book transition using existing typed effects'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'replay':summary})
    print(json.dumps({'controls':9,'next':PLAN,'current_program':PROGRAM}))
if __name__=='__main__':main()
