"""Additive gap successor. Preserve every prior row and evidence file."""
from pathlib import Path
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
OLD=H.parent/'gap-symbolic-refresh-20261026';G=H.parent/'gap-policy-control-refresh-20261026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,x):(G/n).write_text(json.dumps(x,indent=2)+'\n')
assert read(H/'verification.json')['status']=='PASS';assert (H/'author-review.md').exists();G.mkdir(exist_ok=False)
lock={str(p.relative_to(R)):sha(p) for p in OLD.iterdir() if p.is_file()};put('predecessor-lock.json',lock)
a=read(OLD/'audit-status.json');original=copy.deepcopy(a)
a['predecessor']=str(OLD.relative_to(R));a['baseline']='Version 5.24 integrates selected certified observation policies and conditional conversion control/reporting scope; actual source/actor views and acquisition-period authority remain separate.'
entries=[('D45','Certified observation-constrained feasible policies','certified-observation-policy-20261026/result.md',['W03','W04','W05','W11','W12','W16','MC11','MC12','MC13','MC17','MC24','MC25','MC26','MC28','MC33','MC34'],'All 3,872 job proofs revalidated, 3,884 observation rows, 1,766 complementary refinements, 55 signal proofs; 17,420 assertions and nine controls. Complete sets agree in eight problems; only receipt 7/refined/committed has four policies. Actual actor knowledge and source binding remain open.'),('D46','Conversion control date and reporting perimeter dependencies','conversion-control-scope-20261026/result.md',['W05','W06','W07','W08','W16','W17','MC17','MC19','MC20','MC24','MC25','MC28','MC30','MC33','MC34','MC35'],'Seven official primary PDFs and four index pages; 21 conditional cases, 12 refusal controls, 186 assertions. Control may precede conversion; separate/consolidated and business/asset routes remain distinct. All accounting/posting admission withheld. Complete future edition/entity chain and acquisition-period integration remain open.'),('D47','Policy and conversion-scope arguments integrated in both editions','policy-control-integration-20261026/result.md',['W17','MC11','MC12','MC17','MC19','MC20','MC24','MC25','MC26','MC28','MC30','MC33','MC34'],'Version 5.24 preserves all 249 predecessor sources under six named transformations and 178 evidence files. Two complete builds, exact source verification and rendered review retain all equations/citations. Independent reader/domain acceptance remains pending.')]
for ident,title,path,req,desc in entries:
 p=H.parent/path;a['successor_deltas'].append(dict(id=ident,title=title,requirements=req,evidence=str(p.relative_to(R)),sha256=sha(p),current_disposition=desc))
put('audit-status.json',a)
f=read(OLD/'failure-register.json');fo=copy.deepcopy(f)
new=[('An observation label sampled at one witness is applied to an entire region','W03 W04 W16','Split pre-payment cash coverage with exact complementary predicates and certify whole-atom trigger/rate signals.','Selected whole-region refinements checked; general observation maps remain open','certified-observation-policy-20261026/result.md'),('A feasible action for each world is incorrectly called a policy','W03 W04 W05 W16','Intersect allowed actions across indistinguishable histories and compare complete reachable policies with independent forbidden-pair constraints.','Selected successor of X36 checked; actual actor source binding remains open','certified-observation-policy-20261026/result.md'),('Legal conversion date or majority fraction is substituted for accounting control assessment','W06 W07 W08 W16','Preserve substantive potential rights, contingent relevant activities, before/after control and separate acquisition date.','Conditional dependencies checked; actual rights and dated applicability open','conversion-control-scope-20261026/result.md'),('A mid-period acquisition is passed through an unchanged-perimeter report','W07 W08 W12 W16','Distinguish pre-control period, acquisition measurements, post-control results and NCI; require a new compatible continuation.','New integration obligation; current same-perimeter interface cannot establish this','conversion-control-scope-20261026/result.md'),('A chosen cost policy or financing price fills missing acquisition measurement','W06 W07 W08 W16','Keep separate/consolidated and business/asset alternatives; require transaction-specific measurements and entity/edition support.','Unknown-preserving dependency checks pass; no accounting posting admitted','conversion-control-scope-20261026/result.md')]
for i,(failure,packages,case,status,evidence) in enumerate(new,37):f['cross_interface'].append(dict(id='X'+str(i),failure=failure,closure_packages=packages.split(),discriminating_case=case,status=status,evidence='data/accounting-master/'+evidence))
put('failure-register.json',f)
p=read(OLD/'closure-packages.json');po=copy.deepcopy(p)
support={
'W03':'The selected certified observation policies now agree across two complete formulations and the frozen reference; no probabilities or actual access facts are supplied.',
'W04':'All selected regions are now refined by certified observations; robust reachable policy sets agree in all eight supplied problems.',
'W05':'Policy infeasibility now separates insufficient information, missing facility rights and repayment shortfall. Conversion control is assessed separately from legal share issuance.',
'W06':'Primary control/scope paragraphs and 21 conditional cases distinguish economic control assumptions, accounting control dates, reporting scope and missing measurement.',
'W07':'Inspected AASB 10/127/3 and amendment instruments supply conditional paragraph support; all cases withhold actual accounting and posting admission.',
'W08':'A mid-period control acquisition is identified as incompatible with the existing unchanged-opening/closing-perimeter group report. Business/asset, investment-entity and NCI questions remain separate.',
'W11':'Two independent policy formulations compose certified financial leaves with supplied observation cells; no new general language/unknown-value theorem is inferred.',
'W12':'Observation refinement and reachable-history decisions preserve remembered first actions; immutable source/actor-view binding and selective invalidation remain a distinct next unit.',
'W16':'Complete eight-problem policy comparisons and 21 accounting dependency cases add specific counterexamples with nine and twelve refusal controls respectively.',
'W17':'Both selected arguments and seven exact primary references are integrated in protected Version 5.24 with source/evidence locks and rendered author review.'}
nexts={
'W03':'Execute certified-source-views plan: bind source revision, actor availability and observation certificates without importing invented priors or changing earlier knowledge.',
'W04':'Preserve checked policy sets while binding source dependencies; extend dimensions, horizons and nonlinear domains only with new proofs or explicit approximation bounds.',
'W05':'Compose source-bound policy choices with independently admitted financing terms and measurements; preserve persistent rights, repayment and refusal histories.',
'W06':'Execute acquisition-period-authority plan: complete dated entity/edition dependencies and separate control assessment from conversion and valuation.',
'W07':'Finish dated acquisition authority and measurement requirements, alongside mixed-promise/calendar/tax/costing residuals; keep original corporate cases.',
'W08':'Specify acquisition-period continuation over existing group interfaces with NCI, prior interests and intragroup eliminations; retain heterogeneous-origin/EPS and hedge/currency residuals.',
'W11':'Audit source-binding APIs before adding policy dependency records; extend unsupported syntax/types/unknown values only under independent evidence.',
'W12':'Bind immutable source and actor views with precise dependency invalidation; durable restart, authenticated storage and migration remain separate.',
'W16':'Test changed, future, unknown and conflicting source/access cases against complete policy problems; separately test acquisition-perimeter refusal and conditional reporting.',
'W17':'Integrate future source-view and acquisition-period findings; continue whole-document consistency and independent reader/domain acceptance.'}
for row in p['packages']:
 if row['id'] in support:row['existing_support']+=' '+support[row['id']];row['next_action']=nexts[row['id']]
 assert row['status']=='open'
