from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
old='docs/plans/accounting-ordered-eligibility-source-20261026.md'
new='docs/plans/accounting-opening-admission-source-20261026.md'
result='data/accounting-master/ordered-eligibility-source-20261026/result.md'
assert json.loads((HERE/'checks.json').read_text())['passed']
assert (ROOT/new).exists() and (ROOT/result).exists()
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation}
backup=HERE/'control-before'; assert not backup.exists()
note='''## Internal source progress — 26 October 2026

Ordered eligibility source is checked: six exact templates, 38 eligible and
34 refused complete gate results, 35 controls and 603 assertions; 176
predecessor files protected. Native lifecycle functions disabled.
Result: data/accounting-master/ordered-eligibility-source-20261026/result.md.
Next: direct opening admission, then parameter/row recipes and complete selected
company source. Version 5.9 remains the governing candidate; this increment
awaits integration. No whole requirement closes; S6 held and E3 deferred.

'''
proposed={}
for n in concise+history:
    value=before[n].decode(); assert old in value; value=value.replace(old,new,1)
    if n in concise:
        value=value.replace('Current question: can authors write ordered eligibility and bindings directly while preserving exact typed results?', 'Current question: can authors state opening-admission checks directly while preserving all 82 complete results?')
        value=value.replace('Next action: execute '+old+'.','Next action: execute '+new+'.')
    pos=value.find('\n## Prior governing candidate')
    if pos<0: pos=value.find('\nMission:')
    if pos<0: pos=value.find('\n## ',value.find('## Current governing candidate')+5)
    if pos<0: pos=len(value)
    proposed[n]=value[:pos]+'\n'+note+value[pos:]
for n in controls[-2:]:
    value=json.loads(before[n]); active=value.get('active_execution',value.get('active_execution_note'))
    assert active['active_work_plan']==old
    active.update(active_work_plan=new,latest_internal_result=result)
    active['next']=['Author explicit opening-admission checks preserving 82 complete results','Then expose parameter/row recipes and one complete selected-company source','Integrate checked source sequence; preserve broader obligations; S6 held and E3 deferred']
    proposed[n]=json.dumps(value,indent=2)+'\n'
n=navigation[0];proposed[n]=before[n].decode().replace('The [active plan]('+old+') starts direct source authoring with ordered eligibility and explicit bindings.','Direct ordered-eligibility source now preserves all 72 gate results. The [active plan]('+new+') continues with opening-admission declarations.')
n=navigation[1];value=before[n].decode().replace(old,new,1);start=value.index('Version 5.9 integration and combined opening/execution are complete.')
proposed[n]=value[:start]+note+'Version 5.9 integration is complete. Ordered eligibility source is checked; opening source is active. Main links remain 5.9 and standalone 5.5. No background process is running. Do not rerun completed writers.\n'
for n,b in before.items():
    path=backup/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
for n,value in proposed.items():
    assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(value)
for n in controls: assert new in (ROOT/n).read_text()
hashes={n:{'before':sha256(before[n]).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n in before}
(HERE/'control-refresh.json').write_text(json.dumps(dict(controls_agree=10,active_plan=new,updated_files=hashes,candidate_unchanged='5.9',whole_requirements_closed=0),indent=2)+'\n')
print(json.dumps(dict(controls_agree=10,active_plan=new,candidate='5.9 unchanged')))
