"""Refresh the 53-row author assessment after Versions 2.70–2.72."""
import copy,hashlib,json,subprocess
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
assert not (U/'completion.json').exists(),'Completed assessment; preserve it'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());old=json.loads((R/b['prior_assessment']['path']).read_text());d=copy.deepcopy(old)
B=Path('docs/design/proposal/manuscript-arelle-inline-values-20261013');C=Path(b['candidate']);checks={}
checks['prior_assessment']=sha(R/b['prior_assessment']['path'])==b['prior_assessment']['sha256']
source_files={s['path'] for r in old['requirements'] for s in r['current_sources']}
comparison=[]
for p in sorted(source_files):
 rel=Path(p).relative_to(B);q=C/rel;equal=sha(R/p)==sha(R/q)
 comparison.append({'old_path':p,'old_sha256':sha(R/p),'new_path':str(q),'new_sha256':sha(R/q),'equal':equal,'review_basis':'Prior judgment carried by exact bytes' if equal else 'V2.70–2.72 scoped integration/source checks plus author review of changed input'})
fresh=['chapters/03-literature.tex','chapters/11-contracts.tex','sections/apple-inline-occurrences.tex','sections/certain-answer-semantics.tex','references.bib']
for rel in fresh:
 q=C/rel
 comparison.append({'old_path':str(B/rel) if (R/B/rel).is_file() else None,'old_sha256':sha(R/B/rel) if (R/B/rel).is_file() else None,'new_path':str(q),'new_sha256':sha(R/q),'equal':(R/B/rel).is_file() and sha(R/B/rel)==sha(R/q),'review_basis':'New or changed transitive source reviewed under scoped integration'})
comp={x['old_path']:x for x in comparison if x['old_path']};save('source-comparison.json',comparison)
EVIDENCE={
 'apple-inline-occurrences':('data/accounting-master/apple-inline-occurrences-20261013/result.md','Scoped cross-filing occurrence evidence; no generic adapter/runtime acceptance'),
 'certain-answer-semantics':('data/accounting-master/certain-answer-semantics-20261013/result.md','Constructed answer-family and Boolean semantics; no issuer or runtime evidence'),
 'certain-answers-proof-source':('data/accounting-master/certain-answers-proof-source-20261013/result.md','Inspected primary proof and version-qualified input/output semantics; no financial theorem transfer')}
for k,(p,role) in EVIDENCE.items():d['evidence'][k]={'path':p,'sha256':sha(R/p),'role':role}
updates={
 'MC01':('Version2.70 traces ten selected actual inline occurrences across annual/interim endpoints while preserving source/package limits.','Complete wider package, notes, incorporated material and chronology; selected occurrence joins do not close whole-report coverage.'),
 'MC02':('The occurrence trace and query-semantic repair preserve context/unit/accuracy, shared values, answer-family meaning and output scope.','Validate broader actual contexts and typed exchanges; a local proof and selected facts do not establish complete numeric semantics.'),
 'MC03':('Version2.70 distinguishes a converted annual presentation from an actual inline endpoint and repairs the extraction scope.','Continue chronology, publication and source-availability closure; cross-filing comparison is not same-filing extraction.'),
 'MC07':('Actual occurrence counterparts and the certainty example keep repeated equity rows and alternative answer schedules distinct.','Adjudicate wider mappings and populations; no generic grouping/completeness follows.'),
 'MC08':('The2.71 example and2.72 proof audit distinguish shared unknowns, Boolean universal truth, certain rows and answer families.','Extend semantic validation to the supported language and actual records; general theorem hypotheses are not established for every financial output.'),
 'MC09':('The query contract now requires full-family proof coverage and preserves sampled/unresolved scope.','Implement template generation, coverage and search completeness; local finite enumeration is not a general reconstruction algorithm.'),
 'MC10':('The repair keeps factual alternatives, output meanings and unsupported operations separate; primary proof assumptions are stated.','Continue category-specific admission and dependence checks across actual cases.'),
 'MC11':('Answer families remain linked to histories, preventing aggregation after tuple intersection from erasing economic memory.','Implement query-dependent sufficiency and broader state compression checks.'),
 'MC18':('The result contract distinguishes family answers, certain rows and Boolean statuses without vacuous truth on empty families.','Implement general result payloads and numerical/branch failure propagation.'),
 'MC26':('Version2.71 explicitly records model scope, nonempty family, proof coverage and omitted-row interpretation.','Complete source-to-history coverage evidence and review lifecycle.'),
 'MC29':('Full Libkin proof definitions and hypotheses are now inspected with version qualifications.','Inspect relevant competitor/extension sources and preserve blocked papers; no broad literature completion.'),
 'MC30':('The primary proof source is archived, hashed and technically read; exact KR/publisher equivalence remains unchecked.','Continue version/correction/omission and blocked-source work.'),
 'MC32':('Versions2.70–2.72 preserve prior displays/citations and add a reader-facing query distinction.','Human reconstruction and independent review remain pending.'),
 'MC33':('154 manuscript checks, source checks and nine final page inspections support this scoped evidence delta.','Independent domain/engineering acceptance and runtime conformance remain pending.'),
 'MC34':('The current candidate and controls now connect three scoped supplements while preserving the 53-row negative assessment.','Continue requirement interaction review and implementation staging.'),
 'MC35':('The proof source, local derivation and source receipts were completed internally before any outside review.','Continue feasible internal authority, source and implementation work without outreach or fees.') }
