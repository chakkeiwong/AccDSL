"""Add policy evidence without replacing independent finance/manuscript fields."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2];D=H.parent/'prospective-policy-domain-20261027'
G=H.parent/'gap-prospective-partial-refresh-20261027'
NEXT='docs/plans/accounting-prospective-policy-integration-20261027.md'
DONE='docs/plans/accounting-prospective-policy-domain-20261027.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+chr(10))
assert not G.exists() and not (H/'advancement.json').exists()
protected={}
for folder,attempt in [(D,'attempt-03'),(H,'attempt-01')]:
 assert j(folder/attempt/'verification.json')['status']=='PASS'
 for n,h in j(folder/attempt/'source-lock.json').items():assert sha(R/n)==h;protected[n]=h
 assert (folder/'result.md').exists()
 for q in (folder/attempt).glob('*.json'):protected[str(q.relative_to(R))]=sha(q)
 protected[str((folder/'result.md').relative_to(R))]=sha(folder/'result.md')
assert (R/NEXT).exists()
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths};cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);originals=[cp(cat),cp(np)]
a=cat['active_execution_note'];assert a['active_work_plan']==DONE and a['current_candidate']=='5.37;806 pages;not_ready'
assert np['active_execution']['active_work_plan']==DONE
OLD=(R/a['full_gap_program']).parent;assert OLD.name=='gap-conversion-partition-refresh-20261027'
oldlock={str(q.relative_to(R)):sha(q) for q in OLD.iterdir() if q.is_file()}
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:assert sha(R/a[p])==a[k]
audit=j(OLD/'audit-status.json');oa=cp(audit);fail=j(OLD/'failure-register.json');of=cp(fail);packs=j(OLD/'closure-packages.json');op=cp(packs)
result=str((H/'result.md').relative_to(R));domain_result=str((D/'result.md').relative_to(R))
audit['predecessor']=str(OLD.relative_to(R));audit['baseline']='Version5.37 retained;prospective domains and partial policies checked;integration pending.'
for title,evidence,description in [('Prospective original-registry policy domain',domain_result,'10 cases,145 assertions,13 controls;exact coverage/projection;overflow retained.'),('Prospective partial-frontier policy restrictions',result,'12 cases,110 checkpoints,619 assertions,31 controls;exact monotone constraints and unknown/pending preservation.')]:
 audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title=title,requirements=['MC01','MC03','MC05','MC11','MC12','MC13','MC18','MC24','MC25','MC26','MC28','MC33','MC34'],evidence=evidence,sha256=sha(R/evidence),current_disposition=description))
for title,case in [('Hindsight-derived policy domain is presented as prospective','Declare source-head maps before search;test new labels,collisions and overflow.'),('Surviving partial rules or completed temporal search are mistaken for resolved-source feasibility','Preserve pending,unknown,retracted/conflicting and inconsistent cases;reject changed-domain reuse.')]:
 fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=title,closure_packages=['W03','W04','W11','W12','W13','W16'],discriminating_case=case,status='Bounded comparisons pass;general domain changes/horizons open',evidence=result))
for row in packs['packages']:
 if row['id'] in ['W01','W03','W04','W11','W12','W13','W16']:
  row['existing_support']+=' Prospective domains and partial policies pass10 domain cases and110 checkpoints;no complete-family candidate input.'
  row['next_action']='Integrate prospective policies,then specify safe domain changes and broader message/horizon semantics with independent comparisons.'
 if row['id']=='W17':row['next_action']='Execute accounting-prospective-policy-integration-20261027.md;continue whole-document/reader/domain acceptance.'
 assert row['status']=='open'
assert audit['groups']==oa['groups'] and audit['literature']==oa['literature'] and audit['successor_deltas'][:-2]==oa['successor_deltas']
assert fail['cross_interface'][:-2]==of['cross_interface'] and all(fail[k]==of[k] for k in ['original','literature_extensions'])
for row,old in zip(packs['packages'],op['packages']):assert all(row[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
base=str(G.relative_to(R));updates=dict(updated='2026-10-27',active_work_plan=NEXT,compression_next_plan=NEXT,latest_internal_result=result,latest_compression_result=result,prospective_domain_result=domain_result,prospective_partial_policy_result=result,current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,current_internal_status='Version5.37 retained;prospective domain/partial-policy comparisons checked;integrate companions. Measured conversion-to-control remains locally evidence-blocked.')
for v in [a,np['active_execution']]:
 v.update(updates);v['active_work_plans']=list(dict.fromkeys([NEXT]+[p for p in v['active_work_plans'] if p!=DONE]))
 v['latest_internal_results']=list(dict.fromkeys(v.get('latest_internal_results',[])+[domain_result,result]))
 v['next']=['Execute '+NEXT,'Continue financing evidence '+v['financing_next_plan'],'Continue all18 open packages']
 v['gap_program_next']=['Integrate checked prospective-policy and supplied-partition evidence','Specify safe domain-extension relations','Continue finance/source and broader language work']
allowed=set(updates)|{'active_work_plans','latest_internal_results','next','gap_program_next'}
for obj,key,old in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
 assert all(obj[k]==v for k,v in old.items() if k!=key)
 assert all(obj[key][k]==v for k,v in old[key].items() if k not in allowed)
notice=chr(10).join(['## Prospective policy restrictions checked — 27 October 2026','','Version5.37 governs:806 main pages;241 total/220 body simulation pages.','Prospective domains:10 cases/145 assertions. Partial policies:12 cases,','110 checkpoints,619 assertions,31 controls. Unknown/pending remain explicit.','Domain result: '+domain_result+'.','Partial result: '+result+'.','Active execution plan: '+NEXT+'.','Financing evidence plan: '+a['financing_next_plan']+'.','Full program: '+base+'/closure-program.md.','All53 obligations,six interactions,46 operations and18 packages remain open.','S1–S5 partial;S6 held;E3 deferred. No global continuation veto.','',''])
new={paths[0]:json.dumps(cat,indent=2)+chr(10),paths[1]:json.dumps(np,indent=2)+chr(10)}
for p in paths[2:9]:
 title,body=before[p].decode().split(chr(10),1)
 if p in paths[2:4]:body='Governing build: data/accounting-master/debt-exchange-integration-20261027/result.md.\nIndependent reader/domain and whole-document acceptance remain pending.\n'
 new[p]=title+'\n\n'+notice+body.lstrip(chr(10))
new['docs/README.md']=before['docs/README.md'].decode().replace(str(OLD.relative_to(R)),base)
for p,raw in before.items():assert (R/p).read_bytes()==raw,'concurrent_control_drift:'+p
snap=H/'control-before';snap.mkdir(exist_ok=False)
for p,raw in before.items():q=snap/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
G.mkdir(exist_ok=False);dump(G/'predecessor-lock.json',oldlock);dump(G/'audit-status.json',audit);dump(G/'failure-register.json',fail);dump(G/'closure-packages.json',packs)
lines=['# Full closure program after prospective partial-policy comparison','All18 packages remain open;version5.37 retained.']
for row in packs['packages']:
 lines+=['','## '+row['id']+' — '+row['title']]
 for k in ['requirements','depends_on','failure','existing_support','closure_evidence','next_action','limits','status']:
  v=row[k];lines+=['',k+': '+(', '.join(v) or 'none' if isinstance(v,list) else v)]
(G/'closure-program.md').write_text('\n'.join(lines)+'\n')
(G/'remaining-work.md').write_text('# Remaining work\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in packs['packages'])+'\n\nS1–S5 partial;S6 held;E3 deferred.\n')
(G/'plan-review.md').write_text('Exact prospective/partial-policy evidence does not close general domains,horizons or whole-language requirements. Preserve local acquisition evidence blocker and continue integration. Counts are not promotion proxies.\n')
(G/'result.md').write_text('Two checked policy deltas and two challenges added. Original rows,18 open packages,finance plan,version5.37 and stable manuscript links preserved.\n')
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
for p,raw in before.items():assert (R/p).read_bytes()==raw,'prewrite_control_drift:'+p
for p,txt in new.items():
 q=(R/p).with_name(Path(p).name+'.prospective.tmp');assert not q.exists();q.write_text(txt);os.replace(q,R/p)
checks=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
for p,txt in new.items():ck('readback:'+p,(R/p).read_text()==txt)
for p,h in {**oldlock,**protected}.items():ck('protected:'+p,sha(R/p)==h)
for p,target in links.items():ck('stable_link:'+p,str((R/p).resolve())==target)
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('pdf:'+p,sha(R/a[p])==a[k])
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,counts=counts,next=NEXT,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=NEXT)))

