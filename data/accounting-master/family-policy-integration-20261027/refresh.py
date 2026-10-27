"""Add complete-family and common-policy evidence to the live immutable gap predecessor."""
from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
G=H.parent/'gap-family-policy-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(G/n).write_text(json.dumps(v,indent=2)+'\n')
assert read(H/'verification.json')['status']=='PASS' and (H/'author-review.md').exists()
live=read(R/'scripts/accounting_master_catalog.json')['active_execution_note'];OLD=(R/live['full_gap_program']).parent
G.mkdir(exist_ok=False);lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save('predecessor-lock.json',lock)
a=read(OLD/'audit-status.json');base=copy.deepcopy(a);old_delta_count=len(a['successor_deltas'])
a['predecessor']=str(OLD.relative_to(R));a['baseline']='Version5.28 adds complete-family binding and common-history policies under explicitly uncertain observation mechanisms; preserves concurrent financing evidence.'
items=[('Complete temporal-family transport and numerical reuse','temporal-family-binding-20261027/result.md','26 cases,307 assertions,26 controls;117 saved replay assertions. All source/time supports survive numerical sharing; budget stop retains the full original clock domain, not a resumable frontier.'),('Common policies across uncertain observation mechanisms','cross-mechanism-policy-20261027/result.md','21 full policy-set cases,350 assertions,eight controls; independent constraints and exact relabelings. Separate four-policy problems can have no common policy; timing of mechanism revelation changes feasibility.'),('Complete-family and common-policy argument in both editions','family-policy-integration-20261027/result.md','Protected5.28 integrates the mathematical argument and retained counterexamples. Original sources and evidence survive; independent acceptance and general scope remain open.')]
req=['MC01','MC03','MC04','MC05','MC11','MC12','MC13','MC14','MC18','MC24','MC25','MC26','MC28','MC33','MC34','W01','W03','W04','W11','W12','W13','W16','W17']
last=max(int(x['id'][1:]) for x in a['successor_deltas'])
for i,(title,path,scope) in enumerate(items,last+1):
 p=H.parent/path;a['successor_deltas'].append(dict(id='D'+str(i),title=title,requirements=req,evidence=str(p.relative_to(R)),sha256=sha(p),current_disposition=scope))
save('audit-status.json',a)
f=read(OLD/'failure-register.json');prior=copy.deepcopy(f);old_interfaces=len(f['cross_interface']);last=max(int(x['id'][1:]) for x in f['cross_interface'])
new=[('Numerical sharing drops distinct temporal or unresolved source supports','W01 W03 W04 W12 W16','Retain every exact proof leaf and source outcome; compare complete cold/reused rows and policies; reject missing or duplicate supports.','temporal-family-binding-20261027/result.md'),('Budget exhaustion is described as a complete family or saved resumable frontier','W03 W04 W12 W16','Carry the entire original domain as unresolved and return no completed-view policy payload; the predecessor does not retain a partial tree.','temporal-family-binding-20261027/result.md'),('Internal mechanism identifiers are leaked into an actor decision history','W03 W04 W11 W13 W16','Swap H/X message meanings: four policies per mechanism,16 with early observed identity,zero when hidden; bind visibility explicitly.','cross-mechanism-policy-20261027/result.md'),('Later learning is assumed either always to repair earlier conflict or never to change continuation choice','W03 W04 W13 W16','Early conflicting instructions remain infeasible after late revelation; harmless first action permits late resolution; identical first maps permit16 late-tag continuations.','cross-mechanism-policy-20261027/result.md')]
for i,(failure,packages,case,path) in enumerate(new,last+1):f['cross_interface'].append(dict(id='X'+str(i),failure=failure,closure_packages=packages.split(),discriminating_case=case,status='Selected exact conditional cases pass; general observation authority and actual actor knowledge remain open',evidence='data/accounting-master/'+path))
save('failure-register.json',f)
c=read(OLD/'closure-packages.json');priorc=copy.deepcopy(c)
updates={
'W01':('Externally expected family identities bind original sources, clocks, actor and trust; every temporal support remains visible.','Bind supplied actor observation maps to the complete source/world domain; continue actual retained-source availability and whole-disclosure coverage.'),
'W03':('Distinct temporal outcomes survive reuse and decision analysis; unresolved mechanisms do not become selected zero-policy results.','Specify actor-visible observation declarations with exact timing/identity dependencies; keep empirical likelihoods and probabilities separate.'),
'W04':('Complete numerical sharing is checked without erasing supports; common-policy decisions respect cross-mechanism information cells.','Bind observation equivalence/action semantics before broader reuse; separately develop resumable temporal frontiers and justified approximate compression.'),
'W11':('Selected family envelopes and shared-history policy interfaces now carry strict supported fields, actions and unresolved results.','Formalize closed observation-map declarations and invalidation; continue general language/type and independent implementation residuals.'),
'W12':('26 family tampering controls and full cold/reused sets check retained support; no durable cache or authentication claim is made.','Bind changed observation maps, visibility, actor and source time to policy reuse; separately address crash recovery, migration and authentication.'),
'W13':('A common actor-history policy is checked under explicit known/unknown/late mechanism regimes; separate feasibility can fail jointly.','Specify admissible observation maps and their provenance; extend horizon/state/recall semantics only with new exact baselines and preserved unknowns.'),
'W16':('Swapped meanings, late resolution, duplicate same-meaning source heads, unknown outcomes and budget limits add full-set counterexamples.','Add externally bound observation-map change/tampering cases; continue acquisition and other financial-method counterexamples in their independent lane.'),
'W17':('Both5.28 editions integrate complete-family reuse and the common-policy derivation with the preserved failed late-count expectation.','Integrate checked financing companions and future observation results; continue whole-document coherence and independent reader/domain acceptance.')}
for row in c['packages']:
 if row['id'] in updates:row['existing_support']+=' '+updates[row['id']][0];row['next_action']=updates[row['id']][1]
 assert row['status']=='open'
