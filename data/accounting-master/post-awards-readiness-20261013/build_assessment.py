"""Refresh all53 author dispositions, preserving every original obligation."""
import copy,hashlib,json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed assessment.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());old=json.loads((R/b['prior_assessment']['path']).read_text());d=copy.deepcopy(old)
C=Path(b['candidate']);B=Path('docs/design/proposal/manuscript-apple-settlement-paths-20261013')
checks={'prior_assessment':sha(R/b['prior_assessment']['path'])==b['prior_assessment']['sha256']}
files={s['path'] for r in old['requirements'] for s in r['current_sources']}
files.update(str(B/p) for p in ['chapters/14-financing-groups.tex','sections/apple-eps-ownership.tex','references.bib'])
comparison=[]
for p in sorted(files):
    rel=Path(p).relative_to(B);new=C/rel;equal=sha(R/p)==sha(R/new)
    comparison.append({'old_path':p,'old_sha256':sha(R/p),'new_path':str(new),'new_sha256':sha(R/new),'equal':equal,
      'review_basis':'Prior judgment carried by exact bytes' if equal else 'V2.65–2.67 preservation checks bind declared version/input/prose-scope/bibliography changes'})
comp={x['old_path']:x for x in comparison}
save('source-comparison.json',comparison)
d.update({'candidate_version':'2.67','candidate_pdf_sha256':b['candidate_pdf_sha256'],'prior_assessment':b['prior_assessment'],
 'review_class':'author evidence-delta reassessment; no independent acceptance',
 'next_repair':'Inspect pinned Arelle fact equality and occurrence preservation after completing the bounded award chain',
 'next_plan':'docs/plans/accounting-arelle-fact-identity-20261013.md'})
units=['apple-stock-plan-source','apple-performance-award','apple-award-versions']
for unit in units:
    p=f'data/accounting-master/{unit}-20261013/result.md'
    d['evidence'][unit]={'path':p,'sha256':sha(R/p),'role':'New bounded source/contract consequence; actual-grant and full-company admission unresolved'}
updates={
 'MC01':('Three originally unresolved stock-plan references now have retained counterparts; three already located award forms receive selected substantive inspection. Selected statement joins remain delivered.',
          'Complete material meanings, recursive references and queries. Frozen40 labels remain; three supplemental counterparts leave37 without one in that inquiry. Document identity does not establish semantic closure or actual histories.'),
 'MC03':('Selected plan capacity, settlement, performance and versioned survival clauses now produce explicit conditional consequences; blank notices and source qualifications remain visible.',
          'Translate remaining material narrative, amendments, grant terms and other package dependencies. Selected clauses are not exhaustive legal or semantic review.'),
 'MC04':('Reported schedules, blank forms, hypothetical examples and actual-grant unknowns remain distinct. Proxy accelerated wording and form Vesting-Date wording are preserved without declaring a same-award conflict.',
          'Resolve consequential applicability with actual agreements/decisions before admission; maintain independent adjudication and wider review obligations.'),
 'MC05':('Board adoption, shareholder approval, source version, Award Date, performance period, vesting and delivery are distinguished in actual source examples.',
          'Exact historical-byte availability and timezones/cutoffs remain unresolved. Filing/version dates cannot become actual grant facts or retroactive amendments.'),
 'MC07':('Reserve shares, shares underlying awards, target/vested units, net delivery and dividend-equivalent cash retain distinct units and populations.',
          'Adjudicate remaining mappings/partitions and precision; similar labels or net quantities do not prove equivalence. General conformance remains later implementation evidence.'),
 'MC08':('Conditional award branches retain agreement version, performance, absolute-return sign and service eligibility jointly; threshold examples preserve discrete outcomes.',
          'Actual grants, economic events and full-company feasible histories remain unadmitted; illustrative branches do not establish coverage or probabilities.'),
 'MC10':('Unknown rank conventions, blank grant notices, Committee decisions and source applicability remain separate from deterministic contract consequences.',
          'Obtain necessary operative facts/authority; neither fitted totals nor a matching form title admits an actual treatment or event.'),
 'MC11':('Equal net delivery can consume different plan capacity; equal targets and performance can yield different surviving rights under general and CEO forms.',
          'Bind actual versions/dates/service/tax state for the intended query. No general state-equivalence algorithm or approximation guarantee is established.'),
 'MC17':('Equity lifecycle now includes selected actual plan/award terms, capacity recycling, performance caps, survival and later cash/share delivery, with checked conditional examples.',
          'Actual agreements/amendments, rank and general return conventions, tax/expense/EPS and other financing methods remain. Current indentures and wider options/hedges/benchmark methods are not closed.'),
 'MC27':('Actual source-reference review remains delivered; award-form/proxy wording adds a precise version/applicability distinction without a false accounting-conflict verdict.',
          'Independent/human adjudication and eventual workflow conformance remain pending; public clauses do not identify an executed award.'),
 'MC28':('The connected Apple case now carries selected disclosed equity terms into conditional units, reserve usage and cash/share timing, alongside earlier annual/interim history examples.',
          'Complete source-admitted company histories and all material package/authority dependencies; private transaction and grant facts remain unknown.'),
 'MC30':('The adopted-plan filing and selected retained award/proxy clauses add inspected source support, with exact source identities and limitations.',
          'Four foundational full texts, current accounting authority and wider source/version/omission checks remain; contract inspection does not supply accounting law or literature closure.'),
 'MC32':('V2.65–2.67 add a continuous plan-to-performance-to-applicability explanation with checked examples, preserved prior content and inspected final pages.',
          'Continue coherent repair and substantive source/method work; independent comprehension, domain and implementability acceptance remain pending.'),
 'MC33':('Source checks, exact arithmetic, preservation and visual checks are kept separate from legal/accounting validity, empirical forecasting and human acceptance.',
          'Independent acceptance and eventual conformance remain; no stochastic ranking or performance claim follows from counts/builds.'),
 'MC34':('All53 obligations are reassessed after the three award integrations. Acquisition versus substantive inspection and transitive manuscript additions are explicitly reconciled.',
          'Maintain dependencies and choose distinct ready work. Missing private facts are not a reason to append indefinitely many conditional grant examples.'),
 'MC35':('Public plan and retained award clauses were inspected and consequences checked before any external review question; no outreach or paid engagement occurred.',
          'Continue feasible independent source/interface work. Human/domain acceptance remains pending without transferring unfinished internal tasks.')}
