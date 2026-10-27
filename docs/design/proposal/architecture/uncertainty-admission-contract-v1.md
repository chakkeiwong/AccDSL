# Uncertainty admission and revision v1 — partial proposal

A company may have reported an amount without disclosing its composition. An
analyst may also be uncertain about what a note means, which accounting treatment
is permitted, or how management will respond to a future event. These questions
require different evidence and different ways of changing an answer. This
contract specifies those distinctions before attaching any probability model.
It addresses MC10/G15 and the MC04/MC08/MC12/MC14/MC18/MC25/MC27 interfaces.
The complete uncertainty contract still needs joint measures, conditioning,
probability updates and conditional future outcome payloads.

## U1. Inputs, retained records and admission results

An `AdmissionRequest` contains an immutable proposed record, an operation,
a base-view version and a requested layer. Its shared header is:

| Field | Required meaning |
| --- | --- |
| `record_id`, `version`, `predecessor` | Stable logical identity, immutable version and explicit predecessor or null. Reusing an existing version with different content is invalid. A predecessor alone does not authorise supersession. |
| `category`, `payload_version` | One of the six categories below and the version of that category's payload rules. Unknown categories or payload versions remain preserved but unsupported. |
| `context` | Entity, perimeter/version, concept/mapping, dimensions, instant or reporting interval, calendar/version, currency, unit, scale, sign and measurement basis, with explicit unknown/not-applicable values. Numeric rounding follows E3; missing values never imply a global default. |
| `evidence_view`, `review_snapshot`, `time_view` | Exact immutable manifests; the time view includes admission mode, selection, cutoffs, calendars and byte-vintage evidence as required by T1–T3. |
| `scope` | Family ID/version, named branches or explicit all-branches selection, and candidate-selection key/version. Empty branch lists do not silently mean all. |
| `provenance` | Source occurrence/reading versions, derivations or authored assumptions, author, rationale and review-event references. Synthetic support is labelled synthetic. |
| `dependencies` | Exact typed/versioned dependencies, including applicability, information permissions, assumptions and selection membership. An empty list is explicit and still subject to category-required references. |
| `operation`, `requested_layer` | Operation from U3; evidence reading, reported-value, economic-history, accounting-history, decision-input or future-domain layer. Unsupported layer/category combinations return a reason. |

The category payload adds the substantive proposition or policy, not just a tag.
An operation event records its ID, author, rationale, proposed predecessor,
base view, selection changes and intended successor. Submitting an assertion
preserves it even when its interpretation or treatment cannot be admitted.
Invalid structured requests retain their submitted envelope and validation
errors for repair; they do not become valid semantic records.

An `AdmissionResult` contains request/record IDs, the old and proposed new view,
`disposition`, reason codes, requested layer, an admitted predicate or selected
assumption (null when neither is admitted), exact support references, unresolved
obligations, affected dependencies, family/branch effects, preserved record IDs,
and the next permissible operation. It keeps separate fields for:

* evidence review disposition and source truth (`not_established` unless a
  separately justified claim supplies more);
* category admission and conditional assumptions;
* accounting applicability/validity, which this admission alone cannot establish;
* capability support and computation status (these examples execute no engine).

`ADMITTED_CONSTRAINT` means the declared support and layer's admission rules
are satisfied, conditional on all listed assumptions. It does not make the
issuer's assertion true. `ADMITTED_ASSUMPTION` explicitly selects an authored
condition; `RETAINED_ONLY` leaves it unselected. `EVIDENCE_REFUTED` names a
supported predicate and a check that contradicts the candidate in this scope.
`UNRESOLVED` identifies missing information or an undecided check. `UNSUPPORTED`
identifies unavailable authority, semantics or capability. `REQUEST_INVALID`
identifies a malformed transition/reference. `SCOPED_CONFLICT` preserves an
incompatible proposed conjunction and its exact context. These dispositions
must not be collapsed into one Boolean or a probability.

## U2. Six categories and their admission rules

### Disclosure readings: extraction and semantic interpretation

An extraction payload links immutable bytes, occurrence/locator, literal reading
and extraction review. Review that accepts a reading establishes fidelity to the
inspected occurrence within that review's scope. A synthetic scan showing 120
refutes an OCR candidate 720 as a reading; it does not establish an underlying
company balance. A faithful reading of an erroneous issuer statement survives.

