"""Append observation/frontier evidence to the live gap program; preserve all original rows."""
from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;G=H.parent/'gap-observation-frontier-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(G/n).write_text(json.dumps(v,indent=2)+'\n')
assert read(H/'verification.json')['status']=='PASS' and (H/'author-review.md').exists()
live=read(R/'scripts/accounting_master_catalog.json')['active_execution_note'];OLD=(R/live['full_gap_program']).parent
G.mkdir(exist_ok=False);lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save('predecessor-lock.json',lock)
a=read(OLD/'audit-status.json');base=copy.deepcopy(a);old_delta_count=len(a['successor_deltas'])
a['predecessor']=str(OLD.relative_to(R));a['baseline']='Version5.32 preserves the live intragroup edition and integrates actor observation binding and exact resumable temporal partitions; concurrent financing progress remains intact.'
items=[('Actor-visible observation maps and full numerical reuse','observation-map-binding-20261027/result.md','22 cases,342 assertions,30 controls;115 saved-audit assertions. Visible colliding tags do not reveal hidden mechanism identity. All source supports survive exact numerical sharing; actual actor knowledge remains open.'),('Resumable exact temporal partitions preserve pending cells','temporal-frontier-20261027/result.md','47 full predecessor trees across four budgets;10,146 assertions,43 controls. Saved audit checks1060 checkpoints with3191 assertions and five additional controls. Pending cells may be empty; no scalability or durability claim.'),('Observation and continuation arguments preserved with live finance','observation-frontier-rebase-20261027/result.md','Protected5.32 rebases both checked sections on live intragroup5.31; exact predecessor/evidence preservation and bounded rendered review. Whole-document and independent acceptance remain open.')]
req=['MC01','MC03','MC04','MC05','MC11','MC12','MC13','MC14','MC18','MC24','MC25','MC26','MC28','MC33','MC34','W01','W03','W04','W11','W12','W13','W16','W17']
last=max(int(x['id'][1:]) for x in a['successor_deltas'])
for i,(title,path,scope) in enumerate(items,last+1):
 p=H.parent/path;a['successor_deltas'].append(dict(id='D'+str(i),title=title,requirements=req,evidence=str(p.relative_to(R)),sha256=sha(p),current_disposition=scope))
save('audit-status.json',a)
f=read(OLD/'failure-register.json');prior=copy.deepcopy(f);old_interfaces=len(f['cross_interface']);last=max(int(x['id'][1:]) for x in f['cross_interface'])
new=[
('A visible colliding tag is replaced by a unique internal mechanism ID','W03 W04 W11 W13 W16','Distinct early tags yield16 policies; colliding early tags yield zero under the same swapped action meanings. Only declared tokens enter actor history.','observation-map-binding-20261027/result.md','Selected finite cases checked; actual actor knowledge and general maps remain open'),
('A first-stage message map indexes hidden rights, full world IDs or future observations','W01 W03 W11 W13 W16','Require exact declared stage-available key coverage; reject missing/duplicate and unavailable keys.','observation-map-binding-20261027/result.md','Closed finite input profile checked; richer observation languages remain open'),
('Equal policy counts license reuse after messages or action meanings change','W04 W11 W12 W16','Compare complete messages,actions,rows and method identities; changed labels recompute while same-meaning source changes retain supports.','observation-map-binding-20261027/result.md','Exact finite kernels checked; general isomorphism/durable cache remains open'),
('An unresolved observation declaration is reported as a complete empty feasible-policy set','W03 W11 W13 W16','Unknown/untrusted/late tags remain unresolved,distinct from a complete zero-policy result.','observation-map-binding-20261027/result.md','Selected declaration cases checked; tag-induced temporal refinement remains open'),
('Paused temporal search loses complementary siblings or treats known outcomes as exhaustive','W03 W04 W12 W16','Install all exact first-failure children before pause; verify every pending path and complete source supports at1060 saved checkpoints.','temporal-frontier-20261027/result.md','Selected exact frontier checked; scale and crash consistency remain open'),
('A pending temporal cell is assumed feasible or erased because it is probably empty','W03 W04 W13 W16','Pending means unchecked; seven root cells are later proved empty but all remain until their exact contradiction is checked.','temporal-frontier-20261027/result.md','Selected exact proof domains checked; no probability claim'),
('Policy-set monotonicity compares partial functions with changing message domains','W03 W04 W11 W13 W16','Next audited plan requires a fixed full policy domain or explicit extension relation before interpreting partial-known-cell intersections.','temporal-frontier-20261027/result.md','Open; exact contract/API audit and independent partial/full policy comparison required')]
for i,(failure,packages,case,path,status) in enumerate(new,last+1):f['cross_interface'].append(dict(id='X'+str(i),failure=failure,closure_packages=packages.split(),discriminating_case=case,status=status,evidence='data/accounting-master/'+path))
save('failure-register.json',f)
c=read(OLD/'closure-packages.json');priorc=copy.deepcopy(c)
updates={
'W01':('Source/actor/time-bound finite observation declarations preserve all complete-family supports and explicit unknowns.','Continue actual retained-source availability/whole-disclosure coverage; separately specify admitted tag-induced temporal refinement.'),
'W03':('Colliding tags,unknown declarations and hidden-map inputs are distinguished; resumable exact partitions retain known outcomes plus pending domains.','Bind partial temporal results to a fixed policy domain without treating unknown or pending as complete; retain unweighted ambiguity and separate empirical likelihood work.'),
'W04':('Numerical sharing checks full decision semantics;47 exact temporal families resume identically under four step budgets without losing any support.','Connect partial-frontier policy restrictions; keep larger domains,scheduling,approximate reduction and general state equivalence separately justified.'),
'W11':('Closed stage-available observation maps and four-kind temporal frontier nodes have explicit refusal/checking semantics.','Specify total policy domains or extension relations for partial source families; continue general language/type and independent implementation residuals.'),
'W12':('Externally bound frontier requests,caps,methods and reconstructed paths reject tampering and preserve completed certificates; no durable-storage claim.','Bind partial policy caches to full declaration and frontier identities; separately address crash recovery,migration and authentication.'),
'W13':('Exact strict complements and terminal/empty proofs preserve original timing domains through pauses; unknown declaration differs from infeasibility.','Derive sound partial-policy conclusions under fixed semantics; extend general formula,horizon and source-refinement scope only with exact comparisons.'),
'W16':('22 observation cases and47 temporal cases add full-set/support comparisons,43 frontier controls and independent saved-record audit.','Test changing policy-domain support and partial/full conclusions; preserve all live financing counterexamples and extend remaining interaction coverage.'),
'W17':('Protected5.32 preserves the live intragroup edition and adds observation/temporal-continuation arguments with original sources and citations intact.','Continue live financial-method integrations and whole-document coherence; independently check reader/domain/implementation acceptance,without treating author review as completion.')}
for row in c['packages']:
 if row['id'] in updates:
  row['existing_support']+=' '+updates[row['id']][0];row['next_action']=updates[row['id']][1]
 assert row['status']=='open'
