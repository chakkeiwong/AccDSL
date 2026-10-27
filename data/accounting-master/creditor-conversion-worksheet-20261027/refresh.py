"""Credit verified complete creditor conversion evidence without changing the live manuscript."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2];G=H.parent/'gap-creditor-worksheet-refresh-20261027'
NEXT='docs/plans/accounting-debt-exchange-integration-20261027.md';OLDPLAN='docs/plans/accounting-creditor-conversion-worksheet-20261027.md'
def j(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
assert not (H/'advancement.json').exists() and not G.exists()
v=j(H/'attempt-01/verification.json');assert v['status']=='PASS'
protected=j(H/'attempt-01/source-lock.json')
for p,d in protected.items():assert sha(R/p)==d
assert (H/'result.md').exists() and (R/NEXT).exists()
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths};cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
a=cat['active_execution_note'];prior=deepcopy(a);originals=[deepcopy(cat),deepcopy(np)]
assert a['current_candidate']=='5.36;804 pages;not_ready' and a['active_work_plan']==OLDPLAN
assert np['active_execution']['current_candidate']==a['current_candidate']
OLD=(R/a['full_gap_program']).parent;assert OLD.name=='gap-debtor-worksheet-refresh-20261027'
oldlock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()}
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:assert sha(R/a[p])==a[k]
audit=j(OLD/'audit-status.json');oa=deepcopy(audit);audit['predecessor']=str(OLD.relative_to(R));audit['baseline']='Version 5.36 and concurrent observation-frontier work retained; debt-relationship companion awaits integration.'
result=str((H/'result.md').relative_to(R))
audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title='Complete conditional creditor conversion worksheet',requirements=['MC17','MC19','MC20','MC24','MC25','MC28','MC30','MC33','MC34','MC35','W05','W06','W08','W12','W16'],evidence=result,sha256=sha(H/'result.md'),current_disposition='33 cases,20 controls,337 assertions; full creditor impairment/disposal accounts and matched debtor comparisons; all admission remains false.'))
fail=j(OLD/'failure-register.json');of=deepcopy(fail)
for title,case in [('Separate debtor and noncontrolling creditor worksheets are mistaken for a control-changing acquisition method','Inspect acquisition consideration and pre-existing loan settlement when conversion confers control; compare separate transaction allocation before any consolidated numerical result.')]:
    fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=title,closure_packages=['W05','W06','W08','W12','W16'],discriminating_case=case,status='Complete finite creditor accounts checked; control-changing acquisition relationship accounting remains open',evidence=result))
packages=j(OLD/'closure-packages.json');op=deepcopy(packages)
for row in packages['packages']:
    if row['id'] in ['W05','W06','W08','W12','W16']:row['existing_support']+=' Complete creditor worksheet passes33 cases and337 assertions; impairment/disposal decomposition,full reports and matched debtor examples checked.'
    if row['id'] in ['W05','W06','W08']:row['next_action']='Integrate checked debt-scope,debtor and creditor companions under accounting-debt-exchange-integration-20261027.md; then control-changing acquisition relationships.'
    if row['id']=='W17':row['next_action']='Integrate checked debt-conversion and prospective-policy companions; preserve independent work and continue whole-document/reader/domain acceptance.'
    assert row['status']=='open'
assert audit['groups']==oa['groups'] and audit['literature']==oa['literature'] and audit['successor_deltas'][:-1]==oa['successor_deltas']
assert fail['cross_interface'][:-1]==of['cross_interface'] and all(fail[k]==of[k] for k in ['original','literature_extensions'])
for row,old in zip(packages['packages'],op['packages']):assert all(row[k]==x for k,x in old.items() if k not in ['existing_support','next_action'])
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
base=str(G.relative_to(R));updates=dict(updated='2026-10-27',active_work_plan=NEXT,financing_next_plan=NEXT,latest_internal_result=result,latest_financing_result=result,creditor_conversion_worksheet_result=result,current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,current_internal_status='Version 5.36 retained. Complete conditional creditor worksheet checked; protected debt-exchange integration next. Actual tax/source/accounting admission remains open.')
for d in [a,np['active_execution']]:
    d.update(updates);d['active_work_plans']=list(dict.fromkeys([NEXT]+[p for p in d['active_work_plans'] if p!=OLDPLAN]))
    d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[result]))
    d['next']=['Execute '+NEXT,'Continue '+a['compression_next_plan'],'Continue all 18 closure packages']
    d['gap_program_next']=['Integrate checked scope and complete debtor/creditor worksheets','Integrate verified financial and independent prospective-policy companions','Continue remaining broad method/source/acceptance work']
allowed=set(updates)|{'active_work_plans','latest_internal_results','next','gap_program_next'}
for d,key,o in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
    assert all(d[k]==x for k,x in o.items() if k!=key)
    assert all(d[key][k]==x for k,x in o[key].items() if k not in allowed)
notice=f'''## Complete creditor conversion worksheet checked — 27 October 2026

Version 5.36 remains governing: 804 main pages; 239 total / 218 body simulation pages.
ConditionalCreditorConversionWorksheet/1 passes33 cases,20 controls,337 assertions.
Complete conditional creditor journals and reports are checked. Actual
source/accounting admission remains open. Companion awaits manuscript integration.
Result: {result}.
Active financing plan: {NEXT}.
Independent plan: {a['compression_next_plan']}.
Full program: {base}/closure-program.md.
All53 obligations,six interactions,46 operations and18 packages remain open.
S1–S5 partial;S6 held;E3 deferred. Continue feasible internal work.

'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n'}
for p in paths[2:9]:
    title,body=before[p].decode().split('\n',1)
    if p in paths[2:4]:body=body.replace(OLDPLAN,NEXT).replace(str(OLD.relative_to(R)),base)
    new[p]=title+'\n\n'+notice+body.lstrip('\n')
new['docs/README.md']=before['docs/README.md'].decode().replace(str(OLD.relative_to(R)),base)
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
snapshot=H/'control-before';snapshot.mkdir(exist_ok=False)
for p,b in before.items():q=snapshot/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
G.mkdir(exist_ok=False);dump(G/'predecessor-lock.json',oldlock);dump(G/'audit-status.json',audit);dump(G/'failure-register.json',fail);dump(G/'closure-packages.json',packages)
text='# Full closure program after complete creditor conversion worksheet\n\nAll 18 packages remain open; version 5.36 retained.\n'
for row in packages['packages']:
    text+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for key in ['requirements','depends_on','failure','existing_support','closure_evidence','next_action','limits','status']:
        val=row[key];text+=key+': '+(', '.join(val) or 'none' if isinstance(val,list) else val)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Remaining work\n\n'+ '\n'.join('- **'+x['id']+' '+x['title']+':** '+x['next_action'] for x in packages['packages'])+'\n\nS1–S5 partial;S6 held;E3 deferred.\n')
(G/'plan-review.md').write_text('Skeptical audit: complete conditional separate-party accounts do not establish conversion-to-control acquisition methods. Integrate checked examples with exact source and assumption boundaries,then inspect consideration and pre-existing loan settlement. No global continuation veto; independent work preserved.\n')
(G/'result.md').write_text('One complete creditor worksheet delta and one control-changing acquisition interface challenge added. All original rows and18 open packages preserved; version5.36 and four stable links unchanged. Concurrent observation-frontier work is retained.\n')
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
for p,b in before.items():assert (R/p).read_bytes()==b,'prewrite_drift:'+p
for p,s in new.items():
    q=(R/p).with_name(Path(p).name+'.intragroup.tmp');assert not q.exists();q.write_text(s);os.replace(q,R/p)
checks=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,t in links.items():ck('link:'+p,str((R/p).resolve())==t)
for p,d in {**oldlock,**protected}.items():ck('protected:'+p,sha(R/p)==d)
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('pdf:'+p,sha(R/a[p])==prior[k])
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,next=NEXT,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=NEXT)))
