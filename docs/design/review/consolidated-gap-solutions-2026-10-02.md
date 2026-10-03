# Known gaps and proposed solutions after corpus acceptance

Date: 2 October 2026 (Asia/Hong_Kong).
Scope: the Version 1.2 design, eventual executable system and accepted source
panel. This consolidates G1–G18 and the corpus findings; it does not replace
the mission or change MC01–MC35. Solutions below are proposals, not completed
implementation. This is all currently identified work in these records, not
proof that further semantic examination will find no additional gaps.

## Evidence baseline

The agreed source collection is complete: **192/192 annual and interim reports,
nine issuers, eight consecutive years each (2018–2025)**. The panel includes
US GAAP, IFRS-oriented and ASBE reports, with annual plus Q1/Q2/Q3 for the US
issuers and annual plus H1 for the others. Source QA and independent integrity
checks pass. The 168 PDFs contain 32,678 pages; another 24 reports are HTML.
These counts measure source acquisition, not extraction accuracy, semantic
coverage, engine capacity or forecasting validity.

Version 1.2 has specifications, bounded reference cases, exact accounting
checks and an authored-debt semantic validator. It is not yet a general
source-to-IR compiler, company runtime or validated forecasting system.
The corpus has no adjudicated accounting labels, promoted split for a named
model/task, model scores or historical forecast validation. Filing-date
metadata exists for 56 reports; publication dates remain unverified for 136.
Even a known filing date does not establish the historical availability of
every retained byte version.

Sources: [mission requirements](../../plans/accounting-mission-requirements.md),
[repair results](gap-repair-results-2026-10-02.md),
[internal preparation](internal-preparation-results.md),
[corpus results](../../plans/accounting-benchmark-corpus-results.md), and
[benchmark protocol](../../../data/financial-report-benchmark/benchmark-protocol-v1.json).

### Review of this consolidation

The main risks are using the pre-repair document as the current baseline,
equating collected files with a working benchmark, counting overlapping gaps
twice, treating public reports as uniquely identifying latent journals, and
allowing unavailable dates or external feedback to halt unrelated internal
work. This register uses post-repair residuals, keeps the original IDs, maps
corpus refinements to them, and gives bounded completion evidence. No new
experiment, accounting-authority claim, acceptance threshold or software
default is introduced. The documentary plan passes on that basis; each later
implementation or research phase still needs its own reviewed execution plan.

## Sources, historical meaning and complete cases

### G11 — Whole disclosure packages, extraction and narrative meaning

**Gap.** A checked report file does not close incorporated proxy statements,
agreements, exhibits, referenced reports or HTML assets. Source QA does not
validate every cell, continued table, heading, sign, scale or note anchor.
Material policies, qualifications and commitments are not all translated into
supported model meaning.

**Proposed solution.** Build a report-specific source-unit and cross-reference
inventory; retain literal text, table structure and precise page/span anchors.
Check values and context against rendered sources. Give each source unit a
retained, duplicate, structured, unresolved or explicitly scoped-out
disposition. Link narrative assertions to affected amounts and operations.
Preserve uncertainty in phrases such as “substantially all”; do not invent
numeric thresholds. Acquire missing incorporated material where legitimate
access is available and record unresolved obligations otherwise.

**Completion evidence.** A complete inventory for each declared case, checked
source-to-record examples including difficult layouts, and every reference
resolved or visibly outstanding. Source inventory, semantic interpretation and
simulation coverage have separate denominators. An outstanding material
obligation prevents claiming complete semantic coverage.

### G13 — Availability, versions, calendars and longitudinal comparability

**Gap.** The 136 unverified publication dates prevent affected historical
as-of tests. Amendment, translation, mirror and comparative-version links are
incomplete. Fiscal calendars, instantaneous balances, quarter-only versus
year-to-date flows, restated comparatives and policy/perimeter changes require
more than matching year labels.

