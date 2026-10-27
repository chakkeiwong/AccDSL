"""Assemble the authored P19 assessment; does not promote or alter earlier phases."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/accounting-master/deliverables/P19'
DOC = ROOT / 'docs/design/proposal/readiness'
OUT.mkdir(exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)

def load(path):
    return json.loads((ROOT / path).read_text())

def ref(path, locator=None):
    row = {'path': path, 'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
    if locator:
        row['locator'] = locator
    return row

def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

# These are explicit author assessments, not statuses inferred from file counts.
# ID | status | candidate file | contract/evidence | remaining work
rows = '''
MC01|partial|chapters/02-history.tex|Three coverage populations, retained sources, reference traversal and exposed missing dependencies; Apple annual/interim units are inventoried.|Complete the real incorporated package and material assertion/query dispositions; 23 notes retain unresolved meaning.
MC02|specified|sections/portable-values.tex|Exact rational values and typed entity, perimeter, dimensions, unit, currency, basis, scale, sign and temporal context; incompatible operations reject.|Run independent implementation conformance later; preserve source-specific unknown precision and unadmitted contexts now.
MC03|partial|sections/source-admission.tex|Six located Apple policy translations distinguish reported assertions, proposed predicates, missing facts and invalid stronger readings.|Translate remaining material narratives and referenced qualifications in a complete real package.
MC04|partial|sections/source-admission.tex|Layer-specific review, extraction correction, alternatives, supersession and transitive invalidation preserve original claims.|Supply a qualifying real same-context source conflict; the seven-candidate search did not establish one.
MC05|specified|sections/source-admission.tex|Economic/reporting/public-availability/system times and explicit view/cutoff rules reject information that was not available.|Verify actual publication and byte-vintage evidence for historical evaluation; 136 panel dates remain unverified.
MC06|specified|sections/groups-fx-methods.tex|Dated control/perimeter, separate elimination books, goodwill/NCI, retained-control purchase, loss-of-control disposal and group translation are worked.|Acquire actual entity/control facts and source support for each broader exception before real operation admission.
MC07|specified|chapters/02-history.tex|Mapping applicability, measurement transformations, partition requirements and overlap rejection preserve company concepts.|Adjudicate actual company-extension mappings and exercise them in compatible implementations.
MC08|specified|chapters/05-mathematics.tex|Shared variables and joint constraints retain alternative histories across statements, periods and scenarios.|Expand declared templates with evidence; do not claim all real histories from bounded search.
MC09|specified|chapters/07-execution.tex|Template registry, slot instantiation, constraint lowering, witnesses and incomplete-search results expose the reconstruction scope.|Implement and independently test the supported registry; validate broader real-company scope separately.
MC10|specified|chapters/06-language.tex|Evidence readings, facts, permitted treatments, estimates, behavior and shocks have separate admission and dependency meanings.|Populate admissible facts and authority for new domains; unsupported treatments remain unresolved.
MC11|specified|chapters/05-mathematics.tex|Query-scoped economic memory, additive grouping conditions and lost-exposure counterexamples govern refinement and aggregation.|No general equivalence algorithm or empirical approximate-cohort error guarantee is supplied.
MC12|specified|sections/inference-methods.tex|Optional joint laws, one-use likelihoods, retained unresolved mass and finite/Gaussian worked updates state the probability measure.|Target-specific continuous inference and calibration need their own protocol and downstream evidence.
MC13|specified|sections/authorization.tex|EventBasis, separate posting authorization, journal/delta construction and atomic commit bind economic changes to accounting effects.|Execute actual transactional conformance later; source and method admissibility remain required for real books.
MC14|specified|sections/inference-methods.tex|Stress, observation conditioning and intervention have distinct inputs and meanings; information views exclude future realizations.|Acquire a supported company structural model and dated information before causal or predictive claims.
MC15|specified|sections/corporate-methods.tex|Performance versus billing, receivables, contract liabilities, inventory, PPE, payroll and connected lease/tax cases specify bounded operations.|Obtain real transaction facts, operative tax law and broader recognition/measurement exceptions before real admission.
MC16|specified|chapters/13-reference-company.tex|Northstar annual/interim/revision and forecast cases reconcile common-journal balance sheet, income, cash flow and equity; lease/tax adds a connected case.|General note/report execution and a complete real filing-to-projection case remain future evidence.
MC17|partial|sections/financing-methods.tex|Debt issuance, EIR, settlement, modification/extinguishment, equity and compound-instrument cases retain principal/carrying/fair-value distinctions.|Complete broader asset modification, floating benchmarks, options, hedge/EPS/tax and cross-standard lifecycle authority.
MC18|specified|sections/operations-storage.tex|Joint result families retain lineage, unresolved regions/mass and separate default, unsupported, infeasible and numerical outcomes.|Implement result/query behavior and evaluate numerical bounds under each declared capability.
MC19|partial|sections/standards-methods.tex|Dated rule selection and matched lease/tax examples distinguish IFRS-oriented, US and ASBE treatments and their authority strength.|Operative ASC, full ASBE tax/sector texts, amendment/transition chains and real entity applicability remain incomplete.
MC20|specified|chapters/08-modules.tex|Company/sector packages must preserve common context, authority, accounting and reporting semantics; a renamed label cannot change measurement.|Complete and adjudicate each actual industry override and its method-specific authority.
MC21|partial|sections/bank-methods.tex|Loan/allowance lifecycle, funding/default and capital-versus-accounting distinctions have complete finite examples.|Current jurisdictional prudential methods, calibrated staging/liquidity inputs, commitments/restructuring and actual bank facts remain incomplete.
MC22|partial|sections/insurance-methods.tex|PAA/reinsurance, general measurement, nonzero discounting and onerous loss-component expiry cases preserve service/finance and group state.|VFA options/guarantees, transition, acquisition/reinsurance interactions and actuarial estimation need fuller methods and source support.
MC23|specified|chapters/04-architecture.tex|Typed-library/shared-IR is the substantive comparator; matched tasks and identical financial semantics govern the proposed authoring evaluation.|No usability, cost or speed ranking is established; conduct the matched evaluation only under a separate authorized protocol.
MC24|specified|sections/portable-values.tex|Portable schemas, reference closure, types, module/effect checks, versioned operations and matched debt authoring define the proposed initial interface.|Independent implementation conformance is pending; legacy Core 0 syntax is explicitly distinguished from the new portable profile.
MC25|specified|sections/operations-storage.tex|Complete request/result, ownership, receipt-first replay, immutable history, migration and recovery contracts govern the initial store.|Crash/reopen/migration and external adapter execution require product implementation authorization and later conformance.
MC26|specified|sections/inference-methods.tex|Affine/finite capability, exact/approximate results, strict endpoints and bounded numerical method examples expose unsupported computations.|No general nonlinear solver or universally valid tolerance is promised; target-specific numerical protocols remain necessary.
MC27|partial|chapters/09-implementation.tex|Propose/accept/alternative/reject/supersede and dependency invalidation are specified with synthetic corrections and located real readings.|The required genuine source-backed conflict walkthrough and actual human adjudication remain missing.
MC28|partial|chapters/13-reference-company.tex|Complete synthetic Northstar and connected domain cases coexist with the named multi-date Apple disclosure preparation.|Finish representative notes and incorporated documents through real constraints and all affected statements; source acquisition alone is insufficient.
MC29|partial|chapters/12-research.tex|Technical claim limits and source-specific screening are retained; later method papers and official code are assigned explicit roles.|Complete method-specific backward/forward, omission, correction/version and direct-competitor audits for the whole promised scope.
MC30|partial|chapters/12-research.tex|Local paper/authority/report copies and exact source versions are retained without changing the original collection.|Four blocked foundational sources and incomplete current authority remain; counts and intact hashes do not replace technical inspection.
MC31|partial|sections/adapter-methods.tex|Pinned interface inspections, preservation sidecars, failure mapping, adverse cases and fair evaluation protocol define reuse boundaries.|Complete dependency/model/taxonomy/distribution locks and broader interface evidence; actual runtime integrations remain separately unauthorized.
MC32|specified|accounting-product-proposal.tex|The 123-page integrated candidate preserves original mathematics/citations, accepted architecture/methods and final build/render/review records.|Human comprehension remains pending; incomplete whole-product source/method obligations prevent full proposal readiness.
MC33|specified|chapters/10-validation.tex|Canonical cases, corpus/annotation rules, conformance vetoes, staged acceptance and forecast baseline/uncertainty protocols keep evidence classes separate.|Execute and independently adjudicate the applicable later engineering, accounting and scientific checks before their respective promotions.
MC34|specified|chapters/10-validation.tex|One cumulative implementation sequence, explicit initial/later support and current requirement/decision traceability preserve the mission.|Reassess remaining blockers with new evidence; this assessment neither enables implementation nor changes the mission's acceptance wording.
MC35|specified|chapters/10-validation.tex|Missing source, facts, calculations and method work remain internal; human acceptance is not a reason to outsource unfinished work.|Complete each internal dossier before any narrowly scoped professional question; no engagement, fee or outreach is authorized.
'''.strip()

upstream = {s: load(f'data/accounting-master/deliverables/{s}/{f}') for s, f in
            [('P15', 'coverage.json'), ('P16', 'architecture.json'), ('P17', 'methods.json')]}
original = {line.split('|')[1].strip(): line.split('|')[3].strip()
            for line in (ROOT / 'docs/plans/accounting-mission-requirements.md').read_text().splitlines()
            if line.startswith('| MC')}
requirements = []
for line in rows.splitlines():
    identifier, status, filename, contract, remaining = line.split('|')
    path = 'docs/design/proposal/manuscript/' + filename
    requirements.append({'id': identifier, 'status': status, 'scope': 'whole_product',
                         'acceptance_obligation': original[identifier], 'contract': contract,
                         'assessment': contract, 'remaining_work': remaining,
                         'design_consequence': 'Preserve this support boundary in admission, outputs and the next implementation stage; no blanket completion is inferred.',
                         'evidence': [ref(path, 'Complete named chapter/section; current P18 source'),
                                      ref('data/accounting-master/deliverables/P18/manuscript.json', '/source_files')]})

gap_map = {
    'G1': ('specified', ['MC08','MC09','MC11']), 'G2': ('specified', ['MC02','MC24','MC25']),
    'G3': ('specified', ['MC26']), 'G4': ('specified', ['MC15','MC16']),
    'G5': ('partial', ['MC01','MC28']), 'G6': ('specified', ['MC12','MC13','MC14','MC18']),
    'G7': ('partial', ['MC17','MC19','MC21','MC22']), 'G8': ('partial', ['MC29','MC30']),
    'G9': ('partial', ['MC23','MC31']), 'G10': ('specified', ['MC33','MC34']),
    'G11': ('partial', ['MC01','MC03']), 'G12': ('specified', ['MC06','MC07','MC20']),
    'G13': ('specified', ['MC05']), 'G14': ('specified', ['MC14','MC18']),
    'G15': ('specified', ['MC08','MC10','MC12']), 'G16': ('specified', ['MC11']),
    'G17': ('partial', ['MC04','MC27']), 'G18': ('specified', ['MC25','MC34'])}
by_id = {r['id']: r for r in requirements}
gaps = []
for identifier, (status, ids) in gap_map.items():
    selected = [by_id[i] for i in ids]
    gaps.append({'id': identifier, 'status': status, 'scope': 'whole_product',
                 'requirements': ids, 'contract': ' '.join(r['contract'] for r in selected),
                 'assessment': ' '.join(r['assessment'] for r in selected),
                 'remaining_work': ' '.join(r['remaining_work'] for r in selected),
                 'design_consequence': 'Design specification, real-source support, implementation and human acceptance remain distinct.',
                 'evidence': [r['evidence'][0] for r in selected]})

# An answered question is distinguished from the still-partial broader mission.
answers = {
 'P15-E01': (True, 'open', 'The traversal/coverage procedure is specified, but the complete real package and query consequences are still missing.', 'source-preparation-methods-v1.md', 'D1', 'Finish the Apple incorporation and material assertion inventory with located query consequences.'),
 'P15-E02': (False, 'resolved', 'Separate reported assertions, proposed predicates and accepted translations; retain context, modality, exceptions and unsupported thresholds. Six located Apple translations plus the ASBE substitution predicate instantiate this boundary.', 'source-preparation-methods-v1.md', 'D2', 'Expand real-package translation under E01; do not confuse that coverage work with an unspecified translation procedure.'),
 'P15-E03': (False, 'resolved', 'Display scale does not establish nearest rounding. P02 half-unit results are conditional assumptions; unknown convention supplies no hard interval. Closed enclosures and tie-specific endpoints are explicitly distinguished.', 'source-preparation-methods-v1.md', 'D3', 'Preserve source-specific unknowns and admit an issuer convention only on evidence.'),
 'P15-E04': (False, 'resolved', 'P16 admits each historical query only with its required availability, ingestion and byte-vintage evidence; P18 integrates those separate clocks.', None, 'time-contract-v2.md', 'Collect missing actual timing evidence; no silent latest-row fallback.'),
 'P15-E05': (True, 'open', 'Review layers and invalidation are specified, but the required genuine real-source conflict has not been found or worked through.', 'source-preparation-methods-v1.md', 'D4', 'Inspect a bounded candidate set with matched contexts and distinguish extraction/revision from unresolved conflict.'),
 'P15-E06': (False, 'resolved', 'Connected corporate domain with typed authoring first and a matched debt text fragment is the proposed initial profile; it keeps whole-company continuation explicit.', None, 'initial-profile-v1.md', 'Use the cumulative P0–P6 sequence; no empirically unsupported authoring ranking.'),
 'P15-E07': (True, 'open', 'Claim-specific dated primary authority and real applicability are required. US Codification, ASBE tax/sector and broader prudential/insurance support are incomplete.', 'standards-methods-v1.md', 'S2–S5', 'Retrieve operative texts and amendment/effective-date chains, then complete matched method consequences.'),
 'P15-E08': (True, 'open', 'P18 integration is complete within scope, but this P19 assessment still finds material source/method obligations and has not yet passed independent readiness review.', 'literature-methods-v1.md', 'L3', 'Resolve material preparation gaps and independently review exact P19 evidence; keep readiness false meanwhile.'),
 'P15-E09': (False, 'resolved', 'P16 separates disposition, mathematics, computation and admission; unresolved mass and domain-native failures survive into P18 reports.', None, 'failure-contract-v1.md', 'Implement and test the retained domain-specific result states only after authorization.'),
 'P15-E10': (False, 'resolved', 'Portable typed records govern new semantics; historical Core 0 remains a teaching contract. Typed corporate authoring and bounded debt text syntax have matched definitions.', None, 'language-ir-contract-v1.md', 'Execute independent frontend conformance later without expanding the legacy parser promise.'),
 'P15-E11': (False, 'resolved', 'Capability is checked after expansion. Initial affine/finite calculations have exact status and bounded replies; later numerical/inference methods state their target and unsupported cases.', 'forecasting-methods-v1.md', 'Numerical and inference method definitions', 'Require a new target-specific protocol before admitting a broader solver or scientific claim.'),
 'P15-E12': (False, 'resolved', 'P16 query-scoped memory and P17 group/perimeter, bank and insurance transitions supply concrete structural examples; source gaps remain E07/domain obligations.', 'groups-fx-methods-v1.md', 'Group/perimeter and currency methods', 'Retain actual control/cohort/lot facts and prove any new grouping within its query scope.'),
 'P15-E13': (False, 'resolved', 'Initial stress and finite measures, optional Gaussian conditioning, explicit causal counterexample and an empirical evaluation protocol specify the scenario/probability boundary.', 'forecasting-methods-v1.md', 'Conditioning, causal and evaluation methods', 'Gather actual calibration/heldout evidence later; no forecast or causal validity is inferred.'),
 'P15-E14': (True, 'open', 'Adapter roles, sidecars and adverse exchanges are specified, but broader dependency/model/taxonomy and distribution/interface evidence is incomplete.', 'software-reuse-methods-v1.md', 'R1–R4', 'Finish the source/licence/interface lock dossier; runtime evaluation is a distinct implementation task.')}
decisions = []
for inherited in upstream['P17']['open_decisions']:
    blocking, status, answer, method, locator, next_step = answers[inherited['id']]
    row = copy.deepcopy(inherited)
    path = ('docs/design/proposal/methods/' + method if method else
            'docs/design/proposal/architecture/' + locator)
    row.update({'blocks_proposal': blocking, 'status': status, 'proposed_answer': answer,
                'next_step': next_step, 'evidence': [ref(path, locator)],
                'consequence': 'Full readiness remains false while any material blocker persists; this answer does not promote broader domain support.'})
    decisions.append(row)

by_decision = {r['id']: r for r in decisions}
dispositions = []
for stage, d in upstream.items():
    for old in d['open_decisions']:
        if old['blocks_proposal']:
            new = by_decision[old['id']]
            dispositions.append({'stage': stage, 'decision_id': old['id'], 'status': new['status'],
                                 'answer': new['proposed_answer'],
                                 'rationale': 'Reassessed against the located P16–P18 contract; earlier accepted records are preserved unchanged.',
                                 'evidence': new['evidence']})

stages = {s: ref(f'data/accounting-master/deliverables/{s}/{f}') for s, f in
          [('P15','coverage.json'),('P16','architecture.json'),('P17','methods.json'),('P18','manuscript.json')]}
data = {'schema_version': 'accdsl.proposal.p19.v1', 'status': 'not_ready', 'ready': False,
        'assessment_status': 'author_assessment_pending_independent_review',
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'product_implemented': False, 'implementation_enabled': False, 'human_acceptance': 'pending',
        'limitations': 'Negative readiness assessment of the present proposal. Specified means a scoped design contract, not complete real authority, implemented conformance, human comprehension or forecast validity. No original MC requirement or gap is declared closed in full.',
        'source_evidence': [ref('docs/plans/accounting-mission-requirements.md'),
                            ref('docs/plans/accounting-p17-requirements-update-20261006.md'),
                            ref('data/accounting-master/direct-p18-20261006/completion.json')],
        'stage_evidence': stages, 'requirements': requirements, 'gaps': gaps,
        'open_decisions': decisions, 'decision_dispositions': dispositions,
        'initial_profile': [ref('docs/design/proposal/architecture/initial-profile-v1.md')],
        'implementation_sequence': [ref('docs/design/proposal/manuscript/chapters/10-validation.tex')],
        'acceptance_fixtures': [ref('docs/design/proposal/methods/method-cases-v1.json'),
                                ref('docs/design/proposal/architecture/accounting-complete-exchanges-v1.json')],
        'residual_work': [ref('docs/plans/accounting-p19-direct-assessment-20261007.md')],
        'remaining_blockers': [r['id'] for r in decisions if r['blocks_proposal']]}
save(OUT / 'readiness.json', data)

lines = ['# P19 requirement and gap assessment', '',
         'The current proposal is not ready for whole-product promotion. P18 is internally complete for manuscript integration; real-package, conflict, authority, literature and broader adapter evidence remain incomplete. This is an author assessment pending independent review.', '',
         'A `specified` row identifies a concrete scoped design contract. It does not close every wider acceptance obligation. Original requirement wording and accepted P15–P18 bytes remain unchanged.', '',
         '| Requirement | Design status | Current evidence | Remaining work |',
         '| --- | --- | --- | --- |']
for r in requirements:
    lines.append(f"| {r['id']} | {r['status']} | {r['assessment']} | {r['remaining_work']} |")
lines += ['', '| Gap | Design status | Requirements |', '| --- | --- | --- |']
for r in gaps:
    lines.append(f"| {r['id']} | {r['status']} | {', '.join(r['requirements'])} |")
lines += ['', '## Inherited decision dispositions', '',
          'Five of the ten inherited P17 blockers now have a proposed scoped design resolution: E02, E03, E11, E12 and E13. Together with the four P16 resolutions, nine of fourteen questions are answered; five remain blockers. Independent review must assess these dispositions.', '',
          '| Decision | Blocks readiness | Current answer | Next action |', '| --- | --- | --- | --- |']
for r in decisions:
    lines.append(f"| {r['id']} | {str(r['blocks_proposal']).lower()} | {r['proposed_answer']} | {r['next_step']} |")
(DOC / 'assessment-v1.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'requirements': len(requirements), 'gaps': len(gaps),
                  'upstream_dispositions': len(dispositions), 'blockers': data['remaining_blockers'],
                  'ready': False}))
