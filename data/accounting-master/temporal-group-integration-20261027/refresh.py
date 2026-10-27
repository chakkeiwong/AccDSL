"""Preserve all predecessor obligations while adding checked temporal/group evidence."""
from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
OLD=H.parent/'gap-control-history-refresh-20261027';G=H.parent/'gap-temporal-group-refresh-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(G/n).write_text(json.dumps(v,indent=2)+'\n')
assert read(H/'verification.json')['status']=='PASS' and (H/'author-review.md').exists()
G.mkdir(exist_ok=False);lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};save('predecessor-lock.json',lock)
a=read(OLD/'audit-status.json');base=copy.deepcopy(a);assert len(a['successor_deltas'])==53
a['predecessor']=str(OLD.relative_to(R));a['baseline']='Version 5.27 adds complete conditional exact-clock families and control-history/group-method scope; actual admission and general methods remain open.'
items=[('D54','Exact interval and private-access source-view families','source-time-intervals-20261027/result.md','593 assertions; 256 order comparisons; 47 complete saved requests; 1012 proof nodes independently replayed; separate 182-assertion leaf/trust audit. No clock probabilities, actual actor access or cross-view common policy.'),('D55','Conditional control history to group-method scope','control-group-boundary-20261027/result.md','23 cases,15 controls,291 assertions; stable full ownership is only a scope candidate. Changing perimeter, partial ownership and unresolved control retain financial-method requirements.'),('D56','Dual-edition temporal/group integration','temporal-group-integration-20261027/result.md','5.27 preserves 253 predecessor sources and136 evidence files;663 document checks pass. Escaped-reference defect retained/repaired; bounded author review does not establish whole-document acceptance.')]
req=['MC01','MC03','MC05','MC11','MC12','MC13','MC17','MC19','MC20','MC24','MC25','MC26','MC28','MC33','MC34','MC35','W01','W03','W04','W05','W06','W08','W11','W12','W13','W16','W17']
for ident,title,path,scope in items:
 p=H.parent/path;a['successor_deltas'].append(dict(id=ident,title=title,requirements=req,evidence=str(p.relative_to(R)),sha256=sha(p),current_disposition=scope))
