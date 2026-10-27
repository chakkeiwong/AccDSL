from pathlib import Path
import copy,hashlib,json,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-guarded-memory-v522-20261026';T=R/'docs/design/proposal/manuscript-symbolic-regions-v523-20261026';G=R/'data/accounting-master/gap-symbolic-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,s):q=p.with_name(p.name+'.symbolic.tmp');q.write_text(s);os.replace(q,p)
v=j(H/'verification.json');assert v['status']=='PASS';lock=j(H/'source-preservation.json')
for n,h in lock['sources'].items():assert sha(S/n)==h
for n,h in lock['evidence'].items():assert sha(R/n)==h
for d in v['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for n,f in links.items():assert (R/n).resolve()==S/f
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={n:(R/n).read_bytes() for n in paths};backup=H/'control-before';backup.mkdir(exist_ok=False)
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);oldcat=copy.deepcopy(cat);oldnp=copy.deepcopy(np)
assert cat['active_execution_note']['current_candidate'].startswith('5.22;')
finance=cat['active_execution_note']['active_work_plan'];assert (R/finance).exists()
nextunit='docs/plans/accounting-certified-observation-policy-20261026.md';base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));companion='data/accounting-master/exact-region-certificates-20261026/queue-result.md'
a=j(G/'audit-status.json');assert len(a['successor_deltas'])==43
a['successor_deltas'].append({'id':'D44','title':'Exact symbolic-region derivation integrated in both editions','requirements':['MC11','MC12','MC17','MC24','MC25','MC26','MC28','MC33','MC34','W17'],'evidence':result,'sha256':sha(H/'result.md'),'current_disposition':'Version5.23,770 main pages,203 total/185 body simulation pages;248 predecessor sources and187 evidence files retained;696 checks and bounded rendered review. General domains and actor-policy composition remain open.'})
a['baseline']='Version5.23 integrates selected exact method, sequence, region and saved-proof queue certificates; observation-policy and actual financing authority remain independent.'
put(G/'audit-status.json',json.dumps(a,indent=2)+'\n');gv=j(G/'verification.json');gv['counts']['successor_deltas']=44;put(G/'verification.json',json.dumps(gv,indent=2)+'\n')
cp=j(G/'closure-packages.json')
for row in cp['packages']:
 if row['id']=='W17':row['existing_support']+=' The selected symbolic-region derivation is now integrated in both5.23 editions with protected source and rendered checks.';row['next_action']='Integrate future observation-policy and separate funding/authority results; continue whole-document consistency and independent reader/domain review.'
put(G/'closure-packages.json',json.dumps(cp,indent=2)+'\n')
for name in ('closure-program.md','remaining-work.md'):
 p=G/name;put(p,p.read_text().replace('Integrate symbolic certificate findings and separate funding/authority results; continue whole-document consistency and independent reader/domain review.','Integrate future observation-policy and separate funding/authority results; continue whole-document consistency and independent reader/domain review.'))
p=G/'result.md';put(p,p.read_text()+'\nD44 records the protected5.23 dual-edition integration:44 deltas,36 cross-interface challenges. All18 packages remain open.\n')
updates={'updated':'2026-10-26','current_candidate':'5.23;770 pages;not_ready','latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':sha(T/'accounting-product-proposal.pdf'),'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sha(T/'simulation-foundations.pdf'),'current_program':'docs/plans/accounting-symbolic-region-integration-20261026.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-symbolic-region-integration-20261026.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':companion,'compression_next_plan':nextunit,'current_internal_status':'Selected3872 exact-region jobs and saved-proof queue certified and integrated in5.23; observation-policy composition and actual financing control/measurement remain open'}
for d in (cat['active_execution_note'],np['active_execution']):
 d.update(updates);d['active_work_plans']=[finance,nextunit]
 d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+['data/accounting-master/'+p for p in ['symbolic-method-certificate-20261026/result.md','symbolic-path-composition-20261026/result.md','exact-region-certificates-20261026/result.md','exact-region-certificates-20261026/queue-result.md']]))
 d['next']=['Continue '+finance,'Execute certified observation-policy comparison under '+nextunit,'Continue all18 broad packages with their specific closure evidence']
 d['gap_program_next']=['Bind exact certified leaves to observation-measurable feasible policies','Complete active financing control scope, measurement and edition admission','Extend general domains/unknown semantics/durability under separate evidence']
