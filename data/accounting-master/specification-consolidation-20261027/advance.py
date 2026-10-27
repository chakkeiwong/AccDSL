from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
assert not (H/'advancement.json').exists()
v=read(H/'verification-02.json');assert v['passed'] and all(x['passed'] for x in v['checks'])
T=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
for d in v['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
lock=read(H/'layout-source-lock.json')
for n,h in lock['before'].items():assert sha(T/n)==lock['changed'].get(n,h)
for n in ['author-review.md','result.md']:assert (H/n).stat().st_size>1000
plan='docs/plans/accounting-real-company-acceptance-20261027.md';assert (R/plan).is_file()
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths};catalog,nxt=[json.loads(before[p]) for p in paths[:2]]
protected_keys=['latest_gap_program_result','gap_program_review','gap_program_verification']
protected={k:nxt['active_execution'][k] for k in protected_keys}
for obj in [catalog['active_execution_note'],nxt['active_execution']]:
 assert obj['current_candidate']=='5.51;828 pages;not_ready'
 obj.update(current_candidate='5.52;830 pages;not_ready',current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=v['documents'][0]['sha256'],standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=v['documents'][1]['sha256'],
  active_work_plan=plan,active_work_plans=[plan,obj['financing_next_plan']],compression_next_plan=plan,full_gap_plan=plan,
  latest_internal_result=str((H/'result.md').relative_to(R)),specification_consolidation_result=str((H/'result.md').relative_to(R)),failure_dispositions_result='data/accounting-master/integrated-failure-dispositions-20261027/result.md',current_acceptance_progress=str((H/'current-progress.md').relative_to(R)),
  next=['Reconcile all fifteen original real-company dependencies against current interfaces and exact source evidence','Continue C2/C4 complete joins and C3 claim-specific source questions','Preserve whole-document and independent acceptance requirements; S6 held and E3 deferred'],
  current_internal_status='5.52 bounded consolidation verified; 201 original failure targets preserved; scoped bundles and term program complete; all broad acceptance remains open.')
 obj.setdefault('completed_plan_evidence',{}).update({'docs/plans/accounting-integrated-failure-dispositions-20261027.md':'data/accounting-master/integrated-failure-dispositions-20261027/result.md','docs/plans/accounting-specification-consolidation-20261027.md':str((H/'result.md').relative_to(R))})
assert all(nxt['active_execution'][k]==val for k,val in protected.items())
header='''## Current execution — 27 October 2026

Governing candidate **5.52**, 830 main pages and 262 total / 241 body simulation
pages, remains not_ready. Four stable PDF/TeX links select the verified successor.
Main SHA256: 3515dc048a5a0b39551454512bd46ba1a14522d26b88eccee61f62cd38bff2fb.
Simulation SHA256: 74d8950e4b94ff2cbaacdf2b7f429a8153d2a3b028b5dda198227757f53424d3.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Acceptance index: data/accounting-master/acceptance-priority-20261027/release-acceptance.md.
Current progress: data/accounting-master/specification-consolidation-20261027/current-progress.md.
Active plan: docs/plans/accounting-real-company-acceptance-20261027.md.
Result: data/accounting-master/specification-consolidation-20261027/result.md.

The successor reconciles alpha conventions, release milestones, normative file
roots and the selected ordered-term program. Both builds, source/math/citation
preservation and bounded rendered review pass. Two scoped relocated components
and the 201-target failure index remain separately identified evidence; the index
does not claim 201 executed tests. Original 129-delta broad audit stays frozen.
All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Continue current real-company compatibility
and source work; independent acceptance and whole-document review remain pending.
Historical assessments below are preserved.

'''
new={paths[0]:enc(catalog),paths[1]:enc(nxt)}
for p in paths[2:]:
 old=before[p].decode();title,rest=old.split('\n',1)
 if p in paths[-2:]:
  marker='\n## Release-readiness audit';tail=rest[rest.index(marker):] if marker in rest else ''
  new[p]=title+'\n\n'+header+tail
 else:
  first=rest.find('## ');second=rest.find('\n## ',first+3);assert first>=0 and second>=0
  new[p]=title+'\n\n'+header+rest[second+1:]
progress='''# Release progress after 5.52 consolidation

27 October 2026. 5.52 is the provisional governing candidate, not_ready.

| Phase | Completed scope | Remaining work |
|---|---|---|
| C0 | Original-condition and 114-row acceptance reconciliation | Keep subconditions current; no waiver |
| C1 | Historical Core0 and selected-term relocated components; exact normative roots | Full release dependency closure and redistribution dispositions |
| C2 | Seven-interface map; ordered term program; convention and navigation repairs | Remaining company/history/model/report contracts and migrations |
| C3 | Prior dated authority and source findings preserved | Conversion allocation, positive credit recovery, dated insurance groups and consequential literature |
| C4 | 201 original targets preserved; 75 inherited links; X09 audited against full results | Exact remaining failure tests and synthetic/real-company joins |
| C5 | 5.52 bounded source/build/rendered regression | Sequential whole-document semantic/source review |
| C6 | Two scoped isolated reproductions | Complete release reproduction and both volumes |
| C7 | Acceptance requirements preserved | Separate reader, domain and independent implementation evidence |

Current active plan: docs/plans/accounting-real-company-acceptance-20261027.md.
Refresh the original fifteen real-company dependencies against delivered fiscal,
context, population, history and opening interfaces before selecting more work.
Missing issuer facts do not disappear because a reusable interface exists.
The original broad audit remains gap-insurance-stage-refresh-20261027 (129 deltas).
No broad closures: 53 obligations, six interactions, 46 operations, 18 packages.
S1–S5 partial; S6 held; E3 deferred. Source-specific blockers remain local.
'''
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,n in links.items():
 q=R/p;assert q.is_symlink();link_before[p]=os.readlink(q)
 assert 'manuscript-insurance-stage-v551-20261027' in link_before[p]
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,raw in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
(backup/'stable-links.json').write_text(enc(link_before))
(H/'current-progress.md').write_text(progress)
for p,value in new.items():assert (R/p).read_bytes()==before[p];(R/p).write_text(value)
for p,n in links.items():
 q=R/p;tmp=q.with_name(q.name+'.v552-next');assert not tmp.exists() and not tmp.is_symlink()
 tmp.symlink_to(os.path.relpath(T/n,q.parent));os.replace(tmp,q);assert q.resolve()==T/n
for p in paths[:2]:
 d=read(R/p);o=d['active_execution_note'] if p==paths[0] else d['active_execution'];assert o['current_candidate']=='5.52;830 pages;not_ready' and o['active_work_plan']==plan
out=dict(passed=True,timestamp_utc=datetime.now(timezone.utc).isoformat(),candidate='5.52;830 pages;not_ready',next_plan=plan,controls=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],links={p:dict(before=link_before[p],after=os.readlink(R/p)) for p in links},evidence={n:sha(H/n) for n in ['result.md','author-review.md','verification.json','verification-02.json','layout-source-lock.json']},original_gap_audit=protected)
(H/'advancement.json').write_text(enc(out))
print(json.dumps(dict(passed=True,controls=len(paths),links=len(links),candidate=out['candidate'],next_plan=plan)))