A semantic-interpretation payload separately names the extraction version,
contextual meaning, modality, mappings and alternatives. A phrase such as
“credit facility 100” does not establish that 100 is drawn debt. If commitment
and drawn-balance interpretations remain unresolved, retain both. Selecting one
as an explicit analytical assumption creates a conditional reported-value
branch; selecting an interpretation cannot manufacture authority for journals.
Review events must specify whether they concern fidelity or meaning. A semantic
review may admit a meaning at the requested layer only with its source/context
support; an unsupported implication remains unresolved. Competing readings
never receive weights from OCR confidence or reviewer preference. (UA01.)

### Historical facts

A fact payload identifies an economic quantity/event, its declared domain and
supported constraints. Domains may be finite, continuous, mixed or symbolic;
any unsupported solver operation returns its unmodified domain as unresolved.
A continuous real-valued amount is not implicitly discretised to cents.
Evidence and context must support each new constraint, and shared quantities
retain their history-family links. A hypothetical assumption about an unknown
fact remains an assumption, even if it selects one factual value.

For the synthetic same-view amount x, let D0=[0,100]. New admissible evidence
supplies C1=[20,60]. Under unchanged assumptions, D1=D0 intersect C1=[20,60]:
x must satisfy both pairs of endpoint inequalities. Evidence C2=[70,80] gives
D1 intersect C2=empty since x<=60 and x>=70 cannot both hold. This is a conflict
in the named conjunction/branch, not a finding that every family or the real
company is impossible. A candidate x=80 is refuted within D1 because 80>60.
The closed endpoints, exact real domain and common units are explicit fixture
assumptions, not defaults for rounded reported values. (UA02.)

### Accounting elections

An election payload names the dated rule package, exact permission and
eligibility evidence, relevant entity/transaction/class, effective period,
permitted options, chosen option and any consistency/transition obligations.
Permission must originate in the package's reviewed authority, not in a list
asserted by the request. Eligibility false refutes this proposed election within
that package; eligibility unknown remains unresolved. Missing or unverified
permission produces `UNSUPPORTED`, preserving the asserted treatment without
an accounting constraint. Even a selected permitted election needs separate
recognition/measurement/journal checks. An assumed election cannot be substituted
for evidence of what an issuer historically elected.

UA03 uses an explicitly synthetic rule P allowing options A and B during 2026
for class C when eligibility is true. Choosing B is a conditional design example;
option Z is refuted by P's exhaustive permission list. An absent real authority
is unsupported, not evidence that the treatment is prohibited in every regime.
No IFRS, US GAAP, ASBE or tax permission is established by this example. P17
must supply actual dated sources, eligibility and treatment consequences.

### Measurement estimates

An estimate payload states the estimand, economic/measurement date, method and
version, units, inputs and their information dates, judgments, assumptions,
output domain/value and applicability requirements. A model-produced amount
remains an estimate. A reported estimate remains separately a reported assertion;
copying its number does not establish its measurement method.

UA04 uses the synthetic formula e=quantity times a stipulated price estimate:
10 times 2=20. Later admissible input 3 produces a new estimate 30 for a newly
specified view of the same measurement target. The revised estimate is neither
a narrowed factual interval nor evidence that the earlier input was fraudulent.
Retrospective revision is labelled with the later information view; it cannot
be used by a decision confined to the original cutoff. Actual accounting rules
must determine whether a change is prospective, a correction, a restatement or
impermissible. Missing applicability is retained as an obligation. General
estimators are representable; unsupported evaluation returns the symbolic method,
inputs and reason without inventing a value. (UA04.)

### Behaviour policies

A policy payload identifies its decision date(s), feasible actions/constraints,
state and information inputs, versioned decision rule, author and assumption
selection. A policy is a proposed conditional choice rule, not a realised fact.
All reads must resolve to the actor's declared information view at the decision
instant, including dynamically selected inputs and model-generated forecasts.
An audit list alone cannot prove that an eventual plugin obeys this rule.
Runtime information mediation is an interfaces/language obligation.

UA05's decision is dated 2026-03-01. An announcement known on 2026-02-28 about
a June stress can be used as announced information. The actual June outcome,
known in July, cannot be used at that decision date. Admission of the announcement
does not condition a historical probability model or make the June outcome known.
A fixed-action or state-dependent policy is permitted as a selected assumption
when its semantics and information checks are supported; the P06 hold-only
restriction is not a whole-product rule. Optimisation, randomised choices and
causal interventions need separately specified methods. Unsupported evaluation
preserves the policy but produces no executed decision. (UA05.)