gap_updates={
 'G1':('Full-family query proof conditions are explicit, but actual disclosure-to-history construction and theorem domain conditions remain unspecified.','Implement bounded model coverage and retain witness-vs-completeness distinctions.'),
 'G3':('The proof source requires an abstract representation system; continuous nonlinear financial outputs remain outside that support.','Specify supported formula classes and unsupported-operation results.'),
 'G8':('One direct proof source is now inspected and version-qualified; broader competitors, proof predecessors and blocked papers remain.','Continue substantive backward/forward/version and omission screening.'),
 'G10':('The output contract and proof obligations are more determinate within scope; implementation and independent acceptance remain open.','Define executable conformance and workload evidence later.'),
 'G15':('Shared unknowns, Boolean certainty, certain rows and answer families now have separate semantics and scope.','Extend category/dependence admission across actual accounting cases.'),
 'G16':('Answer families retain history links and query-dependent aggregation limits are explicit.','Implement supported state resolutions and invalidation checks.'),
 'G17':('Source and proof receipts, version qualifications and evidence-delta controls preserve invalidation boundaries.','Complete independent adjudication and review workflow.'),
 'G18':('The 2.72 manifest and versioned source receipt preserve replay identity for the scoped document repair.','Implement runtime recovery and broader replay conformance.') }
for prev,row in zip(old['requirements'],d['requirements']):
 checks[row['id']+':obligation']=all(row[k]==prev[k] for k in ['id','requirement','acceptance_obligation','status','historical_status'])
 row['prior_assessment_text']=prev['current_assessment']
 row['current_sources']=[{'path':comp[s['path']]['new_path'],'sha256':comp[s['path']]['new_sha256'],'review_basis':comp[s['path']]['review_basis']} for s in prev['current_sources']]
 if row['id'] in updates:
  additions=[]
  if row['id'] in {'MC01','MC02','MC03','MC07','MC33'}:additions.append(C/'sections/apple-inline-occurrences.tex')
  if row['id'] in {'MC08','MC09','MC10','MC11','MC18','MC26','MC29','MC30','MC32','MC33','MC34','MC35'}:additions.append(C/'sections/certain-answer-semantics.tex')
  for p in additions:row['supplemental_evidence'].append({'path':str(p),'sha256':sha(R/p),'role':'Scoped new transitive section inspected in exact candidate integration'})
 if row['id'] in updates:
  row['current_assessment']=prev['current_assessment']+' '+updates[row['id']][0];row['remaining_work']=prev['remaining_work']+' '+updates[row['id']][1]
  row['review_basis']='Versions2.70–2.72 scoped evidence delta; acceptance unchanged'
 else: row['review_basis']='Prior disposition carried; changed transitive files checked separately; no new substantive evidence for this requirement'
 if row['id']=='MC15':
  row['current_assessment']='The retained Northstar and corporate-method sections specify collections, purchases/payments, inventory, payroll, PPE, financing, simplified tax, statements and annual/interim timing; Versions2.70–2.72 add no new general corporate operation or authority.'
  row['remaining_work']='Complete actual company operation facts and operative revenue, lease, tax, FX and asset methods; source-admitted whole-company path and runtime event/report conformance remain open.'
  row['review_basis']='Corrected prior disposition drift: cash-pair/bounds text belonged to joint-result evidence, not ordinary corporate operations; retained Section7.5 and corporate-methods reviewed'
 if row['id']=='MC26':
  row['current_assessment']=prev['current_assessment']+' The2.71 satisfiability explanation adds a logical proof obligation but no new numerical fragment or solver validation.'
  row['remaining_work']=prev['remaining_work']+' Specify and validate each supported solver/search capability and its failure behavior; no theorem transfers to arbitrary financial computation.'
 if row['id']=='MC31':
  row['remaining_work']='Resolve other proposed tool/interface/terms questions; actual cross-filing occurrence preservation is now delivered within scope, but pinned runtime compatibility and matched evaluation remain open.'
 if row['id']=='MC32':
  row['remaining_work']='Continue substantive source and method repairs; human reconstruction and independent domain/implementability acceptance remain pending.'
 if row['id']=='MC33':
  row['remaining_work']='Define and run eventual conformance and independent acceptance; counts and clean builds do not establish readiness.'
 if row['id']=='MC34':
  row['remaining_work']='Maintain dependencies and continue distinct ready E01/E05/E07/E08/E14 work; the actual occurrence inquiry and proof audit are complete within scope, and implementation remains held.'
 if row['id']=='MC35':
  row['remaining_work']='Continue feasible source, authority, software and document preparation internally; no outreach, fee or publication is authorised.'
