"""Advance local mission controls without touching frozen controller fields."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-native-return-design-20261023.md'
def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    c=json.loads((HERE/'checks.json').read_text()); assert c['passed'] and len(c['checks'])==43
    m=json.loads((HERE/'manifest.json').read_text())
    for group in ['inputs','implementation','outputs']:
        for name,h in m[group].items(): assert sha(ROOT/name)==h,name
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json']
    note=('## Shared-book module boundary checked\n\n'
        'The retained return-state method passes 43 exact checks and read-only\n'
        'replay; 22 protected files are unchanged. Original owner/context/view,\n'
        'shared cash and complete after-state are retained. Proposals are\n'
        'uncommitted; Northstar lacks seven explicit native return capabilities.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Design recovered-stock lots, refund/recovery memory, source findings,\n'
        'current/deferred tax, reports and annual carry before adding an\n'
        'operation. Preserve the existing homogeneous inventory and all legacy\n'
        'scenarios. Version 3.54 stays 415 pages, not_ready and unchanged.\n'
        'Portable authoring and this boundary await manuscript integration.\n'
        'S1–S5 partial; S6 held; S7 deferred; no whole requirement closes.\n'
        'Earlier entries are historical checkpoints.\n\n')
    before={}
    for name in names:
        p=ROOT/name; before[name]=sha(p); dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:
                rest=('PDF: docs/design/proposal/manuscript-company-language-20261023/accounting-product-proposal.pdf\n'
                    'SHA256: 8ca29eb2f2f2fbce11c2b02245e599e75493545f964782e1c450bf6690b84f6e.\n'
                    'Portable:62 checks,168 records,67 blobs,558 locks. Module boundary:43 checks,22 locks.\n'
                    'Both recorded and replayed; no active command. No commit, subagent or forecast experiment.\n'
                    'Next inspect retained CompanyComposition source/tax facts, and native inventory/report invariants.\n')
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); legacy={k:v for k,v in d.items() if k!='active_execution'}
    a=d['active_execution']; a.update(active_work_plan=PLAN,latest_result=REL+'/result.md')
    a['latest_results'].append(a['latest_result']); a['completed_increments'].append('Shared-book module boundary:43 checks/replay;22 locks;retained return method,immutable proposal,seven native capability gaps')
    a['next'][0]='Specify native return component state, recovered inventory lots, tax/report semantics and annual carry before engine extension'
    dump(p,d); assert legacy=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
    p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); legacy={k:v for k,v in d.items() if k!='active_execution_note'}
    d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md'); dump(p,d)
    assert legacy=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
    dump(HERE/'replay-observation.json',{'passed':True,'checks':43,'protected_files':22,'wall_seconds':0.1715196929872036,'read_only_replay':True})
    dump(HERE/'coverage-delta.json',{'advanced':['MC02','MC04','MC05','MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],
        'whole_rows_closed':0,'remaining':['native module state and syntax','full normalized IR','actual source admission','durability','domain/human acceptance']})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
    print(json.dumps({'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
