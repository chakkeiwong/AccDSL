"""Advance checked documents and current routes, retaining concurrent finance fields."""
from pathlib import Path
import copy,hashlib,json,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-policy-control-v524-20261026';T=R/'docs/design/proposal/manuscript-source-policies-v525-20261027';G=H.parent/'gap-source-policy-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,t):q=p.with_name(p.name+'.source-policy.tmp');q.write_text(t);os.replace(q,p)
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
assert cat['active_execution_note']['current_candidate'].startswith('5.24;');finance=cat['active_execution_note']['active_work_plan'];assert (R/finance).exists()
assert np['active_execution']['active_work_plan']==finance
nextunit='docs/plans/accounting-source-time-intervals-20261027.md';assert (R/nextunit).exists();base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));gv=j(G/'verification.json');assert gv['status']=='PASS'
updates={'updated':'2026-10-27','current_candidate':f"5.25;{main['pages']} pages;not_ready",'latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':main['sha256'],'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sim['sha256'],'current_program':'docs/plans/accounting-source-policy-integration-20261027.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-source-policy-integration-20261027.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':'data/accounting-master/source-policy-invalidation-20261027/result.md','compression_next_plan':nextunit,'active_work_plans':[finance,nextunit],'current_internal_status':'Selected source/actor views and dependency-scoped numerical reuse integrated in5.25; exact interval/private access, live control history and dated accounting authority remain open.'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+['data/accounting-master/certified-source-views-20261026/result.md','data/accounting-master/source-policy-invalidation-20261027/result.md']))
 d['next']=['Continue '+finance,'Execute '+nextunit,'Continue all18 broad packages using their specific closure evidence']
 d['gap_program_next']=['Extend exact interval/private source access without fabricated actor knowledge','Continue live control-history and separate dated acquisition authority/measurement','Continue general numerical domains, persistence and independent acceptance']
text=f'''# Current AccDSL master program

Updated 27 October 2026. Governing candidate **5.25**, {main['pages']} pages, not_ready.
Simulation volume: **{sim['pages']} total / {sim['body_pages']} body pages**, 26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-source-policies-v525-20261027/.
Integration: {result}.
Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.

Conditional source views distinguish publication, actor access, ingestion/review
and economic effective time. All29 revision cases and eight complete policy sets
agree. Seven dependency nodes separate numerical reuse from source/actor binding;
29 change masks and12 tampering controls pass. Same-meaning corrections can reuse
numerical policies while rebinding sources. No actual access or probability follows.
The5.24 control-boundary repair and its unresolved interval histories remain intact.

Active financing lane: {finance}.
Next independent unit: {nextunit}.
Parallel authority dependency: docs/plans/accounting-acquisition-period-authority-20261026.md.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All53 obligations, six interactions,46 operations, nine literature gaps and
18 broad packages remain open;51 deltas and46 interface challenges preserve
provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and
whole-document acceptance remain pending. Continue feasible internal work.
No fees, outreach, publication or background campaign is authorized.

Preserve accepted writers, all predecessor sources and failed diagnostics.
General clocks/private access, actual source/accounting admission, authentication,
durable recovery and production scale require their own evidence.
Current controls: {str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 27 October2026, Version5.25

Use docs/plans/accounting-master-current.md for concise recovery.
Version5.25: {main['pages']} main pages; {sim['pages']} total/{sim['body_pages']} body simulation pages; not_ready.
Selected source/actor views and numerical dependency reuse are integrated.
Actual source truth, general clocks/private access and accounting admission remain open.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Next independent plan: {nextunit}.
All53 obligations, six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Earlier entries remain historical evidence.

'''
for p in paths[4:9]:title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode().replace('Version 5.24, 775 pages',f"Version 5.25, {main['pages']} pages").replace('dated 26 October 2026','dated 27 October 2026').replace('**209 pages**',f"**{sim['pages']} pages**").replace('**190 body pages**',f"**{sim['body_pages']} body pages**").replace('gap-policy-control-refresh-20261026/remaining-work.md','gap-source-policy-refresh-20261027/remaining-work.md').replace('policy-control-integration-20261026/result.md','source-policy-integration-20261027/result.md')
s=s.replace('- [Certified observation policies]','- [Source revision and actor views](../data/accounting-master/certified-source-views-20261026/result.md).\n- [Dependency-scoped policy reuse](../data/accounting-master/source-policy-invalidation-20261027/result.md).\n- [Certified observation policies]');new['docs/README.md']=s
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,f in links.items():assert (R/p).resolve()==S/f
for p,s in new.items():put(R/p,s)
for path,f in links.items():p=R/path;q=p.with_name(p.name+'.source-policy-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for d,key,old in [(cat,'active_execution_note',oldcat),(np,'active_execution',oldnp)]:
 ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key});ck('finance_preserved',d[key]['active_work_plan']==old[key]['active_work_plan']);ck('other_active_fields',all(d[key][k]==v for k,v in old[key].items() if k not in set(updates)|{'latest_internal_results','next','gap_program_next'}))
for n,h in j(G/'predecessor-lock.json').items():ck('prior_gap:'+n,sha(R/n)==h)
for n,h in lock['sources'].items():ck('prior_source:'+n,sha(S/n)==h)
for n,h in lock['evidence'].items():ck('evidence:'+n,sha(R/n)==h)
for p,f in links.items():ck('link:'+p,(R/p).resolve()==T/f)
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
ck('all_packages_open',all(p['status']=='open' for p in j(G/'closure-packages.json')['packages']));ck('short_checkpoint',len(text.splitlines())<50)
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps(dict(status='PASS',candidate='5.25',count=len(checks),checks=checks,finance=finance,next=nextunit,counts=gv['counts'],mission_complete=False),indent=2)+'\n')
print(json.dumps(dict(status='PASS',candidate='5.25',checks=len(checks),main_pages=main['pages'],simulation_pages=sim['pages'],body_pages=sim['body_pages'],finance=finance,mission_complete=False)))