**Proposed solution.** Attach independently evidenced publication/availability
information to the specific report version, with explicit date-only and
same-day policies. Preserve separate economic, reporting, availability and
ingestion times. Link original, amended, translated and different-basis
versions without assuming they are interchangeable. Implement original,
latest-available and harmonised views; test valid and invalid interim
subtraction, selective revisions, acquisitions/disposals, segment changes and
standards transitions. Leave unavailable dates unknown.

**Completion evidence.** Multi-date fixtures return the expected records and
reject incompatible subtraction or future information. Every report used in
an as-of evaluation has sufficient source-version availability evidence for
that task. Undated reports remain usable for chronology-independent tasks.

### G12 — Report identity, company concepts, mappings and partitions

**Gap.** Issuer and year alone do not establish report identity or measurement
equivalence. Parent and consolidated reports, different accounting bases,
languages, gross/net amounts, company extensions and overlapping dimensions
can be conflated. Report-level basis QA does not settle jurisdictional
applicability or concept-level accounting meaning.

**Proposed solution.** Carry legal entity, consolidation perimeter, basis,
jurisdiction, language, period, currency, units, scale, sign and precision
through the model. Implement context-dependent equivalence, component,
reclassification and measurement-transformation mappings, with dated
applicability. Require disjoint/exhaustive partition evidence where sums need
it, and retain unallocated amounts and unresolved mappings. Cross-standard
measurement conversion must have its own supported rule.

**Completion evidence.** Positive and rejection fixtures cover similar labels
with different measurements, different labels for equivalent quantities,
parent/group confusion, company extensions, changing perimeter, and overlapping
product/geographic classifications. Rejected Allianz parent reports and the
distinct Ping An interim bases supply retained source-identity cases.

### G5 — Complete real-company case and financial reconciliation

**Gap.** Apple's acquired sources and partial financing analysis do not yet
form a complete real-company reconstruction and conditional execution case.
All material notes and incorporated documents have not been connected to the
model. There is no corpus-wide checked statement/note/cross-period
reconciliation layer.

**Proposed solution.** Complete one declared Apple annual/interim package from
source units through contextual records, material note meanings, constraints,
admissible alternatives, explicit scenarios, journals and statements. Prepare
expected results before using them to judge the engine. Reconcile statement
totals, notes, cash and equity movements and opening/closing bridges using
disclosed rounding and adjustments. Classify extraction errors separately from
genuine disclosure conflicts. Add targeted other-basis, bank and insurer
contrasts; do not infer their support from a corporate case.

**Completion evidence.** A reproducible source-to-statements case with common
underlying journal/state data, traceable reconciliations, recorded unresolved
meanings and no unexplained balancing plugs. A real report need not identify
one unique latent history; the case must preserve that distinction.

## Language, reconstruction and numerical semantics

### G2 — General language, shared IR and compilation

**Gap.** The authored debt profile and frozen registry checks do not establish
general compilation, package loading, mappings, dimensions or interactions
between all uncertainty categories. A schema-valid object can still be
semantically wrong.

**Proposed solution.** Complete the supported lexical/grammar rules, package
resolution, symbol binding, type/context checking and source-to-IR lowering.
Implement the typed-library frontend against the same intermediate
representation and runtime. Extend valid and schema-valid-invalid fixtures
beyond debt, including dependencies, source binding and interactions. Define
unsupported features explicitly.

**Completion evidence.** Matched DSL and typed-library programs produce the
same canonical supported IR and results, preserve the same evidence and
alternatives, and reject the same invalid constructions. Independent
implementability remains a separate later assessment.

### G1 — Joint historical reconstruction and honest completeness

**Gap.** Checked hand-authored bridges do not implement general template-to-
constraint construction. A feasible witness or independently computed account
range does not establish the complete joint family of admissible histories.

**Proposed solution.** Lower declared template registries and candidate slots
into joint constraints across accounts, notes, contracts and dates. Preserve
discrete choices and continuous unknowns, contradiction evidence, unresolved
results and omitted model scope. Use synthetic companies with known histories
and bounded real disclosures whose expected alternatives are checked.

**Completion evidence.** For exactly enumerable small cases, recover the
expected family and reject incompatible combinations. Larger results state
the supported scope, search limits and completeness status; no single witness
is called the unique real history without supporting identification evidence.

