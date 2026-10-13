"""Update author dispositions without changing original acceptance obligations."""
import copy
import hashlib
import json
from pathlib import Path

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(UNIT/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((UNIT/'baseline.json').read_text())
old=json.loads((ROOT/b['prior_assessment']['path']).read_text())
d=copy.deepcopy(old);cand=Path(b['candidate'])
checks={'prior_assessment':sha(ROOT/b['prior_assessment']['path'])==b['prior_assessment']['sha256']}
d.update({'candidate_version':'2.64','candidate_pdf_sha256':b['candidate_pdf_sha256'],
          'review_class':'author delta reassessment; no independent acceptance',
          'prior_assessment':b['prior_assessment'],
          'next_repair':'Resolve distinct employee stock-plan source dependencies after the completed conditional company joins',
          'next_plan':'docs/plans/accounting-apple-stock-plan-source-20261013.md'})
units=['apple-statement-network','apple-interim-network','apple-history-compatibility',
       'apple-coupled-completion','apple-settlement-paths']
for unit in units:
    path='data/accounting-master/'+unit+'-20261013/result.md'
    d['evidence'][unit]={'path':path,'sha256':sha(ROOT/path),'role':'New scoped integration result; actual full-company admission unresolved'}
updates={
 'MC01':('Selected annual102-row and next-quarter100-row statement populations now join their endpoint and component relationships. Earlier package retention and narrative crosswalk evidence remains.',
         'Complete material meanings and external-reference/query dependencies across the declared package. Frozen40 unresolved exhibit targets and relevant recursion remain; actual histories and semantic closure are not established.'),
 'MC03':('Source notes constrain the conditional expense/liability repair; broad contingency, lease and liability descriptions are kept distinct from evidence of a particular event.',
         'Complete material narrative/qualification translations across the package; retained wording and selected mappings do not establish every economic event.'),
 'MC04':('Reported rows, exact illustrative centres, residual requirements and hypothesized events remain distinct. Actual source-reference conflict evidence is retained.',
         'Source-admit events and mappings before promoting conditional histories. Independent actual adjudication and wider conflict workflow acceptance remain pending.'),
 'MC07':('Annual and interim rows preserve units, dash/absence, operating/noncash and nested liability distinctions. Matching totals with different detailed-row assignments is explicitly rejected.',
         'Adjudicate actual mappings, partitions and context; prove equivalence only for the stated query and scope. General runtime mapping conformance remains later work.'),
 'MC08':('A fixed company remainder cannot accompany both PP&E histories. A conditional coupled transformation preserves annual rows only under joint mapping/tax assumptions; future cash alternatives retain branch identity.',
         'Admit actual event and classification facts and construct feasible full-company bases; conditional transformations and selected witnesses do not exhaust actual histories.'),
 'MC09':('Existing joint template construction is applied to scoped compatibility and repair conditions; necessary subtraction conditions are explicitly not candidate journal evidence.',
         'Expand source-supported templates and complete actual model coverage. General registry/solver execution and independent implementation remain later evidence.'),
 'MC10':('Unresolved actual obligations, inherited asset hypotheses, conditional reporting maps and counterexample failures have separate dispositions.',
         'Acquire actual facts and operative authority; no unsupported treatment becomes admissible because it balances or fits reported totals.'),
 'MC11':('Settlement examples prove that aggregate liability3082 preserves only the final undiscounted-total query within scope. Cash categories and timing require liability kind, terms and shared branch.',
         'Bind actual dates and asset/tax/cohort state for broader queries; no general equivalence algorithm or empirical approximation guarantee is established.'),
 'MC13':('Conditional settlement journals debit previously recognised liabilities and credit cash; all five scoped statement effects reconcile without new expense or invented financing.',
         'Supply actual contracts, obligations and behaviour facts before real-book admission; transactional conformance remains in the held implementation stage.'),
 'MC14':('Common-date, capital-first and expense-first settlements are explicit ex post scenarios with no probabilities or historical information claim.',
         'Bind actual scenarios to permitted information and causal/behavioural assumptions; runtime information and intervention conformance remains separate.'),
 'MC15':('Joint cash pairs reject independently selected marginal extrema; category/timing queries retain the producing history.',
         'Implement typed query/result and failure behaviour later, with supported model scope and bound certification. No exact whole-company bounds are established.'),
 'MC16':('The five selected annual statements and next-quarter statements now join; scoped alternative journals, detailed cash rows and subsequent settlements are checked.',
         'Complete material note dependencies and source-admitted whole-company histories. Actual quarterly residuals remain unexplained; later report-engine conformance is separate.'),
 'MC18':('Conditional differences show why equal historical aggregates can give different cash paths; no probability or forecast accuracy follows.',
         'Complete actual state and structural assumptions before company forecasts; target-specific inference/calibration and uncertainty evidence remain separately required.'),
 'MC28':('The real annual/interim statement network is connected to existing asset hypotheses, fixed-remainder rejection, conditional repair and joint settlement paths.',
         'Resolve external package, actual obligation/tax/classification/settlement and cohort facts; construct full admissible company histories and affected future outputs without inventing residual events.'),
 'MC32':('Five material integrations throughVersion2.64 preserve earlier mathematics and citations and include scoped final-page reviews.',
         'Continue source/method repairs and coherent integration; independent human comprehension, domain and implementability acceptance remain pending.'),
 'MC33':('Hard mathematical/source vetoes, conditional transformation evidence and actual accounting admission are separated. Candidate failures trigger specified repairs.',
         'Complete independent acceptance and later executable conformance; author arithmetic and clean builds do not establish scientific forecast validity.'),
 'MC34':('This53-row refresh replaces stale statement-join scheduling with the completed V2.60–2.64 evidence while preserving every original obligation.',
         'Maintain interactions and source dependencies; choose distinct ready work rather than indefinitely append unresolved conditional examples.'),
 'MC35':('Statement/source/arithmetic, conditional history and settlement preparation completed internally; no paid engagement or outreach.',
         'Continue feasible source and fact preparation. Human review is pending acceptance, not a transfer of unfinished internal work.'),
}
new_sections=['sections/apple-statement-network.tex','sections/apple-interim-network.tex',
              'sections/apple-history-compatibility.tex','sections/apple-coupled-completion.tex',
              'sections/apple-settlement-paths.tex','sections/apple-operating-assets.tex']
comp={r['old_path']:r for r in json.loads((UNIT/'source-comparison.json').read_text())}
for oldrow,row in zip(old['requirements'],d['requirements']):
    rid=row['id']
    checks[rid+':obligation_preserved']=all(row[k]==oldrow[k] for k in ['id','requirement','acceptance_obligation','status','historical_status'])
    row['prior_assessment_text']=oldrow['current_assessment']
    row['current_sources']=[{'path':comp[s['path']]['new_path'],'sha256':comp[s['path']]['new_sha256'],
        'review_basis':'Prior judgment carried by exact source equality' if comp[s['path']]['equal'] else 'Scoped additive input/version change reviewed; prior content retained'} for s in oldrow['current_sources']]
    if rid in updates:
        row['current_assessment'],row['remaining_work']=updates[rid]
        row['review_basis']='New scoped source/method result review; prior acceptance unchanged'
        row['dependency']='Actual sources and economic premises -> admitted joint history -> query-specific state and consequences'
        row['supplemental_evidence']=list(row.get('supplemental_evidence',[]))+[
            {'path':str(cand/s),'sha256':sha(ROOT/cand/s),'role':'Transitive input and new conditional/statement argument'} for s in new_sections]
    else:
        row['review_basis']='Prior disposition carried; this unit supplies no new domain acceptance'
gap_updates={
 'G1':('The common-remainder rejection and conditional repair exercise joint history construction while separating required residuals from events.',
       'Admit actual templates/events and establish full-company feasibility and declared search coverage; no witness completeness claim.'),
 'G4':('Annual/interim statements and explicit conditional settlement journals connect selected corporate operations to all affected statements.',
       'Actual tax, contract, classification, cohort and settlement facts remain necessary; no full operating-company forecast.'),
 'G5':('Full selected Apple annual and next-quarter statement rows join, and conditional history/repair/path examples are delivered.',
       'Complete actual full-company feasible histories and material package/query dependencies; preserve external-reference and private-fact limits.'),
 'G6':('Joint conditional settlement alternatives remain unweighted; independent cash-flow extrema are rejected.',
       'Actual structural/information assumptions and target-specific calibration remain necessary for scientific forecasts.'),
 'G10':('Current author reassessment creditsV2.60–2.64 and preserves original negative readiness.',
        'Independent acceptance plus substantive source/method/real-case closure remains necessary; counts do not confer readiness.'),
 'G11':('Full statement populations and selected note-to-cash-flow dependencies are explicit; broad source meanings do not identify a new obligation.',
        'Complete declared material meanings, references and queries with actual evidence or typed unknowns.'),
 'G12':('Reported-category and noncash mapping counterexamples reveal mismatches concealed by matched totals.',
        'Adjudicate mappings and partitions using source/authority; later composition conformance remains open.'),
 'G14':('Settlement timing scenarios explicitly avoid an as-of historical forecast or probability claim.',
        'Bind actual information and structural assumptions before empirical forecasting and intervention interpretation.'),
 'G15':('Counterexample rejection, conditional mapping equality and actual-history admission have distinct outcomes.',
        'Supply actual economic premises and authority; residuals and balancing do not admit events.'),
 'G16':('Identical aggregate liabilities fail cash-category and interim-date queries; final undiscounted cash agrees only in the fixed scope.',
        'Preserve actual contract/cohort/tax memory and recheck sufficiency as query/horizon/scenario changes.'),
}
for a,r in zip(old['gaps'],d['gaps']):
    checks[r['id']+':obligation_preserved']=all(r[k]==a[k] for k in ['id','title','original_obligation','status','historical_status'])
    r['prior_assessment_text']=a['current_assessment']
    if r['id'] in gap_updates:
        r['current_assessment'],r['remaining_work']=gap_updates[r['id']]
        r['review_basis']='New scoped integrated-case evidence; no independent acceptance'
    else:r['review_basis']='Prior disposition carried; no new gap closure'
checks['35_requirements']=len(d['requirements'])==35
checks['18_gaps']=len(d['gaps'])==18
checks['readiness_negative']=not d['ready'] and d['status']=='not_ready'
for path,digest in b['frozen'].items():checks['frozen:'+path]=sha(ROOT/path)==digest
for path,digest in b['candidate_files'].items():checks['candidate:'+path]=sha(ROOT/path)==digest
for key,e in d['evidence'].items():checks['evidence:'+key]=sha(ROOT/e['path'])==e['sha256']
frontier_path='docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
frontier=json.loads((ROOT/frontier_path).read_text())
counts={}
for r in frontier['reference_frontier']:counts[r['document_status']]=counts.get(r['document_status'],0)+1
checks['frozen_frontier70']=len(frontier['reference_frontier'])==70
checks['frozen_unresolved40']=counts['unresolved_target']==40
save('reference-frontier-check.json',{'path':frontier_path,'sha256':sha(ROOT/frontier_path),'counts':counts,'scope':'Frozen20261007 dispositions, not a new exhaustive source acquisition or semantic acceptance','selected_target':next(r for r in frontier['reference_frontier'] if r['id']=='annual.exhibit.10.13')})
save('assessment.json',d)
lines=['# Requirement dispositions after Version2.64','','Author delta assessment; readiness **not_ready**. All original obligations are retained in assessment.json. Twenty-one unchanged manuscript sources carry prior judgments; new transitive inputs are credited separately.','','| Requirement | Status | Current evidence | Remaining acceptance work |','| --- | --- | --- | --- |']
for r in d['requirements']:lines.append('| '+' | '.join([r['id'],r['status'],r['current_assessment'],r['remaining_work']])+' |')
lines+=['','| Gap | Status | Current evidence | Remaining work |','| --- | --- | --- | --- |']
for r in d['gaps']:lines.append('| '+' | '.join([r['id'],r['status'],r['current_assessment'],r['remaining_work']])+' |')
(UNIT/'dispositions.md').write_text('\n'.join(lines)+'\n')
failed=[k for k,v in checks.items() if not v];save('integrity-checks.json',{'passed':sum(checks.values()),'failed':failed,'checks':checks})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'updated_requirements':len(updates),'updated_gaps':len(gap_updates),'ready':d['ready']}))
raise SystemExit(bool(failed))
