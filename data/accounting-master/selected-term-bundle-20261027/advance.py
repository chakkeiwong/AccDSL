"""Save current progress and next acceptance dependency without new manuscript."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
assert not (H/'advancement.json').exists()
assert read(H/'attempt-02/verification.json')['passed']
assert read(B/'selected-term-program-20261027/attempt-01/checks.json')['passed']
for p,h in read(H/'attempt-02/source-lock.json').items():assert sha(R/p)==h,p
plan='docs/plans/accounting-integrated-failure-dispositions-20261027.md'
assert (R/plan).is_file()
results=['acceptance-priority-20261027','release-bundle-recovery-20261027','profile-compatibility-20261027','selected-term-program-20261027','selected-term-bundle-20261027']
identities={str((B/n/'result.md').relative_to(R)):sha(B/n/'result.md') for n in results}
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths};catalog,nxt=[json.loads(before[p]) for p in paths[:2]]
for obj in [catalog['active_execution_note'],nxt['active_execution']]:
    assert obj['current_candidate']=='5.51;828 pages;not_ready'
    obj.update(active_work_plan=plan,active_work_plans=[plan,obj['financing_next_plan']],current_program='docs/plans/accounting-release-closure-20261027.md',
      latest_internal_result='data/accounting-master/selected-term-bundle-20261027/result.md',
      selected_term_program_result='data/accounting-master/selected-term-program-20261027/result.md',
      selected_term_bundle_result='data/accounting-master/selected-term-bundle-20261027/result.md',
      core0_bundle_result='data/accounting-master/release-bundle-recovery-20261027/result.md',
      profile_compatibility='data/accounting-master/profile-compatibility-20261027/compatibility.md',
      current_acceptance_progress='data/accounting-master/selected-term-bundle-20261027/current-progress.md',
      compression_next_plan=plan,
      next=['Reconcile 201 failure obligations with exact evidence and tests','Complete remaining C2/C4 joins and modern bundle scope','Continue local accounting-source work; S6 held and E3 deferred'],
      current_internal_status='C0 index complete; two scoped bundles relocated; selected term program complete; global C1/C2/C4 acceptance remains open.')
text='''## Current execution — 27 October 2026

Governing candidate **5.51**, 828 main pages and 262 total / 241 body simulation
pages, remains not_ready. PDFs, stable links and their hashes are unchanged.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Acceptance index: data/accounting-master/acceptance-priority-20261027/release-acceptance.md.
Current progress: data/accounting-master/selected-term-bundle-20261027/current-progress.md.
Active plan: docs/plans/accounting-integrated-failure-dispositions-20261027.md.

Completed since recovery: original-condition reconciliation; historical Core 0
relocation; seven-interface/six-edge compatibility audit; SelectedTermProgram/1
with twenty complete result comparisons and fifteen adverse controls; modern
term-program relocation with full-result hashes and restricted dependency reads.
These are specification companions, not a new manuscript or broad acceptance.
All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Source-dependent work remains local.
Historical assessments below are preserved; follow the current index and plan.

'''
new={paths[0]:enc(catalog),paths[1]:enc(nxt)}
for p in paths[2:]:
    old=before[p].decode();title,rest=old.split('\n',1)
    if p in paths[-2:]:
        marker='\n## Release-readiness audit';tail=rest[rest.index(marker):] if marker in rest else ''
        new[p]=title+'\n\n'+text+tail
    else:
        first=rest.find('## ');second=rest.find('\n## ',first+3);assert first>=0 and second>=0
        new[p]=title+'\n\n'+text+rest[second+1:]
progress='''# Current release work after selected-term relocation

27 October 2026. Governing manuscript 5.51 unchanged; not_ready.

| Step | Completed evidence | Remaining dependency |
|---|---|---|
| C0 acceptance | All 35 original mission conditions and 114 tracked rows reconciled; no waiver | Keep decisions current; independent acceptance remains separate |
| C1 reproducible bundle | Historical Core 0 component and selected-term component relocate exactly | Remaining modern profiles, full manuscript and redistribution dispositions |
| C2 compatible specification | Seven interfaces/six edges; full selected-term ordered program now specified and checked | Broader shared company/sector interfaces, migration, report scope and notation reconciliation |
| C3 source/accounting | Credit/insurance predecessor findings preserved | Conversion allocation, positive credit recovery, dated insurance groups and consequential literature |
| C4 integrated evidence | Two term programs/twenty commands and fifteen failure controls | Bind all 201 failure mechanisms to precise evidence or tests; complete selected real/synthetic joins |
| C5 whole manuscript | Previous version-specific source/build checks preserved | Whole-document semantic/source/rendered regression on a protected successor |
| C6 complete isolated reproduction | Two scoped components pass | Full declared release dependency closure and both volumes |
| C7 independent acceptance | Original requirements and internal preparation retained | Separate reader, implementer and domain evidence after internal work |

Current package actions remain in the acceptance-priority index, with W11/W12/
W14/W16 now supplemented by the completed program and relocated components.
Do not repeat those successful writers. The next active plan is
docs/plans/accounting-integrated-failure-dispositions-20261027.md. Complete
row-specific reconciliation before choosing another scientific or financial
increment. No product/forecast launch or external engagement is authorized.
'''
(H/'current-progress.md').write_text(progress)
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,raw in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
for p,value in new.items():assert (R/p).read_bytes()==before[p];(R/p).write_text(value)
for p in paths[:2]:
    v=read(R/p);v=v['active_execution_note'] if p==paths[0] else v['active_execution'];assert v['active_work_plan']==plan
assert all(sha(R/p)==h for p,h in identities.items())
(H/'advancement.json').write_text(enc(dict(passed=True,results=identities,controls=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],candidate='5.51 unchanged',next_plan=plan)))
print(json.dumps(dict(passed=True,controls=len(paths),results=len(identities),next_plan=plan)))
