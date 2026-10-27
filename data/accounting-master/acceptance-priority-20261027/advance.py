"""Refresh current navigation once; preserve every prior control byte."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
def read(p):return json.loads(p.read_text())
assert not (H/'advancement.json').exists()
v=read(H/'verification.json');assert v['passed'] and v['counts']['original_MC_conditions']==35
assert all(sha(R/p)==h for p,h in read(H/'source-lock.json').items())
plan='docs/plans/accounting-release-bundle-recovery-20261027.md'
compat='docs/plans/accounting-profile-compatibility-20261027.md'
base=str(H.relative_to(R));result=base+'/result.md'
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths}
a,b=[json.loads(before[p]) for p in paths[:2]]
changes=dict(updated='2026-10-27',active_work_plan=plan,current_program='docs/plans/accounting-release-closure-20261027.md',
    release_acceptance=base+'/release-acceptance.json',acceptance_priority_result=result,
    closure_packages=base+'/closure-packages.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',
    full_gap_program='docs/plans/accounting-release-closure-20261027.md',full_gap_plan=plan,
    active_work_plans=[plan,'docs/plans/accounting-conversion-allocation-evidence-20261027.md'],
    compression_next_plan=compat,bank_next_plan='docs/plans/accounting-release-closure-20261027.md',
    insurance_next_plan='docs/plans/accounting-release-closure-20261027.md',
    next=['Recover the historical Core 0 normative bundle in a relocated root','Consolidate current profile compatibility and integrated evidence','Continue local source work; S6 held and E3 deferred'],
    gap_program_next=['C1 reproducible dependency repair','C2 compatible specification','C3 source authority and C4 integrated cases'],
    current_internal_status='Acceptance decisions reconciled; 35 original conditions preserved; no broad closure.')
for obj in [a['active_execution_note'],b['active_execution']]:
    assert obj['current_candidate']=='5.51;828 pages;not_ready'
    obj.update(changes)
    obj['completed_plan_evidence']={
      'docs/plans/accounting-coupon-program-resume-20261027.md':'data/accounting-master/coupon-program-resume-20261027/result.md',
      'docs/plans/accounting-credit-recovery-intake-20261027.md':'data/accounting-master/credit-recovery-intake-20261027/result.md',
      'docs/plans/accounting-insurance-shared-group-audit-20261027.md':'data/accounting-master/insurance-shared-group-audit-20261027/result.md'}
summary='''## Current execution — 27 October 2026

Governing candidate **5.51**, 828 main pages, 262 total / 241 body simulation
pages; not_ready. Its PDFs, source hashes and stable links are unchanged.

Current acceptance: data/accounting-master/acceptance-priority-20261027/release-acceptance.md.
Current package actions: data/accounting-master/acceptance-priority-20261027/remaining-work.md.
Master sequence: docs/plans/accounting-release-closure-20261027.md.
Active plan: docs/plans/accounting-release-bundle-recovery-20261027.md.
Following plan: docs/plans/accounting-profile-compatibility-20261027.md.
Result: data/accounting-master/acceptance-priority-20261027/result.md.

All 35 original mission conditions are preserved. All 53 obligations, six
interactions, 46 operations and 18 packages remain open with current actions.
Delivered source authoring is retained; stale coupon/recovery/insurance plans
are evidence, not instructions to rerun them. Conversion-allocation, positive
credit recovery and dated insurance group evidence remain local dependencies.
S1–S5 partial; S6 held; E3 deferred. Historical assessments below are preserved;
use the current acceptance index for execution rather than older next actions.

'''
new={paths[0]:enc(a),paths[1]:enc(b)}
for p in paths[2:]:
    text=before[p].decode();title,rest=text.split('\n',1)
    if p in paths[-2:]:
        marker='\n## Release-readiness audit'
        tail=rest[rest.index(marker):] if marker in rest else ''
        new[p]=title+'\n\n'+summary+tail
    else:
        first=rest.find('## ');second=rest.find('\n## ',first+3)
        assert first>=0 and second>=0,p
        new[p]=title+'\n\n'+summary+rest[second+1:]
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,raw in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
for p,content in new.items():
    assert (R/p).read_bytes()==before[p],p
    (R/p).write_text(content)
for p in paths[:2]:
    obj=read(R/p);obj=obj['active_execution_note'] if p==paths[0] else obj['active_execution']
    assert obj['active_work_plan']==plan and obj['release_acceptance']==base+'/release-acceptance.json'
assert all(sha(R/p)==h for p,h in read(H/'source-lock.json').items() if p not in paths)
(H/'advancement.json').write_text(enc(dict(passed=True,changes=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],candidate='5.51 unchanged',phase='C1 bundle recovery',immutable_predecessor_preserved=True)))
print(json.dumps(dict(passed=True,controls=len(paths),active_plan=plan,candidate='5.51 unchanged')))
