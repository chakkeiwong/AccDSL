"""Refresh all53 dispositions with source deltas; preserve acceptance and status."""
import copy,hashlib,json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
assert not (U/'completion.json').exists(),'Completed assessment; preserve it'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());old=json.loads((R/b['prior_assessment']['path']).read_text());d=copy.deepcopy(old)
B=Path('docs/design/proposal/manuscript-apple-award-versions-20261013');C=Path(b['candidate'])
checks={'prior_assessment':sha(R/b['prior_assessment']['path'])==b['prior_assessment']['sha256']}
files={s['path'] for r in old['requirements'] for s in r['current_sources']}
files.update(str(B/x) for x in ['sections/adapter-methods.tex','references.bib','accounting-product-proposal.tex'])
comparison=[]
for p in sorted(files):
    rel=Path(p).relative_to(B);q=C/rel;equal=sha(R/p)==sha(R/q)
    comparison.append({'old_path':p,'old_sha256':sha(R/p),'new_path':str(q),'new_sha256':sha(R/q),'equal':equal,'review_basis':'Prior judgment carried by exact bytes' if equal else 'V2.68/2.69 exact preservation checks and author inspection bind version/additive section inputs/bibliography'})
comp={x['old_path']:x for x in comparison};save('source-comparison.json',comparison)
units=['arelle-fact-identity','arelle-inline-values']
for unit in units:
    p=f'data/accounting-master/{unit}-20261013/result.md';d['evidence'][unit]={'path':p,'sha256':sha(R/p),'role':'Pinned static interface evidence and constructed witnesses; no runtime or accounting acceptance'}
updates={
 'MC02':('Pinned value/format/scale/sign/precision/nil paths are distinguished; constructed exact witnesses expose double transformation and binary-float identity loss.','Validate actual facts and proposed exchange later; retain original bytes, typed values, source accuracy and validation state rather than promote helper output.'),
 'MC03':('Source text assembly now explicitly retains exclusions and continuation outcomes; nonempty partial text does not establish a complete narrative.','Complete material narrative/reference translation and actual continuation tracing; rawValue alone cannot establish source completeness.'),
 'MC04':('Raw bytes, assembled readings, typed values, diagnostics and constructed examples are separated; no source-only inquiry is called an executed parser test.','Admit actual mappings and preserve independent adjudication; checked static behavior is not an issuer-error finding.'),
 'MC07':('Aspect matching, value comparisons, complete-subset reduction and set consistency use different conditions; optional query views retain source members.','Validate actual concept/context/unit equality and grouping decisions; equality or precision does not justify silently discarding occurrences.'),
 'MC25':('The proposed interface now specifies pre-reduction copying, operation/options provenance, transform order and continuation/error retention.','Implement and test exchange, crash/reopen/migration and adapter lifecycle later; no runtime authority follows from source inspection.'),
 'MC27':('Occurrence memberships and conflicting precise values remain reviewable rather than being erased by a convenient reduction.','Independent/human adjudication and actual workflow execution remain pending; hypothetical comparisons are not issuer acceptance.'),
 'MC30':('Six new official helper responses and retained exact sources support line-bound pinned interface findings; receipts, failures and source limits remain traceable.','Four foundational texts, operative authority and wider source/version/omission work remain; no source-only technical audit closes those obligations.'),
 'MC31':('Pinned Arelle equality, reduction, inline text and transformation boundaries are now inspected in addition to existing cache/controller/Docling work.','Finish remaining proposed tool/interface/terms questions and actual-filing preservation examples; later pinned runtime compatibility and matched evaluation remain separate.'),
 'MC32':('Version2.69 teaches value construction before equality and preserves every prior passage/display/citation with six final images per integration.','Continue substantive preparation and coherent repair; human reconstruction, independent domain and implementability acceptance remain pending.'),
 'MC33':('Static source checks and exact constructed arithmetic are explicitly distinct from runtime/schema/accounting validity and scientific performance.','Independent acceptance and eventual conformance remain; counts and clean builds cannot establish readiness.'),
 'MC34':('All53 obligations are refreshed after the two adapter integrations; changed source inputs and transitive additions receive explicit scoped dispositions.','Continue a distinct actual source-occurrence inquiry; prevent completed-method replay and keep the held implementation boundary explicit.'),
 'MC35':('Feasible pinned source research and proposed exchange consequences are prepared internally before any outside review.','Continue actual-source and authority work internally; no outreach, fees or publication are authorized.')}
