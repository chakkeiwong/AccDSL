"""Add only new scoped evidence to the latest frozen gap inventory."""
from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
OLD=H.parent/'gap-policy-control-refresh-20261026';G=H.parent/'gap-source-policy-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(G/n).write_text(json.dumps(v,indent=2)+'\n')
assert read(H/'verification.json')['status']=='PASS' and (H/'author-review.md').exists();G.mkdir(exist_ok=False)
lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save('predecessor-lock.json',lock)
a=read(OLD/'audit-status.json');base=copy.deepcopy(a);assert len(a['successor_deltas'])==48
a['predecessor']=str(OLD.relative_to(R));a['baseline']='Version 5.25 adds conditional immutable source/actor policy selection and dependency-scoped numerical reuse, while preserving the live financing/control-history lane.'
items=[('D49','Conditional immutable source and actor policy views','certified-source-views-20261026/result.md','29 cases, eight exact scenario mappings,275 assertions and15 controls. Reuses existing identity/timing mechanisms without priors; unknown/retracted/conflicting access remains unresolved. Actual source admission and broader clocks remain open.'),('D50','Dependency-scoped complete-policy reuse','source-policy-invalidation-20261027/result.md','29 independent masks,198 assertions and12 tampering controls. Thirteen cases reuse numerical policy sets with complete cold-run equality; source/actor bindings invalidate separately. No performance, authentication or durable-cache claim.'),('D51','Source-timed policy argument integrated in both editions','source-policy-integration-20261027/result.md','Protected Version5.25 integrates selected source revision/access and seven-node dependency argument; all prior source/evidence preserved. Independent acceptance and real-company use remain open.')]
for ident,title,path,scope in items:
 p=H.parent/path;a['successor_deltas'].append(dict(id=ident,title=title,requirements=['MC01','MC02','MC03','MC11','MC12','MC13','MC24','MC25','MC26','MC28','MC33','MC34','W01','W03','W04','W12','W16','W17'],evidence=str(p.relative_to(R)),sha256=sha(p),current_disposition=scope))
save('audit-status.json',a)
f=read(OLD/'failure-register.json');prior=copy.deepcopy(f)
new=[('Source selection silently imports a prior into an unweighted robust-policy problem','W03 W04 W16','Reuse identity/ancestry/time mechanisms but preserve the full unweighted world family and both complete policy solvers.','certified-source-views-20261026/result.md'),('Publication, actor access, system review and economic effective time are collapsed into one timestamp','W01 W03 W12 W16','Compare29 revisions/cutoffs including delayed ingestion, actor-specific access, unknown clocks, conflict and retraction.','certified-source-views-20261026/result.md'),('Equal numerical policies permit reuse of an obsolete source or actor binding','W03 W04 W12 W16','Independent seven-node change masks separate semantic numerical reuse from replaced source/actor identities.','source-policy-invalidation-20261027/result.md'),('Transported rows or prior results self-authenticate after alteration','W04 W12 W16','Check content against external expected identities; reject lost/duplicate worlds, changed signals/rights and altered prior sets/graphs.','source-policy-invalidation-20261027/result.md')]
for i,(failure,packages,case,path) in enumerate(new,43):f['cross_interface'].append(dict(id='X'+str(i),failure=failure,closure_packages=packages.split(),discriminating_case=case,status='Selected conditional controls pass; actual admission/general scope remains open',evidence='data/accounting-master/'+path))
save('failure-register.json',f)
c=read(OLD/'closure-packages.json');priorc=copy.deepcopy(c)
updates={
'W01':('Conditional public-document source views now distinguish publication, actor access, ingestion/review and economic effective time.','Extend exact interval/private-access semantics; continue actual retained disclosure/indenture availability with no invented timestamps.'),
'W02':('All eight selected source interpretations retain complete certified world rows; no normalized probability model is introduced.','Extend an evidenced missing event/domain without losing the joint persistent-history family; keep actual source interpretation separate.'),
'W03':('Twenty-nine revision/access cases preserve future/unknown/conflicting/retracted heads and complete robust policies.','Execute exact source-time interval/access plan, preserving unweighted possible views; actual likelihood/strategic disclosure work remains separate.'),
'W04':('Seven explicit dependency nodes separate numerical policy reuse from source and actor rebinding; complete cold/reused sets match in29 cases.','Extend clocks and broader numerical domains; verify error/policy transfer before any approximate merge or production scaling claim.'),
'W11':('The adapter reuses existing identity, time and policy engines under a closed two-slot profile; external expected identities protect transported inputs.','Specify interval/private-access extension before code; continue general type/unknown-value and independent implementation residuals.'),
'W12':('Changed source meaning, source identity, actor and cutoff have separate checked invalidation effects;12 corruption controls reject altered inputs and prior results.','Extend exact interval/private access; separately prove authenticated trust, durable recovery, migration and efficient general dependency maintenance.'),
'W16':('Twenty-nine complete source-view cases and independent reuse masks add actor/time and tampering counterexamples; original failure records are retained.','Test interval-boundary and private-access possibilities with complete policy/world sets; continue financing/control-history and acquisition cases.'),
'W17':('Source-timed selection and numerical/source dependency argument is integrated in protected5.25 editions with preserved mathematical and source support.','Integrate future interval-control, authority and source-clock results; continue whole-document coherence and independent reader/domain acceptance.')}
for row in c['packages']:
 if row['id'] in updates:row['existing_support']+=' '+updates[row['id']][0];row['next_action']=updates[row['id']][1]
 assert row['status']=='open'
save('closure-packages.json',c)
text='# Full closure program after source-timed policy reuse\n\n27 October2026. All18 broad packages remain open. Original obligations and predecessor evidence remain preserved; selected deterministic results do not establish whole-company completeness.\n'
for row in c['packages']:
 text+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  val=row[key];text+=label+': '+(', '.join(val) or 'none' if isinstance(val,list) else val)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nConditional public-document source/actor views and selected dependency reuse are checked and integrated. Interval/private access, actual source/measurement admission, control history, dated authority, general domains and durable recovery remain open.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in c['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. No global continuation veto has fired. Continue feasible internal work without fees/outreach/publication.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: complete cold/reused policies and independent node-change masks are primary, while counts/page totals/runtime are explanatory. No prior is inserted into robust policy selection. Source truth, actual actor access, whole-second/private scope, authentication and crash durability stay separate. Preserve all inherited rows and the live financing plan, including any concurrent completed work, before advancing.\n')
counts=dict(read(OLD/'verification.json')['counts']);counts.update(successor_deltas=51,cross_interface_challenges=46)
assert a['groups']==base['groups'] and a['literature']==base['literature'] and a['successor_deltas'][:48]==base['successor_deltas']
assert all(f[k]==prior[k] for k in ['original','literature_extensions']) and f['cross_interface'][:42]==prior['cross_interface']
for row,old in zip(c['packages'],priorc['packages']):assert all(row[k]==val for k,val in old.items() if k not in ['existing_support','next_action'])
for n,h in lock.items():assert sha(R/n)==h
save('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0,scope='Selected source-policy trace reconciliation; no full scientific/domain acceptance'))
(G/'result.md').write_text('# Full-program source-policy refresh\n\n27 October2026. All53 obligations, six interactions,46 operations, nine literature gaps,67 original failures and48 literature extensions survive unchanged. D49–D51 and X43–X46 bring totals to51 successor deltas and46 interface challenges. All18 broad packages remain open. The live financing/control-history lane remains preserved; exact source-time intervals and private-access scope are the next computational unit.\n')
print(json.dumps({'status':'PASS','counts':counts,'predecessor_files':len(lock)}))
