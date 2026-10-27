"""Correct refresh's stale next-plan constants; preserve first write evidence."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
OLD='docs/plans/accounting-conversion-control-scope-20261026.md'
NEXT='docs/plans/accounting-control-history-contract-20261026.md'
names=['MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md',
 'data/accounting-master/recovery-current-20261026.md','scripts/accounting_master_catalog.json',
 'data/accounting-master/next-plan.json']
assert not (H/'pointer-repair.json').exists()
before={n:(R/n).read_bytes() for n in names};updates={}
backup=H/'pointer-before';backup.mkdir(exist_ok=False)
for n,data in before.items():
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
for n in names[:7]:
 # Preserve historical notes; replace only the current front occurrence.
 text=before[n].decode();text=text.replace(OLD,NEXT,1)
 updates[n]=text.encode()
for n in names[7:]:
 obj=json.loads(before[n]);a=obj['active_execution_note' if n.startswith('scripts/') else 'active_execution']
 if a.get('active_work_plan')==OLD:a['active_work_plan']=NEXT
 a['active_work_plans']=[NEXT if p==OLD else p for p in a.get('active_work_plans',[])]
 a['financing_next_plan']=NEXT
 a['control_boundary_result']='data/accounting-master/control-boundary-repair-20261026/result.md'
 a['control_scope_result']='data/accounting-master/conversion-control-scope-20261026/result.md'
 a['financing_authority_result']='data/accounting-master/contingent-conversion-authority-20261026/result.md'
 a['next']=[x.replace(OLD,NEXT) for x in a.get('next',[])]
 a['latest_internal_results']=list(dict.fromkeys([*a.get('latest_internal_results',[]),a['control_scope_result'],a['control_boundary_result']]))
 updates[n]=(json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)).encode()
for n,data in before.items():assert (R/n).read_bytes()==data,'concurrent change:'+n
for n,data in updates.items():(R/n).write_bytes(data)
for n,data in updates.items():assert (R/n).read_bytes()==data
record=dict(status='PASS',next_plan=NEXT,reason='The copied refresh retained old plan constants; corrected without rerunning evidence or its first writer.',before={k:sha256(v).hexdigest() for k,v in before.items()},after={k:sha256(v).hexdigest() for k,v in updates.items()})
(H/'pointer-repair.json').write_text(json.dumps(record,indent=2)+chr(10));print(json.dumps({'status':'PASS','next_plan':NEXT,'controls':len(updates)}))
