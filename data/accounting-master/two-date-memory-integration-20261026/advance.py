from pathlib import Path
import json,hashlib,os,copy,re
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-continuous-guards-v520-20261026';T=R/'docs/design/proposal/manuscript-two-date-memory-v521-20261026'
G=R/'data/accounting-master/gap-memory-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,s):q=p.with_name(p.name+'.memory-refresh.tmp');q.write_text(s);os.replace(q,p)
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
assert cat['active_execution_note']['current_candidate'].startswith('5.20;')
finance=cat['active_execution_note']['active_work_plan'];assert (R/finance).exists()
nextunit='docs/plans/accounting-guarded-memory-runtime-20261026.md'
a=j(G/'audit-status.json');assert len(a['successor_deltas'])==34
a['successor_deltas'].append({'id':'D35','title':'Two-date memory integrated in both editions','requirements':['MC05','MC11','MC12','MC26','MC28','MC33','MC34','W17'],'evidence':str((H/'result.md').relative_to(R)),'sha256':sha(H/'result.md'),'current_disposition':'Version5.21,765 main pages,198 total/180 body simulation pages;246 prior sources and61 evidence files retained;566 checks and bounded rendered review. No whole requirement closes.'})
a['baseline']='Version5.21 integrates continuous guard and two-date memory references; separate financing authority/measurement companions remain active.'
put(G/'audit-status.json',json.dumps(a,indent=2)+'\n');gv=j(G/'verification.json');gv['counts']['successor_deltas']=35;put(G/'verification.json',json.dumps(gv,indent=2)+'\n')
cp=j(G/'closure-packages.json')
for row in cp['packages']:
 if row['id']=='W17':
  row['existing_support']+=' The two-date continuous-memory explanation is integrated in both5.21 editions with all prior sources retained.'
  row['next_action']='Integrate separate funding and authority/measurement findings; continue main-chapter consistency and independent reader/domain review.'
put(G/'closure-packages.json',json.dumps(cp,indent=2)+'\n')
p=G/'closure-program.md';put(p,p.read_text().replace('Next action: Integrate the checked two-date continuation and the separate funding/authority findings; continue main-chapter consistency and independent reader/domain review.','Next action: Integrate separate funding and authority/measurement findings; continue main-chapter consistency and independent reader/domain review.'))
p=G/'remaining-work.md';put(p,p.read_text().replace('Integrate the checked two-date continuation and the separate funding/authority findings; continue main-chapter consistency and independent reader/domain review.','Integrate separate funding and authority/measurement findings; continue main-chapter consistency and independent reader/domain review.'))
p=G/'result.md';put(p,p.read_text()+'\nD35 records the protected5.21 dual-edition integration. There are35 successor deltas and27 cross-interface challenges; all18 packages remain open.\n')
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R))
updates={'updated':'2026-10-26','current_candidate':'5.21;765 pages;not_ready','latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':sha(T/'accounting-product-proposal.pdf'),'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sha(T/'simulation-foundations.pdf'),'current_program':'docs/plans/accounting-two-date-memory-integration-20261026.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-two-date-memory-integration-20261026.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':'data/accounting-master/two-date-continuous-memory-20261026/result.md','compression_next_plan':nextunit,'current_internal_status':'One-date and two-date continuous memory references integrated in5.21; common runtime/budget/revision work remains; active financing authority preserved'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['active_work_plans']=[finance,nextunit]
 d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[updates['latest_compression_result']]))
 d['next']=['Continue '+finance,'Inspect and bind guarded memory under '+nextunit,'Integrate funding/source findings and continue the full18-package queue']
 d['gap_program_next']=['Bind continuous regions to common typed execution and budget/revision guarantees','Complete active financing authority and measurement','Continue all open packages without promoting bounded examples']
