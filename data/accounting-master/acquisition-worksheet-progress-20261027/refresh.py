"""Credit two verified worksheet companions while retaining live manuscript."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2]
G=H.parent/'gap-acquisition-worksheet-refresh-20261027'
PLAN='docs/plans/accounting-acquisition-revisions-20261027.md'
RESULTS=['data/accounting-master/acquisition-worksheet-20261027/result.md','data/accounting-master/acquisition-consideration-20261027/result.md']
def j(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert not (H/'advancement.json').exists()
for result in RESULTS:
    d=(R/result).parent;assert j(d/'attempt-01/verification.json')['status']=='PASS'
    for p,h in j(d/'attempt-01/source-lock.json').items():assert sha(R/p)==h
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md']
before={p:(R/p).read_bytes() for p in paths};cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
a=cat['active_execution_note'];old=deepcopy(a)
assert a['current_candidate']=='5.29;790 pages;not_ready'
assert a['active_work_plan']=='docs/plans/accounting-acquisition-worksheet-20261027.md'
assert np['active_execution']['current_candidate']==a['current_candidate']
independent=a['compression_next_plan'];OLD=(R/a['full_gap_program']).parent
assert OLD.name=='gap-acquisition-design-refresh-20261027'
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:assert sha(R/a[p])==a[k]
snapshot=H/'control-before';snapshot.mkdir(exist_ok=False)
for p,b in before.items():q=snapshot/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
G.mkdir(exist_ok=False);lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save(G/'predecessor-lock.json',lock)
audit=j(OLD/'audit-status.json');orig=deepcopy(audit);audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version5.29 retained; new conditional acquisition worksheet/consideration companions await integration.'
for p,title,scope in zip(RESULTS,['Item-level synthetic acquisition worksheet','Cash/new-parent-equity acquisition consideration'],['4 full comparisons,26 refusals,238 assertions; original legal books, all adjustments and selected reports match independent expectations.','13 full comparisons,13 refusals,287 assertions; cash/noncash components and parent equity remain distinct; actual debt conversion remains unresolved.']):
    audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title=title,requirements=['MC05','MC17','MC19','MC20','MC24','MC25','MC28','MC33','MC34','MC35','W05','W06','W08','W11','W12','W16'],evidence=p,sha256=sha(R/p),current_disposition=scope))
save(G/'audit-status.json',audit);fail=j(OLD/'failure-register.json');of=deepcopy(fail)
for title,case,p in [('Pre-control subsidiary profit leaks into group-period income','Retain pre-control equity separately and compare complete post-control accounts and reports.',RESULTS[0]),('Noncash equity consideration creates fictitious cash or drops acquired cash','Compare cash120/equity0,cash0/equity120 andcash50/equity70 with complete group cash/equity bridges.',RESULTS[1])]:
    fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=title,closure_packages=['W05','W06','W08','W12','W16'],discriminating_case=case,status='Selected synthetic profile passes; actual/general accounting remains open',evidence=p))
save(G/'failure-register.json',fail);packages=j(OLD/'closure-packages.json');op=deepcopy(packages)
for row in packages['packages']:
    if row['id'] in ['W05','W06','W08','W11','W12','W16']:row['existing_support']+=' Cash-only and cash/new-parent-equity synthetic acquisition worksheets pass complete account/journal/report comparisons; actual admission remains false.'
    if row['id'] in ['W05','W06','W08']:row['next_action']='Execute accounting-acquisition-revisions-20261027.md; then extend prior-interest/debt conversion,loss/ownership,eliminations and general item methods with independent full reports.'
    if row['id']=='W17':row['next_action']='Integrate verified worksheet/consideration companions and subsequent revisions; preserve live independent observation-map results and continue whole-document/reader/domain acceptance.'
    assert row['status']=='open'
save(G/'closure-packages.json',packages)
text='# Full closure program after acquisition worksheet comparisons\n\n27 October2026. Version5.29 remains governing. All18 packages remain open.\n'
for row in packages['packages']:
    text+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
        v=row[key];text+=label+': '+(', '.join(v) or 'none' if isinstance(v,list) else v)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Remaining work\n\nDated measurement revisions are next. Actual debt conversion/prior interests,loss/ownership,full tax/elimination/FX,source admission and reader acceptance remain open.\n\n'+'\n'.join('- **'+x['id']+' '+x['title']+':** '+x['next_action'] for x in packages['packages'])+'\n\nAll53 obligations,six interactions,46 operations and18 packages remain. S1–S5 partial;S6 held;E3 deferred.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: full synthetic account/journal/report comparisons do not establish actual measurements or general tax/acquisition support. Newly issued parent equity is distinct from creditor debt conversion. Revision views must rebind embedded actor/cutoff,retain original evidence and require conditional acquisition-date information. Independent observation-map work continues.\n')
assert audit['groups']==orig['groups'] and audit['literature']==orig['literature'] and audit['successor_deltas'][:-2]==orig['successor_deltas']
assert fail['cross_interface'][:-2]==of['cross_interface'] and all(fail[k]==of[k] for k in ['original','literature_extensions'])
for row,prior in zip(packages['packages'],op['packages']):assert all(row[k]==v for k,v in prior.items() if k not in ['existing_support','next_action'])
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
save(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
(G/'result.md').write_text('# Acquisition worksheet progress\n\nTwo scoped deltas and two interface challenges are added. All originals and18 open packages remain. Version5.29 and independent observation-map work are preserved; new companions await manuscript integration.\n')
base=str(G.relative_to(R));updates=dict(updated='2026-10-27',active_work_plan=PLAN,financing_next_plan=PLAN,current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,latest_internal_result=RESULTS[-1],latest_financing_result=RESULTS[-1],acquisition_worksheet_result=RESULTS[0],acquisition_consideration_result=RESULTS[1],current_internal_status='Version5.29 unchanged. Synthetic acquisition worksheets and cash/noncash consideration pass full comparisons; dated revisions next. Actual debt conversion/admission remain unresolved.')
originals=[deepcopy(cat),deepcopy(np)]
for d in [a,np['active_execution']]:
    d.update(updates);d['active_work_plans']=list(dict.fromkeys([PLAN]+[p for p in d.get('active_work_plans',[]) if p!=old['active_work_plan']]))
    d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+RESULTS))
    d['next']=['Execute '+PLAN,'Continue '+independent,'Continue all18 closure packages']
    d['gap_program_next']=['Bind dated acquisition revisions to complete actor views','Extend missing prior-interest/control/measurement methods','Continue independent observation-map,recovery and acceptance work']
notice=f'''## Acquisition worksheets checked — 27 October2026

Version5.29 remains governing:790 main pages;223 total/204 body simulation pages.
Cash-only worksheet:4 full cases,26 controls,238 assertions.
Cash/new-parent-equity extension:13 full cases,13 controls,287 assertions.
Results:{RESULTS[0]};{RESULTS[1]}. Companions await integration.
Active financing plan:{PLAN}.
Independent plan:{independent}.
Full program:{base}/closure-program.md.
All53 obligations,six interactions,46 operations and18 packages remain open.
S1–S5 partial;S6 held;E3 deferred. No actual accounting admission follows.

'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n'}
for p in paths[2:]:
    title,body=before[p].decode().split('\n',1)
    if p in paths[2:4]:
        body=body.replace(old['active_work_plan'],PLAN).replace(str(OLD.relative_to(R)),base)
    new[p]=title+'\n\n'+notice+body.lstrip('\n')
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,h in lock.items():assert sha(R/p)==h
for p,s in new.items():
    dest=R/p;tmp=dest.with_name(dest.name+'.worksheet-progress.tmp');assert not tmp.exists();tmp.write_text(s);os.replace(tmp,dest)
checks=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,target in links.items():ck('links:'+p,str((R/p).resolve())==target)
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('pdf:'+p,sha(R/a[p])==old[k])
for p,h in lock.items():ck('protected:'+p,sha(R/p)==h)
allowed=set(updates)|{'active_work_plans','latest_internal_results','next','gap_program_next'}
for d,key,o in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
    ck('legacy_fields',all(d[k]==v for k,v in o.items() if k!=key));ck('independent_fields',all(d[key][k]==v for k,v in o[key].items() if k not in allowed))
save(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,next=PLAN,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=PLAN)))