put('closure-packages.json',p)
program='# Full closure program after certified policies and conversion scope\n\n26 October 2026. All 18 broad packages remain open. Every inherited obligation, literature record and failure remains preserved. New evidence is scoped, not a new exhaustive audit.\n'
for row in p['packages']:
 program+='\n## '+row['id']+' — '+row['title']+'\n\n'
 for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
  value=row[key];program+=label+': '+(', '.join(value) or 'none' if isinstance(value,list) else value)+'\n\n'
(G/'closure-program.md').write_text(program)
remaining='# Complete remaining-work queue\n\nThe selected financial-region and observation-policy comparison is complete. Actual source/actor binding, dated accounting authority, acquisition-period integration, general domains and durable recovery remain open. All 18 packages continue.\n\n'
remaining+='\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in p['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. No global continuation veto has fired. No fees, outreach, installations, publication or independent acceptance is implied.\n'
(G/'remaining-work.md').write_text(remaining)
(G/'plan-review.md').write_text('Skeptical audit passes with exact predecessor preservation and separately scoped claims. Eight policy comparisons preserve physical worlds; a policy count is not optimality or probability. Primary-source scope checks are not actual accounting admission. Source access, ingestion, review and effective time remain distinct. Majority votes do not set control date. Existing unchanged-perimeter reports cannot represent mid-period acquisition. Page counts and builds are documentary diagnostics, not whole-program acceptance. Current master and all legacy controller fields are preserved except explicitly advanced current routes.\n')
counts=dict(read(OLD/'verification.json')['counts']);counts.update(successor_deltas=47,cross_interface_challenges=41)
assert a['groups']==original['groups'] and a['literature']==original['literature'] and a['successor_deltas'][:44]==original['successor_deltas']
assert all(f[k]==fo[k] for k in ['original','literature_extensions']) and f['cross_interface'][:36]==fo['cross_interface']
assert [r['id'] for r in p['packages']]==[r['id'] for r in po['packages']]
for r,old in zip(p['packages'],po['packages']):assert all(r[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
for n,h in lock.items():assert sha(R/n)==h
for row in a['successor_deltas'][44:]:assert sha(R/row['evidence'])==row['sha256']
put('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0,scope='Trace reconciliation with scoped policy/control findings; no broad completeness claim'))
(G/'result.md').write_text('# Additive full-program refresh\n\n26 October 2026. Version 5.24 integrates certified observation policies and conditional conversion control/reporting scope. All 53 obligations, six interactions, 46 operations, nine literature gaps, 67 original failures and 48 literature extensions remain byte-equivalent as data. D45–D47 and X37–X41 bring the successor totals to 47 deltas and 41 cross-interface challenges. All 18 packages remain open. The exact selected policy sets and conditional dependencies are accepted only within their supplied scopes; source/actor binding and acquisition-period authority continue next.\n\nChecks preserve the predecessor gap files, complete inherited rows, package identities/dependencies/requirements and all legacy limits. No original requirement or human/domain acceptance closes.\n')
print(json.dumps({'status':'PASS','counts':counts,'predecessor_files':len(lock)}))