### Future innovations

A future-innovation payload identifies driver, future period, unit, scenario
version, feasible domain, joint constraints and assumptions. It may specify
unweighted possibilities. UA06 uses the synthetic continuous rate change
[-1/10,1/10], with no law. The future-domain layer can admit that authored domain
as a selected assumption without claiming any probability, independence,
expectation or relative plausibility. Correlated/shared driver constraints must
survive; the six category tags do not make variables independent.

A probability attachment, likelihood update, conditional distribution or measure
conversion requires the later joint-measure contract. For this slice these
operations return `UNSUPPORTED: JOINT_MEASURE_CONTRACT_REQUIRED`, preserving
the proposed model. No uniform distribution, equal branch weights, confidence
weights or normalization over successful branches is allowed. Absence of a law
is not grounds for rejecting an otherwise admissible unweighted scenario.

## U3. Operations and revisions

Each operation names a base view and exact input versions. The support must pass
context, review, authority where applicable, and time checks for the requested
layer. A stale base view is `REQUEST_INVALID: STALE_BASE_VIEW`; retry requires
rebasing and reassessing newly competing evidence. No partial write may expose
new constraints with old dependency metadata. Persistence must atomically save
the new records, review/selection events, dependency changes and successor view;
its transaction/replay mechanism is still to be specified.

| Operation | Preconditions | Postconditions |
| --- | --- | --- |
| `new_evidence` | Resolved source/reading references, explicit context and view, category checks. New evidence can also be retained while checks are unresolved. | Preserve the source and proposal; admit only supported predicates at the requested layer. Recompute candidate membership even when the new candidate is not selected. A new source cannot silently replace the incumbent. |
| `narrow` | Same target, units, assumptions, interpretation/election choices and branch scope; new constraint has independent admissible support. | Child domain is the intersection of old domain and supported new constraint. Retain both supports. Empty intersection creates a scoped conflict; unknown intersection remains unresolved. Domain enlargement or changed assumptions is not narrowing. |
| `correct` / `supersede` | Exact predecessor, supported explanation of the error/correction and a review event naming which assertion/meaning/constraint is replaced and in which view. | New immutable version removes only the superseded active constraint in the successor view and supplies its replacement. No monotonic-domain claim. Original source and frozen views survive; other constraints still apply. A different economic target normally requires a new record, not replacement. |
| `select_assumption` | Authored proposition and alternatives, explicit rationale, scope and time view; requested layer permits conditional assumptions. | New conditional branch retains the original uncertainty and selected assumption. Unselected assumptions impose no constraint. Selection cannot establish factual truth or missing accounting permission. |
| `select_election` | Dated authority, eligibility and consistency/transition obligations established within scope; selection distinguishes assumed treatment from evidenced historical election. | New election version/conditional branch plus its obligations. Actual postings remain subject to accounting checks. Unsupported permission admits no treatment branch. |
| `revise_estimate` | Named old estimate, new method/input/judgment versions, same estimand or explicitly new target, valid information view and method applicability. | New estimate and lineage, invalidated dependent measurements/results, frozen prior estimate. Record how information date differs from measurement date; accounting treatment of the revision remains separately determined. |
| `revise_policy` / `revise_driver` | Named predecessor, explicit changed rule/domain/information set/scenario and rationale, capability and information checks. | New selected assumption/version. Reassess all affected paths and membership; no automatic narrowing, causal effect or change in historical weights. Old paths remain frozen. |

For a supported correction of [20,60] to [10,90], keeping background [0,100],
the new domain is [0,100] intersect [10,90]=[10,90]. Intersecting with the
superseded [20,60] would retain a known obsolete restriction. This example
stipulates that the correction replaces that entire bound and that no other
constraint survives; actual mixed-support claims must identify precisely which
part is corrected. A frozen prior query still returns [20,60]. (UA07a.)

Invalidation uses reverse dependencies, not only selected-record IDs. If the
old reading feeds interpretation I, fact constraint C, family F and query Q,
changing the reading invalidates I, C, F and Q for *current* reuse. If an estimate
E also uses C, its result is affected as well. Adding a rival source changes the
selection-population revision even if the winning candidate stays identical;
F and Q depend on that revision. Missing dependency metadata makes current reuse
unestablished. Unrelated families may be reused only with complete unchanged
dependencies and matching query/time views. Invalidation changes reuse status,
not the bytes of old results, and is not evidence that every old number changed.
A frozen export identifies its original version, assumptions and supersession
status; it never advertises an old result as current. (UA07b.)