save('closure-packages.json',c)
t='# Full closure program after common-information policy work\n\n27 October2026. All18 broad packages remain open. Original obligations and all predecessor evidence remain preserved. Current financing work continues independently.\n'
for row in c['packages']:
 t+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  val=row[key];t+=label+': '+(', '.join(val) or 'none' if isinstance(val,list) else val)+'\n\n'
(G/'closure-program.md').write_text(t)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nComplete-family transport and selected common-history policy analysis are checked and integrated. Bound observation-map authority, actual source/actor knowledge, general numerical domains, saved frontiers and durable recovery remain open. Preserve the independent acquisition/financial-method lane.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in c['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. No global continuation veto fired. Continue feasible internal work. No fees, outreach or publication.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: full policy sets and complete proof/source supports are primary; counts and page totals are explanatory. Hidden mechanism identity is not an actor observation. Late revelation cannot fix an earlier conflict but can diversify later instructions. The first incorrect late-count expectation and its exact repair are retained. A conservative whole-domain remainder is not a resumable frontier. Preserve all original gap rows, legacy controller fields and live financing progress.\n')
counts=dict(read(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(a['successor_deltas']),cross_interface_challenges=len(f['cross_interface']))
assert a['groups']==base['groups'] and a['literature']==base['literature'] and a['successor_deltas'][:old_delta_count]==base['successor_deltas']
assert all(f[k]==prior[k] for k in ['original','literature_extensions']) and f['cross_interface'][:old_interfaces]==prior['cross_interface']
for row,old in zip(c['packages'],priorc['packages']):assert all(row[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
for n,h in lock.items():assert sha(R/n)==h
save('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0,predecessor=str(OLD.relative_to(R))))
(G/'result.md').write_text(f'# Full-program family/policy refresh\n\n27 October2026. All53 obligations, six interactions,46 operations, nine literature gaps,67 original failures and48 literature extensions are preserved. The additive trace now contains{counts["successor_deltas"]} deltas and{counts["cross_interface_challenges"]} interface challenges. All18 packages remain open. Next computational unit: bound actor observation maps. Preserve live financing lane: {live["active_work_plan"]}.\n')
print(json.dumps({'status':'PASS','counts':counts,'predecessor':str(OLD.relative_to(R)),'predecessor_files':len(lock)}))
