from pathlib import Path
import json,hashlib,os,time,re,sys
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;clock=time.monotonic()
rel=str(D.relative_to(R));T=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027';B=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(p.read_bytes())
def load(p):return json.loads(p.read_text())
def js(o):return (json.dumps(o,indent=2,ensure_ascii=False)+chr(10)).encode()
assert load(D/'final-verification.json')['pass']
package=load(D/'v552r1/package-record.json');assert sha(T/'package-manifest.json')==package['manifest_sha256']
main=package['inputs']['main_pdf'];sim=package['inputs']['simulation_pdf']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for name,target in links.items():assert (R/name).is_symlink() and (R/name).resolve()==B/target,('candidate changed',name)
mds=['MISSION_CONTROL.md','docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-program.md','data/accounting-master/next-plan.md']
json_names=['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
names=mds+['docs/README.md']+json_names
before={n:(R/n).read_bytes() for n in names};next_doc=json.loads(before[json_names[0]]);cat=json.loads(before[json_names[1]]);a=next_doc['active_execution'];note=cat['active_execution_note']
assert a['current_candidate']=='5.52;830 pages;not_ready',a['current_candidate']
active=a['active_work_plan'];assert (R/active).is_file();original_active={k:a.get(k) for k in ['active_work_plan','active_work_plans','next','phase_status','financing_next_plan','full_gap_plan','compression_next_plan']}
snapshot=D/'control-before-integration';snapshot.mkdir(exist_ok=False)
for n,b in before.items():p=snapshot/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
old_links={n:str((R/n).readlink()) for n in links};(D/'rollback-map.json').write_bytes(js({'date':'2026-10-27','before_files':[{'path':n,'snapshot':str((snapshot/n).relative_to(R)),'sha256':sha_bytes(b)} for n,b in before.items()],'before_symlinks':old_links,'warning':'Restore only after checking that no subsequent authorised work would be overwritten. Multi-file integration is not an atomic transaction.'}))
summary=f'''## Current execution — 27 October 2026

Governing candidate **5.52-R1**, 830 main pages and 262 total / 241 body
simulation pages, remains **not_ready**. Four stable PDF/TeX links select the
checked provisional successor.
Main SHA256: {main}.
Simulation SHA256: {sim}.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Acceptance index: {rel}/release-acceptance.md.
Clause-level work: {rel}/acceptance-clauses.md.
Current result: {rel}/result.md.
Remaining release work: {rel}/remaining-work.md.
Active plan: {active}.

Thirteen plan-review findings are addressed in the closure sequence. The
successor preserves 5.52, repairs stale profile descriptions, supplies exact
references and two scoped companions, and passes source/build/relocation checks.
The declared 409-file package is verified. All 17 changed-text pages were viewed;
whole-document and independent acceptance are still open. The 176-key citation
index and 27-claim location map support navigation, not complete source approval.
All 35 original MC provisions and 114 acceptance rows are preserved; the 156
authored clauses are work units, not 156 accepted conditions. MC06/21/22 separate
required capabilities from particular additional examples without any waiver.

Current company audit: data/accounting-master/real-company-acceptance-20261027/result.md.
Its fifteen original dependency categories and exact unknown issuer facts remain
visible. The active debt-source investigation and financing-source plan continue
unchanged. The 201 failure rows are targets/evidence, not 201 executed tests.
All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Internal work continues before any specific
external referral; no publication or paid engagement is authorized here.
Historical assessments below are preserved.

'''
after={}
for n in mds:
 s=before[n].decode();start=s.index('## Current execution — 27 October 2026');end=s.find(chr(10)+'## ',start+4);assert end!=-1,n
 after[n]=(s[:start]+summary+s[end+1:]).encode()
s=before['docs/README.md'].decode();assert 'currently **Version 5.51, 828 pages**' in s
s=s.replace('currently **Version 5.51, 828 pages**','currently **Version 5.52-R1, 830 pages**',1)
s=s.replace('The proposal recommends joint families','The current candidate remains **not_ready**; full specification, source,\nreproduction and independent acceptance work is listed in the current master.\n\nThe proposal recommends joint families',1).replace('\n',chr(10))
s=s.replace('../data/accounting-master/gap-insurance-stage-refresh-20261027/remaining-work.md','../'+rel+'/remaining-work.md',1)
s=s.replace('../data/accounting-master/insurance-stage-integration-20261027/result.md','../'+rel+'/result.md',1)
needle='- [Current master program](plans/accounting-master-current.md).';assert needle in s
s=s.replace(needle,needle+chr(10)+'- [Executed plan review and repairs](../'+rel+'/result.md).'+chr(10)+'- [Current acceptance decisions](../'+rel+'/release-acceptance.md).'+chr(10)+'- [Citation and source navigation](../'+rel+'/citation-source-index.md).',1)
after['docs/README.md']=s.encode()
fields={'updated':'2026-10-27','current_candidate':'5.52-R1;830 pages;not_ready','current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':main,'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sim,'latest_result':rel+'/result.md','latest_internal_result':rel+'/result.md','remaining_work':rel+'/remaining-work.md','full_gap_remaining_work':rel+'/remaining-work.md','release_acceptance':rel+'/release-acceptance.json','current_acceptance_progress':rel+'/result.md','current_internal_status':'5.52-R1 selected provisionally; scoped repairs/builds/relocation/package checks pass; C0-C7 broad acceptance remains open. Active source work is preserved.','latest_reset_memo':rel+'/reset-memo.md','release_plan_execution':{'result':rel+'/result.md','plan_review':rel+'/plan-review.md','clauses':rel+'/acceptance-clauses.json','acceptance':rel+'/release-acceptance.json','source_index':rel+'/citation-source-index.json','claim_map':rel+'/current-claim-map.json','package':str(T.relative_to(R)),'manifest_sha256':package['manifest_sha256'],'verification':rel+'/final-verification.json','integration':rel+'/integration-result.json','remaining_work':rel+'/remaining-work.md','status':'bounded_repairs_complete_release_not_ready'}}
for k,v in fields.items():a[k]=v;note[k]=v
results=['acceptance-priority-20261027','release-bundle-recovery-20261027','profile-compatibility-20261027','selected-term-program-20261027','selected-term-bundle-20261027','integrated-failure-dispositions-20261027','specification-consolidation-20261027','real-company-acceptance-20261027','release-plan-execution-20261027']
for key in ['latest_results','latest_internal_results']:
 dest=a.setdefault(key,[])
 for name in results:
  path='data/accounting-master/'+name+'/result.md'
  if (R/path).is_file() and path not in dest:dest.append(path)
for text in ['Version 5.52: compatible notation, release stages, normative roots and selected term program consolidated; not_ready.','Version 5.52-R1: thirteen plan refinements, protected manuscript repairs, scoped relocated package and current acceptance/source indexes; not_ready.']:
 if text not in a['completed_increments']:a['completed_increments'].append(text)
after[json_names[0]]=js(next_doc);after[json_names[1]]=js(cat)
assert {k:a.get(k) for k in original_active}==original_active
for n in names:assert (R/n).read_bytes()==before[n],('concurrent control change',n)
for n in links:assert str((R/n).readlink())==old_links[n],('concurrent link change',n)
for name,h in [('accounting-product-proposal.pdf',main),('simulation-foundations.pdf',sim)]:assert sha(T/name)==h
journal={'date':'2026-10-27','status':'in_progress','candidate':'5.52-R1','updated_files':[],'updated_links':[],'preserved_active':original_active,'snapshots':str(snapshot.relative_to(R)),'command':[sys.executable,str(Path(__file__).resolve())],'plan':rel+'/integration-plan.md'}
J=D/'integration-result.json';J.write_bytes(js(journal))
for n in names:
 assert (R/n).read_bytes()==before[n],('concurrent control change',n)
 p=R/n;q=p.with_name(p.name+'.release-plan-integration.tmp');assert not q.exists();q.write_bytes(after[n]);os.replace(q,p)
 journal['updated_files'].append({'path':n,'before_sha256':sha_bytes(before[n]),'after_sha256':sha(p)});J.write_bytes(js(journal))
for n,target in links.items():
 p=R/n;assert str(p.readlink())==old_links[n],('concurrent link change',n);new=os.path.relpath(T/target,p.parent);q=p.with_name(p.name+'.release-plan-integration.tmp');assert not q.exists() and not q.is_symlink();q.symlink_to(new);os.replace(q,p)
 journal['updated_links'].append({'path':n,'before':old_links[n],'after':new});J.write_bytes(js(journal))
for n in names:assert (R/n).read_bytes()==after[n],('post integration mismatch',n)
for n,target in links.items():assert (R/n).resolve()==T/target
check=load(R/json_names[0]);assert {k:check['active_execution'].get(k) for k in original_active}==original_active
journal.update(status='provisional_candidate_selected',pass_checks=True,seconds=time.monotonic()-clock,limitations='No release promotion. Atomic replacement per file only; complete old controls and links retained. Active unfinished plans and legacy controller state preserved.')
J.write_bytes(js(journal));print(json.dumps({'status':journal['status'],'files':len(names),'links':len(links),'active_plan_preserved':active,'seconds':journal['seconds']}))
