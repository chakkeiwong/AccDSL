from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
P=R/'data/accounting-master/gap-runtime-refresh-20261026';O=R/'data/accounting-master/gap-symbolic-refresh-20261026';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/n).read_text())
def write(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
lock={str(p.relative_to(R)):sha(p) for p in P.iterdir() if p.is_file()};write('predecessor-lock.json',lock)
a=read('audit-status.json');cp=read('closure-packages.json');f=read('failure-register.json')
old=copy.deepcopy(a);oldf=copy.deepcopy(f)
results=[
('Selected quantified affine/Boolean method certificate','symbolic-method-certificate-20261026/result.md','Eight methods in two charts; independent effects/guards/memory and pinned full metadata;190 checks and26 controls. Known-value profile only, no whole-region completion by this unit.'),
('Complete conditional symbolic sequence','symbolic-path-composition-20261026/result.md','32 variants,96 conditional branches,1771 checks and10 controls; complete accounts/memory/flows/guards and reduced prior oracle agree; reachability not inferred by this unit.'),
('Exact partitions for the selected3872 region jobs','exact-region-certificates-20261026/result.md','All3872 selected jobs checked;918 accepted and2960 refused nonempty leaves;4772 weighted contradiction certificates. Complete financial relations checked on all retained leaves. Observations/policies, general domains and authority remain open.'),
('Verified saved region proofs and certificate-bound queue','exact-region-certificates-20261026/queue-result.md','All3872 saved proofs revalidated;19414 assertions,8 controls; zero/mixed budget resumes match uninterrupted certified frontier. No authenticated or crash-durable storage claim.'),
('Conditional contingent conversion authority','contingent-conversion-authority-20261026/result.md','Five primary sources with bounded technical inspection; issuer/holder/intervening measurement and control-perimeter questions separated. Future edition chain and actual2027/2028 admission remain unresolved; next financing control-scope plan preserved.')]
for title,path,disp in results:
 p=R/'data/accounting-master'/path;assert p.exists()
 a['successor_deltas'].append({'id':f"D{len(a['successor_deltas'])+1}",'title':title,'requirements':['MC11','MC12','MC17','MC24','MC25','MC26','MC28','MC33','MC34','W04','W11','W12','W13','W16','W17'] if 'conversion' not in title else ['MC17','MC19','MC24','MC25','MC28','MC30','MC33','MC34','MC35','W06','W07','W08'],'evidence':str(p.relative_to(R)),'sha256':sha(p),'current_disposition':disp})
a['baseline']='Version5.22 plus selected symbolic method/sequence/region proofs, verified saved queue and conditional financing authority; documentary successor selected separately by the live master.'
a['predecessor']={'path':str(P.relative_to(R)),'lock':'predecessor-lock.json'}
changes={
'W03':('Selected financial regions now have exact partition proofs; actor-information mapping is still an independent dependency.','Bind certified financial leaves to immutable actor observations; compare exact nonanticipative feasible-policy sets against the prior independent reference.'),
'W04':('All3872 selected two-rate/order jobs now have verified exhaustive partitions; witnesses establish nonemptiness and symbolic relations establish entire-leaf outcomes.','Connect certified leaves to observation-measurable policies; extend domains and capacity only under new proofs or explicit approximation error bounds.'),
'W05':('Complete symbolic sequences retain signed profit/expense accounts, gross flows and paid/used history; refusals retain accrued claims.','Compose selected policy certification with independently admitted financing terms and measurement; preserve decision versus economic feasibility.'),
'W06':('New conditional authority matrix separates issuer/holder measurement, edition and post-conversion control scope.','Complete the active conversion-control-scope source/dependency work and2027/2028 authority chain; no invented valuation inputs.'),
'W07':('Five primary financing sources receive bounded technical inspection; actual applicability remains unresolved.','Continue conversion-control-scope and measurement preparation, plus mixed-promise/calendar/tax/costing gaps; preserve all corporate cases.'),
'W11':('Known-valued affine/Boolean selected methods and complete sequences are now checked against independent forms with full pinned metadata.','Extend beyond selected methods only with explicit syntax/type/unknown-value proofs; independent compatible implementations remain separate.'),
'W12':('A new scope-bound finite queue revalidates saved region proofs before completion and preserves zero/mixed budget JSON continuation.','Connect actual source/actor views and efficient certificate invalidation; durable store/restart/migration behavior needs separate fault evidence.'),
'W13':('Independent weighted-sum checks certify every pruned child in the two-dimensional exact profile; strict and singleton boundaries are retained.','Extend numerical fragments with independent inequality certificates or justified approximation; investigate quantization and non-affine operations before promotion.'),
'W16':('Exact method, path, region and saved-queue comparators reject semantic/structural corruption; failed diagnostic repairs remain preserved.','Compose certified observation policies with admitted source/measurement and financing; keep complete states and invalidity comparators.'),
'W17':('Selected method/sequence/region evidence is ready for protected dual-edition integration.','Integrate symbolic certificate findings and separate funding/authority results; continue whole-document consistency and independent reader/domain review.')}
for row in cp['packages']:
 if row['id'] in changes:
  support,action=changes[row['id']];row['existing_support']+=' '+support;row['next_action']=action
 assert row['status']=='open'
newfail=[
('Correct monetary formulas hide an altered parameter binding or unused declaration',['W04','W11','W16'],'Compare independent bindings, exact parameter occurrence paths and complete non-expression metadata.'),
('Affine local agreement is mistaken for a complete dated sequence',['W05','W11','W16'],'Compare all six substitutions, pre/post guards, full account/memory/flow formulas and both unpaid refusal prefixes.'),
('An infeasible branch is discarded without a valid strict inequality proof',['W04','W13','W16'],'Check rational nonnegative multipliers against original rows; retain equality points and strict contradiction counterexamples.'),
('A saved region job is marked complete from a witness or self-consistent checksum',['W04','W12','W16'],'Revalidate exhaustive partition trees and full financial relations before accepting an externally bound proof fingerprint.'),
('Different actions on indistinguishable financial worlds are reported as a policy',['W03','W04','W05','W16'],'Next unit must bind certified leaves to actor information and forbid anticipative/information-cell-inconsistent choices.')]
for i,(failure,packages,case) in enumerate(newfail):
 f['cross_interface'].append({'id':f"X{len(f['cross_interface'])+1}",'failure':failure,'closure_packages':packages,'discriminating_case':case,'status':'Bounded controls checked; broad package open' if i<4 else 'Open next discriminating unit','evidence':'data/accounting-master/'+results[min(i,3)][1] if i<4 else 'docs/plans/accounting-certified-observation-policy-20261026.md'})
write('audit-status.json',a);write('closure-packages.json',cp);write('failure-register.json',f)
lines=['# Full closure program after selected symbolic certificates','','26 October2026. All18 broad packages remain open. Original obligations, literature and failures are preserved; this is evidence reconciliation, not a fresh exhaustive audit.','']
for q in cp['packages']:
 lines += [f"## {q['id']} — {q['title']}",'','Requirements: '+', '.join(q['requirements'])+'.','','Dependencies: '+(', '.join(q['depends_on']) or 'none')+'.','','Known failure: '+q['failure'],'','Existing support: '+q['existing_support'],'','Closure evidence: '+q['closure_evidence'],'','Next action: '+q['next_action'],'','Limits: '+q['limits'],'','Status: open.','']
(O/'closure-program.md').write_text('\n'.join(lines))
(O/'remaining-work.md').write_text('# Complete remaining-work queue\n\nAll3872 selected known-valued two-rate jobs now have checked exact partitions and a verified saved-proof frontier. General symbolic domains, information-constrained policies, actual authority, durability and scale remain open. Preserve the active financing-control scope lane.\n\n'+'\n'.join(f"- **{q['id']} {q['title']}:** {q['next_action']}" for q in cp['packages'])+'\n\nAll18 broad packages remain open. S1–S5 partial; S6 held; E3 deferred. Human reader/domain acceptance remains pending; feasible internal work continues. No outreach, fees or background campaign authorized.\n')
assert a['groups']==old['groups'] and a['literature']==old['literature'] and a['successor_deltas'][:38]==old['successor_deltas']
assert all(f[k]==oldf[k] for k in ('original','literature_extensions')) and f['cross_interface'][:31]==oldf['cross_interface']
assert all(sha(R/n)==h for n,h in lock.items())
counts={'obligations':53,'interactions':6,'operations':46,'literature_gaps':9,'original_failures':67,'literature_extensions':48,'cross_interface_challenges':len(f['cross_interface']),'successor_deltas':len(a['successor_deltas']),'closure_packages':18}
write('verification.json',{'status':'PASS','counts':counts,'original_rows_preserved':True,'all_packages_open':True,'whole_requirements_closed':0,'scope':'Trace reconciliation; selected exact-region completion does not close general policy/domain requirements'})
(O/'plan-review.md').write_text('The reviewed integration plan requires complete predecessor preservation and separate claims for method, sequence, region, queue and actual authority. Counts, pages and synthetic completeness cannot close whole-company obligations. Current financing routes and legacy controller fields must remain unchanged. Audit passes with those controls; next computational question is observation-measurable policy equivalence.\n')
(O/'result.md').write_text('# Master program after symbolic certificates\n\nD39–43 add selected method, complete sequence, exact-region, saved-queue and conditional financing authority evidence. The successor preserves53 obligations,6 interactions,46 operations,9 literature gaps,67 original failures and48 extensions, with43 deltas and36 cross-interface challenges. All18 broad packages remain open. Source hashes and unchanged predecessor rows verify. Documentary integration adds its own successor evidence after rendered review.\n')
print(json.dumps({'status':'PASS','counts':counts}))
