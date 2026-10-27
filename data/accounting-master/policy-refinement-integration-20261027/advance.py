"""One successful integration advancement, retaining independent live work."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy as cp
import importlib.util,json,os
H=Path(__file__).resolve().parent;R=H.parents[2];G=H.parent/'gap-policy-refinement-integration-refresh-20261027'
NEXT='docs/plans/accounting-two-decision-source-views-20261027.md';DONE='docs/plans/accounting-policy-domain-transport-20261027.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+chr(10))
checks=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
assert not G.exists() and not (H/'advancement.json').exists()
assert (H/'author-review.md').exists() and (H/'result.md').exists() and (R/NEXT).exists()
s=importlib.util.spec_from_file_location('new_integration',H/'integrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
lock=j(H/'source-preservation.json');S=R/lock['source'];T=R/lock['target'];v=j(H/'verification.json')
ck('document_checks',v['status']=='PASS' and v['checks']==675)
for p,h in lock['sources'].items():ck('source:'+p,sha(S/p)==h);ck('candidate:'+p,(T/p).read_text()==m.transform(p,(S/p).read_text()))
for p,h in lock['evidence'].items():ck('evidence:'+p,sha(R/p)==h)
for p,h in lock['added'].items():ck('added:'+p,sha(T/p)==h)
for p,h in lock['integration_inputs'].items():ck('input:'+p,sha(H/p)==h)
for d in v['documents']:ck('pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths};cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);oldobjs=[cp(cat),cp(np)];a=cat['active_execution_note']
ck('live_baseline',a['current_candidate']=='5.38;810 pages;not_ready' and a['active_work_plan']==DONE)
for k in ['current_candidate','active_work_plan','current_pdf','current_pdf_sha256','standalone_pdf','standalone_pdf_sha256','full_gap_program','financing_next_plan']:ck('control_agreement:'+k,a[k]==np['active_execution'][k])
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('old_pdf:'+p,sha(R/a[p])==a[k])
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
for p,t in links.items():ck('old_link:'+p,Path(t).parent==S)
OLD=(R/a['full_gap_program']).parent;ck('old_gap',OLD.name=='gap-prospective-integration-refresh-20261027')
oldlock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()}
audit=j(OLD/'audit-status.json');oa=cp(audit);packs=j(OLD/'closure-packages.json');op=cp(packs)
result=str((H/'result.md').relative_to(R));base=str(G.relative_to(R))
audit['predecessor']=str(OLD.relative_to(R));audit['baseline']='Version5.39 integrates exact renaming/refinement;5.38 sources retained.'
audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title='Protected policy-refinement manuscript integration',requirements=['MC01','MC03','MC05','MC11','MC12','MC13','MC17','MC18','MC19','MC20','MC24','MC25','MC26','MC28','MC30','MC32','MC33','MC34','MC35'],evidence=result,sha256=sha(H/'result.md'),current_disposition='675 document checks preserve268 sources and121 evidence files;bounded author review;independent acceptance pending.'))
for folder,title,disposition in [('policy-domain-transport-20261027','Exact global policy-message renaming','22 comparisons,281 assertions,12 controls;full candidate permutation;not expansion.'),('policy-observation-refinement-20261027','Declared observation erasure and lifting','17 comparisons,360 assertions,10 controls;exact lift set and reached behavior comparisons.')]:
 evidence=H.parent/folder/'result.md'
 audit['successor_deltas'].insert(len(audit['successor_deltas'])-1,dict(id='',title=title,requirements=['MC03','MC05','MC11','MC12','MC13','MC18','MC24','MC25','MC26','MC28','MC33','MC34'],evidence=str(evidence.relative_to(R)),sha256=sha(evidence),current_disposition=disposition))
for i in range(len(oa['successor_deltas']),len(audit['successor_deltas'])):audit['successor_deltas'][i]['id']='D'+str(i+1)
for row in packs['packages']:
 ck('open:'+row['id'],row['status']=='open')
 if row['id'] in ['W01','W03','W04','W05','W06','W08','W11','W12','W13','W16','W17']:row['existing_support']+=' Version5.39 integrates exact renaming and declared refinement;independent acceptance pending.'
 if row['id'] in ['W03','W04','W11','W12','W13','W16']:row['next_action']='Execute accounting-two-decision-source-views-20261027.md;preserve fixed-input relation scope and broader horizons.'
 if row['id']=='W17':row['next_action']='Integrate future checked domain changes;continue whole-document,independent reader and domain acceptance.'
for row,old in zip(packs['packages'],op['packages']):ck('package_preserved:'+row['id'],all(row[k]==x for k,x in old.items() if k not in ['existing_support','next_action']))
ck('audit_preserved',audit['groups']==oa['groups'] and audit['literature']==oa['literature'] and audit['successor_deltas'][:-3]==oa['successor_deltas'])
counts=dict(j(OLD/'verification.json')['counts']);counts['successor_deltas']=len(audit['successor_deltas'])
ck('counts',counts==dict(obligations=53,interactions=6,operations=46,literature_gaps=9,original_failures=67,literature_extensions=48,cross_interface_challenges=86,successor_deltas=94,closure_packages=18))
updates=dict(updated='2026-10-27',active_work_plan=NEXT,compression_next_plan=NEXT,current_candidate='5.39;812 pages;not_ready',latest_result=result,latest_internal_result=str((H.parent/'policy-observation-refinement-20261027/result.md').relative_to(R)),latest_compression_result=str((H.parent/'policy-observation-refinement-20261027/result.md').relative_to(R)),policy_renaming_result=str((H.parent/'policy-domain-transport-20261027/result.md').relative_to(R)),policy_refinement_result=str((H.parent/'policy-observation-refinement-20261027/result.md').relative_to(R)),current_program='docs/plans/accounting-policy-refinement-integration-20261027.md',full_gap_plan='docs/plans/accounting-policy-refinement-integration-20261027.md',current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=v['documents'][0]['sha256'],standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=v['documents'][1]['sha256'],current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,current_internal_status='Version5.39 integrates renaming/refinement. Joint two-decision source views next;measured conversion-to-control locally evidence-blocked;all packages open.')
for obj in [a,np['active_execution']]:
 obj.update(updates);obj['active_work_plans']=list(dict.fromkeys([NEXT]+[p for p in obj['active_work_plans'] if p!=DONE]));obj['next']=['Execute '+NEXT,'Continue financing evidence '+obj['financing_next_plan'],'Continue all18 broad packages'];obj['gap_program_next']=['Audit joint source views across two decisions','Continue financing evidence','Continue broader language/source/reader acceptance work']
allowed=set(updates)|{'active_work_plans','next','gap_program_next'}
for obj,key,old in [(cat,'active_execution_note',oldobjs[0]),(np,'active_execution',oldobjs[1])]:
 ck('legacy_preserved:'+key,all(obj[k]==x for k,x in old.items() if k!=key));ck('independent_preserved:'+key,all(obj[key][k]==x for k,x in old[key].items() if k not in allowed))
summary=chr(10).join(['Updated 27 October 2026. Governing candidate **5.39**,812 main pages,not_ready.','Simulation246 total/225 body pages. Four stable PDF/TeX links select this candidate.','Main SHA256: '+a['current_pdf_sha256']+'.','Simulation SHA256: '+a['standalone_pdf_sha256']+'.','Result: '+result+'.','','Exact message renaming and declared observation refinement are integrated.','675 document checks preserve268 sources and121 evidence','files. All added pages/covers received bounded author review;independent reader,','domain and whole-document acceptance remain pending.','','Active execution plan: '+NEXT+'.','Financing evidence plan: '+a['financing_next_plan']+'.','Full program: '+base+'/closure-program.md.','Remaining work: '+base+'/remaining-work.md.','','All53 obligations,six interactions,46 operations and18 packages remain open.','S1–S5 partial;S6 held;E3 deferred. Measured conversion-to-control remains locally','evidence-blocked. Continue independent ready work;no global continuation veto.',''])
new={paths[0]:json.dumps(cat,indent=2)+chr(10),paths[1]:json.dumps(np,indent=2)+chr(10),paths[2]:'# Current AccDSL master program\n\n'+summary,paths[3]:'# Current AccDSL master program\n\n'+summary}
for p in paths[4:9]:title,body=before[p].decode().split(chr(10),1);new[p]=title+'\n\n## Prospective policies integrated — 27 October 2026\n\n'+summary+'\n'+body.lstrip(chr(10))
readme=before['docs/README.md'].decode()
for old,newtext in [('Version 5.38, 810 pages','Version 5.39, 812 pages'),('**244 pages**','**246 pages**'),('**223 body pages**','**225 body pages**'),('prospective-policy-integration-20261027/result.md','policy-refinement-integration-20261027/result.md'),(str(OLD.relative_to(R)),base)]:ck('readme:'+old,old in readme);readme=readme.replace(old,newtext)
new['docs/README.md']=readme
for p,raw in before.items():ck('prewrite:'+p,(R/p).read_bytes()==raw)
for p,t in links.items():ck('prewrite_link:'+p,str((R/p).resolve())==t)
snap=H/'control-before';snap.mkdir(exist_ok=False)
for p,raw in before.items():q=snap/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
dump(snap/'stable-links.json',links);G.mkdir(exist_ok=False);dump(G/'predecessor-lock.json',oldlock);dump(G/'audit-status.json',audit);dump(G/'closure-packages.json',packs);(G/'failure-register.json').write_bytes((OLD/'failure-register.json').read_bytes())
lines=['# Full closure program after prospective-policy integration','Version5.39;all18 packages remain open.']
for folder,title,disposition in [('policy-domain-transport-20261027','Exact global policy-message renaming','22 comparisons,281 assertions,12 controls;full candidate permutation;not expansion.'),('policy-observation-refinement-20261027','Declared observation erasure and lifting','17 comparisons,360 assertions,10 controls;exact lift set and reached behavior comparisons.')]:
 evidence=H.parent/folder/'result.md'
 audit['successor_deltas'].insert(len(audit['successor_deltas'])-1,dict(id='',title=title,requirements=['MC03','MC05','MC11','MC12','MC13','MC18','MC24','MC25','MC26','MC28','MC33','MC34'],evidence=str(evidence.relative_to(R)),sha256=sha(evidence),current_disposition=disposition))
for i,item in enumerate(audit['successor_deltas']):item['id']='D'+str(i+1)
for row in packs['packages']:
 lines+=['','## '+row['id']+' — '+row['title']]
 for k in ['requirements','depends_on','failure','existing_support','closure_evidence','next_action','limits','status']:
  value=row[k];lines+=['',k+': '+(', '.join(value) or 'none' if isinstance(value,list) else value)]
(G/'closure-program.md').write_text('\n'.join(lines)+'\n');(G/'remaining-work.md').write_text('# Remaining work\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in packs['packages'])+'\n\nS1–S5 partial;S6 held;E3 deferred.\n')
(G/'plan-review.md').write_text('Exact5.38 comparator and additive source transformation checked;bounded author review supports provisional5.39 only. Two previously uncredited methods plus one integration;finance plan andall18 packages preserved.\n')
(G/'result.md').write_text('Two method deltas andone integration delta. Independent acceptance and measured acquisition remain open;no requirement closure.\n');dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
for p,raw in before.items():ck('commit_control:'+p,(R/p).read_bytes()==raw)
for p,txt in new.items():q=(R/p).with_name(Path(p).name+'.v539.tmp');assert not q.exists();q.write_text(txt);os.replace(q,R/p)
for p in links:
 name='simulation-foundations' if 'simulation' in p else 'accounting-product-proposal';target=T/(name+('.pdf' if p.endswith('.pdf') else '.tex'));q=(R/p).with_name(Path(p).name+'.v539-link');assert not q.exists();q.symlink_to(os.path.relpath(target,(R/p).parent));os.replace(q,R/p);links[p]=str(target)
for p,txt in new.items():ck('readback:'+p,(R/p).read_text()==txt)
for p,t in links.items():ck('advanced_link:'+p,str((R/p).resolve())==t)
for p,h in oldlock.items():ck('gap_preserved:'+p,sha(R/p)==h)
for p,h in lock['sources'].items():ck('source_preserved:'+p,sha(S/p)==h)
for p,h in lock['evidence'].items():ck('evidence_preserved:'+p,sha(R/p)==h)
for d in v['documents']:ck('final_pdf:'+d['document'],sha(T/(d['document']+'.pdf'))==d['sha256'])
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,next=NEXT,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=NEXT)))