for prev,row in zip(old['gaps'],d['gaps']):
 checks[row['id']+':obligation']=all(row[k]==prev[k] for k in ['id','title','original_obligation','status','historical_status'])
 row['prior_assessment_text']=prev['current_assessment']
 if row['id'] in gap_updates:
  row['current_assessment']=prev['current_assessment']+' '+gap_updates[row['id']][0];row['remaining_work']=prev['remaining_work']+' '+gap_updates[row['id']][1];row['review_basis']='Versions2.70–2.72 scoped evidence delta; no gap closure'
 else: row['review_basis']='Prior disposition carried; no new evidence'
 if row['id']=='G11':
  row['remaining_work']='Complete remaining narrative/reference/query dependencies and whole-package semantics; selected actual occurrences are now traced, but that does not establish broad completeness.'
 if row['id']=='G12':
  row['remaining_work']='Adjudicate broader concept mappings, partitions and population reconciliations; general composition conformance remains pending.'
 if row['id']=='G17':
  row['remaining_work']='Independent adjudication, actual applicability and eventual workflow conformance remain pending.'
 if row['id']=='G18':
  row['remaining_work']='Later crash/reopen/migration, event/stream identity and adapter recovery conformance remain; documentary preservation is not a working persistence engine.'
d.update(prior_assessment=b['prior_assessment'],candidate_version='2.72',candidate_pdf_sha256=b['candidate_pdf_sha256'],review_class='author evidence-delta reassessment; no independent acceptance',next_repair='Inspect the direct SQL/null-semantics competitor through the retained author link; preserve source, query-class and soundness limits.',next_plan='docs/plans/accounting-sql-three-valued-logic-20261013.md')
checks.update({'all35requirements':len(d['requirements'])==35,'all18gaps':len(d['gaps'])==18,'negative_readiness':not d['ready'] and d['status']=='not_ready' and not d['implementation_enabled'],'five_E_preserved':d['remaining_blockers']==['E01','E05','E07','E08','E14']})
for p,h in b['frozen'].items():checks['frozen:'+p]=sha(R/p)==h
for p,h in b['candidate_files'].items():checks['candidate:'+p]=sha(R/p)==h
for k,v in d['evidence'].items():checks['evidence:'+k]=sha(R/v['path'])==v['sha256']
for row in d['requirements']:
 for src in row['current_sources']:
  if isinstance(src,dict): checks['source:'+row['id']+':'+src['path']]=sha(R/src['path'])==src['sha256']
 for src in row['supplemental_evidence']:
  if isinstance(src,dict): checks['source:'+row['id']+':'+src['path']]=sha(R/src['path'])==src['sha256']
for unit,report in [('apple-inline-occurrences','manuscript-checks.json'),('certain-answer-semantics','manuscript-checks.json'),('certain-answers-proof-source','manuscript-checks.json')]:
 p=R/f'data/accounting-master/{unit}-20261013/{report}'
 checks['integration:'+unit]=not json.loads(p.read_text())['failed']
failed=[k for k,v in checks.items() if not v];save('assessment.json',d)
lines=['# All requirement and gap dispositions after Version2.72','','Author evidence-delta review; not_ready. Original acceptance wording/statuses preserved.','','| Requirement | Status | Current evidence | Remaining work |','|---|---|---|---|']
for r in d['requirements']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
lines+=['','| Gap | Status | Current evidence | Remaining work |','|---|---|---|---|']
for r in d['gaps']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
(U/'dispositions.md').write_text('\n'.join(lines)+'\n')
save('integrity-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed,'updated_requirements':len(updates),'updated_gaps':len(gap_updates),'compared_files':len(comparison),'unchanged_files':sum(p['equal'] for p in comparison)})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'requirements':35,'gaps':18,'candidate_version':'2.72'}));raise SystemExit(bool(failed))
