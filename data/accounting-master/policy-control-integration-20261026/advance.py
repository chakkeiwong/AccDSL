"""Advance only current document/master routes, preserving legacy controller state."""
from pathlib import Path
import copy,hashlib,json,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-symbolic-regions-v523-20261026';T=R/'docs/design/proposal/manuscript-policy-control-v524-20261026';G=H.parent/'gap-policy-control-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,s):q=p.with_name(p.name+'.policy.tmp');q.write_text(s);os.replace(q,p)
v=j(H/'verification.json');assert v['status']=='PASS';assert (H/'author-review.md').exists();lock=j(H/'source-preservation.json')
for n,h in lock['sources'].items():assert sha(S/n)==h
for n,h in lock['evidence'].items():assert sha(R/n)==h
for d in v['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for n,f in links.items():assert (R/n).resolve()==S/f
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={n:(R/n).read_bytes() for n in paths};backup=H/'control-before';backup.mkdir(exist_ok=True)
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists() or p.read_bytes()==b,'saved_control_drift:'+n;p.write_bytes(b)
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);oc=copy.deepcopy(cat);on=copy.deepcopy(np)
assert cat['active_execution_note']['current_candidate'].startswith('5.23;')
assert cat['active_execution_note']['active_work_plan']=='docs/plans/accounting-control-history-contract-20261026.md'
finance=cat['active_execution_note']['active_work_plan'];nextunit='docs/plans/accounting-certified-source-views-20261026.md'
for path in [finance,nextunit]:assert (R/path).exists()
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));gv=j(G/'verification.json');assert gv['status']=='PASS'
main,sim=v['documents'];assert main['document']=='accounting-product-proposal' and sim['document']=='simulation-foundations'
updates={'updated':'2026-10-26','current_candidate':f"5.24;{main['pages']} pages;not_ready",'latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':main['sha256'],'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sim['sha256'],'current_program':'docs/plans/accounting-policy-control-integration-20261026.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-policy-control-integration-20261026.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':'data/accounting-master/certified-observation-policy-20261026/result.md','latest_financing_result':'data/accounting-master/control-boundary-repair-20261026/result.md','compression_next_plan':nextunit,'active_work_plan':finance,'active_work_plans':[finance,nextunit],'current_internal_status':'Selected certified policies, conversion scope and repaired control-history alternatives integrated in 5.24; source/actor bindings, interval-control history and dated authority continue.'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[updates['latest_compression_result'],updates['latest_financing_result']]))
 d['next']=['Execute '+finance,'Execute '+nextunit,'Continue all 18 packages against their specific closure evidence']
 d['gap_program_next']=['Bind source revisions and actor access to certified policies without inventing probabilities','Finish dated authority/entity chain and acquisition-period requirements','Continue general domains, persistence and independent acceptance separately']
text=f'''# Current AccDSL master program

Updated 26 October 2026. Governing candidate **5.24**, {main['pages']} pages, not_ready.
Simulation volume: **{sim['pages']} total / {sim['body_pages']} body pages**, 26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-policy-control-v524-20261026/.
Integration: {result}.
Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.

Certified observation policies now compose the 3,872 exact financial jobs with
whole-region observation refinements. Two independent complete policy sets agree
in eight problems; only receipt 7/refined/committed has four feasible policies.
No probabilities, ranking or actual-manager information is inferred.
Conversion scope preserves control before/after share issuance, distinct reporting
perimeters and business/asset routes. The repaired /2 reference retains all nine
endpoint combinations and possible intervening changes; every case withholds posting.
Dated entity/edition applicability and acquisition measurements remain unresolved.

Active financing lane: {finance}.
Next independent unit: {nextunit}.
Parallel authority dependency: docs/plans/accounting-acquisition-period-authority-20261026.md.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All 53 obligations, six interactions, 46 operations, nine literature gaps and
18 broad packages remain open; 48 deltas and 42 interface challenges preserve
provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and
whole-document acceptance remain pending. Continue feasible internal work.
No fees, outreach, publication or background campaign is authorized.

Preserve all accepted writers, predecessor sources and failed diagnostics.
Selected policy completion does not establish actual source/actor admission,
general compiler correctness, accounting compliance or durable recovery.
Current controls: {str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 26 October 2026, Version 5.24

Use docs/plans/accounting-master-current.md for concise recovery.
Version 5.24: {main['pages']} main pages; {sim['pages']} total / {sim['body_pages']} body simulation pages; not_ready.
Certified observation policies, conversion scope and repaired control-history alternatives are integrated.
Selected policy feasibility does not establish actual actor knowledge or accounting admission.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Next independent plan: {nextunit}.
All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Earlier entries remain historical evidence.

'''
for path in paths[4:9]:
 title,body=before[path].decode().split('\n',1);new[path]=title+'\n\n'+top+body.lstrip('\n')
r=before['docs/README.md'].decode().replace('Version 5.23, 770 pages',f"Version 5.24, {main['pages']} pages").replace('**203 pages**',f"**{sim['pages']} pages**").replace('**185 body pages**',f"**{sim['body_pages']} body pages**").replace('gap-symbolic-refresh-20261026/remaining-work.md','gap-policy-control-refresh-20261026/remaining-work.md').replace('symbolic-region-integration-20261026/result.md','policy-control-integration-20261026/result.md')
r=r.replace('- [Exact region proofs','- [Certified observation policies](../data/accounting-master/certified-observation-policy-20261026/result.md).\n- [Conversion control and reporting scope](../data/accounting-master/conversion-control-scope-20261026/result.md).\n- [Control-history boundary repair](../data/accounting-master/control-boundary-repair-20261026/result.md).\n- [Exact region proofs');new['docs/README.md']=r
for p,b in before.items():assert (R/p).read_bytes()==b,'control_drift:'+p
for p,f in links.items():assert (R/p).resolve()==S/f
for p,s in new.items():put(R/p,s)
for path,f in links.items():
 p=R/path;q=p.with_name(p.name+'.policy-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append(dict(name=n,pass_=bool(ok)));assert ok,n
for d,key,old in [(cat,'active_execution_note',oc),(np,'active_execution',on)]:
 ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key})
 ck('retained_active_fields',all(d[key][k]==val for k,val in old[key].items() if k not in set(updates)|{'latest_internal_results','next','gap_program_next'}))
for p,f in links.items():ck('link:'+p,(R/p).resolve()==T/f)
for n,h in j(G/'predecessor-lock.json').items():ck('prior_gap:'+n,sha(R/n)==h)
for n,h in lock['sources'].items():ck('prior_source:'+n,sha(S/n)==h)
for n,h in lock['evidence'].items():ck('evidence:'+n,sha(R/n)==h)
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
ck('all_packages_open',all(p['status']=='open' for p in j(G/'closure-packages.json')['packages']))
ck('short_current_checkpoint',len(text.splitlines())<50)
for path,s in new.items():ck('readback:'+path,(R/path).read_text()==s)
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps(dict(status='PASS',candidate='5.24',count=len(checks),checks=checks,finance=finance,next=nextunit,counts=gv['counts'],mission_complete=False),indent=2)+'\n')
print(json.dumps(dict(status='PASS',candidate='5.24',checks=len(checks),main_pages=main['pages'],simulation_pages=sim['pages'],body_pages=sim['body_pages'],mission_complete=False)))
