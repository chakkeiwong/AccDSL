"""Add checked partial-policy companion to the live full program without replacing PDFs."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,os,re
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;G=H.parent/'gap-partial-frontier-policy-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def save(n,x):(G/n).write_text(json.dumps(x,indent=2)+'\n')
def put(p,s):tmp=p.with_name(p.name+'.partial-frontier.tmp');assert not tmp.exists();tmp.write_text(s);os.replace(tmp,p)
assert j(H/'attempt-01/verification.json')['status']==j(H/'audit-01/verification.json')['status']=='PASS'
for n,h in j(H/'attempt-01/source-lock.json').items():assert sha(R/n)==h
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={n:(R/n).read_bytes() for n in paths};cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]]);oldcat=cp(cat);oldnp=cp(np);live=cat['active_execution_note'];OLD=(R/live['full_gap_program']).parent
assert np['active_execution']['full_gap_program']==live['full_gap_program'];finance=live['active_work_plan'];assert np['active_execution']['active_work_plan']==finance
links={n:{'target':os.readlink(R/n),'sha256':sha(R/n)} for n in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
G.mkdir(exist_ok=False);lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save('predecessor-lock.json',lock)
backup=H/'control-before';backup.mkdir(exist_ok=False)
for n,v in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
a=j(OLD/'audit-status.json');olda=cp(a);a['predecessor']=str(OLD.relative_to(R));a['baseline']=live['current_candidate']+' retained; fixed-domain partial-policy companion checked without claiming prospective domain discovery.'
last=max(int(x['id'][1:]) for x in a['successor_deltas']);result=str((H/'result.md').relative_to(R))
a['successor_deltas'].append({'id':'D'+str(last+1),'title':'Partial temporal policies over an explicitly fixed declared domain','requirements':['MC01','MC03','MC05','MC11','MC12','MC13','MC18','MC24','MC25','MC26','MC28','MC33','MC34','W01','W03','W04','W11','W12','W13','W16'],'evidence':result,'sha256':sha(H/'result.md'),'current_disposition':'Five retrospective cases,98 checkpoints,680 assertions,24 controls;185 saved-audit assertions and seven additional controls. Complete candidate sets and rejection witnesses agree. Actual prospective domain discovery remains open; manuscript integration pending.'});save('audit-status.json',a)
f=j(OLD/'failure-register.json');oldf=cp(f);last=max(int(x['id'][1:]) for x in f['cross_interface'])
f['cross_interface'].append({'id':'X'+str(last+1),'failure':'A policy universe obtained from completed outcomes is presented as a prospective online declaration','closure_packages':['W01','W03','W04','W11','W13','W16'],'discriminating_case':'Construct the declared key universe from original source inputs before inspecting the complete-family outcome list; a newly visible correction label must be covered or explicitly change the question. Current fixed-domain evidence is retrospective only.','status':'Open; the retrospective comparison passes but prospective coverage and unresolved-map extension remain separately planned','evidence':result});save('failure-register.json',f)
c=j(OLD/'closure-packages.json');oldc=cp(c)
for row in c['packages']:
 if row['id'] in ['W03','W04','W11','W12','W13','W16']:
  row['existing_support']+=' FixedDomainPartialPolicy/1 compares98 saved pauses with two full-set formulations and explicit refused-row witnesses; pending cells and source supports remain exact. Retrospective domain construction is disclosed.'
  row['next_action']='Declare policy message domains from original inputs before completing temporal search; specify unknown-map and extension semantics,then compare partial/full policies independently. '+row['next_action']
 if row['id']=='W17':row['existing_support']+=' The partial-policy result is a checked companion awaiting a later protected integration; current PDFs remain unchanged.'
 assert row['status']=='open'
save('closure-packages.json',c)
t='# Full closure program after fixed-domain partial-policy comparison\n\n27 October2026. Current manuscript and live financing progress are retained. All18 broad packages remain open.\n'
for row in c['packages']:
 t+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  v=row[key];t+=label+': '+(', '.join(v) or 'none' if isinstance(v,list) else v)+'\n\n'
(G/'closure-program.md').write_text(t)
nextunit='docs/plans/accounting-prospective-policy-domain-20261027.md';assert (R/nextunit).exists() and (R/finance).exists()
(G/'remaining-work.md').write_text('# Remaining work after fixed-domain partial policies\n\nThe98-checkpoint comparison establishes selected retrospective conclusions only. Build a prospective policy-domain declaration from original inputs; explicitly handle unknown maps and extension relations. Preserve current financing plan:'+finance+'. The checked partial-policy explanation awaits manuscript integration.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in c['packages'])+'\n\nAll18 packages remain open;S1–S5 partial,S6 held,E3 deferred. Actual sources,full company methods,general numerical and language domains,durable recovery and independent acceptance remain open. Continue feasible internal work; no fees,outreach or publication.\n')
(G/'plan-review.md').write_text('Skeptical audit passes within the retrospective fixed-domain target: raw reachable-rule sets cannot establish monotonicity when their domains differ. Full total assignments and independent extensions agree at every selected pause; empty sets can disprove conditional feasibility while nonempty partial sets remain unresolved. The complete saved family supplies the declared comparison domain,so online discovery is expressly unproved. The next plan must establish prospective coverage before inspection of complete outcomes. Preserve all live financing fields,PDF links and original gap rows.\n')
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(a['successor_deltas']),cross_interface_challenges=len(f['cross_interface']))
assert a['groups']==olda['groups'] and a['literature']==olda['literature'] and a['successor_deltas'][:-1]==olda['successor_deltas']
assert f['original']==oldf['original'] and f['literature_extensions']==oldf['literature_extensions'] and f['cross_interface'][:-1]==oldf['cross_interface']
for x,y in zip(c['packages'],oldc['packages']):assert all(x[k]==v for k,v in y.items() if k not in ['existing_support','next_action'])
save('verification.json',{'status':'PASS','counts':counts,'original_rows_preserved':True,'all_packages_open':True,'whole_requirements_closed':0,'predecessor':str(OLD.relative_to(R))})
(G/'result.md').write_text(f'# Partial-policy full-program refresh\n\n27 October2026. Current {live["current_candidate"]} retained. All53 obligations,six interactions,46 operations,nine literature gaps,67 original failures and48 literature extensions remain preserved. Trace contains{counts["successor_deltas"]} deltas and{counts["cross_interface_challenges"]} interface challenges; all18 packages remain open. Next independent plan:{nextunit}. Live finance:{finance}.\n')
base=str(G.relative_to(R));updates={'updated':'2026-10-27','current_audit':base+'/audit-status.json','remaining_work':base+'/remaining-work.md','full_gap_remaining_work':base+'/remaining-work.md','full_gap_plan':'docs/plans/accounting-partial-frontier-policy-20261027.md','full_gap_program':base+'/closure-program.md','closure_packages':base+'/closure-packages.json','failure_register':base+'/failure-register.json','latest_gap_program_result':base+'/result.md','gap_program_review':base+'/plan-review.md','gap_program_verification':base+'/verification.json','gap_program_trace_counts':counts,'latest_compression_result':result,'compression_next_plan':nextunit,'active_work_plans':[finance,nextunit],'current_internal_status':'Current manuscript retained;98 exact fixed-domain partial-policy checkpoints checked. Result remains retrospective; prospective declaration and live financing work continue.'}
for d in [cat['active_execution_note'],np['active_execution']]:
 d.update(updates);d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[result]));d['next']=['Continue '+finance,'Execute '+nextunit,'Integrate checked partial-policy companion in a protected manuscript successor','Continue all18 broad closure packages'];d['gap_program_next']=['Declare prospective policy domains and unknown-map semantics','Continue live financing plan:'+finance,'Continue whole-company methods,general domains,durable recovery and independent acceptance']
short=f'''# Current AccDSL master program

Updated27 October2026. Governing candidate:{live['current_candidate']}.
Current PDF:{live['current_pdf']}.
Main SHA256:{live['current_pdf_sha256']}.
Simulation PDF:{live['standalone_pdf']}.
Simulation SHA256:{live['standalone_pdf_sha256']}.
Manuscript result:{live['latest_result']}.
Four stable PDF/TeX links remain unchanged by this companion refresh.

Observation binding and exact resumable frontiers are integrated. New companion:
{result}. Five cases/98 pauses pass680 assertions and24 controls;
saved audit passes185 assertions and seven controls. Known-cell infeasibility
can precede completion; surviving partial policies remain unresolved. The fixed
universe comes from a completed reference:prospective coverage remains open.
Companion awaits protected manuscript integration.

Active financing plan:{finance}.
Latest financing result:{live.get('latest_financing_result','not recorded')}.
Independent plan:{nextunit}.
Full program:{base}/closure-program.md.
Remaining work:{base}/remaining-work.md.
Verification:{base}/verification.json.

All53 obligations,six interactions,46 operations,nine literature gaps and18 broad
packages remain open;{counts['successor_deltas']} deltas and{counts['cross_interface_challenges']} interface challenges preserve traceability.
S1–S5 partial;S6 held;E3 deferred. Independent reader/domain,actual source/accounting
admission,whole-company methods and general durable/scalable implementation remain
open. Continue feasible internal work. Preserve accepted writers,sources,failed
attempts and current finance work. No fees,outreach or publication.
Controls before refresh:{str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:short,paths[3]:short}
top=f'''## Fixed-domain partial-policy comparison checked — 27 October2026

Current manuscript retained:{live['current_candidate']}. Five cases/98 checkpoints
pass680 assertions and24 controls; saved audit adds185 assertions/seven controls.
Result:{result}. This is retrospective fixed-domain evidence; prospective policy
coverage remains open and the companion awaits manuscript integration.
Active financing plan:{finance}.
Independent plan:{nextunit}.
Full program:{base}/closure-program.md.
All18 packages remain open;S1–S5 partial,S6 held,E3 deferred. Continue internal work.

'''
for n in paths[4:9]:title,body=before[n].decode().split('\n',1);new[n]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode();s=re.sub(r'\[Full remaining-work queue\]\([^)]*\)','[Full remaining-work queue](../'+base+'/remaining-work.md)',s)
s=s.replace('- [Resumable exact temporal partitions]','- [Partial temporal policy conclusions](../'+result+').\n- [Resumable exact temporal partitions]');new['docs/README.md']=s
for n,b in before.items():assert (R/n).read_bytes()==b,'concurrent_control_drift:'+n
for n,h in lock.items():assert sha(R/n)==h,'prior_gap_changed:'+n
for n,v in links.items():assert os.readlink(R/n)==v['target'] and sha(R/n)==v['sha256']
for n,s in new.items():put(R/n,s)
checks=[]
def ck(n,ok):checks.append({'name':n,'pass':bool(ok)});assert ok,n
for n,s in new.items():ck('readback:'+n,(R/n).read_text()==s)
for n,h in lock.items():ck('prior_gap:'+n,sha(R/n)==h)
for n,v in links.items():ck('unchanged_link:'+n,os.readlink(R/n)==v['target'] and sha(R/n)==v['sha256'])
for now,old,key in [(cat,oldcat,'active_execution_note'),(np,oldnp,'active_execution')]:
 ck('legacy_fields',{k:v for k,v in now.items() if k!=key}=={k:v for k,v in old.items() if k!=key});ck('retained_active_fields',all(now[key][k]==v for k,v in old[key].items() if k not in set(updates)|{'latest_internal_results','next','gap_program_next'}))
ck('all18_open',len(c['packages'])==18 and all(x['status']=='open' for x in c['packages']))
(H/'refresh.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'candidate':live['current_candidate'],'finance':finance,'next':nextunit,'counts':counts,'mission_complete':False},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'candidate':live['current_candidate'],'finance':finance,'next':nextunit,'counts':counts,'mission_complete':False}))
