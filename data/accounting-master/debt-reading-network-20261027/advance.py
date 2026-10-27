from pathlib import Path
from hashlib import sha256
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
assert not (H/'advancement.json').exists()
for folder in [H,B/'debt-dash-source-20261027']:
 assert read(folder/'attempt-01/verification.json')['passed']
 for n,h in read(folder/'attempt-01/source-lock.json').items():assert sha(R/n)==h,n
old_plan='docs/plans/accounting-debt-dash-source-20261027.md';plan='docs/plans/accounting-debt-reading-integration-20261027.md'
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths};new={};identities={}
for p in paths[:2]:
 d=json.loads(before[p]);o=d['active_execution_note'] if p==paths[0] else d['active_execution']
 assert o['current_candidate']=='5.52-R1;830 pages;not_ready' and o['active_work_plan']==old_plan
 for key in ['current_pdf','standalone_pdf']:assert sha(R/o[key])==o[key+'_sha256'];identities[o[key]]=o[key+'_sha256']
 o.update(active_work_plan=plan,active_work_plans=[plan,o['financing_next_plan']],compression_next_plan=plan,full_gap_plan=plan,latest_internal_result=str((H/'result.md').relative_to(R)),debt_source_reading_result='data/accounting-master/debt-dash-source-20261027/result.md',debt_reading_network_result=str((H/'result.md').relative_to(R)),
  next=['Integrate verified reported-zero reading and full-network consequences into a protected 5.52-R1 successor','Resume consequential current-claim/source review and complete interface joins','Preserve broader acceptance, S6 held and E3 deferred'])
 o.setdefault('completed_plan_evidence',{}).update({old_plan:'data/accounting-master/debt-dash-source-20261027/result.md','docs/plans/accounting-debt-reading-network-20261027.md':str((H/'result.md').relative_to(R))})
 new[p]=enc(d)
for p in paths[2:]:
 s=before[p].decode();needle='Active plan: '+old_plan+'.';assert s.count(needle)==1
 s=s.replace(needle,'Active plan: '+plan+'.',1)
 anchor='Historical assessments below are preserved.';assert s.count(anchor)==1
 s=s.replace(anchor,'Debt-source result: data/accounting-master/debt-dash-source-20261027/result.md.\nNetwork result: data/accounting-master/debt-reading-network-20261027/result.md.\nThe selected reported-zero interpretation passes full-network exact checks;\nthe original PDF dash, rounding uncertainty and issuer unknowns remain explicit.\n'+anchor,1)
 new[p]=s
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,raw in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
for p,s in new.items():assert (R/p).read_bytes()==before[p];(R/p).write_text(s)
for p,h in identities.items():assert sha(R/p)==h
(H/'advancement.json').write_text(enc(dict(passed=True,candidate='5.52-R1 preserved',controls=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],pdf_identities=identities,next_plan=plan)))
print(json.dumps(dict(passed=True,controls=len(paths),candidate='5.52-R1 preserved',next_plan=plan)))
