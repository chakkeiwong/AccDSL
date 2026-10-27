"""Compare current predecessors, preserve controls, update live annotations only."""
from pathlib import Path
import copy,hashlib,json,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=R/'docs/design/proposal/manuscript-decision-conversion-v519-20261026'
T=R/'docs/design/proposal/manuscript-continuous-guards-v520-20261026'
G=R/'data/accounting-master/gap-continuous-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def put(p,s):
 t=p.with_name(p.name+'.continuous-refresh.tmp');t.write_text(s);os.replace(t,p)
V=j(H/'verification.json');assert V['status']=='PASS';assert (H/'review.md').exists()
LOCK=j(H/'source-preservation.json')
for n,h in LOCK['sources'].items():assert sha(S/n)==h
for n,h in LOCK['evidence'].items():assert sha(R/n)==h
for d in V['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for n,f in links.items():assert (R/n).resolve()==S/f,'concurrent manuscript drift'
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={n:(R/n).read_bytes() for n in paths}
backup=H/'control-before';backup.mkdir(exist_ok=False)
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
c=json.loads(before[paths[0]]);n=json.loads(before[paths[1]]);oldc=copy.deepcopy(c);oldn=copy.deepcopy(n)
assert c['active_execution_note']['current_candidate'].startswith('5.19;')
finance_plan=c['active_execution_note']['active_work_plan'];assert (R/finance_plan).exists()
assert finance_plan!='docs/plans/accounting-continuous-integration-20261026.md'
# Append the checked documentary integration without rewriting previous deltas.
a=j(G/'audit-status.json');assert len(a['successor_deltas'])==32
new={'id':'D33','title':'Continuous guard explanation integrated in both editions','requirements':['MC11','MC26','MC28','MC33','MC34','W04','W17'],'evidence':str((H/'result.md').relative_to(R)),'sha256':sha(H/'result.md'),'current_disposition':'Version5.20,763 main pages,196 total/178 body simulation pages;245 sources and29 evidence files preserved,532 checks, bounded author review; broader requirements remain open.'}
a['successor_deltas'].append(new);a['baseline']='Version5.20 protected successor plus funding/measurement companions; current financing-authority work preserved. Trace reconciliation, not independent whole-design acceptance.'
put(G/'audit-status.json',json.dumps(a,indent=2)+'\n')
v=j(G/'verification.json');v['counts']['successor_deltas']=33;put(G/'verification.json',json.dumps(v,indent=2)+'\n')
put(G/'result.md',(G/'result.md').read_text().replace('Five new evidence deltas','Six new evidence deltas').replace('to32 deltas','to33 deltas')+'\nThe sixth delta records the checked5.20 dual-edition integration, not a new scientific comparison.\n')
cp=j(G/'closure-packages.json')
for row in cp['packages']:
 if row['id']=='W17':row['existing_support']=row['existing_support'].replace('checked continuous-guard addition is being integrated in a protected successor','checked continuous-guard addition is integrated in Version5.20')
put(G/'closure-packages.json',json.dumps(cp,indent=2)+'\n')
p=G/'closure-program.md';put(p,p.read_text().replace('checked continuous-guard addition is being integrated in a protected successor','checked continuous-guard addition is integrated in Version5.20'))
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));compress='data/accounting-master/continuous-guards-20261026/result.md';nextcompress='docs/plans/accounting-two-date-continuous-memory-20261026.md'
common={'updated':'2026-10-26','current_candidate':'5.20;763 pages;not_ready','latest_result':result,'current_pdf':str((T/'accounting-product-proposal.pdf').relative_to(R)),'current_pdf_sha256':sha(T/'accounting-product-proposal.pdf'),'standalone_pdf':str((T/'simulation-foundations.pdf').relative_to(R)),'standalone_pdf_sha256':sha(T/'simulation-foundations.pdf'),'current_audit':base+'/audit-status.json','current_program':'docs/plans/accounting-continuous-integration-20261026.md','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-continuous-integration-20261026.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':v['counts'],'latest_compression_result':compress,'compression_next_plan':nextcompress,'current_internal_status':'Continuous guard reference integrated in5.20; dated funding and accounting measurement audit are separate checked companions; active contingent-financing authority work preserved','gap_program_next':['Continue active contingent-conversion authority and intervening measurement','Extend exact continuous reference to two dates with persistent hidden terms','Integrate checked funding/source findings and continue every open package']}
for target in [c['active_execution_note'],n['active_execution']]:
 target.update(common)
 target['active_work_plans']=list(dict.fromkeys([finance_plan,nextcompress,'docs/plans/accounting-continuous-integration-20261026.md']))
 target['latest_internal_results']=list(dict.fromkeys(target.get('latest_internal_results',[])+['data/accounting-master/conversion-rights-bridge-20261026/result.md','data/accounting-master/dated-funding-bundle-20261026/result.md','data/accounting-master/conversion-measurement-audit-20261026/result.md',compress]))
 target['next']=['Continue '+finance_plan,'Execute '+nextcompress,'Integrate funding and authority findings, then follow the full18-package queue']