The provenance/derivation graph must resolve all references and must not contain
unsupported cycles. A reference to a version that does not exist is a dangling
reference, even if a record with the same logical name exists. Cyclic economic
relations are a different matter: x+y=100 can jointly constrain both variables
in one supported constraint block without either being independently known.
Mutually constrained quantities do not imply a cyclic derivation or independent
random variables. A simultaneous block names its formula, variables and external
support; an unsupported block is retained as unresolved. Category substitution
(e.g. replacing an unknown fact with an election under the same identity) is
invalid. A legitimate cross-category inference creates a distinct record with
explicit derivation and category-specific admission. (UA08.)

## U4. Interactions, failures and next operations

| Contract | Exchange and responsibility |
| --- | --- |
| Evidence E1/E3/E4 | Supplies occurrences, extraction and interpretation review, context, conflicts and assumptions. Admission returns the predicate/assumption actually used, its scope and unresolved supports. Retention is independent of admission; no source text is overwritten. |
| Time T1–T3 | Supplies cutoff-qualified evidence and byte-vintage/review views. Admission checks information access at measurement and decision dates, and records later-information revisions separately. Unknown availability cannot pass a historical-information requirement. |
| Histories H1/H2/H5 | Consumes jointly admitted predicates, selected assumptions and membership revisions. Returns conditional families/candidate regions and unresolved obligations. Partial support never validates membership in the complete accounting-history family. |
| Accounting | Must establish package authority, eligibility, recognition, measurement and revision consequences. Receives retained unsupported treatments separately from selected permitted elections; returns layer-specific applicability and journal obligations. |
| Language/IR | Must encode category payloads, exact domains/units, simultaneous blocks, dependency types and explicit operation transitions. Unknown versions cannot be decoded using a convenient existing variant. These JSON examples do not select a runtime format/library. |
| Persistence | Owns atomic version/view creation, idempotency, stale-write detection, migration and reverse dependencies. Frozen reads must be distinguishable from current reuse; a failed write leaves the old view current with an explicit failure receipt. |
| Interfaces and failure semantics | Show requested layer, retained content, disposition, conditions, time view, unresolved obligations and next action. Preserve partial results on capability/resource failure. Harmonize reason codes without converting unsupported/unknown into false or successful computation. |

A refuted candidate can be reconsidered under a supported correction or an
explicitly different conditional view; its refutation remains valid in the old
scope. An unsupported treatment needs authority/applicability work. A dangling
reference needs correction, not solver execution. A local conflict needs source,
context or interpretation review; arbitrary deletion of the inconvenient source
is not a repair. Solver timeout preserves the expression and unresolved region.
It cannot establish evidence refutation or global family infeasibility.

Full scenario-mode semantics, stochastic information filtrations, joint measures,
likelihood identity/reuse, probability normalization and conditional outcome
payloads are the next uncertainty task. No operation in U3 changes probability
weights. A future implementation that attaches a model must identify that later
contract and preserve unavailable outcome regions rather than renormalizing
successful computations. The proposed interface here is a dependency obligation,
not a claim that these semantics are already complete.

## U5. Matched encoding alternatives and default audit

Both alternatives receive the same UA01–UA08 requests and must return the same
expected dispositions, retained records, family effects and invalidations.
Neither representation is credited for accepting more unsupported cases.

| Same fixture question | Tagged variants with shared header | Generic record with versioned validator registry |
| --- | --- | --- |
| UA01: fidelity versus meaning | Two explicit payload variants within disclosure readings require different fields/reviews. | A category/subtype validator must distinguish them; generic fields alone cannot. |
| UA02: continuous domains | Domain variant carries exact endpoints/symbolic predicates; no finite-only restriction. | Domain-validator version must be pinned; changing it cannot silently change endpoint meaning. |
| UA03: permission versus asserted choice | Election variant requires authority and eligibility references; absence returns unsupported. | Registry validator must enforce the same sourced permissions, not trust arbitrary fields. |
| UA04: estimate/date revision | Estimate transition checks input versions and view separately from fact narrowing. | Operation and category validators must be coordinated and versioned together. |
| UA05: future information | Policy variant exposes decision inputs and their information roles. | Extensible policy validator must still use the shared information rule; extensions cannot bypass it. |
| UA06: unweighted future domain | Law attachment is explicitly optional; this slice rejects probability operations. | Registry must separate domain admission from a later probability plugin and report its absence. |
| UA07: corrections and invalidation | Shared revision header and typed dependency edges support the declared successor/frozen distinction. | Shared validator protocol must supply all changed dependencies; an extension that omits them cannot support reuse. |
| UA08: substitutions and cycles | Closed category discriminants reject wrong payload/identity changes; simultaneous blocks have their own representation. | Unknown/new categories are easier to register but must return unsupported until reviewed migration/admission semantics exist. |

