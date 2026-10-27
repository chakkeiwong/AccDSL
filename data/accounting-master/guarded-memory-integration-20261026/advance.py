from pathlib import Path
import json,hashlib,os,copy
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-two-date-memory-v521-20261026';T=R/'docs/design/proposal/manuscript-guarded-memory-v522-20261026';G=R/'data/accounting-master/gap-runtime-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,s):q=p.with_name(p.name+'.guarded-refresh.tmp');q.write_text(s);os.replace(q,p)
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
assert cat['active_execution_note']['current_candidate'].startswith('5.21;')
finance=cat['active_execution_note']['active_work_plan'];assert (R/finance).exists()
nextunit='docs/plans/accounting-symbolic-method-certificate-20261026.md';base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));companion='data/accounting-master/guarded-memory-runtime-20261026/result.md'
a=j(G/'audit-status.json');assert len(a['successor_deltas'])==37
a['successor_deltas'].append({'id':'D38','title':'Common execution and checkpoint explanation integrated','requirements':['MC11','MC12','MC17','MC24','MC25','MC26','MC28','MC33','MC34','W17'],'evidence':result,'sha256':sha(H/'result.md'),'current_disposition':'Version5.22,767 main pages,200 total/182 body simulation pages;247 source files and60 evidence files retained;567 build/source checks and bounded rendered review. No whole requirement closes.'})
a['baseline']='Version5.22 integrates common guarded accounting and concrete replay; symbolic-region certification and financing authority remain separate active work.'
put(G/'audit-status.json',json.dumps(a,indent=2)+'\n');gv=j(G/'verification.json');gv['counts']['successor_deltas']=38;put(G/'verification.json',json.dumps(gv,indent=2)+'\n')
cp=j(G/'closure-packages.json')
for row in cp['packages']:
 if row['id']=='W17':
  row['existing_support']+=' Common accounting/replay findings are integrated in both5.22 editions under source-preservation and bounded rendered checks.'
  row['next_action']='Integrate separate funding/authority findings and future checked symbolic certificates; continue main-chapter consistency and independent reader/domain review.'
put(G/'closure-packages.json',json.dumps(cp,indent=2)+'\n')
for name in ['closure-program.md','remaining-work.md']:
 p=G/name;put(p,p.read_text().replace('Integrate checked common-runtime/checkpoint findings and separate funding/authority results; continue main-chapter consistency and independent reader/domain review.','Integrate separate funding/authority findings and future checked symbolic certificates; continue main-chapter consistency and independent reader/domain review.'))
p=G/'result.md';put(p,p.read_text()+'\nD38 records the protected5.22 dual-edition integration. The register now contains38 deltas and31 cross-interface challenges. All18 packages remain open.\n')
updates={'updated':'2026-10-26','current_candidate':'5.22;767 pages;not_ready','latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':sha(T/'accounting-product-proposal.pdf'),'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sha(T/'simulation-foundations.pdf'),'current_program':'docs/plans/accounting-guarded-memory-integration-20261026.md','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-guarded-memory-integration-20261026.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':gv['counts'],'latest_compression_result':companion,'compression_next_plan':nextunit,'current_internal_status':'Common typed concrete bridge and replay checkpoints integrated in5.22; full symbolic certification and financing authority remain open'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['active_work_plans']=[finance,nextunit]
 d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[companion]))
 d['next']=['Continue '+finance,'Execute symbolic interface audit under '+nextunit,'Integrate funding/source findings and continue the full18-package queue']
 d['gap_program_next']=['Certify symbolic effects/guards/memory across supported regions','Complete active financing authority and measurement','Continue all open packages without promoting bounded concrete examples']