gapupdates={
 'G2':('Value/type/precision, raw/transformed text and invalid/nil boundaries are now source-grounded.','Legacy Core0 and later general conformance limits remain; source-only helpers do not admit actual facts.'),
 'G9':('Arelle transform/equality/reduction paths have explicit pinned source consequences and preservation requirements.','Other tool/version/terms questions and later runtime/empirical comparison remain; no universal parser ranking.'),
 'G11':('Excluded and continued narrative text can differ from a nonempty assembled reading; original fragments and unresolved chain diagnostics are required.','Trace material actual source occurrences and remaining package/reference meanings; static paths are not whole-package closure.'),
 'G12':('Concept/context/unit/language grouping remains distinct from values and source occurrences; set consistency differs from pair consistency.','Adjudicate actual mappings and populations, and later composition conformance.'),
 'G17':('Conflicting precise observations and original members remain available for review even when a reduced query view is formed.','Independent adjudication, actual applicability and workflow conformance remain pending.'),
 'G18':('The source-preserving exchange now specifies capture before destructive export and before source-spelling loss.','Crash/reopen/migration and adapter recovery conformance remain held implementation evidence.')}
newsections=[C/'sections/arelle-fact-identity.tex',C/'sections/arelle-inline-values.tex']
for previous,row in zip(old['requirements'],d['requirements']):
    checks[row['id']+':obligation']=all(row[k]==previous[k] for k in ['id','requirement','acceptance_obligation','status','historical_status'])
    row['prior_assessment_text']=previous['current_assessment']
    row['current_sources']=[{'path':comp[x['path']]['new_path'],'sha256':comp[x['path']]['new_sha256'],'review_basis':comp[x['path']]['review_basis']} for x in previous['current_sources']]
    if row['id'] in updates:
        row['current_assessment']=previous['current_assessment']+' '+updates[row['id']][0]
        row['remaining_work']=previous['remaining_work']+' '+updates[row['id']][1]
        row['review_basis']='New scoped adapter source evidence plus explicitly carried earlier judgment; acceptance unchanged'
        row['supplemental_evidence']+= [{'path':str(p),'sha256':sha(R/p),'role':'New transitive source-grounded section inspected through checked integration'} for p in newsections]
    else:row['review_basis']='Prior disposition carried; no new substantive evidence on this requirement'
for previous,row in zip(old['gaps'],d['gaps']):
    checks[row['id']+':obligation']=all(row[k]==previous[k] for k in ['id','title','original_obligation','status','historical_status'])
    row['prior_assessment_text']=previous['current_assessment']
    if row['id'] in gapupdates:
        row['current_assessment']=previous['current_assessment']+' '+gapupdates[row['id']][0]
        row['remaining_work']=previous['remaining_work']+' '+gapupdates[row['id']][1]
        row['review_basis']='Scoped interface preparation; no gap closure'
    else:row['review_basis']='Prior disposition carried; no new evidence on this gap'
d.update(candidate_version='2.69',candidate_pdf_sha256=b['candidate_pdf_sha256'],prior_assessment=b['prior_assessment'],review_class='author evidence-delta reassessment; no independent acceptance',next_repair='Trace selected actual Apple inline numeric occurrences to retained instance counterparts with exact contexts/units/accuracy; no runtime adapter execution',next_plan='docs/plans/accounting-apple-inline-occurrences-20261013.md')
checks['all35requirements']=len(d['requirements'])==35;checks['all18gaps']=len(d['gaps'])==18
checks['negative_readiness']=not d['ready'] and d['status']=='not_ready' and not d['implementation_enabled']
checks['five_E_preserved']=d['remaining_blockers']==['E01','E05','E07','E08','E14']
for group in ['frozen','candidate_files']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
for k,x in d['evidence'].items():checks['evidence:'+k]=sha(R/x['path'])==x['sha256']
for unit in units:
    for name in ['source-arithmetic-checks','manuscript-checks','closeout-checks']:
        a=json.loads((R/f'data/accounting-master/{unit}-20261013/{name}.json').read_text());checks[unit+':'+name]=not a['failed']
checks['prior_contract_sources_remain']=all((R/s['path']).is_file() and sha(R/s['path'])==s['sha256'] for r in d['requirements'] for s in r['current_sources'])
save('assessment.json',d)
lines=['# All requirement and gap dispositions after Version2.69','','Author delta review; not_ready. Original acceptance wording/statuses preserved. Unchanged judgments carried by source hash.','','| Requirement | Status | Current evidence | Remaining work |','|---|---|---|---|']
for r in d['requirements']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
lines+=['','| Gap | Status | Current evidence | Remaining work |','|---|---|---|---|']
for r in d['gaps']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
(U/'dispositions.md').write_text('\n'.join(lines)+'\n')
failed=[k for k,v in checks.items() if not v];result={'checks':checks,'passed':sum(checks.values()),'failed':failed,'updated_requirements':len(updates),'updated_gaps':len(gapupdates),'compared_files':len(comparison),'unchanged_files':sum(x['equal'] for x in comparison)};save('integrity-checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='checks'}));raise SystemExit(bool(failed))