save('closure-packages.json',c)
t='# Full closure program after observation and temporal continuation work\n\n27 October2026. All18 broad packages remain open. Preserve all original obligations and live financing progress.\n'
for row in c['packages']:
 t+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  val=row[key];t+=label+': '+(', '.join(val) or 'none' if isinstance(val,list) else val)+'\n\n'
(G/'closure-program.md').write_text(t)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nObservation binding and exact resumable frontiers are checked and integrated. Next computational unit: partial-frontier policy conclusions under a fixed domain. Actual source/actor knowledge,tag-induced refinement,general numerical domains,durable recovery and independent acceptance remain open. Continue live financing plan: '+live['active_work_plan']+'.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in c['packages'])+'\n\nS1–S5 partial;S6 held;E3 deferred. No global continuation veto fired. Continue feasible internal work. No fees,outreach or publication.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: full policies,proof trees and source supports are primary; counts/page totals do not close requirements. Pending cells are unchecked,not necessarily feasible. Full complement coverage and unchanged proof work are verified at every saved pause. Visible colliding tags do not reveal mechanism IDs. Fixed-domain policy semantics remain a pre-implementation condition for the next unit. Rebase on current live financing sources and preserve all concurrent financial work; retain legacy controls and frozen evidence.\n')
counts=dict(read(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(a['successor_deltas']),cross_interface_challenges=len(f['cross_interface']))
assert a['groups']==base['groups'] and a['literature']==base['literature'] and a['successor_deltas'][:old_delta_count]==base['successor_deltas']
assert all(f[k]==prior[k] for k in ['original','literature_extensions']) and f['cross_interface'][:old_interfaces]==prior['cross_interface']
for row,old in zip(c['packages'],priorc['packages']):assert all(row[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
for n,h in lock.items():assert sha(R/n)==h
save('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0,predecessor=str(OLD.relative_to(R))))
(G/'result.md').write_text(f'# Full-program observation/frontier refresh\n\n27 October2026. All53 obligations,six interactions,46 operations,nine literature gaps,67 original failures and48 literature extensions remain preserved. Additive trace now contains{counts["successor_deltas"]} deltas and{counts["cross_interface_challenges"]} interface challenges. All18 packages remain open. Next computational plan:docs/plans/accounting-partial-frontier-policy-20261027.md. Preserve live financing plan:{live["active_work_plan"]}.\n')
print(json.dumps({'status':'PASS','counts':counts,'predecessor':str(OLD.relative_to(R)),'predecessor_files':len(lock)}))