assert {k:v for k,v in c.items() if k!='active_execution_note'}=={k:v for k,v in oldc.items() if k!='active_execution_note'}
assert {k:v for k,v in n.items() if k!='active_execution'}=={k:v for k,v in oldn.items() if k!='active_execution'}
text=f'''# Current AccDSL master program

Updated26 October2026. Governing candidate **5.20**,763 pages, not_ready.
Simulation volume:196 total /178 body pages,26 chapters. Both PDF/TeX pairs
select docs/design/proposal/manuscript-continuous-guards-v520-20261026/.
Integration: {result}.
Main SHA256:{common['current_pdf_sha256']}.
Standalone SHA256:{common['standalone_pdf_sha256']}.

Current question: preserve contractual memory and available information while
joining financing/measurement and extending continuous simulation across dates.
The checked one-date reference covers264 complete symbolic comparisons and24
controls; it retains32 regions with14 shared calculations. No scaling claim.
Dated funding passes four full-party cases/20 controls; its timing and source
premises remain explicit. The measurement audit refuses automatic reuse of the
older maturity-only admission;15 checks are in saved JSON (prose says17).

Active financing lane: {finance_plan}.
Independent next unit: {nextcompress}.
Full dependency-ordered program: {base}/closure-program.md.
All remaining work: {base}/remaining-work.md.
Gap verification: {base}/verification.json.

All53 obligations,6 interactions,46 operations,9 literature gaps and18 broad
packages remain open;33 successor deltas and24 interface challenges retain
provenance. S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and
whole-document acceptance remain pending. These statuses do not block ready
internal work. No paid outreach, deployment or background campaign authorized.

Do not rerun successful evidence writers. Preserve both failed attempts and
accepted results. All preceding controls are saved under
{str(backup.relative_to(R))}/; detailed history stays in linked result files.
'''
newcontent={paths[0]:json.dumps(c,indent=2)+'\n',paths[1]:json.dumps(n,indent=2)+'\n',paths[2]:text,paths[3]:text}
summary=f'''## Current routes — 26 October2026, Version5.20

The current recovery checkpoint is docs/plans/accounting-master-current.md.
Version5.20 has763 main pages; the shared simulation edition has196 total/178
body pages and26 chapters, not_ready. Exact continuous guards and information-
constrained policies are integrated with245 predecessor sources preserved.
Result: {result}.
Full program and remaining work: {base}/closure-program.md and remaining-work.md.
Active financing plan: {finance_plan}.
Independent continuation: {nextcompress}.
All53 obligations,6 interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Historical dated entries below do not
override the current recovery checkpoint. Prior controls are preserved in
{str(backup.relative_to(R))}/.

'''
for path in paths[4:9]:
 old=before[path].decode();title,body=old.split('\n',1);newcontent[path]=title+'\n\n'+summary+body.lstrip('\n')
readme=before['docs/README.md'].decode().replace('Version 5.18, 757 pages','Version 5.20, 763 pages').replace('**190 pages**','**196 pages**').replace('**172 body pages**','**178 body pages**').replace('vintage-carry-integration-20261026/result.md','continuous-guards-integration-20261026/result.md')
readme=readme.replace('- [Current integration and checks]', '- [Current master program](plans/accounting-master-current.md).\n- [Full remaining-work queue](../data/accounting-master/gap-continuous-refresh-20261026/remaining-work.md).\n- [Exact continuous guard comparison](../data/accounting-master/continuous-guards-20261026/result.md).\n- [Current integration and checks]')
newcontent['docs/README.md']=readme
# All preparations precede the final compare and replacement.
for path,b in before.items():assert (R/path).read_bytes()==b,'concurrent control drift:'+path
for path,f in links.items():assert (R/path).resolve()==S/f,'concurrent manuscript drift'
for path,content in newcontent.items():put(R/path,content)
for path,f in links.items():
 p=R/path;tmp=p.with_name(p.name+'.continuous-link');assert not tmp.exists();tmp.symlink_to(os.path.relpath(T/f,p.parent));os.replace(tmp,p)
for path,f in links.items():assert (R/path).resolve()==T/f
assert j(R/paths[0])['active_execution_note']['active_work_plan']==finance_plan
assert j(R/paths[1])['active_execution']['active_work_plan']==oldn['active_execution']['active_work_plan']
assert all(sha(R/name)==h for name,h in j(G/'predecessor-lock.json').items())
assert all(sha(R/name)==h for name,h in LOCK['evidence'].items())
(H/'advancement.json').write_text(json.dumps({'status':'PASS','candidate':'5.20','links':{k:str((R/k).readlink()) for k in links},'preserved_financing_plan':finance_plan,'legacy_fields_unchanged':True,'control_backups':str(backup.relative_to(R)),'counts':v['counts'],'source_hashes':{d['document']:d['sha256'] for d in V['documents']}},indent=2)+'\n')
print(json.dumps({'status':'PASS','candidate':'5.20','main_pages':763,'standalone_pages':196,'standalone_body_pages':178,'active_financing_plan':finance_plan,'independent_next':nextcompress,'control_files':len(paths)}))