text=f'''# Current AccDSL master program

Updated 26 October 2026. Governing candidate **5.22**, 767 pages, not_ready.
Simulation volume: **200 total / 182 body pages**, 26 chapters.
Both PDF/TeX pairs select docs/design/proposal/manuscript-guarded-memory-v522-20261026/.
Integration: {result}.
Main SHA256: {updates['current_pdf_sha256']}.
Standalone SHA256: {updates['standalone_pdf_sha256']}.

Current question: certify the symbolic relation between retained history regions
and common accounting methods while finishing actual financing authority.
The concrete bridge passes28 complete programs/two charts, including full books,
journals, cash flows, reports and refusal prefixes. Replay checkpoints pass16
resume cases and retain3872 continuous-region obligations as unresolved. No
concrete witness is promoted to a whole-region certificate. Shared engines are
unchanged. Detailed evidence: {companion}.

Active financing lane: {finance}.
Next independent unit: {nextunit}.
Full program: {base}/closure-program.md.
All remaining work: {base}/remaining-work.md.
Gap verification: {base}/verification.json.

All53 obligations, six interactions,46 operations, nine literature gaps and
18 broad packages remain open;38 deltas and31 interface challenges preserve
provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and
whole-document acceptance remain pending. Ready internal work continues before
paid review; no fees, outreach or background campaign authorized.

Preserve accepted evidence writers and all prior failures. Financial execution,
concrete replay, continuous certification, actual source admission and durable
recovery have separate acceptance criteria. Previous controls are retained under
{str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 26 October 2026, Version 5.22

Use docs/plans/accounting-master-current.md for the concise recovery state.
Version5.22 has767 main pages; the matching simulation edition has200 total /
182 body pages across26 chapters, not_ready. Common accounting/replay findings
are integrated; symbolic-region certification and actual authority remain open.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Next independent plan: {nextunit}.
All53 obligations, six interactions,46 operations and18 packages remain.
S1–S5 partial; S6 held; E3 deferred. Older dated notes are retained evidence,
not overrides of the current recovery checkpoint.

'''
for path in paths[4:9]:
 title,body=before[path].decode().split('\n',1);body=body.lstrip('\n')
 if body.startswith('## Current routes'):
  pos=body.find('\n## ',4);body=body[pos+1:] if pos!=-1 else ''
 new[path]=title+'\n\n'+top+body
r=before['docs/README.md'].decode().replace('Version 5.21, 765 pages','Version 5.22, 767 pages').replace('**198 pages**','**200 pages**').replace('**180 body pages**','**182 body pages**').replace('gap-memory-refresh-20261026/remaining-work.md','gap-runtime-refresh-20261026/remaining-work.md').replace('two-date-memory-integration-20261026/result.md','guarded-memory-integration-20261026/result.md')
r=r.replace('- [Two-date cash and contractual memory]','- [Common accounting and checkpoint evidence](../data/accounting-master/guarded-memory-runtime-20261026/result.md).\n- [Two-date cash and contractual memory]');new['docs/README.md']=r
for path,b in before.items():assert (R/path).read_bytes()==b,'concurrent control drift:'+path
for path,f in links.items():assert (R/path).resolve()==S/f,'concurrent manuscript drift'
for path,s in new.items():put(R/path,s)
for path,f in links.items():
 p=R/path;q=p.with_name(p.name+'.guarded-link');assert not q.exists();q.symlink_to(os.path.relpath(T/f,p.parent));os.replace(q,p)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for d,key,old in [(cat,'active_execution_note',oldcat),(np,'active_execution',oldnp)]:
 ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key});ck('active_financing',d[key]['active_work_plan']==old[key]['active_work_plan'])
for path,f in links.items():ck('link:'+path,(R/path).resolve()==T/f)
for name,h in j(G/'predecessor-lock.json').items():ck('old_gap:'+name,sha(R/name)==h)
for name,h in lock['sources'].items():ck('prior_source:'+name,sha(S/name)==h)
for name,h in lock['evidence'].items():ck('evidence:'+name,sha(R/name)==h)
prev=j(R/'data/accounting-master/gap-memory-refresh-20261026/audit-status.json');ck('inherited_rows',a['groups']==prev['groups'] and a['literature']==prev['literature'] and a['successor_deltas'][:35]==prev['successor_deltas'])
for delta in a['successor_deltas'][35:]:ck('delta_hash:'+delta['id'],sha(R/delta['evidence'])==delta['sha256'])
ck('all_open',all(p['status']=='open' for p in cp['packages']))
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
ck('concise_checkpoint',len(text.splitlines())<50)
v['readiness']='independent_reader_pending';put(H/'verification.json',json.dumps(v,indent=2)+'\n')
(H/'advancement.json').write_text(json.dumps({'status':'PASS','candidate':'5.22','checks':checks,'count':len(checks),'preserved_financing_plan':finance,'next_independent_plan':nextunit,'control_backup':str(backup.relative_to(R)),'counts':gv['counts'],'mission_complete':False},indent=2)+'\n')
print(json.dumps({'status':'PASS','candidate':'5.22','checks':len(checks),'main_pages':767,'simulation_pages':200,'body_pages':182,'active_financing_plan':finance,'mission_complete':False}))
