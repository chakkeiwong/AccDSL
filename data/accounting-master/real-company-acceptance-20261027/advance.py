from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
assert not (H/'advancement.json').exists()
v=read(H/'attempt-01/verification.json');assert v['passed']
for n,h in read(H/'attempt-01/source-lock.json').items():assert sha(R/n)==h,n
old_plan='docs/plans/accounting-real-company-acceptance-20261027.md';plan='docs/plans/accounting-debt-dash-source-20261027.md'
assert (R/plan).is_file()
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths};new={}
for p in paths[:2]:
 d=json.loads(before[p]);o=d['active_execution_note'] if p==paths[0] else d['active_execution']
 assert o['current_candidate']=='5.52;830 pages;not_ready' and o['active_work_plan']==old_plan
 o.update(active_work_plan=plan,active_work_plans=[plan,o['financing_next_plan']],compression_next_plan=plan,full_gap_plan=plan,latest_internal_result=str((H/'result.md').relative_to(R)),real_company_decisions=str((H/'current-decisions.md').relative_to(R)),latest_reset_memo=str((H/'reset-memo.md').relative_to(R)),
  next=['Audit retained FY2024 debt-issuance tagged zero against PDF dash, context and exact affected relations','Continue remaining C2/C4 joins and C3 source questions without inventing issuer facts','Preserve S6 held, E3 deferred and whole-document/independent acceptance'])
 o.setdefault('completed_plan_evidence',{})[old_plan]=str((H/'result.md').relative_to(R));new[p]=enc(d)
for p in paths[2:]:
 s=before[p].decode();needle='Active plan: '+old_plan+'.';assert s.count(needle)==1
 s=s.replace(needle,'Active plan: '+plan+'.',1)
 anchor='Historical assessments below are preserved.'
 assert s.count(anchor)==1
 s=s.replace(anchor,'Current company audit: data/accounting-master/real-company-acceptance-20261027/result.md.\nAll fifteen dependencies retain current capability and exact missing issuer facts.\nA retained tagged-zero lead now receives a separate source audit.\n'+anchor,1)
 new[p]=s
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,raw in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
for p,s in new.items():assert (R/p).read_bytes()==before[p];(R/p).write_text(s)
assert read(B/'next-plan.json')['active_execution']['active_work_plan']==plan
(H/'advancement.json').write_text(enc(dict(passed=True,controls=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],result=sha(H/'result.md'),next_plan=plan,candidate='5.52 unchanged')))
print(json.dumps(dict(passed=True,controls=len(paths),next_plan=plan,candidate='5.52 unchanged')))