### G15 — Admission and propagation of different uncertainties

**Gap.** Checks are incomplete for factual unknowns, disclosure readings,
accounting elections, estimates, behaviour and shocks, especially their
interactions. Balanced entries cannot establish that a proposed treatment is
permissible.

**Proposed solution.** Implement category-specific admission, provenance,
dependency, update and refutation rules. Preserve source assertions separately
from accepted interpretations. Retain admissible alternatives, identify
unsupported treatments, and exclude evidence-refuted possibilities with
reasons. Leave alternatives unweighted unless a defensible measure exists.

**Completion evidence.** Positive and negative cases for all six categories
and their relevant interactions, including a retained source error, a permitted
election, an unsupported treatment and an alternative invalidated by new facts.

### G3 — Numerical operations, bounds and resource limits

**Gap.** Exact illustrative rational calculations do not supply production
quantisation, integer handling, optimisation or operational failure behaviour.
Strict endpoints, reported rounding and certified versus sampled bounds need
consistent execution semantics.

**Proposed solution.** Implement the declared rational-linear/finite-choice
fragment, applicable integer constraints, rounding-aware feasible intervals,
quantisation and attained/unattained bounds. Define tolerances only where
needed and justified. Return infeasible, unknown, unsupported, timed-out and
resource-limited results distinctly. Add nonlinear operations only with their
own method and validation.

**Completion evidence.** Compare small cases with exact independent oracles;
test boundary values, rounding conflicts and interrupted optimisation. Do not
silently discard unresolved branches or present sampled extrema as certified.

### G14 — Scenario meaning and information restrictions

**Gap.** Static stress typing does not enforce information access during
execution. Stress paths, observational conditioning and causal intervention
have different meanings; selecting a scenario must not silently update beliefs
as if it were observed evidence.

**Proposed solution.** Implement explicit supported scenario modes and role-
and-date information access for behaviour and measurement operations. Separate
observed-data updates from imposed paths, and real-world from pricing measures.
Declare unsupported intervention/conditioning operations until their semantics
and methods are ready; causal identification needs separate research support.

**Completion evidence.** Adversarial future-data access is rejected; paired
cases show the intended differences between modes and preserve conditional
history/scenario dependence, including failed and unresolved branches.

### G16 — Resolution, state memory and aggregation

**Gap.** The design has exact grouping conditions and counterexamples, but no
general implemented policy proving that a grouping retains the state required
for a particular query, horizon and scenario family.

**Proposed solution.** Specify required contract/lot/vintage/cohort state and a
bounded set of justified grouping transformations. Recheck sufficiency when
the query or horizon changes. For proposed approximations, retain detailed
references and predeclare the error measure and acceptable use.

**Completion evidence.** Grouped and detailed executions agree within declared
exact scope; counterexamples expose lost maturity, rate, guarantee or cohort
effects. Approximate use requires measured error for its intended task.

## Accounting, economics and research support

### G4 — Corporate operations, financing and common statements

**Gap.** Synthetic ordinary-company examples do not supply the full
source-supported revenue, tax, lease, FX, consolidation and financing methods.
Operation specifications and general event-to-statement execution remain open.

**Proposed solution.** Extend dated operation packages with preconditions,
recognition, measurement, economic state changes, postings and note schedules.
Cover relevant revenue/collection and purchase/payment cycles, inventory,
assets/depreciation, payroll/closing, tax, leases and foreign operations;
complex control, goodwill, tax/FX and retained interests in consolidation; and
bond modification, early repurchase, conversion, default, classification and
equity movements. Build each supported annual/interim case from common state
and journals into balance sheet, income/OCI, direct/indirect cash flow, equity
and related notes.

**Completion evidence.** Source-backed operation contracts and exact
multi-period cases reconcile, including non-cash movements, closing and
failure cases. Balanced journals alone do not certify the accounting treatment.

### G7 — Primary authority, accounting bases, banks, insurers and hybrids

