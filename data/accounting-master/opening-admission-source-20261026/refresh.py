from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
old='docs/plans/accounting-opening-admission-source-20261026.md'
new='docs/plans/accounting-method-recipe-source-20261026.md'
result='data/accounting-master/opening-admission-source-20261026/result.md'
assert json.loads((HERE/'checks.json').read_text())['passed'] and (ROOT/new).exists()
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation};backup=HERE/'control-before';assert not backup.exists()
note='''## Opening-source progress — 26 October 2026

Two 21-stage opening templates and all 82 complete results match. Twenty
controls and 579 assertions pass; 194 predecessor files are protected. Native
lifecycle and operating builder are disabled. Result:
data/accounting-master/opening-admission-source-20261026/result.md.
Next: parameter/row recipes, complete selected-company source, then integration.
Version 5.9 remains governing; no whole requirement closes. S6 held; E3 deferred.

'''
proposed={}
for n in concise+history:
    value=before[n].decode();assert old in value;value=value.replace(old,new,1)
    if n in concise:
        value=value.replace('Current question: can authors state opening-admission checks directly while preserving all 82 complete results?','Current question: can direct parameter and row recipes preserve all 38 complete construction cases?')
        value=value.replace('Next action: execute '+old+'.','Next action: execute '+new+'.')
    pos=value.index('## Internal source progress');proposed[n]=value[:pos]+note+value[pos:]
for n in controls[-2:]:
    value=json.loads(before[n]);active=value.get('active_execution',value.get('active_execution_note'));assert active['active_work_plan']==old
    active.update(active_work_plan=new,latest_internal_result=result)
    active['next']=['Author parameter and ordered-row recipes preserving 38 complete constructions','Compose one complete selected-company source; integrate the checked sequence','Retain wider domain/source obligations; S6 held; E3 deferred']
    proposed[n]=json.dumps(value,indent=2)+'\n'
n=navigation[0];value=before[n].decode();assert old in value
proposed[n]=value.replace(old,new,1).replace('continues with opening-admission declarations.','continues with parameter and row recipes.',1)
n=navigation[1];value=before[n].decode().replace(old,new,1);pos=value.index('## Internal source progress')
proposed[n]=value[:pos]+note+'Eligibility and opening source are checked. Method recipes are active. Governing links remain Version 5.9 and standalone Version 5.5. No background process is running. Do not rerun completed writers.\n'
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
for n,value in proposed.items():assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(value)
for n in controls:assert new in (ROOT/n).read_text()
hashes={n:{'before':sha256(before[n]).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n in before}
(HERE/'control-refresh.json').write_text(json.dumps(dict(controls_agree=10,active_plan=new,updated_files=hashes,candidate_unchanged='5.9',whole_requirements_closed=0),indent=2)+'\n')
print(json.dumps(dict(controls_agree=10,active_plan=new,candidate='5.9 unchanged')))