newsections=['sections/apple-stock-plan.tex','sections/apple-performance-award.tex','sections/apple-award-versions.tex']
for a,r in zip(old['requirements'],d['requirements']):
    checks[r['id']+':obligation']=all(r[k]==a[k] for k in ['id','requirement','acceptance_obligation','status','historical_status'])
    r['prior_assessment_text']=a['current_assessment']
    r['current_sources']=[{'path':comp[x['path']]['new_path'],'sha256':comp[x['path']]['new_sha256'],'review_basis':comp[x['path']]['review_basis']} for x in a['current_sources']]
    if r['id'] in updates:
        r['current_assessment'],r['remaining_work']=updates[r['id']]
        r['review_basis']='New scoped source/contract evidence; acceptance unchanged'
        r['supplemental_evidence']=list(r.get('supplemental_evidence',[]))+[{'path':str(C/s),'sha256':sha(R/C/s),'role':'New transitive manuscript section reviewed through checked integration'} for s in newsections]
    else:r['review_basis']='Prior disposition carried; no new domain evidence from awards'
gapupdates={
 'G4':('Selected equity operations now connect plan reserve, performance, surviving rights and settlement to source versions and actual disclosure populations.', 'Actual grants/tax/expense and broader corporate operation authority remain necessary; no complete company forecast.'),
 'G5':('Three new exhibit counterparts and selected equity-clause consequences extend the connected Apple case.', 'Complete whole-package material meanings, actual histories and future outputs; three source acquisitions do not close the company case.'),
 'G7':('Equity contract examples are materially extended, while earlier banking/insurance preparation is preserved.', 'No new ASC/ASBE/IFRS authority is established by contract forms. Wider corporate, bank, insurance and actuarial methods remain.'),
 'G10':('All53 original obligations remain current after V2.65–2.67; readiness stays negative.', 'Independent acceptance and remaining substantive closures are required; arithmetic/build/source counts are not readiness.'),
 'G11':('Blank fields, distinct date roles and selected plan/award qualifiers now have explicit meanings or unknowns and checked consequences.', 'Complete remaining narrative/reference/query dependencies; selected operative clauses are not exhaustive semantic translation.'),
 'G12':('Plan reserve capacity, outstanding instruments and delivered shares show why superficially similar quantity labels cannot be combined.', 'Adjudicate broader concept mappings, partitions and context; actual population reconciliation and general composition conformance remain.'),
 'G13':('Actual plan/award dates distinguish approval, version, grant, performance, vesting and delivery; later terms do not automatically amend earlier awards.', 'Historical exact-byte availability and actual-grant applicability remain; no later evidence may silently enter earlier information sets.'),
 'G15':('Missing grants, rank convention and Committee decisions remain typed unknowns; conditional deterministic examples are not promoted into actual events.', 'Obtain facts/authority for actual admission and preserve uncertainty kinds; no arbitrary weights or interval filling.'),
 'G16':('Contract version and service state change surviving units/cash even with the same target and performance; net shares alone lose capacity information.', 'Bind actual state and recheck sufficiency for each query/horizon; no universal compression claim.'),
 'G17':('Source-version and proxy-summary differences are retained without inventing a same-award conflict or overwriting earlier evidence.', 'Independent adjudication, actual award applicability and later workflow conformance remain pending.')}