| Subgap | Proposed solution | Completion evidence |
| --- | --- | --- |
| Primary authority and applicability | Obtain and inspect relevant primary ASC provisions and official applicable ASBE texts through legitimate access; verify the jurisdiction/period applicability of the IFRS-related sources used. Maintain dated rules, elections and transitions, with explicit source-access blocks. | Each implemented treatment has a precise authority anchor, scope, effective period and permitted alternatives. Company disclosure or an AASB text is not silently promoted into universal authority for other jurisdictions. |
| Cross-standard measurement | Work the same economic facts under selected supported IFRS, US GAAP and ASBE treatments, including transitions and company elections. Separate nomenclature changes from measurement differences. | Matched cases explain and reconcile supported differences; missing authority or operations remain explicit. |
| Banking | Complete credit-loss/allowance lifecycles and the IFRS 9/CECL distinctions; model deposits, funding, liquidity, actual jurisdictional capital rules and their interaction with management behaviour. | Dated source-backed bank cases reconcile accounting movements and prudential capital and expose funding/default behaviour; illustrative regulatory numbers remain labelled until replaced. |
| Insurance | Extend the short-duration example to general measurement, contractual service margin, variable fees, transition and onerous groups; develop defensible risk-adjustment estimation and asset/reinsurance interactions, including separate eligibility and timing. | Complete multi-period gross/reinsurance roll-forwards, source-backed recognition and measurement, sensitivity cases and an explicit actuarial uncertainty method. |
| Hybrid instruments and complex groups | Extend classification, embedded rights, conversion and relevant group/control cases across supported bases. | The same contractual facts produce explainable supported alternatives, with all journal/state/statement consequences shown. |

These are separate substantial tasks inside G7. An unresolved source-access
question blocks claims depending on that authority, not unrelated internal
engineering or research.

### G6 — Behaviour, probabilities, calibration and forecasting

**Gap.** Transparent assumptions and finite illustrative weights do not
establish calibrated behaviour, continuous inference or forecast accuracy.
Joint measures, evidence updates and treatment of unresolved probability mass
need executable methods and target-specific evidence.

**Proposed solution.** Start from a transparent deterministic operating model.
Specify required data, calibration periods and assumptions. Add probabilistic
methods only for a defined target, with justified dependence, priors/likelihoods
and information timing; retain unweighted alternatives where appropriate.
Evaluate historical forecasts separately using evidenced source vintages,
matched naive and credible tuned baselines, out-of-time evaluation and
predeclared uncertainty analysis. Use continuous inference only where the
target requires it.

**Completion evidence.** Calibration and forecast protocols, reproducible data
and runs, preserved branch/mass accounting, target-specific numerical checks
and uncertainty-supported evaluation. A coherent conditional scenario is not
automatically an accurate forecast or identified causal effect.

### G8 — Technical literature and source-specific support

**Gap.** Individual metadata screening improves the research record but does
not establish technical support for every adopted method or later module.
Consequential omissions and blocked sources remain.

**Proposed solution.** Inspect relevant methods, derivations, evaluation and
appendices of adopted and competing research, together with official code
where available. Archive tractable versions, record source-specific inclusion
or exclusion reasons, and link design claims to exact inspected material.
Treat unavailable sources as uninspected; repair, narrow or defer dependent
claims rather than filling the gap by citation alone.

**Completion evidence.** Each adopted method has an inspected support record,
a reproduction or derivation appropriate to the claim, and a fair account of
alternatives and limitations. No blanket requirement to read irrelevant papers
or infer correctness from library size.

## Runtime, integrations, review and recovery

### G18 — Execution identity, transactional storage and recovery

**Gap.** Reference identity/replay examples are not a working persistent
company engine. Atomic state/journal updates, duplicate-event handling,
migration, restart and stable random-stream allocation need execution tests.

**Proposed solution.** Implement the bounded Northstar path with explicit
state ownership, transactional journal/state changes, deterministic event
identity, idempotent retry, immutable evidence/model/run lineage and versioned
migration. Retain partial progress and typed failures. Allocate random streams
by stable semantic identities where stochastic execution is supported.