Provisionally prefer tagged payload variants with the shared header for the
initial specification: the six categories have materially different admission
conditions, and explicit variants make missing conditions visible to reviewers.
A versioned registry remains credible where later domains need additional
payload types. The choice does not select Python classes, JSON as a wire format,
a database or a solver. Either needs an extension/migration policy preserving
old record interpretation, adapter conformance and unknown-version retention.
Changing category meaning requires a new version and explicit migration, never
reinterpretation of frozen content. This is a semantic comparison, not an
implemented benchmark or performance ranking.

| Material choice | Provenance and justification | Failure mode | Smallest diagnostic | Status |
| --- | --- | --- | --- | --- |
| Six categories, explicit semantic subtype | MC10/P15 G15 and E1; different admission rules | Treat extraction fidelity as factual truth | UA01 competing reading/meaning | User requirement; encoding proposed |
| Full shared context/view/header | E3/T1/H1/H5 and MC25/27 | Mix periods, views or source with assumptions | Inspect every fixture's context and layer | Proposed integration |
| Immutable versions and reverse membership dependencies | H5 and MC27 | Old query reused after a new rival source | UA07 closure and frozen read | Proposed behavior; transaction mechanism open |
| Intersect only for same-assumption narrowing | Set definition in U2/U3 | Widening called narrowing or correction overconstrained | UA02/UA07 exact endpoints | Derived semantics in declared example |
| Exact closed real intervals | Synthetic exercise, to expose continuous uncertainty | Accidentally infer cents or reported-rounding behavior | Check interior 1/3 in [0,100] and stated endpoints | Fixture convenience only |
| Synthetic P and multiply estimator | Bounded interface examples, no new authority research | Mistake permission or formula for accounting law | Check synthetic labels and pending accounting obligations | Convenience, never production default |
| Tagged variants | Matched U5 comparison | Hard-to-extend closed enumeration or concealed custom fields | UA08 unknown version and future migration review | Provisional proposal |
| Unweighted scenarios and no implicit independence | MC08/12/14/18 | Invent probabilities from enumeration/confidence | UA06 absent-law outcomes and deferred attachment | Required preservation; measure design unfinished |
| P06 finite facts, finite weighted innovations, hold-only policy and restricted methods | Historical `admit_uncertainty` at lines 539–686 | Promote probe limits into universal requirements | Compare UA02, UA05 and UA06 with those branches | Historical baseline only; not adopted |

## U6. Scope of completion and source support

The companion fixture file specifies eight groups with explicit inputs, support,
expected results and preserved records. Its sources are synthetic by construction.
Local diagnostics check document/reference consistency, example arithmetic and
dependency closure. They cannot establish that a future implementation enforces
the rules, that source-grounded treatments are valid, or that forecasting works.
Independent substantive review and human acceptance remain pending.

The requirements come from `docs/plans/accounting-mission-requirements.md`
(MC04/08/10/12/14/18/25/27) and the accepted P15 `coverage.json` rows MC10/12/14
and G15. Interactions use proposed evidence-contract-v3 E1/E3/E4,
time-contract-v2 T1–T3 and history-families-contract-v1 H1/H2/H5. The inspected
P06 implementation is historical counterevidence for accidental defaults, not
accounting authority. No new academic theorem or official accounting permission
is asserted; the two interval relations are derived in U2/U3 and the estimate
multiplications are stipulated arithmetic.

Completion of this admission slice leaves the whole uncertainty contract
unfinished. The next separately reviewed task must specify justified joint
measures, conditioning, probability updates and conditional outcome payloads,
then reconcile both groups before registering uncertainty as a complete proposed
contract. Accounting, language/IR, persistence, interfaces and failure semantics,
initial-profile selection and dependency order also remain open. All fourteen
P15 decisions and MC01–MC35/G1–G18 remain active. Optional bounded result review
must not become a prerequisite that blocks the next reviewed drafting task;
full independent P16 result review remains required before phase acceptance.