text=f'''# Current AccDSL master program

Updated 26 October 2026. Governing candidate **5.21**, 765 pages, not_ready.
Simulation volume: **198 total / 180 body pages**, 26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-two-date-memory-v521-20261026/.
Integration: {result}.
Main SHA256: {updates['current_pdf_sha256']}.
Standalone SHA256: {updates['standalone_pdf_sha256']}.

Current question: connect exact retained histories, available information and
financing memory to common execution and actual accounting authority.
One-date continuous sharing passes 264 complete symbolic comparisons.
The two-date continuation passes 2,828 complete-state comparisons and exact
action-domain checks across 968 rate/mode/receipt cells. First borrowing,
repayment, used-facility memory and unpaid claims survive; receipt6 versus7
changes feasibility under explicit synthetic premises. No scaling claim.

Active financing lane: {finance}.
Next independent unit: {nextunit}.
Full dependency program: {base}/closure-program.md.
All remaining work: {base}/remaining-work.md.
Gap verification: {base}/verification.json.

All 53 obligations, six interactions, 46 operations, nine literature gaps and
18 broad packages remain open; 35 successor deltas and 27 interface challenges
preserve provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/
domain and whole-document acceptance remain pending. Continue feasible internal
research before paid review; no fees, outreach or background campaign authorized.

Preserve successful writers and all failed attempts. The two-date schema repair
and reviewed attempt extension are recorded with the exact reference. Detailed
history and previous control text are retained in linked results and
{str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 26 October 2026, Version 5.21

Use docs/plans/accounting-master-current.md for the concise recovery state.
Version 5.21 has 765 main pages; the matching simulation edition has
198 total / 180 body pages across 26 chapters, not_ready.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Next independent plan: {nextunit}.
All 53 obligations, six interactions, 46 operations and 18 packages remain.
S1–S5 partial; S6 held; E3 deferred. Historical dated notes below are retained
evidence and do not override the current checkpoint.

'''
for path in paths[4:9]:
 old=before[path].decode();title,body=old.split('\n',1);body=body.lstrip('\n')
 # Replace the immediately preceding live-routes block, preserving all older
 # dated material and its complete saved predecessor.
 if body.startswith('## Current routes'):
  pos=body.find('\n## ',4);body=body[pos+1:] if pos!=-1 else ''
 new[path]=title+'\n\n'+top+body
r=before['docs/README.md'].decode().replace('Version 5.20, 763 pages','Version 5.21, 765 pages').replace('**196 pages**','**198 pages**').replace('**178 body pages**','**180 body pages**').replace('gap-continuous-refresh-20261026/remaining-work.md','gap-memory-refresh-20261026/remaining-work.md').replace('continuous-guards-integration-20261026/result.md','two-date-memory-integration-20261026/result.md')
r=r.replace('- [Exact continuous guard comparison]','- [Two-date cash and contractual memory](../data/accounting-master/two-date-continuous-memory-20261026/result.md).\n- [Exact continuous guard comparison]');new['docs/README.md']=r
for path,b in before.items():assert (R/path).read_bytes()==b,'concurrent control drift '+path
for path,f in links.items():assert (R/path).resolve()==S/f
for path,s in new.items():put(R/path,s)
for path,f in links.items():
 p=R/path;q=p.with_name(p.name+'.memory-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for d,key,old in [(cat,'active_execution_note',oldcat),(np,'active_execution',oldnp)]:
 ck('legacy_fields', {k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key})
 ck('active_financing',d[key]['active_work_plan']==old[key]['active_work_plan'])
for path,f in links.items():ck('link:'+path,(R/path).resolve()==T/f)
for name,h in j(G/'predecessor-lock.json').items():ck('old_gap:'+name,sha(R/name)==h)
for name,h in lock['sources'].items():ck('prior_source:'+name,sha(S/name)==h)
for name,h in lock['evidence'].items():ck('evidence:'+name,sha(R/name)==h)
prev=j(R/'data/accounting-master/gap-continuous-refresh-20261026/audit-status.json')
ck('inherited_rows',a['groups']==prev['groups'] and a['literature']==prev['literature'] and a['successor_deltas'][:33]==prev['successor_deltas'])
for delta in a['successor_deltas'][33:]:ck('new_delta_hash:'+delta['id'],sha(R/delta['evidence'])==delta['sha256'])
ck('all_open',all(p['status']=='open' for p in cp['packages']))
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
ck('concise_checkpoint',len(text.splitlines())<50)
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps({'status':'PASS','candidate':'5.21','checks':checks,'count':len(checks),'preserved_financing_plan':finance,'next_independent_plan':nextunit,'control_backup':str(backup.relative_to(R)),'counts':gv['counts'],'mission_complete':False},indent=2)+'\n')
print(json.dumps({'status':'PASS','candidate':'5.21','checks':len(checks),'main_pages':765,'simulation_pages':198,'simulation_body_pages':180,'active_financing_plan':finance,'mission_complete':False}))