**Completion evidence.** Interrupt at transaction boundaries, restart and
compare with uninterrupted execution. Test duplicate/conflicting events,
reordered independent events, branch reorder, source correction and migration.
Declare which results must match exactly and justify any numerical tolerance.

### G17 — Review actions, corrections and dependent-result invalidation

**Gap.** A transitive-invalidation oracle does not implement a usable local
review workflow with all state transitions and preserved historical decisions.

**Proposed solution.** Implement propose, accept, accept-alternative, reject
and supersede actions with required evidence, reasons and consistency checks.
Separate extraction confidence, reviewer decisions and model probabilities.
Invalidate affected downstream interpretations, models and runs, while
preserving prior results under their original evidence views. Provide a local
interface for examining conflicts and unresolved source spans.

**Completion evidence.** Exercise raw extraction through competing readings,
correction, rejection and supersession; verify exactly the dependent results
are marked stale and recomputed. Model-generated annotations remain proposals
until the declared acceptance process is satisfied.

### G9 — Reusable software and a fair DSL comparison

**Gap.** Inspected interfaces and licences do not prove integration. Only Z3
has been exercised. Arelle, ACTUS, QuantLib, Docling and ledger exchanges, and
the DSL-versus-typed-library evaluation, remain pending.

**Proposed solution.** Pin selected versions and implement small adapters with
explicit units, calendars, conventions, supported operations, errors and
provenance. Run retained input/output cases and adversarial failures. Compare
DSL and typed-library authoring on identical tasks, underlying IR, accounting
methods, source information and runtime. Separate semantic equivalence from
human authoring effort and readability.

**Completion evidence.** Reproducible adapter conformance results and a matched
frontend comparison with no hidden implementation advantages. Any claimed
human usability benefit needs its own study; an adapter smoke test or shorter
program does not establish superiority.

## Benchmark, capacity and acceptance

### G10 — A usable benchmark and release evidence

Acquisition is closed for the agreed panel. The remaining benchmark work is:

| Subgap | Proposed solution | Completion evidence |
| --- | --- | --- |
| Reference annotations and executable expected answers | Prepare literal/context/span records without using evaluated-model predictions to choose labels. Reconcile machine-detectable conflicts; preserve initial readings, evidence, alternatives and unresolved answers. Combine real disclosures with known-history synthetic cases. | Versioned task-specific reference sets and exact expected outputs or admissible-answer rules. A single invented latent journal history is never the gold answer to an underidentified real disclosure. |
| Exposure and split design | Audit exposure for each named model/task; keep issuer families, years, amendments, languages and duplicates together where required. Freeze development/validation/test roles before evaluation. Use temporal cutoffs where the task requires them. | Documented split and exposure history. All current issuers have source-QA exposure; the proposed finance/insurance-heavy test families are not a representative sector-balanced sample. |
| Coverage of difficult cases | Inventory actual events, layouts and accounting transitions in the retained reports, including revisions, complex groups, unusual financing and sector-specific cases. Acquire additional reports only for demonstrated gaps. | A task-by-case coverage matrix that distinguishes absent, present and not inspected. Difficult cases are not yet inventoried; their absence has not been established. |
| Scoring and statistical evidence | Define task denominators, partial/unresolved outcomes, material errors, failure treatment and uncertainty before testing. Account for issuer and time dependence rather than treating 192 reports as independent observations. | Reproducible scores with the declared uncertainty and hard-error checks. Zero critical errors in a finite conformance set is a bounded result, not universal certification. |
| Capacity and graceful failure | Measure extraction/model workloads in facts, constraints, branches and note links, together with runtime, peak memory and storage. Test bounded resource limits, timeout, interruption and restart. | Measured supported envelopes, recoverable partial results and visible unresolved work. A 32,678-page source collection is not evidence of engine capacity. |
| Independent acceptance | Separate engineering conformance, accounting validity, reader comprehension, implementability and forecast validity. Prepare narrowly scoped unresolved questions before external assessment. | Distinct evidence and acceptance records, including remaining uncertainty; no automatic promotion from arithmetic/build/source checks to other forms of validity. |