for a,r in zip(old['gaps'],d['gaps']):
    checks[r['id']+':obligation']=all(r[k]==a[k] for k in ['id','title','original_obligation','status','historical_status'])
    r['prior_assessment_text']=a['current_assessment']
    if r['id'] in gapupdates:r['current_assessment'],r['remaining_work']=gapupdates[r['id']];r['review_basis']='New bounded award-source evidence; no gap closure'
    else:r['review_basis']='Prior disposition carried; no new evidence on this gap'
checks['requirements35']=len(d['requirements'])==35;checks['gaps18']=len(d['gaps'])==18
checks['negative_readiness']=not d['ready'] and d['status']=='not_ready' and not d['implementation_enabled']
checks['five_E_preserved']=d['remaining_blockers']==['E01','E05','E07','E08','E14']
for p,h in b['frozen'].items():checks['frozen:'+p]=sha(R/p)==h
for p,h in b['candidate_files'].items():checks['candidate:'+p]=sha(R/p)==h
for k,x in d['evidence'].items():checks['evidence:'+k]=sha(R/x['path'])==x['sha256']
front=R/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json';f=json.loads(front.read_text())['reference_frontier']
supp=R/'data/accounting-master/apple-stock-plan-source-20261013/reference-supplement.json';s=json.loads(supp.read_text())
checks['frozen70']=len(f)==70;checks['frozen40']=sum(x['document_status']=='unresolved_target' for x in f)==40
checks['three_new']=len(s['dispositions'])==3 and {x['reference_id'] for x in s['dispositions']}=={'annual.exhibit.10.13','annual.exhibit.10.14','annual.exhibit.10.15'}
checks['remaining37']=s['residual_from_original_unresolved']==37
checks['three_previously_located']=all(next(x for x in f if x['id']==rid)['document_status']=='retained_target_located' for rid in ['annual.exhibit.10.18','annual.exhibit.10.20','annual.exhibit.10.22'])
save('reference-frontier-check.json',{'frozen_path':str(front.relative_to(R)),'frozen_sha256':sha(front),'rows':70,'unresolved':40,'supplement_path':str(supp.relative_to(R)),'supplement_sha256':sha(supp),'new_counterparts':3,'without_supplemental_counterpart':37,'previously_located_forms_now_inspected':3,'semantic_closure':False,'publication_counts':'Unchanged frozen56/136,35 supplements,101 without supplements'})
save('assessment.json',d)
lines=['# Requirement dispositions after Version2.67','','Author delta review; not_ready. All acceptance wording and statuses are preserved. Unchanged source judgments are carried, not independently re-reviewed.','','| Requirement | Status | Current evidence | Remaining work |','| --- | --- | --- | --- |']
for r in d['requirements']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
lines+=['','| Gap | Status | Current evidence | Remaining work |','| --- | --- | --- | --- |']
for r in d['gaps']:lines.append('| '+' | '.join(r[k] for k in ['id','status','current_assessment','remaining_work'])+' |')
(U/'dispositions.md').write_text('\n'.join(lines)+'\n')
failed=[k for k,x in checks.items() if not x];save('integrity-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed,'updated_requirements':len(updates),'updated_gaps':len(gapupdates),'compared_files':len(comparison),'unchanged_files':sum(x['equal'] for x in comparison)})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'updated_requirements':len(updates),'updated_gaps':len(gapupdates),'compared_files':len(comparison),'unchanged_files':sum(x['equal'] for x in comparison)}));raise SystemExit(bool(failed))