text=f'''# Current AccDSL master program

Updated26 October2026. Governing candidate **5.23**,770 pages,not_ready.
Simulation volume: **203 total /185 body pages**,26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-symbolic-regions-v523-20261026/.
Integration: {result}.
Main SHA256: {updates['current_pdf_sha256']}.
Simulation SHA256: {updates['standalone_pdf_sha256']}.

Selected known-valued method relations, complete sequences and all3872 two-rate/
order jobs now have checked exact certificates. The partition has918 accepted
and2960 refusal leaves;4772 empty children have weighted contradiction proofs.
The saved archive and JSON queue revalidate before completion. Historical
concrete checkpoints retain their original unresolved scope. No probability,
general compiler proof, actual authority or production-scale claim follows.
Detailed evidence: {companion}.

Active financing lane: {finance}.
Next independent unit: {nextunit}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All53 obligations, six interactions,46 operations, nine literature gaps and
18 broad packages remain open;44 deltas and36 interface challenges preserve
provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and
whole-document acceptance remain pending. Ready internal work continues before
paid review; no fees, outreach or background campaign authorized.

Preserve accepted writers and all failures. Numerical region completion,
observation-measurable policies, actual authority, unknown-value semantics and
durable recovery have separate acceptance criteria. Current controls saved in
{str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes —26 October2026, Version5.23

Use docs/plans/accounting-master-current.md for the concise recovery state.
Version5.23 has770 main pages and203 total/185 body simulation pages,not_ready.
Selected method/sequence/region certificates and proof-bound queue are integrated.
All3872 selected jobs have exact partitions; this does not close general domains,
actor-information policy, actual accounting authority or durability requirements.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Next computational plan: {nextunit}.
All53 obligations, six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Earlier dated records remain historical.

'''
for path in paths[4:9]:
 title,body=before[path].decode().split('\n',1);new[path]=title+'\n\n'+top+body.lstrip('\n')
r=before['docs/README.md'].decode().replace('Version 5.22, 767 pages','Version 5.23, 770 pages').replace('**200 pages**','**203 pages**').replace('**182 body pages**','**185 body pages**').replace('gap-runtime-refresh-20261026/remaining-work.md','gap-symbolic-refresh-20261026/remaining-work.md').replace('guarded-memory-integration-20261026/result.md','symbolic-region-integration-20261026/result.md')
r=r.replace('- [Common accounting and checkpoint evidence]','- [Exact region proofs and saved queue](../data/accounting-master/exact-region-certificates-20261026/queue-result.md).\n- [Common accounting and checkpoint evidence]');new['docs/README.md']=r
for path,b in before.items():assert (R/path).read_bytes()==b,'concurrent_control_drift:'+path
for path,f in links.items():assert (R/path).resolve()==S/f,'concurrent_link_drift'
for path,s in new.items():put(R/path,s)
for path,f in links.items():
 p=R/path;q=p.with_name(p.name+'.symbolic-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for d,key,old in ((cat,'active_execution_note',oldcat),(np,'active_execution',oldnp)):
 ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key});ck('financing_route',d[key]['active_work_plan']==old[key]['active_work_plan'])
for path,f in links.items():ck('link:'+path,(R/path).resolve()==T/f)
for n,h in j(G/'predecessor-lock.json').items():ck('old_gap:'+n,sha(R/n)==h)
for n,h in lock['sources'].items():ck('predecessor_source:'+n,sha(S/n)==h)
for n,h in lock['evidence'].items():ck('evidence:'+n,sha(R/n)==h)
prev=j(R/'data/accounting-master/gap-runtime-refresh-20261026/audit-status.json');ck('inherited',a['groups']==prev['groups'] and a['literature']==prev['literature'] and a['successor_deltas'][:38]==prev['successor_deltas'])
for delta in a['successor_deltas'][38:]:ck('delta:'+delta['id'],sha(R/delta['evidence'])==delta['sha256'])
ck('all_packages_open',all(p['status']=='open' for p in cp['packages']));ck('concise_checkpoint',len(text.splitlines())<50)
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps({'status':'PASS','candidate':'5.23','count':len(checks),'checks':checks,'preserved_financing_plan':finance,'next_plan':nextunit,'counts':gv['counts'],'mission_complete':False},indent=2)+'\n')
print(json.dumps({'status':'PASS','candidate':'5.23','checks':len(checks),'main_pages':770,'simulation_pages':203,'body_pages':185,'finance':finance,'next':nextunit,'mission_complete':False}))