### Cross-cutting obligations within the existing mission

| Obligation | Remaining work and proposed solution |
| --- | --- |
| Governing design and reader comprehension — MC32 | Incorporate validated method/case changes into the LaTeX argument, preserve equations and source qualifications, and inspect the rendered result. Test comprehension and independent implementability separately; author checks and compilation do not establish either. Continue provisional internal improvement while feedback is pending. |
| Traceability and resumability — MC34 | Keep MC01–MC35, G1–G18, source versions, implemented scope, unresolved decisions and next actions connected. Update current registers/reset notes after meaningful changes; preserve historical results and frozen release hashes. A plan, implemented feature, checked accounting method and validated forecast require distinct statuses. |
| Internal preparation before paid review — MC35 | Resolve feasible source, arithmetic, extraction, software and research questions internally. For any consequential remainder, prepare the exact facts, dated authority, proposed answer, strongest alternative and checked consequences. Seek only the required judgment under separately authorised scope and cost; ordinary reader/software feedback need not be an accounting-firm engagement. |

These obligations are not additional independent findings beyond G1–G18.

## Where the corpus findings fit

| Corpus-driven refinement | Existing gaps affected |
| --- | --- |
| Publication chronology and historical versions | G13, G14, G6, G10 |
| Report identity, consolidation perimeter and accounting basis | G12, G7, G11 |
| Longitudinal comparability and valid interim arithmetic | G13, G12, G4 |
| Faithful extraction and complete disclosure packages | G11, G5, G9 |
| Statements, notes and cross-period reconciliation | G5, G4, G10 |
| Reference answers preserving unidentified histories and ambiguity | G1, G15, G10 |
| Exposure-safe evaluation, dependence and difficult-case coverage | G10, G7 |
| Measured scale and explicit failure behaviour | G3, G16, G18, G10 |

## Proposed execution order

1. **Prepare complete bounded cases and expected answers.** Finish the chosen
   Apple annual/interim source package and material note map, with extraction
   and reconciliation checks. Prepare targeted other-basis, bank and insurer
   contrasts before fixing shared type assumptions. Record unsupported
   meanings and alternatives explicitly rather than claiming whole-company
   completion prematurely.
2. **Implement the shared core against those cases.** Extend source-to-IR
   compilation and package/type validation; build joint reconstruction,
   uncertainty admission, mappings and the supported numerical operations.
   Keep DSL and typed-library inputs aligned.
3. **Execute the bounded company path.** Start with the known-history Northstar
   oracle, implement atomic state/journal updates and all common statements,
   then apply the supported path to the real case. Include information-date
   enforcement, review invalidation and restart/migration tests from the start.
4. **Expand supported methods and integrations.** Add source-backed corporate,
   cross-standard and sector operations and the selected adapters; check that
   required state and aggregation still support the requested scenarios.
5. **Promote a benchmark only when its reference answers and split are ready.**
   Freeze task/model exposure, score definitions and hard cases; measure real
   workloads and record failures. Expand the panel only for demonstrated
   coverage needs. Annotation design and easy internal preparation can begin
   during earlier steps.
6. **Evaluate calibration and forecasting separately.** Use eligible dated
   source vintages, matched baselines and uncertainty under a reviewed research
   plan. Undated sources can continue supporting other tasks.
7. **Maintain the governing design and seek narrow independent assessments.**
   Update the narrative and requirements evidence throughout. Refer a question
   only after its internal preparation is exhausted; do not wait for unrelated
   future modules, and do not make external feedback a stop condition for
   independent authorised work.

Authority acquisition, publication/version evidence and technical reading run
alongside the dependent engineering tasks. This order is a proposed dependency
sequence, not a claim that all sector methods or all 192 report annotations
must be complete before useful core work can begin.

## Status of this update

This update consolidates known residuals, solutions and completion evidence.
It corrects the obsolete acquisition wording in the internal-before-expert
register and leaves historical repair results and pinned corpus-release
controls unchanged. It does not implement any technical solution above,
produce benchmark scores, close G1–G18, or commission professional review.
