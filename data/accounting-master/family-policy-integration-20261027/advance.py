"""Advance verified 5.28 links and current routes; retain frozen controller history."""
from pathlib import Path
import copy,hashlib,json,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-temporal-group-v527-20261027';T=R/'docs/design/proposal/manuscript-family-policies-v528-20261027';G=H.parent/'gap-family-policy-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,t):q=p.with_name(p.name+'.family-policy.tmp');q.write_text(t);os.replace(q,p)
v=j(H/'verification.json');assert v['status']=='PASS' and (H/'author-review.md').exists();lock=j(H/'source-preservation.json')
for n,h in lock['sources'].items():assert sha(S/n)==h
for n,h in lock['evidence'].items():assert sha(R/n)==h
main,sim=v['documents']
for d in v['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for p,f in links.items():assert (R/p).resolve()==S/f
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths};backup=H/'control-before';backup.mkdir(exist_ok=False)
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);oldcat=copy.deepcopy(cat);oldnp=copy.deepcopy(np)
assert cat['active_execution_note']['current_candidate'].startswith('5.27;');oldfinance=cat['active_execution_note']['active_work_plan'];assert np['active_execution']['active_work_plan']==oldfinance
finance=oldfinance
nextunit='docs/plans/accounting-observation-map-binding-20261027.md'
for n in [finance,nextunit]:assert (R/n).exists()
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));gv=j(G/'verification.json');assert gv['status']=='PASS'
updates={'updated':'2026-10-27','current_candidate':f"5.28;{main['pages']} pages;not_ready",'latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':main['sha256'],'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sim['sha256'],'current_program':'docs/plans/accounting-family-policy-integration-20261027.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-family-policy-integration-20261027.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':'data/accounting-master/cross-mechanism-policy-20261027/result.md','compression_next_plan':nextunit,'active_work_plan':finance,'active_work_plans':[finance,nextunit],'current_internal_status':'Complete-family transport and shared-history policies integrated in5.28; observation-map binding, live financing methods and actual admission remain open.'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+['data/accounting-master/temporal-family-binding-20261027/result.md','data/accounting-master/cross-mechanism-policy-20261027/result.md']))
 d['next']=['Continue '+finance,'Execute '+nextunit,'Continue all18 broad packages using their specified closure evidence']
 d['gap_program_next']=['Bind actor observation maps and information timing before policy reuse','Continue the live financing plan: '+finance,'Continue saved temporal frontiers, general numerical domains, durable recovery and independent acceptance']
text=f'''# Current AccDSL master program

Updated 27 October 2026. Governing candidate **5.28**, {main['pages']} main pages, not_ready.
Simulation: **{sim['pages']} total / {sim['body_pages']} body pages**, 26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-family-policies-v528-20261027/.
Result: {result}.
Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.

Complete temporal-family binding passes26 cases,307 assertions and26 controls;
117 saved-replay checks retain all source supports and full numerical results.
Common-history policy analysis passes21 cases,350 assertions and eight controls.
Two separately feasible four-policy mechanisms can have no common hidden-mechanism
policy; early identity revelation yields16. Late learning depends on whether an
earlier conflict has already occurred. The failed expected count is preserved.
Both editions pass{v['count']} document checks with bounded added-page review.

Active financing plan: {finance}.
Latest financing result: {cat['active_execution_note'].get('latest_financing_result','not recorded')}.
Independent next plan: {nextunit}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All53 obligations, six interactions,46 operations, nine literature gaps and
18 broad packages remain open;{gv['counts']['successor_deltas']} deltas and{gv['counts']['cross_interface_challenges']} interface challenges preserve provenance.
S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and whole-document
acceptance remain pending. Continue feasible internal work. Preserve accepted
writers, predecessor sources, current financing work and failed diagnostics.
No fees, outreach, publication or background campaign is authorized.
Protected pre-advancement controls: {str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 27 October 2026, Version 5.28

Concise recovery: docs/plans/accounting-master-current.md.
Version 5.28: {main['pages']} main pages; {sim['pages']} total / {sim['body_pages']} body simulation pages; not_ready.
Complete-family reuse and cross-mechanism common policies are integrated.
Observation-map assumptions remain explicit; no actual actor/accounting admission follows.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Independent plan: {nextunit}.
All53 obligations, six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Earlier entries remain historical evidence.

'''
for p in paths[4:9]:title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode().replace('Version 5.27, 783 pages',f"Version 5.28, {main['pages']} pages").replace('**216 pages**',f"**{sim['pages']} pages**").replace('**197 body pages**',f"**{sim['body_pages']} body pages**")
prior_gap=j(G/'verification.json')['predecessor'];s=s.replace(prior_gap+'/remaining-work.md',base+'/remaining-work.md').replace('temporal-group-integration-20261027/result.md','family-policy-integration-20261027/result.md')
s=s.replace('- [Exact temporal source-view families]','- [Complete temporal-family binding](../data/accounting-master/temporal-family-binding-20261027/result.md).\n- [Policies across uncertain observation mechanisms](../data/accounting-master/cross-mechanism-policy-20261027/result.md).\n- [Exact temporal source-view families]');new['docs/README.md']=s
assert cat['active_execution_note']['full_gap_program']==base+'/closure-program.md'
assert oldcat['active_execution_note']['full_gap_program']==prior_gap+'/closure-program.md','gap_predecessor_drift'
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,f in links.items():assert (R/p).resolve()==S/f
for p,s in new.items():put(R/p,s)
for path,f in links.items():p=R/path;q=p.with_name(p.name+'.family-policy-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for d,key,old in [(cat,'active_execution_note',oldcat),(np,'active_execution',oldnp)]:
 ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key});ck('other_active_fields',all(d[key][k]==val for k,val in old[key].items() if k not in set(updates)|{'latest_internal_results','next','gap_program_next'}))
for n,h in j(G/'predecessor-lock.json').items():ck('prior_gap:'+n,sha(R/n)==h)
for n,h in lock['sources'].items():ck('prior_source:'+n,sha(S/n)==h)
for n,h in lock['evidence'].items():ck('evidence:'+n,sha(R/n)==h)
for p,f in links.items():ck('link:'+p,(R/p).resolve()==T/f)
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
ck('all_packages_open',all(p['status']=='open' for p in j(G/'closure-packages.json')['packages']));ck('short_checkpoint',len(text.splitlines())<50)
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps(dict(status='PASS',candidate='5.28',count=len(checks),checks=checks,finance=finance,next=nextunit,counts=gv['counts'],mission_complete=False),indent=2)+'\n')
print(json.dumps(dict(status='PASS',candidate='5.28',checks=len(checks),main_pages=main['pages'],simulation_pages=sim['pages'],body_pages=sim['body_pages'],finance=finance,mission_complete=False)))