save('audit-status.json',a)
f=read(OLD/'failure-register.json');prior=copy.deepcopy(f)
new=[('Midpoint or closed-boundary replacement erases a possible information view','W01 W03 W04 W12 W16','Use exact points/half-open ranges and strict complements; straddling correction access retains both full policy sets.','source-time-intervals-20261027/result.md'),('Independent clock classifications accept an impossible joint chronology','W01 W03 W04 W12 W16','Retain correlated original inequalities and verify complete first-failure partitions with exact witnesses or contradiction cycles.','source-time-intervals-20261027/result.md'),('Public release and private actor delivery are conflated','W01 W03 W12 W16','Require an explicit actor-addressed route; public release cannot invent access and private delivery need not follow release.','source-time-intervals-20261027/result.md'),('A favorable temporal view or budget prefix is reported as the whole family','W03 W04 W12 W13 W16','Retain zero/four policy outcomes separately and mark budget exhaustion incomplete; whole-family transport remains next.','source-time-intervals-20261027/result.md'),('Stable control and full ownership are treated as permission to issue group statements','W05 W06 W08 W11 W12 W16','Keep all admission/execution flags false; a scope-fitting request with missing legal reports still refuses.','control-group-boundary-20261027/result.md')]
assert len(f['cross_interface'])==48
for i,(failure,packages,case,path) in enumerate(new,49):f['cross_interface'].append(dict(id='X'+str(i),failure=failure,closure_packages=packages.split(),discriminating_case=case,status='Selected conditional cases pass; general methods and actual admission remain open',evidence='data/accounting-master/'+path))
save('failure-register.json',f)
c=read(OLD/'closure-packages.json');priorc=copy.deepcopy(c)
updates={
'W01':('Exact clock intervals and explicit public/private actor routes retain unknown observations and joint chronology.','Bind complete temporal families to evidence/policy dependencies; continue actual retained-source availability and whole-document disclosure coverage.'),
'W03':('Complete temporal partitions preserve selected and unresolved revision outcomes without clock probabilities.','Transport all view supports and budget incompleteness; separately specify common observations/actions before claiming one cross-view robust policy.'),
'W04':('Exact rational difference constraints and strict-complement partitions represent timestamp continua symbolically.','Complete family-level transport/reuse, then broader numerical domains and justified approximate policy transfer; keep scalability claims separate.'),
'W05':('Conditional control history is bound to the original group request with explicit exact calendar and reporting-basis premises.','Complete dated acquisition-period authority and conditional acquisition/loss measurement before composing financial statements.'),
'W06':('Stable full ownership, partial ownership and changing perimeter now have distinct scope routes; none authorizes reports.','Specify acquisition/loss and NCI methods, dated member/flow allocation and complete journal/report comparisons.'),
'W08':('The source/history-to-group boundary has23 complete cases and an unchanged baseline report replay.','Continue acquisition-period authority and financial-method specification; source hashes do not establish accounting applicability.'),
'W11':('Exact source-clock and group-scope interfaces have explicit precision, route, identity, basis and refusal semantics.','Specify a bound complete-family envelope and general schema/unknown semantics; preserve non-admission flags.'),
'W12':('Temporal proof replay checks1012 nodes; the group adapter rejects stale basis/source/time links.','Bind full family and externally expected identities; retain unfinished timing scope; separately address authentication, durable recovery and migration.'),
'W13':('An unresolved access interval retains both zero-policy and four-policy answers over the same financial population.','Define a common actor observation/action domain for policy choice across uncertain mechanisms; do not intersect incompatible labels or invent weights.'),
'W16':('Boundary, private-access, correlated-clock and group-scope counterexamples extend the preserved adversarial suite.','Add family tampering/reuse cases and acquisition-period cases with independent full expected outputs.'),
'W17':('Both5.27 editions integrate the temporal and group-method arguments while protecting every predecessor source/citation.','Integrate completed successor findings; continue whole-document coherence, deeper literature coverage and independent reader/domain acceptance.')}
for row in c['packages']:
 if row['id'] in updates:row['existing_support']+=' '+updates[row['id']][0];row['next_action']=updates[row['id']][1]
 assert row['status']=='open'
save('closure-packages.json',c)
t='# Full closure program after exact temporal families and group-scope binding\n\n27 October2026. All18 broad packages remain open. Original obligations and predecessor evidence remain preserved. Selected deterministic cases do not establish whole-company completeness.\n'
for row in c['packages']:
 t+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  val=row[key];t+=label+': '+(', '.join(val) or 'none' if isinstance(val,list) else val)+'\n\n'
(G/'closure-program.md').write_text(t)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nExact temporal families and conditional group scope are integrated. Complete-family transport/reuse, acquisition/loss/NCI methods, actual source/authority admission, common cross-view policy semantics, general numerical domains and durable recovery remain open.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in c['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. No global continuation veto fired. Continue feasible internal work. No fees, outreach or publication.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: whole exact partitions and complete policy populations are the scientific criteria; document preservation and bounded render review govern this integration. Counts/runtime/pages are explanatory. Stable group scope is not report authorization. No source truth, clock probability or universal cross-view policy follows. Complete-family transport and acquisition authority are the next separate dependencies. Preserve all original rows, legacy controller fields and any newer financing route before advancing.\n')
counts=dict(read(OLD/'verification.json')['counts']);counts.update(successor_deltas=56,cross_interface_challenges=53)
assert a['groups']==base['groups'] and a['literature']==base['literature'] and a['successor_deltas'][:53]==base['successor_deltas']
assert all(f[k]==prior[k] for k in ['original','literature_extensions']) and f['cross_interface'][:48]==prior['cross_interface']
for row,old in zip(c['packages'],priorc['packages']):assert all(row[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
for n,h in lock.items():assert sha(R/n)==h
save('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
(G/'result.md').write_text('# Full-program temporal/group refresh\n\n27 October2026. All53 obligations, six interactions,46 operations, nine literature gaps,67 original failures and48 literature extensions are preserved. D54–D56 and X49–X53 bring totals to56 deltas and53 interface challenges. All18 packages remain open. Next computational unit: complete temporal-family binding. Next financing unit: acquisition-period authority and method specification.\n')
print(json.dumps({'status':'PASS','counts':counts,'predecessor_files':len(lock)}))
