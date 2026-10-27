# P15 proposal audit

## Retained findings and their design consequences

The existing work supports a proposal built around traceable disclosures,
jointly admissible histories and explicit accounting operations. It does not
yet determine the product architecture. Source acquisition, source interpretation,
feasible reconstruction and accounting treatment answer different questions;
success at one does not supply the missing evidence at the next. In particular,
Core 0, exact rational arithmetic and SQLite are explored choices. Their
availability is useful evidence about possible contracts, not a reason to select
them as product defaults.

This opening integrates the saved P00–P14 register, the eight v2 assessments
(MC01–MC05, G11, G13 and G17), the MC25/G18 reconciliation and the MC07/G12
analysis. It preserves their partial requirement statuses and remaining
obligations. MC34's provenance repair is also retained. The history/uncertainty,
accounting/sector and language/research assessments are saved below. Matched
initial-profile comparison and the integrated assessment are also saved below.
P15 audit preparation is complete; full independent result review remains pending.
The original requirements and gaps are unchanged [S01–S03].

### Disclosure coverage must precede claims about company histories

The manuscript now gives a substantive procedure for filing-package coverage:
reconcile contents and statement indexes with headings, preserve parent and
child disclosure units, follow references, and record unavailable or ambiguous
targets and resource-limited exits. This repairs part of the older G11 omission.
It does not establish that every material assertion in a real package has been
interpreted. The Apple preparation has 125 monetary observations and 34 selected
bridges, while all 23 annual/interim notes retain unresolved meaning. Those
counts describe inspected work; they are not a denominator for semantic or
simulation coverage [S04–S05].

The earlier Apple manifest and later P02 work also describe different acquisition
states: P02 acquired the proxy and inspected selected Part III material after
the older manifest called it unacquired. The proposal must preserve both dates
and identify the remaining indentures, series instruments and omitted instruments.
It must not repeat an obsolete access limitation or infer package closure from
the later acquisition. MC01/G11 still need an acceptance package spanning annual,
quarterly and semi-annual reports, including missing continuations, reference
cycles, ambiguous targets and consequences for affected queries.

MC03 adds a distinct obligation. Permission to repurchase is an available action;
a conditional guarantee is an obligation only when its condition holds;
“substantially all” supplies no numeric threshold without a separately identified
assumption. Apple's swaps can change the economic exposure of fixed-coupon
notes. The combined note-and-swap position cannot inherit a fixed-rate restriction
from the note alone. Source wording, accepted extraction, interpretation and
constraint admission therefore need separate records. Literal-to-constraint
examples must carry scope, dates, exceptions and affected quantities, with
rejected translations as well as successful ones [S04–S05].

### Context and evidence clocks constrain admissible reconstruction

MC02's context is part of the quantity: entity, perimeter, basis, currency,
unit, period, calendar and dimensions determine whether arithmetic is meaningful.
Apple's displayed assets of 364,980 in millions can be represented exactly as
USD 364,980,000,000 while preserving the original display. That example does not
authorise addition across currencies, measurement bases, reporting periods or
perimeters. P03's bounded context checks supply useful rejection examples;
their declared exclusions remain exclusions [S04–S05].

Rounding is still an explicit design decision. P02's closed half-unit bounds
assume nearest rounding while recording an unknown tie rule. The general
contract treats an unknown rounding convention as an unresolved reading. An
unknown tie rule and an unknown convention are different information states.
The proposed answer in P15-E03 is to retain reported precision separately and
mark the half-unit interval as a conditional compatibility model unless source
evidence supports the convention. A solver can prove compatibility with that
assumed interval without proving the assumption true [S04].

MC04, MC05, G13 and G17 interact through correction and query admission. Reading
720 where the page says 120 is an extraction error. A later issuer correction
from 120 to 110 changes the assertion while leaving the earlier reading faithful
to its original document. P07 demonstrates local replacement, supersession,
transitive invalidation and retrieval of the old view. This supplies a concrete
mechanism for preserving the distinction; it does not decide whether a source
or accounting interpretation is correct [S04, S07–S08].

The temporal fixture makes a further distinction. Corrected H1 of 110 and FY of
260 in the compatible vintage imply H2 of 150. Subtracting the original H1 of
120 instead gives 140 and is rejected without an independently supported
compatibility relationship. Publication eligibility and system ingestion answer
different questions: a later-acquired archive can support an historical
availability query without proving what a particular database contained then.
P06's missing-ingestion fallback and optional byte-vintage requirement cannot
become silent product defaults. P15-E04 calls for explicit admission rules and
unresolved/rejected results when the claim requires missing evidence [S04].

The remaining design obligation is a layer-specific admission contract and a
source-backed conflict walkthrough, including unaffected conclusions and newly
invalid descendants. Retrospective policy/error changes and prospective estimates
also need authority-specific effective dates and opening bridges. Review status
must never be converted into a probability over alternative histories. These
are feasible internal specification tasks under MC35, not reasons to substitute
a broad paid review for unfinished preparation.

### Mapping and aggregation have more structure than label matching

The v6 MC07/G12 analysis credits existing specification: five mapping relations,
dated applicability, transformation and partition references, composition examples
and a partition schema already exist. Calling all of this absent would be wrong.
P06 implements a narrower subset: active direct edges for equivalence, component
and reclassification; guarded contextual compatibility; and finite partition
operations. A fixture provenance string and two differently spelled concepts
do not establish source-backed measurement equivalence [S06].

The proposal still needs relation-specific composition, complete applicability
predicates, versioned company-concept identity and ambiguity rules. P06 rejects
cycles over the supplied graph and does not traverse mapping chains. These
choices are not a general composition algebra. In particular, a directed
equivalence edge does not itself establish how reverse edges, non-overlapping
dates or competing paths should behave.

Finite partition checks are likewise conditional on the declared population.
They detect duplicate members, overlap and omission within that set. They do
not prove that the set contains every relevant economic item, identify aliases,
or measure an unknown residual. Product and geography totals classify the same
population along different axes; adding both totals double counts, while a
joint product-by-geography table remains unidentified without further evidence.
The full contract must bind population identity, quantities, periods, bases and
perimeters, preserve unallocated residuals and require an explicit transformation
or refusal for unlike measurements. Dated extension changes must propagate
through derived results without overwriting the original concepts [S06].

MC07/G12 remain partial. The retained v6 analysis has not received substantive
acceptance. Its exact claims and evidence are preserved rather than expanded
into general cross-company comparability or accounting validity.

### Persistence evidence informs contracts without selecting storage

The earlier claim that transactions and migrations were unimplemented is wrong
relative to P07. Its local single-writer SQLite probe commits state, journals,
measurements, dependencies and receipts transactionally. Retained fault cases
exercise rollback or a complete cursor around process interruption. Reopened
and uninterrupted runs agree for the 32-event Northstar fixture, and selected
journal/statement invariants have a separate verifier [S07–S08].

The comparison shares the P05 engine. It can demonstrate faithful persistence
and detect selected arithmetic inconsistencies while preserving a common engine
error. Schema 1-to-2 migration preserves decoded values during a representation
conversion; it is not a demonstrated accounting-policy migration. Stream checks
cover identity and domain separation, not stochastic outcome invariance.
Hardware power loss, distributed writers and general stochastic execution remain
outside this evidence.

MC25/G18 therefore need portable API inputs/results and errors, ownership of
evidence/model/run state, identity and version compatibility, exact canonical
examples and explicit durability limits. Formatting changes, evidence corrections,
branch permutations, duplicate events and independent-event reordering need
separate expected behaviours. Representation migration must be distinguished
from a semantic change requiring new model/run identity. Stochastic execution
needs generator/transform versions, coupling and branch-consumption rules; an
identity tuple alone cannot establish those semantics [S07].

The actual execution-1 result review accepted the bounded MC25/G18 reconciliation
and MC34 provenance/reporting repair, with no issues. That acceptance is recorded
here and in current coverage. It does not extend to MC07/G12, the other retained
assessments or full P15. Historical v7 resolution preserves the exact earlier
coverage bytes; it is not an exemption for current evidence hashes. The retired
ad hoc completion-file task is not a condition of proposal acceptance [S08–S10].

## What each historical phase contributes

The fifteen dispositions below retain the roles in the saved register [S05,
`/prior_work/0` through `/prior_work/14`]. “Source evidence” identifies the
principal contribution; P02 and P12 also contain exploratory code. P08 contains
authority preparation alongside its exploratory operation. “Unexecuted” follows
the retained phase states and contracts, not merely the absence of a filename.
Earlier bank, insurance and manuscript illustrations remain available as separate
inputs, but they cannot be presented as executed P09, P10 or P14 results.

| Phase and role | Supported contribution and scope | Limit and consequence for the proposal |
| --- | --- | --- |
| P00 — source evidence | The retained baseline verifies the frozen 192-report source release and bounded reference examples. | Acceptance concerns source preservation and stated checks. Preserve those inputs and define future semantic/accounting acceptance separately; a report or test count is not a completion criterion. |
| P01 — source evidence | One work record per accepted report retains source/extraction identity, basis passages, publication metadata and unresolved work. | Byte-specific historical availability, complete packages and adjudicated labels remain missing. Separate filing, publication, ingestion and byte-version evidence in query admission. |
| P02 — source evidence | Apple annual/interim preparation links selected quantities, contexts, notes, source bridges and incorporation work; its adapter is secondary exploratory evidence. | All 23 notes retain unresolved meaning. Specify quantity-to-source bindings, package obligations and linked unknowns, including debt/swap allocation, noncash movements and cohorts. Source preparation must remain useful without being called complete reconstruction. |
| P03 — exploratory probe | Source and typed declarations lower to shared Core0.1 IR with bounded package, binding, type and context checks. | Events, broad mappings, multiple entities/books/currencies/calendars and wider uncertainty are outside its profile. Keep explicit unsupported behaviour and matched authoring tasks; select the interface only after comparison, including shared-implementation risk. |
| P04 — exploratory probe | Declared templates and rational-linear/finite choices exercise joint constraints, strict endpoints, rounding and incomplete search, with finite/algebraic comparators. | No arbitrary-history discovery, general nonlinear inference or scaling result follows. Specify model scope and template provenance, endpoint attainment and honest Unknown/PartialSearch results independently of the solver. |
| P05 — exploratory probe | Northstar events produce linked journals and statements with checks for duplicates, atomic rejection, funding default, unsupported operations and internal failure. | Half-year accrual, simple tax and zero OCI are synthetic conventions. The Apple stress assumes exposure and is not an identified company forecast. Require a shared journal basis, failure classification and retention of failed branches and their original mass. |
| P06 — exploratory probe | Bounded contexts, mappings, partitions, evidence views, cumulative subtraction, uncertainty admission and query-dependent resolution interact. | Identity harmonisation is not general measurement conversion; finite domains and DCF conventions are assumptions. Specify query-sensitive resolution, revision dependencies and evidence for approximation error; do not generalise a guarded rejection into a conversion method. |
| P07 — exploratory probe | Local review, single-writer transactions, replay, invalidation and representation migration are demonstrated on the bounded company engine. | Shared-engine equality, process-failure tests and stream identities leave independent semantics, hardware durability and stochastic outcomes open. Derive portable identity, correction and recovery contracts without selecting SQLite. |
| P08 — exploratory probe | A synthetic Australian AASB compound-bond lifecycle has paragraph-based authority preparation; later EU work covers conditional scope/eligibility. | P08 remains needs_repair. A second applicable same-fact lifecycle is missing. P17 must establish jurisdiction/date/entity/contract applicability and complete both settlement outcomes before making a cross-regime comparison. |
| P09 — unexecuted | Its contract proposes bank credit/allowance, funding and capital work distinguishing IFRS 9, CECL, prudential rules and behaviour. | No P09 lifecycle or calibration result exists in retained state. Preserve source-specific timing, liquidity and capital obligations for P17 and a matched multi-period case. |
| P10 — unexecuted | Its contract proposes insurance general measurement, CSM, variable fees, transition, onerous groups, risk adjustment and reinsurance interactions. | Short-duration illustrations cannot set the whole insurance scope. Require multi-period gross/reinsurance examples and explicit uncertainty methods before treating these operations as specified and checked. |
| P11 — exploratory probe | Six matched source/typed cases execute through shared validated IR and a synthetic debt runtime, with independent arithmetic checks. | Zero external integrations completed. Authoring equivalence and interoperability need separate acceptance evidence; availability discovery and authored exchanges cannot establish upstream compatibility or usability advantage. |
| P12 — source evidence | Provisional source references, dependence/exposure records, scoring rules and finite chronology/workload exercises inform evaluation design. | Zero source-extraction tasks were evaluated. Dependent purposive issuer-years and tiny workloads support neither a clean heldout claim nor capacity/ranking. Require adjudicated source-to-result tasks and a realistic, predeclared evaluation protocol. |
| P13 — unexecuted | Its contract proposes eligible-vintage calibration and forecasting against naive and credible tuned comparators with uncertainty and veto rules. | No executed forecast comparison exists. Specify information sets, calibration targets, defensible joint weights and unresolved mass before empirical claims; conditional stress is insufficient. |
| P14 — unexecuted | Its contract proposes manuscript integration, rendered comparison with a protected baseline and internally prepared review questions. | No P14 integration/render result exists. P18 must preserve substantive obligations and source/PDF consistency; compilation and engineering review do not establish comprehension or human acceptance. |

Three qualifications matter particularly when this history is used to choose a
profile. First, P08's engineering repair is not the missing accounting comparison.
The later execution-1 record has 51 passing tests and no errors, but criterion 3
is incomplete and `phase_criteria_complete` is false. The EU disposition has
`admission_allowed=false`; compound classification/issuance and measurement/
settlement/note operations remain pending. The conditional FASB classification
and unresolved ASBE work cannot fill those gaps. The zero-byte v6 final-check
is unusable. The proposal must keep matched economic facts and both cash
redemption and maturity conversion, then complete applicable authority and
methods in P17 [S05, S11–S12].

Second, P11's actual AGREE review supersedes its result note's earlier “acceptance
pending” wording. It accepts an honest bounded result, including unavailable
engines; it does not establish five external integrations. The unavailability
finding concerns the captured interpreter/PATH/local-path scope, not permanent
infeasibility of Arelle, ACTUS, QuantLib, Docling or a ledger backend. ACTUS and
Ledger/hledger translators, inline-XBRL scale and physical PDF page/table
exchanges remain unfinished. P17's software-reuse assessment needs actual pinned
exchange evidence before promoting a dependency [S13–S14].

Third, P12's twelve chronology cases and fifteen small workload repetitions
address finite conformance. Four Apple references were prepared provisionally,
and no source-extraction task was scored. All nine issuer families had acquisition/
QA exposure, years are dependent, evaluated-model training exposure is unknown,
and semantic duplicates remain unresolved. Timing differences are descriptive;
no statistical ranking is supported. The historical review's temporary-directory
workaround is also environment-specific and supplies no wider performance
evidence [S15–S16]. These findings inform MC28/MC33 and G5/G10 evaluation
obligations; they do not close them.

The retained register's review chronology distinguishes P02–P07, P11 and P12
bounded internal acceptance from P00/P01 baseline/work-register acceptance, for
which it found no separate independent result-review record. The broader P15
history synthesis still needs substantive review [S05, S17].

## Evidence boundaries and remaining sequence

| Evidence class | What may be carried into the proposal | What remains to be established |
| --- | --- | --- |
| Specified design | Inspected manuscript rules, record shapes, contracts and declared unsupported cases. | Compatible whole-product semantics and complete requirement interactions; mention of a topic is insufficient. |
| Exploratory code | Concrete candidate operations, interfaces and failure cases in the historical profiles. | Architecture selection and contracts for broader supported operations. No product module is created by this audit. |
| Tested invariants | Retained deterministic results for their exact inputs, versions and fault models. | Conformance of any future implementation or broader profile. These historical suites were not rerun here. |
| Accounting validity | Source-bound identities and synthetic journals under stated assumptions. | Applicable authority, eligibility, complete treatment/transition methods and appropriate substantive review. Balanced journals alone are insufficient. |
| Empirical forecast validity | Conditional stress and finite chronology checks. | Eligible historical information, identified assumptions, calibration, matched baselines and uncertainty evidence. No superiority or calibrated-forecast claim follows. |
| Human acceptance | Pending status. | Reader comprehension and acceptance of the governing design, separately from automated and internal review. |

The initial-profile choice remains open. The Initial-profile comparison section
now compares corporate/shared-IR, typed-library-first, instrument-first and broad
sector-first on matched requirements. Interface and domain scope are separate
choices, so they may be combined. Retained work supplies examples and limits;
no architecture is selected. P15-E01–E14 make the unresolved decisions explicit.

The retained-findings, history-and-uncertainty, accounting-and-sectors and
language-research-integration groups are saved as bounded proposal-audit
contributions. The five previously generic gap obligations G2/G5/G8/G9/G10 now
name specific missing design, source and case evidence. Full substantive
acceptance remains pending, including MC07/G12; only the previously bounded
MC25/G18/MC34 review is accepted.

The profile comparison and final integration are saved below. All four P15
criteria are addressed as audit deliverables, with every original
MC01–MC35/G1–G18 obligation retained. The supervisor's full independent result
review is next, explicitly including MC07/G12. No ad hoc completion JSON is
required. Preparation and structural checks do not confer substantive acceptance.

## Entity, control and perimeter (MC06)

The manuscript separates legal books from a dated consolidation adjustment book.
In `08-modules.tex` lines 298–324, control is assumed for the worked acquisition;
80% ownership determines the illustrative proportional non-controlling interest,
not the control conclusion. Parent cash 60 and subsidiary cash 30 produce group
cash 90; investment 40 is eliminated against subsidiary equity 50, leaving NCI
10 and group assets/equity 110. The intragroup loan 10 is eliminated only for
matched obligations. Full disposal for 44 produces the illustrative gain 4 and
remaining cash/equity 104. These are specified arithmetic cases with no goodwill,
tax or acquisition remeasurement. The fixture's `/consolidation` fields record
these assumptions and expected values; they are not a dated accounting authority.

P06 provides a different kind of evidence. `Context` carries entity, perimeter
and perimeter version; `compatible_context` rejects mismatches rather than
mapping them away. Its retained conformance report includes MC06 among nine
observed obligations. This supports an exploratory compatibility check, not a
control-assessment or consolidation engine. `adapt_core_context` explicitly
requires a perimeter version and gross/net supplement because Core 0 omits them
(lines 833–842). The proposal must reconcile that representation boundary.
The retained MC07/G12 analysis already assigns general mapping semantics; this
section does not reopen that completed analysis.

P16 must specify persistent legal-entity identity, dated ownership links, a
separate evidence-backed control conclusion, perimeter versions and their
invalidation consequences for observations, histories and statements. P17 must
supply dated rule applicability, supported acquisition/disposal and NCI elections,
purchase allocation, tax/FX dependencies and adjustment-book operations with
source and rule references. Missing control evidence or unmatched intragroup
amounts remain unresolved inputs; no balancing entry can supply their meaning.
The accounting sections below assess those operations and authority in detail.
This completes MC06's current assessment, while G4/G7 and the accounting-method
obligations remain open. Neither the structural example nor P06 establishes
accounting validity or human acceptance.

## Joint histories and the meaning of complete search (MC08–MC09; G1/G3)

A history is a joint explanation of accounts, notes and dates. The manuscript's
construction procedure creates shared observation and contract variables,
instantiates declared event slots, and applies all accepted readings to one
formula. A named view restricts that family; it is not automatically a disjoint
economic hypothesis. P03 lowers the authored single-book debt expressions but
explicitly excludes general multi-entity compilation, reconstruction and finite
choices. P04 explores a separate bounded construction interface: explicit
registries and slots provide posting incidence and economic-state transitions;
shared economic IDs, exact contexts and original observation domains constrain
the same balances. Unknown rounding or unmatched observations remain obligations.
Neither prototype discovers an adequate template registry from an arbitrary filing.

The retained P04 observations support specific joint properties. Observation 7
examines 32 linked-choice cells, with two feasible and thirty infeasible;
observation 20 rejects incompatible marginal extrema and retains intersection
and union queries on the original family. These establish retained synthetic
examples, not a complete real-company reconstruction. Observation 9 records a
zero-budget search with sixteen unresolved cells and a one-cell search with
fifteen unresolved cells even though a feasible witness exists. The solver's
completion branch requires every finite cell decided and no unresolved matching
obligation. Its unvisited suffix retains the original formula. Existence of a
witness, complete search of declared cells and adequacy of the declared economic
scope are therefore three distinct conclusions.

G3 is partly repaired by an explicit change of variables. With disclosed debt
D in [99.5,100.5), nonnegative amounts F and V satisfy F+V=D; the one-year stress
interest is 0.05F+0.07V. The manuscript derives the attainable lower value 4.975
and unattained supremum 7.035. For D>0, alpha=F/D gives the equivalent fraction
representation; at D=0 alpha is undefined. A fixed threshold alpha>=a becomes
F>=aD only with known a and established positive D. This derivation supports that
rewrite, not a general elimination of unknown-by-unknown products. The retained
strict-bound and integer/rounding observations distinguish endpoint attainment,
posting quantisation and continuous analysis. Nonlinear constraints, unbounded
integer search and unknown solver replies remain outside exact certification.

P16 must retain the whole formula, identities, evidence view, ModelScope and
coverage accounting in every history-family interface, including failure replies.
P17 must specify how accepted real-disclosure readings nominate templates and
slots, how omitted structures are disclosed, and how context/source obligations
are discharged. A reviewable case must contain an included history, a rejected
joint combination and an economically relevant excluded history. The numerical
capability table must state sign/domain proofs for rewrites, integer budgets,
strict attainment rules and what survives unsupported or interrupted solving.
P18 must reconcile these narrower, explicit capabilities with manuscript phrases
that presently call the linear core the initial implementation; P16's profile
comparison still controls that proposal. G1/G3 stay open for those method and
coverage obligations. Their present defects do not erase the bounded P04 evidence.

## Uncertainty, aggregation and optional probabilities (MC10–MC12; G15/G16)

The six uncertainty categories now have more than names. P06's retained code and
category-specific rejection cases extend the earlier authored-debt admission
probe. Their scope is still a declared local registry and finite examples:

| Category | Inspected P06 admission | Remaining substantive obligation |
| --- | --- | --- |
| ExtractionReading | Accepted decision, resolved source and registered locator. | Preserve the original assertion and competing readings even when a reading or its accounting interpretation is rejected. |
| HistoricalFact | Accepted evidence, finite domain and evidence constraints. | General joint fact domains and contradictory/corrected evidence must propagate through the family. |
| AccountingElection | Package scope and effective dates, package permissions and eligibility evidence. | A dated authoritative rule and actual eligibility analysis must justify the package's content. |
| MeasurementEstimate | Named supported method, available dated inputs and checked input domain. | Specify method applicability and dependence; the local direct/observable/one-payment DCF methods do not cover sector valuation. |
| BehaviourPolicy | Only the hold policy; dated information references. | Design operating and management policies and their permitted information access. |
| FutureInnovation | Finite joint law, future period, driver coordinates and consistent measure. | Justify the law and dependence; real-world and pricing labels do not validate either distribution. |

These distinctions are exercised in accepted/rejected synthetic records, including
out-of-domain facts, ineligible elections, future information and measure mismatch.
They do not verify external accounting authority or probability calibration. P16
must define which operation narrows a fact domain, replaces a source reading,
changes an eligible policy or updates a probability measure. Dependent records
need invalidation and preserved old evidence views. P17 must ground permission
and applicability in inspected sources; an unsupported treatment remains evidence
of what was asserted, not an admitted alternative merely because it balances.

Aggregation is conditional on the query. The manuscript's additive transition
and reporting argument requires additivity for every admitted driver, plus
matching contract memory. P06 explores only unhedged fixed-rate bullet debt,
simple accrual, principal/interest outputs and horizons before maturity. It
retains constituent IDs and a signature covering query and constituents; a changed
horizon, scenario or output cannot reuse the old approval. The retained tests
compare aggregate interest 17/2 on principal 150 with direct summation and reject
insufficient grouping keys, maturity crossings and floating resets. They do not
prove an equivalence rule for guarantees, netting, inventory impairments or
insurance cohorts.

P06 also supplies a narrow analytic approximation certificate, improving on a
blanket statement that all approximate grouping is unevaluated. For nonnegative
principals P_i and horizon T, replacing fixed rates r_i by r* changes simple
interest by |T sum_i P_i(r_i-r*)| <= T sum_i P_i |r_i-r*|. The code checks this
triangle-inequality bound and compares the declared bound with a declared
tolerance; the retained case has error 1/2 and bound 3/2. This is an output-specific
deterministic guarantee under those assumptions, not empirical sector validation
or permission to reuse the tolerance. P16/P17 must specify contract/lot/cohort
memory, supported transformations, error units and admissible query domains;
retain detail for refinement and invalidate evidence when those domains change.
The prototype supplies an optional method candidate, not a default compression.

Probability is optional and attaches to a joint economic model. The manuscript's
fixed/floating illustration starts with weights 3/5 and 2/5 and interest 5 and 7;
stress alone leaves weights unchanged and gives illustrative mean 29/5. New
observed information with event likelihoods 1/5 and 4/5 yields masses 3/25 and
8/25, hence posterior weights 3/11 and 8/11. P04's finite-measure code requires
complete scalar coordinates with distinct atoms, nonnegative weights summing to
one, a justification field and single-use information-block IDs. It rejects a
zero normalising mass. These mechanics check a declared finite model; neither a
nonempty justification string nor a new block ID establishes empirical support
or prevents semantic duplication of the same source under different IDs.

The posterior example and missing-outcome example must stay distinct: the retained
posterior is 3/11 versus 8/11, whereas the separate summary retains complete mass
3/5 and unsupported mass 2/5 and returns no unconditional mean. Unsupported
outcomes cannot disappear by renormalisation. Overlapping query labels are events
on the same atoms, not extra mixture components. P16 must bind measures, information
blocks and conditional denominators to family identity. P17 must supply a justified
joint example including historical uncertainty and future innovations, show the
unweighted alternative, and define evidence updates without double counting totals
and components. Continuous densities, reparameterisation and downstream numerical
validation remain separate method obligations; no probability or sampler default
is selected by these finite examples.

## Scenarios, available information and incomplete outcomes (MC14/MC18; G6/G14)

The specification distinguishes three operations. Exogenous stress supplies
hypothetical drivers without changing historical evidence or weights.
Observational conditioning needs actual evidence and a joint model with a
positive normalising mass. Structural intervention needs an explicitly named
structural model and a supported equation replacement; an accounting identity
alone does not supply that model. Core 0 text specifies exogenous stress only.
P06's information-view guard explicitly rejects conditioning and intervention;
P05 separately explores finite conditioning through the P04 measure. The proposed
interfaces must therefore advertise capabilities per operation, not infer a
common implemented capability from similar scenario names.

The information examples distinguish a forecast distribution available to a
manager or measurement procedure from an outer simulation's realised future.
P05's behaviour and measurement consumers both check roles, economic/publication/
ingestion dates, and explicit stress declarations. P06 checks dated references,
announced paths and real-world/pricing measure identifiers. These checks support
the bounded callers; they are not an access boundary for arbitrary plugins.
P16 must define the information capability supplied at each decision and
measurement date, restrict direct future-state access, and specify inner valuation
versus outer realised randomness. P17 must give paired manager/measurement cases,
including allowed announced stress, forbidden future information, an observed
likelihood update and unsupported intervention. Pricing-to-real-world conversion
requires a justified transformation, not merely different identifiers.

P05 supplies a transparent conditional operating example for G6: authored drivers
change sales, collections, purchases, supplier payments, payroll, capex, tax and
financing through economic events, journals and statement bridges. That is useful
engineering evidence about one declared mechanism. Synthetic timing, simple tax,
zero OCI and no-borrowing conventions remain assumptions, and the fixed/floating
endpoint executions do not exhaust the continuous history family. The separate
Apple financing stress is conditional on an assumed effective exposure; it does
not infer that exposure or validate a forecast. P17 must expose each operating
relation, behavioural parameter, timing rule, funding constraint and calibration
source as an assumption or supported method. Empirical validation remains future
work; no new scientific run is part of this audit.

The retained results show why failure type is part of the economic answer.
P05's joint stress has complete mass 1/2, economic funding default mass 1/4 and
unsupported mass 1/4. Its malformed-branch example retains rejected mass 2/3 and
complete mass 1/3. Both return no unconditional mean. Conditioning on the declared
synthetic observation produces complete mass 3/4 and default mass 1/4, with zero
unsupported mass because of the supplied likelihood, not silent removal by the
executor. Default preserves an unpaid obligation and last committed state;
unsupported operations and internal execution failures are distinct. P04 similarly
labels bounds from incomplete search as explored-cells-only and retains unattained
endpoints. These are exact statements about retained finite examples.

The full result design is still larger. P16 must reconcile P04's search statuses,
P05's Rejected/InternalFailure/EconomicFundingDefault statuses and the normative
RunResult vocabulary. Every requested cell needs its joint history condition,
scenario/path/date, context, exact/symbolic/sample/bound status, missing-output
reason, and dependency consequences. A sampled minimum is not a family bound;
separate marginal endpoints need not coexist in one path. Weighted runs must
account for all mass by outcome and execution status, while unweighted runs
retain every unresolved region. A conditional-on-success statistic must be a
separate requested quantity with its denominator, not an alternative spelling
of the unconditional answer. P17 must supply correlated multi-output and partially
executable worked cases, full-statement paths, funding/default consequences and
unknown/cancelled/numerical-failure examples at the proposal level. Accounting
validity, empirical forecast validity and human acceptance remain unestablished.

## Corporate operations, statements and group boundaries (MC13/MC15/MC16; G4)

Northstar supplies a connected corporate example: sales on delivery, collections,
purchases, payments, consumption of inventory, payroll, plant, depreciation,
interest, tax, dividends and closing. The execution chapter gives their
preconditions and journal templates, and separates economic events from treatment
selection and postings. These are substantive specifications. They are stronger
than the original G4 inventory of duties, but apply to a declared synthetic
company, not a dated IFRS, US GAAP or ASBE corporate package.

The distinction from the retained calculation is precise. In
`scripts/check_repair_conformance.py:26–60`, `post` receives postings already
chosen by the fixture, checks their signed sum and event identity, then changes
account balances. Northstar's historical `state_changes` are empty. A passing
atomic-rejection example therefore demonstrates rejection of an unbalanced batch;
it does not verify recognition eligibility, available inventory, the economic
state update or rollback across economic state, journals and explanation edges.
Those remain part of MC13's proposed contract. A future operation must expose its
payload, rule applicability, measurement, economic effects and postings together.
The proposed commit checks must reject an overcollection or unavailable inventory
even when the proposed debits equal credits.

Northstar's accounting scope is explicit: one homogeneous good costing 5,
aggregate half-year events, fixed depreciation lives, 20% tax on positive profit,
no deferred tax, and no leases, returns, FX, subsidiaries or OCI. These assumptions
come from the teaching case and justify its arithmetic; they are not imported
company defaults. A first acceptance example should expose any accidental reuse
of them by presenting a service obligation, a return, a loss with tax-basis
differences or a foreign-currency invoice and requiring either a supported
separate treatment or an explicit unsupported result. Aggregate dates also cannot
answer daily liquidity questions without a finer event schedule.

The historical statement figures are internally traceable. Revenue 260 less
cost of sales 165, payroll 42, depreciation 11 and interest 5 gives pre-tax profit
37; tax 7.4 gives profit 29.6. Opening equity 70 plus profit less dividends 9 gives
90.6. Operating cash 45.6, investing cash −22 and financing cash −9 give a cash
increase of 14.6 and closing cash 74.6. Assets 220.6 equal debt 100, payables 30
and equity 90.6. Total comprehensive income equals profit only because OCI is
excluded. These are the manuscript/fixture values and the retained report's
annual-statements check. The reporting oracle uses preassigned cash classes;
reconciling their sum does not establish that a real transaction was classified
correctly. MC16 still needs versioned income/OCI, cash/noncash, equity and note
mappings, including closing once, mixed payments and cash-policy elections.

The separate consolidation case assumes control of an 80%-owned subsidiary,
already measured net assets and no goodwill or tax. It specifies elimination of
investment 40 against subsidiary equity 50, leaving NCI 10 and group assets 110;
a matched intragroup loan of 10 is eliminated. Full disposal for 44 gives gain 4
and remaining cash/equity 104. The retained checker verifies the total/NCI and
disposal arithmetic; it does not execute the full dated control, acquisition or
intragroup matching procedure. MC06's saved assessment remains applicable.
Unmatched dates/currencies and unknown purchase allocation cannot become balancing
entries. The required foreign-currency case T12 names an invariant, while the
inspected corporate/consolidation examples supply no complete FX roll-forward.

P17 must join operation-level rules, dated authority and full expected statements
in one reference package, carrying a correction and a perimeter or currency change.
Revenue/performance and invoice/settlement timing, costing, leases, impairment,
current/deferred tax, currency remeasurement/translation, acquisition and disposal
must each have a supported method or a specific later-profile obligation. The
proposal should preserve noncash acquisitions, NCI, exchange effects and separate
elimination books in the mappings. This connects G4 to source lineage in G5,
measurement/perimeter compatibility in G12 and state resolution in G16 without
claiming those gaps are closed. Product modules and accounting-validity judgments
remain held; P15's contribution is the source-backed boundary and next methods.

## Instruments and dated reporting treatments (MC17/MC19)

The contract and accounting records must remain distinct. The manuscript stores
principal, proceeds, terms and rights alongside carrying amount, classification,
effective interest and fair-value disclosures; equity also has a dated quantity
register. Its zero-coupon example raises 100 and accrues to 105 then 110.25 before
redemption. Its ordinary-equity example issues ten shares at 12 with par 1,
separating cash 120, legal capital 10 and premium 110. Neither example establishes
that every instrument qualifies for those treatments. Splits, dilution, repurchases
and EPS require the share schedule, not only monetary equity or closing shares.

Actual P08 provides a narrower, useful lifecycle. Its economic facts fix a
synthetic issuer, AUD functional and contract currency, proceeds/fair value 100,
two annual coupons of 5, principal 100, a comparable nonconvertible yield of 10%
and conversion into ten ordinary shares at maturity. Under its admitted
Australian AASB issuer profile, liability is 5/1.1 + 105/1.1² = 11050/121 and
residual equity is 1050/121. After the first coupon liability is 1050/11; after
the second it is 100. Redemption settles that liability for cash; maturity
conversion instead transfers it to equity and issues ten shares. Retained AASB
132 AG30–AG32 concerns the issuer's compound instrument, the comparable-liability
measurement and maturity conversion. It does not supply the holder's treatment.

The source register uses the 31 December 2022 AASB 132/9/7 compilations for
Australian Tier 1 for-profit calendar 2024/2025 cases, with no optional early
adoption of subsequent amendments. AASB 132's retained cover specifies annual
periods beginning from 1 January 2023 to before 1 July 2026. These are concrete
source and period restrictions, not universal IFRS authority. The inspected
`corporate_financing_v1.py` checks reporting context and rejects non-functional
currency, non-January annual starts, other conversion terms and excluded features.
It computes the narrow events and commits only after its balance/funding checks.
It excludes fees, tax, modifications, default and additional options. No general
contract engine, market yield estimation or real issuer eligibility is established.
The yield, fair-value proceeds and funding are synthetic inputs whose provenance
must remain visible in any reuse.

The second-regime comparison is incomplete. The canonical P08 result preserves
one `supported_bounded` AASB row and unresolved US GAAP, ASBE and EU-endorsed IFRS
rows, with null amounts for the unresolved treatments. The later historical
checker records 51 passing engineering tests while criterion 3 and overall phase
completion remain incomplete/false. It does not turn the missing lifecycle into
an accepted comparison. The saved prior-work register therefore correctly retains
P08 as an incomplete exploratory probe.

There has been real US-source preparation. The locally retained FASB ASU 2020-06
communicates amended 470-20-25-12 treatment of convertible debt in its entirety as
a liability unless the embedded-derivative or substantial-premium exceptions
apply. Its cover expressly distinguishes an ASU from the authoritative
Codification. The saved inspection records a visual check of amendment markup;
the extracted text mixes deleted and inserted words. Its supported finding is a
conditional classification difference from the AASB residual-equity split, not
admission of the synthetic US contract. Full ASC 815-15 and 815-40 eligibility,
general debt measurement and extinguishment, subsequent amendments and the
issuer's adoption history remain specific internal tasks. No US amount is inferred
from the conditional rule alone.

The EU v6 disposition similarly records conditional scope/eligibility preparation,
not a complete basis. `admission_allowed` is false and substantive applicability
review is pending. Its unresolved groups identify compound classification and
issuance; measurement, settlement and notes; actual amendments/corrigenda; and a
later matched lifecycle. Publication year alone does not settle original versus
later retrospective application. The applicability review is a dependency for
admission, not a reason to abandon other authorised research. Official ASBE/CAS
22/37 edition and transition support remain uninspected in the retained record;
prior access failures are preserved and were not rerun here.

The manuscript's inventory comparison is also usefully narrower than three fully
supported standards packages. For ten units at 5 and ten at 7, selling twelve
costs 64 under FIFO, 80 under LIFO and 72 under periodic weighted average, leaving
56, 40 and 48 respectively. The inspected AASB 102 paragraphs 25/27 support the
FIFO/average formulas for their stated inventories. The manuscript cites
Caterpillar's disclosed LIFO policy and a provisional ASBE reproduction; neither
supplies complete current US/Chinese authority. The same physical deliveries and
cash payments can have different permitted book values, so G12 concept mappings
must not erase the measurement difference. Inventory write-down/reversal also
requires retained cost and impairment history, connecting the method to G16.

P17 must produce a dated treatment matrix and matched economic-event cases with
operation-level authority, eligibility, elections, transition and disclosure rules.
The minimum comparison retains the same terms, rates, quantities and both maturity
outcomes while varying only the supported reporting context. It must explain an
actual supported difference where one exists; adding a second jurisdiction does
not guarantee a different result. Fees, modification/derecognition, early
repurchase, induced conversion, FX and default/recovery need their own methods or
specific later-profile entries. Remaining revenue, tax, lease, FX and group-method
queues in P08 should feed this proposal research without restarting held product
implementation. Accounting validity and human acceptance remain separate decisions.

## Company extensions and bank methods (MC20/MC21)

The proposed extension discipline is substantive: standard packages delimit
permitted treatments; sector packages add economic state and operations; company
packages supply evidenced labels and elections. The language chapter requires an
acyclic override graph and exactly one maximal applicable recognition rule.
No rule, conflicting rules and an unresolved symbolic guard produce distinct
unsupported, conflict and unknown-applicability outcomes. A company package may
override only a declared extension point within the standard's policy domain.
Loading it last cannot make a mandatory accounting rule disappear.

MC20 remains partial because the sector arithmetic is not an admission test for
that extension system. P16 must specify manifests, state types, effective context,
elections, dependencies and version invalidation; P17 must provide state and
method examples that exercise them. A permitted election, a forbidden mandatory
rule override, a cycle, competing rules and a guard with insufficient evidence
should each have an explicit expected disposition. The invalid company example
must fail even if its postings balance. This builds on G12: a source label whose
measurement, gross/net scope or perimeter differs is not made equivalent by a
company mapping. P15 does not select Core 0 merely because its demonstration
registry exists.

The bank case supplies a useful structural distinction. Origination of 20 adds a
loan and customer deposit; transfer of 15 then consumes settlement cash. Interest
received 6, deposit interest 2 and a supplied allowance change from 0.8 to 2.4
leave cash 21, gross loans 120, allowance 2.4, deposits 117 and equity 21.6.
Net assets are 138.6. Runoff 25 draws 4 from a facility capped at 10 and leaves
cash zero; runoff 40 instead leaves 9 unpaid. The manuscript retains that
obligation and default outcome rather than assuming additional funding.

The retained oracle computes these figures directly from supplied fixture inputs.
It checks the shortfall and facility arithmetic; it does not implement the bank
lifecycle or derive an allowance from observed loan data. The illustrative
prudential calculation deducts 2 from equity and applies a 75% risk weight to
loans, giving capital 19.6 and RWA 90. These inputs are teaching assumptions,
expressly not Basel defaults. No jurisdictional buffer, eligibility, exposure
classification or calibration is established. P09 remains unexecuted in the
saved historical register; the manuscript example must not be described as its
completed result.

The richer loss expression in the manuscript is a proposed calculation under
declared scenario/default-time probabilities, discount factors and conditional
exposure-times-severity expectations. Its dependence structure is relevant to the
core: replacing the conditional expectation of EAD times LGD by a product of
unconditional means would change the target. This expression alone does not choose
IFRS 9 stages, CECL horizons, ASBE classification, cash-shortfall timing or the
information legally and empirically available at a measurement date. Nor does the
single-horizon PD×LGD×EAD illustration supply the full accounting allowance.

P17 must specify those choices and a dated movement bridge for origination,
derecognition, transfers, assumption changes, currency and write-offs. It must
separate accounting measurement from forecast probability calibration and the
management funding policy, and reconcile accounting equity/perimeter to the
applicable prudential calculation. Repricing, deposit runoff, collateral,
encumbrance, settlement and default examples need operation-level treatment and
explicit unknowns. Cohort aggregation must preserve the credit, liquidity and
repricing attributes that affect the requested scenario; this is the concrete
bank obligation under G16, not an assertion that one average exposure is sufficient.

## Insurance measurement and the remaining sector obligation (MC22; G7)

The insurance illustration supplies a genuine gross/ceded roll-forward under
explicit restrictions. Both policies and treaty cover one year and begin together;
service is uniform; there are no acquisition cash flows, investment components,
significant financing effects or onerous remaining coverage. Claims and recoveries
are expected within a year of the claims being incurred. AASB 17 paragraphs 53(b)
and 69(b) apply separately to issued contracts and reinsurance held, and paragraphs
62–62A govern treaty recognition. Short policies alone do not establish treaty
eligibility. The retained Australian compilation has the same stated 2023-to-before-
July-2026 annual-period window; it is not blanket current IFRS authority.

Premium 120 and capital 20, less ceded premium 24 and claims paid 30, plus recovery
cash 15 leave cash 101. Half-year service releases gross revenue 60 and ceded
expense 12. Claims 40 plus an assumed gross risk adjustment 2, less payments 30,
leave an incurred-claims liability 12. Expected recovery 20 plus separately
assumed transferred risk 1, less receipts 15, leaves a claims recovery asset 6.
Together with ceded remaining coverage 12, assets are 119; gross remaining
coverage 60 and incurred claims 12 give liabilities 72. Profit 27 increases equity
to 47. The retained dossier checker supplies signed journal sequences as well as
these totals, so its evidence is more specific than a balance-sheet equality.
It still checks stated assumptions, not a real insurer's eligibility or estimates.

The independent ceded assumptions matter. The dossier's counterexample changes
transferred risk from 1 to 1.5 while leaving gross risk unchanged: recovery assets
become 6.5 and profit 27.5. A separate assumed non-performance reduction of 2 gives
recovery assets 4 and profit 25. AASB 17 paragraphs 63–64 distinguish reinsurer
non-performance from transferred non-financial risk. A blanket rule that halves
all gross balances computes the wrong quantity for these cases. The coverage and
claims components here are an internal movement decomposition, not a claim that
each must be a separate face line. The risk inputs are assumptions; no actuarial
estimation has been established by their exact journal reconciliation.

The chain-ladder example is a separate method illustration. Its triangle
(100,150,180), (120,180), (140) gives factors 1.5 and 1.2 and remaining projections
36 and 112, totalling 148. Inspected Mack sections 2–3, equations (1)–(3), set out
conditional development means, independence across origin years and a variance
relation. The paper explicitly discusses the missing final-factor variance and
additional assumptions for it. One final development observation in the tiny
example cannot determine that variance empirically. This audit makes no claim to
have re-established Mack's full error theorem; the source supports the specific
assumption and uncertainty boundary inspected here. The point projection supplies
neither a predictive distribution nor an accounting risk adjustment.

MC22 therefore remains partial. P17 must specify actual contract/treaty grouping,
recognition, boundaries, service/claims/recovery timing, onerous and loss-recovery
operations, and non-performance/transferred-risk methods. General measurement
needs fulfilment cash flows, discount/finance effects, risk adjustment, CSM,
coverage units and attributed movements; variable-fee and transition approaches
and asset interactions need their own operations or specific later-profile tasks.
P10 is unexecuted. A proposed sequence for these quantities cannot stand in for
its methods or calculations. Feasible internal fact collection, authority review
and competing calculations precede any narrow professional question; no engagement
is authorised or initiated here.

G7's remaining obligation is consequently concrete across domains. P17 must
complete the dated standards matrix and genuinely supported matched treatments;
the admitted instrument lifecycle and missing modifications/options; bank
allowance, funding and prudential bridges; and insurance eligibility, measurement,
reinsurance and uncertainty. P16 must preserve the extension boundaries and state
needed by these methods. G5 requires eventual source-to-result explanations,
G12 requires basis/perimeter/measurement-compatible mappings, and G16 requires
cohorts that retain guarantees, timing and dependence. Staging an initial profile
can defer operations with explicit limits; it cannot turn the existing teaching
cases into whole-sector support or remove those broader obligations.

## Language, solver and review contracts (MC23–MC27; G2/G17)

The proposed common representation can separate authoring convenience from financial meaning. The architecture chapter already gives typed ordinary code a credible role: a schema, database and disciplined library can implement the same financial semantics. XBRL supplies reported facts and contexts; a ledger records admitted transactions; a rule language can express dated policy; a probabilistic program requires an explicit probability model. These are useful components with different responsibilities. Their limitations do not by themselves establish a benefit from a new textual language. The chapter's IR-first implementation decision must be reconsidered by P16 alongside the other initial profiles, because it predates the proposal-first instruction.

P03 provides evidence for a much narrower claim. Its typed and text frontends preserve a bounded debt program's fields, contexts, bindings, assumptions and constraints through a shared compiler. Selected generated fields also feed exact interest calculations. That supports consistency for the exercised authoring task, but common compiler logic can preserve the same mistake in both frontends. Independently constructed expected results and semantic-negative cases therefore matter in addition to agreement. No journal execution, general package loading, source-conflict reconciliation, broader uncertainty semantics or human authoring advantage follows. P16 needs matched tasks for disclosure correction, contextual quantity checking, alternative histories and dated accounting policy before specifying a fair later authoring evaluation.

The old G2 finding must be narrowed. Core 0 revision 2 includes exact rational encoding, context equality, domain rules and a complete named built-in table; the IR schema now includes the formerly missing history, probability, scenario, review and result records. These are specified behavior. P03 instead supports one bounded DemoDebt profile and explicitly marks other declarations unsupported. For example, the general contract defines dimensional simpleInterest, while the lowering profile excludes its general use and checks selected debt calculations separately. P16 must make the relationship explicit: which constructs are admitted, how they lower, how package capabilities are resolved, which semantics are checked statically, and which runtime/result/error cases must agree. Schema acceptance alone does not answer those questions. Source maps, original literal spelling and semantic identity also have separate jobs and must survive the same cases.

The numerical boundary is equally consequential. In P04, strict-cell feasibility precedes closure optimization; an endpoint is then checked against the original inequalities. Partial search reports only the explored cells' bounds. Debt amounts F and V with F+V=D avoid silently introducing a product of two unknown quantities when the disclosed total is rounded. Dividing by D, or multiplying an inequality through by D, requires a proved nonzero sign; otherwise the proposed linear method does not apply. Disclosure rounding constrains possible reported amounts, whereas posting quantisation changes the journal amount at a declared stage. Unknown rounding remains unresolved. These rules are meaningful bounded method evidence, but nonlinear operations, arbitrary symbolic rounding and unbounded integer search remain excluded. P17 must classify actual accounting formulas against this boundary, and P16 must carry infeasible, unsupported, resource-limited, unbounded and incomplete outcomes through to reports without conflation.

Local review already has more than a list of states. The P07 profile and tests show extraction rejection, accepted repair, later correction, incompatible alternatives, transitive invalidation and access to old frozen views. A late-created descendant of a superseded reading is also rejected in the current view. G17's saved assessment is retained. What remains is the complete analyst-facing case across layers: accepting a literal as correctly extracted does not accept its interpretation, and accepting an interpretation does not establish an accounting treatment. P16 must connect evidence requirements and permitted transitions to each layer, with ownership of dependency edges and explicit reuse rules. P17 must prepare actual competing interpretations and their consequences. The bounded persistence tests neither decide the storage architecture nor establish human adjudication or accounting validity; MC25/G18 retain their separately reviewed limits.

## Research support and reusable software (MC29–MC31; G8/G9)

The repaired literature record is useful because it separates decisions that previously looked alike. The 179 unique forward-query candidates now have individual title/metadata dispositions. The first entry, a provenance survey, is explicitly relevant but deferred until richer provenance is required; it is no longer silently dismissed as outside the core. Selected backward links identify their literal source anchors, while technical support remains in a different ledger. This corrects the old blanket-screening defect without claiming that every candidate's method and appendix has been read.

The catalogue contains 32 archived papers and four source-blocked works. All 32 listed PDF hashes matched in this audit. The unavailable catalogue entries are McCarthy (1982), Caiani and colleagues (2016), Imielinski and Lipski (1984), and Tamer (2010); their technical claims remain prohibited by the support records. A local text file or rejected download with a similar name cannot substitute for verified primary text. The original paper collection and financial-report release are preserved. New sources must retain edition/version, legitimate retrieval, hashes, inspected technical anchors and correction status. Integrity is evidence about the bytes, not the correctness or applicability of the argument.

The existing support boundaries should guide P17's research. For example, the archived source for Mernik, Heering and Sloane is the December 2003 CWI report SEN-E0309 corresponding to their 2005 publication. Its inspected comparison sections treat application libraries as credible competitors and discuss the costs and limitations of standalone languages; they supply no measured result about AccDSL. The support record anchors this claim to the working paper rather than assuming that its pagination or every argument is identical to the published version. The positive-provenance support record excludes general negative, nonlinear and probabilistic accounting operations. Extending either local claim requires additional technical argument. P17 must connect its chosen reconstruction, aggregation, accounting, bank, insurance and forecasting methods to inspected assumptions, derivations and relevant appendices, with official code reviewed where available. Important competing and negative results need a supported disposition. Citation counts, venue metadata, a downloaded paper or a populated ledger do not decide an architecture or establish research completion.

The software evidence has a similar distinction. Official snapshots expose potentially useful interfaces: Arelle facts carry context references and units, for example. The tool ledger also records licences and mutable branch-version limits. P11 then attempted bounded discovery and retained adapter conventions, but its structured result records zero completed external integrations. Arelle, QuantLib and Docling were absent from the recorded interpreter; the ACTUS executable was absent from its captured PATH. No local ledger engine was selected. These are distinct reasons for the recorded unavailable results. The audit does not infer that these tools are generally unavailable or inadequate. Six matched frontend tasks are authoring evidence and cannot fill this integration gap. The retained code's success count is tied to actual adapter pass status, so discovery cannot be counted as a successful external execution.

P17 must define each proposed adapter's accounting boundary. XBRL import must retain nil, duplicates, scale, taxonomy extensions and full contexts; PDF extraction needs physical page/region provenance and model-licence checks. Contract engines can produce economic schedules without deciding recognition. Valuation engines need dated inputs, conventions and calibration assumptions. Ledger exchange must preserve currencies, posting signs, rounding and identity. ACTUS service translation, Ledger/hledger wire translation, inline scaling and physical PDF locations remain explicitly unexercised in P11. Pinning a dependency, documenting malformed-reply handling and proposing independent fixtures are feasible design work; successful real-engine integration remains later execution evidence. No installation or external service was used for this audit.

## Cases, manuscript and acceptance work (MC28/MC32–MC35; G5/G10)

Northstar and Apple answer different questions. The synthetic company connects opening state, operations, alternative financing, a correction and future statements under explicit assumptions. Its expected postings make arithmetic inspectable, as the earlier accounting section explains, but do not establish a general recognition engine. Apple instead demonstrates acquired annual/interim source coverage, contextual facts and a bounded marginal exposure calculation. The manuscript expressly distinguishes inventory coverage from semantic formalisation and says that undisclosed contracts and unmodelled operations prevent a complete Apple forecast. P17 must supply the missing real-company chain from each material disclosure through jointly admissible histories, economic events, dated accounting treatment, journals and statements. Unknown facts must remain unknown throughout that chain.

P12 does not close that gap. Its preparation names four provisional Apple references and a source-evaluation denominator of zero. Its retained run passes twelve chronology cases and fifteen scheduled repetitions across five synthetic workload cells. These are finite deterministic engineering observations. The family/exposure record also describes nine purposive issuer families, dependent years and comparative disclosures, acquisition/QA exposure and three proposed test families concentrated in banking/insurance. Training exposure of an evaluated model is unknown; there was no extraction-model evaluation. Future empirical work must handle issuer-family dependence, mirrors/revisions, semantic duplicates and information cutoffs explicitly. The existing timing repetitions cannot rank methods or establish production capacity.

The manuscript already separates engineering, accounting and scientific validity. That distinction should govern P16–P19: canonical positive and semantic-negative results establish specified behavior; dated rules and actual contract facts support accounting treatment; historical vintages, matched baselines and uncertainty analysis support forecast claims. A naive or conventional baseline must receive the same information and scenario conditions as the proposed method. Single-interpretation and alternative-preserving variants must distinguish the effect of ambiguity representation from changes to the economic model. The provisional 10,000 observations, 100 event slots, 64 cells and 30 seconds per solver operation are workload hypotheses, not measured capacity or scientific defaults. Their exhaustion must leave explicit partial coverage.

This audit read the current PDF text on pages 12, 61 and 67 and inspected freshly rendered pages 12 and 67 without rebuilding the manuscript. The company example and its exposure limitation are legible; the workload page explicitly preserves provisional limits and separate release evidence. The retained author review reports the broader 79-page Version 1.2 render and baseline preservation. Those are historical inspection records, not a renewed claim that every current page has been reviewed here or that humans find the manuscript clear. P18 must integrate the new architecture/method decisions, preserve the mathematics and source qualifications against the protected baseline, record a stable-input build and inspect the resulting complete candidate. Independent implementability and ordinary reader comprehension still require their own review.

Mission traceability also depends on preserving the scope of prior acceptance. The MC25/G18 reconciliation and bounded MC34 provenance repair were accepted; MC07/G12 and full P15 were not. P08 remains incomplete and P09/P10/P13/P14 unexecuted. Earlier manuscript instructions to build the shared IR first are candidate choices for P16, not permission to proceed with product code. The matched initial-profile comparison and final integration are saved below; full independent P15 result review remains pending. Subsequent phases must carry every whole-product obligation forward even if the initial profile cannot execute it.

The remaining internal work is concrete. Complete real-company annotations and incorporation obligations; reconcile dated authority and transitions; prepare alternative interpretations and their journal/statement consequences; resolve software-contract and source-support questions; and repair the integrated manuscript. Only a residual judgment that this preparation cannot settle belongs in a later professional brief, with exact source paragraphs, proposed answer and counterargument. No such referral, fee or outreach is authorised here. Human feedback can remain pending while provisional drafting continues. Accounting judgment cannot substitute for empirical forecast or causal validation, and ordinary reader feedback does not require an accounting firm.

## Interactions retained for profile selection

| Connected gaps | Requirement interaction and next design obligation |
| --- | --- |
| G1/G3/G6/G14 | MC08–MC09/MC14/MC18/MC26: a declared history scope, solver capability and information cutoff must constrain the same scenario query; P16 must preserve incomplete results and P17 must supply the operating baseline. |
| G2/G12/G15 | MC07/MC10/MC20/MC24: language admission must preserve mapping populations, measurement contexts and uncertainty categories; broad record schemas cannot erase profile restrictions. |
| G4/G7 | MC13/MC15–MC17/MC19–MC22: common state and journal interfaces need operation-specific corporate, group, instrument, bank and insurance methods and dated authority in P17. |
| G5/G11/G13 | MC01/MC03/MC05/MC28: report-wide source coverage, narrative meaning and evidence clocks must reach the same real-company case; acquisition cannot substitute for semantic closure. |
| G8/G9 | MC23/MC29–MC31: method claims and tool reuse require inspected technical sources and actual interface evidence; neither metadata screens nor discovery counts imply implementation. |
| G16 | MC06/MC07/MC11/MC20: aggregation must preserve query-relevant contract memory, dependencies and measures; P16/P17 must state exact equivalence or bounded approximation. |
| G17/G18 | MC04/MC25/MC27/MC34: review layers, invalidation, identity and replay must preserve old views and distinguish semantic change from representation migration; bounded review remains bounded. |
| G10 | MC32–MC35 and all above: P18 must teach the integrated proposal and P19 must bind claim-specific evidence and decisions to every requirement; feasible internal preparation precedes external judgment. |

These connections retain all eighteen gaps without repeating completed source
analysis or declaring them closed. The following comparison applies them to
every alternative on the same terms.

## Initial-profile comparison

The four candidates answer two different questions: which accounting operations
should first be executable, and how should analysts author the same financial
meaning? Corporate/shared-IR is a domain and representation proposal.
Typed-library-first is an authoring proposal that can be combined with any of
the domain scopes. For a fair comparison below, its domain is exactly the
corporate candidate's domain. Instrument-first and broad sector-first change
domain scope; either could subsequently use typed constructors, reviewed
structured data or a textual frontend. Calling these four mutually exclusive
architectures would hide that distinction.

The comparison uses the original MC01–MC35 obligations [S01], the requirement
interactions above and the retained P00–P14 register [S05]. It compares proposed
coverage and unresolved dependencies, not measured development effort or product
performance. The manuscript's shared-IR decision is an existing proposal
(`04-architecture.tex`, lines 4–79). P03's `/unsupported` list and P11's
`/matched_frontends` expose the narrow common-compiler comparison; neither
establishes an authoring advantage. P05 supplies synthetic company operations;
P08's `/acceptance` remains incomplete. P09/P10 are unexecuted, and P12 scored
zero extraction tasks. These source boundaries constrain every candidate.

### Candidate definitions and scope held constant

**A — corporate/shared-IR.** Specify one bounded operating company from reviewed
disclosures and opening state through joint histories, dated events and a full
statement set. Keep evidence, model assumptions, treatment and results distinct
in a common typed representation. Revenue/collection, purchasing/payment,
inventory, assets, payroll, simple financing and closing each need a declared
operation and limitation. Northstar is a transparent synthetic witness; Apple
is source-preparation evidence, not its real-company equivalent. Textual
authoring is an option to evaluate, not part of this candidate's justification.

**B — typed-library-first over the same corporate domain.** Hold A's source
package, operations, information dates, history family and expected statements
fixed. Author declarations with typed constructors and reviewed structured
records, with a serialised common representation available for inspection and
replay. Defer a mandatory textual frontend. This still needs enforceable domain
validation, source bindings and clear diagnostics; arbitrary Python control
flow is not a substitute for specified financial semantics. Python itself is a
replaceable engineering choice. B can implement A's proposed meaning and cannot
claim reduced accounting work merely because parsing is deferred.

**C — instrument-first.** Begin with one explicitly scoped issuer/holder bond
or equity lifecycle and its source facts, alternative contractual histories,
dated treatments, cash events and connected journal/report contributions.
Issuance, accrual and both admitted settlement outcomes need complete methods.
P08's Australian compound-bond example nominates a case; its missing applicable
second-regime lifecycle prevents using it as a completed cross-standard oracle.
The company's other disclosures and operating state stay visible but unresolved.
This can be a first method slice; it cannot alone satisfy whole-company scope.

**D — broad sector-first.** Specify initial corporate, bank and insurer operations
with groups/FX and dated IFRS, US GAAP and ASBE applicability. The initial scope
would include the interactions that A–C stage later: loan cohorts, allowance and
funding dynamics, insurance gross/reinsurance state and sector-specific reporting.
The existing sector illustrations can challenge interfaces, but the missing
authority and multi-period methods remain initial-scope dependencies for D.
Representing every sector by a package name would not meet this definition.

### Matched obligation comparison

Each row applies one obligation to all four candidates. A narrower initial
operation set changes what is executed first, not the mission's eventual
acceptance requirement. An explicit later-profile assignment is required for
each deferred operation; “out of scope” alone is insufficient.

| Common obligation and requirements | A: corporate/shared-IR | B: typed library, same corporate scope | C: instrument-first | D: broad sector-first |
| --- | --- | --- | --- | --- |
| Complete evidence accounting, context and narrative (MC01–MC04/MC07; G5/G11/G12) | Reconcile a real annual/interim package, including unresolved notes and incorporated contracts; selected Northstar/Apple facts cannot stand for full semantics. | Identical package and denominators; constructors must retain original amounts, source locations and unresolved predicates without hidden defaults. | Retain company-wide coverage records while formalising selected contract facts; disclose every unmodelled note/statement dependency affecting the instrument or company totals. | Apply the same coverage rules to corporate, bank and insurer packages and their standards-specific contexts; a wider document inventory is not semantic coverage. |
| Joint histories and search scope (MC06/MC08–MC09; G1/G3) | Share accounts, contract state, control/perimeter and dates across operating and financing alternatives; declare template coverage and incomplete cells. | Same family and candidate-generation rules; library-created objects must not silently allocate separate unknowns for the same economic fact. | Link terms, proceeds, principal/carrying values and issuer/holder perspective through the lifecycle; compatible instrument histories leave corporate histories unidentified. | Add borrower/contract/cohort, control and insurance-group dependencies before search; finite synthetic choices cannot certify these broader families. |
| Economic events and treatment (MC13/MC15/MC17/MC19; G4/G7) | Specify operating preconditions, behaviour, recognition and atomic posting separately; Northstar's simple tax/accrual assumptions remain conditional. | Same events, rules and expected postings; host-language functions cannot bypass rule eligibility or atomic rejection. | A schedule or balanced issuance entry is insufficient: qualify treatment and complete accrual, redemption/conversion and unsupported modification/default outcomes. | Supply dated corporate, credit/allowance and insurance operations with transition rules; bank/insurance authority and methods are prerequisites, not presumed extensions. |
| Statements and notes (MC16/MC18/MC28; G4/G5) | Produce balance sheet, income/OCI, direct/indirect cash flow, equity and admitted notes from one path with closing/reopening rules. | Same mappings and outputs as A, independently expected as well as serialisation-equivalent. | Give instrument contributions and their bridge into a declared issuer/holder book; do not label isolated schedules as complete company statements. | Reconcile sector-specific statements, allowance/insurance movements and group eliminations from common dated state; differences in reporting basis remain explicit. |
| Uncertainty, economic memory and probability (MC10–MC12; G15/G16) | Keep fact, reading, election, estimate, policy and innovation distinct; preserve contract/cohort memory and unweighted alternatives. | Same categories, joint measures and refinement rules; ordinary containers must not imply independence or equal weights. | Preserve rights, resets, maturities, options and counterparties; use conditional valuation/stress only under declared measures, not probability from contract counts. | Specify cohort/default/recovery and insurance claims/reinsurance dependence, risk adjustment and aggregation error; teaching scalars cannot supply those methods. |
| Chronology, scenarios and outcomes (MC05/MC14/MC18; G6/G13/G14) | Separate economic/reporting/publication/ingestion times; show unavailable information, unsupported branches, funding default and numerical failure distinctly. | Identical cutoffs, status payloads and retained mass; library callbacks need explicit information access. | Preserve issue/reset/exercise/settlement dates and availability of terms; a pricing measure cannot silently become a company forecast law. | Add allowance updates, coverage/service/claims timing, reporting transitions and prudential dates while retaining those same cutoff and failure rules. |
| Review, persistence and recovery (MC04/MC25/MC27; G17/G18) | Preserve accepted layer, corrections, dependencies, historical views and exact-versus-tolerant replay; P07 does not select storage. | Same review actions and portable records; Python identity, pickling or shared-engine replay cannot define cross-implementation semantics. | Corrected terms or treatment must invalidate affected schedules and reports while old views remain reproducible; small scope does not remove recovery work. | Propagate corrections across cohorts, group books and reinsurance dependencies; define migration boundaries without overwriting earlier reporting bases. |
| Language and extension boundary (MC20/MC23–MC26; G2/G12/G16) | Define common types, capabilities and package contracts that retain state needed by later sectors; Core 0 is a candidate notation, not the boundary of the mission. | Defer mandatory text syntax but retain serialisable semantics, validation, versioning, errors and extension admission. Match authoring tasks to A before usability claims. | Require a demonstrated path from instrument state to corporate books and later sector state; reject an instrument-specific schema that erases exposure or context. | Specify common invariants and sector-owned operations without allowing overrides to bypass units, perimeter, chronology or source obligations. |
| Authority, research and software (MC19/MC29–MC31/MC35; G7–G9) | Prepare dated support for every admitted corporate operation and inspect proposed adapter boundaries. | Same accounting/research burden; bypassing a parser supplies no authority and proves no upstream tool integration. | Resolve actual terms, jurisdiction, edition and eligibility before matched treatments; ACTUS/valuation outputs need a separate accounting mapping. | Resolve all admitted standards and sector methods before claiming broad scope; missing US GAAP/ASBE or insurance authority limits the affected operation, not unrelated research. |
| Acceptance and mission continuity (MC28/MC32–MC34; G5/G10) | Couple synthetic exact outputs with a real source-backed path and explicit unknowns; preserve all later-sector obligations. | Same inputs/outputs and semantic-negative cases, plus matched authoring/correction tasks; no usability evidence exists yet. | Accept only the declared instrument slice and connected-book contribution; assign full corporate and sector methods to later profiles with explicit dependencies. | Require complete specified examples for each admitted sector and cross-sector interaction; a compilation, schema or three isolated demos cannot certify that scope. |

### Tradeoffs, dependencies and selection evidence

A exposes ordinary operating/financing interactions and the full statement
relationship within its proposed first slice. Its unresolved burden is connecting
real disclosure meaning and applicable treatments to that synthetic breadth.
It is disqualified as a whole-company claim if it substitutes Northstar's
authored transactions or Apple's debt stress for reconstructed real-company
histories. The Northstar fixture may remain a reference case without making its
tax, accrual or zero-OCI assumptions new defaults.

B can defer the textual grammar and its migration/training obligations while
retaining A's financial scope. That is a difference in specified deliverables,
not evidence of lower total cost or easier use. Hidden host-language behaviour,
unserialisable assumptions or validation confined to a particular caller would
disqualify its portability claim. P16 needs the same corrected-disclosure,
alternative-history, policy-change and failed-event tasks in both authoring
forms, with independently specified meaning and diagnostics. P03/P11 agreement
through shared code is insufficient; later human task evidence is needed for
learning-effort or usability claims. Designing the DSL remains an MC23 obligation
even if its implementation is staged later.

C makes contractual timing, issuer/holder perspective and treatment divergence
central to the first lifecycle. It postpones operating-company feedback and
therefore needs an explicit bridge into company history, funding and reports.
It cannot pass the whole-company acceptance criteria on instrument-only outputs.
P16 would need to justify that staging and specify the corporate continuation;
P17 must finish applicable matched treatments and settlement outcomes. The
existing P08 code and authority preparation confer no preference on C.

D brings sector interactions into initial admission rather than relying on
future compatibility. Its dependency set includes the missing bank and insurance
methods and applicable standards now, whereas A–C must give those methods named
later obligations. This dependency inclusion is a logical consequence of the
proposed scope, not an estimated duration or complexity ranking. D cannot be
selected as a broad executable scope while those operations have only illustrative
arithmetic. It remains useful as a challenge to whether narrower interfaces can
retain loan, insurance, consolidation and uncertainty state without redesign.

For every candidate, P16 must specify dependencies among source/context/review
admission, joint histories, dated event/treatment interfaces, statements and
result failures, correction/migration/replay and authoring/adapter interfaces.
History construction itself needs declared event templates and state transitions;
it cannot be specified independently of their accounting and economic meaning.
P16 must justify a candidate-specific dependency order rather than copy the old
prototype sequence. P17 supplies operation methods and authority; P18 integrates
the governing manuscript; P19 assesses proposal readiness. These are proposal
obligations, not permission to implement. No candidate currently has all that
evidence. This audit selects none.

The decisive proposed fixtures are common in purpose: an annual/interim source
package with an unresolved incorporated reference; two jointly admissible
histories that agree on past totals but respond differently to a scenario; a
correction that preserves an old view and invalidates only affected descendants;
an admitted event with independently expected postings and report effects; and
unsupported treatment, funding-default and interrupted-search replies retaining
their distinct meanings. Each candidate must state exactly which operations
it admits in these fixtures. Sector and instrument candidates add their named
lifecycle obligations; they do not earn credit for unexecuted generic labels.
For A versus B the inputs, domain, expected results and information dates must
be identical. Across A/C/D, record changed domain coverage explicitly rather
than presenting unlike task totals or runtimes as a ranking.

### Material decisions carried into P16

The existing decisions P15-E01–E05 (coverage, narrative admission, rounding,
chronology and review layers), E07 (dated authority), E08 (acceptance evidence)
and E09 (incomplete outcomes) apply to every candidate. They remain unresolved.
E06 now asks for separate domain and authoring decisions using the comparison
above. The following additional choices make consequential inherited assumptions
explicit; their proposed answers are hypotheses for P16/P17, not approvals.

| Decision | Proposed answer and credible alternative | Consequence and evidence needed |
| --- | --- | --- |
| E10: representation and authoring | Specify portable, inspectable financial meaning; compare typed constructors and textual notation on the same tasks. Alternative: library-specific state or a text-only semantic authority. | Decide which records and semantics are normative and how all admitted frontends preserve them; provide independent expected meaning, source locations, errors and migration examples. Reconsider exact IR/Python/Core 0 choices if they cannot express required state. |
| E11: numerical capability | Declare admitted formula fragments and partial/unsupported outcomes. Alternative: route all cases through one linear solver or promise an unqualified nonlinear engine. | Map actual corporate/instrument/sector formulas to numerical capability, with rounding, strict endpoints and budget semantics. Broader method promises require source-backed methods and acceptance examples, not a new solver default. |
| E12: entity and aggregation memory | Preserve entity/control/perimeter versions and query-relevant contract/lot/cohort state. Alternative: only aggregate account balances with later reconstruction. | Give exact safe/unsafe grouping and perimeter-change examples; specify lost exposure, refinement and invalidation before choosing storage/IR fields. |
| E13: scenarios and weights | Begin with explicit conditional scenarios and optional justified joint measures. Alternative: require a probabilistic forecast by default or report successful branches alone. | Specify operating behaviour, available information, conditioning denominators and unresolved mass. P13 is unexecuted; calibration and forecast comparisons remain separate empirical work. |
| E14: software and ownership of semantics | Keep source import, contract schedules, valuation, accounting rules and ledger exchange distinct, with pinned adapter contracts. Alternative: let an upstream tool define treatment or postpone all interface analysis. | Reconcile actual official interfaces, retained fields, losses and unavailable-backend behavior. P11's zero integrations cannot select a dependency; P17 prepares feasible internal evidence before professional questions. |

The default audit is therefore explicit. The common representation and
rational-linear fragment originate in the manuscript and P03/P04; they are
candidate design hypotheses with expressiveness/capability fixtures as their
early checks. Northstar and Apple are retained examples whose limitations must
be challenged by the real-company fixture. Python and local SQLite originate
in prototypes and remain replaceable convenience choices; portable-record and
replay examples test the relevant promises. No probability law, numerical
threshold, cost estimate or performance preference is inherited from those
choices. Structural checking can veto corrupt evidence, but only substantive
review can assess whether this comparison and the later selected contracts
meet the requirements.

The profile comparison is integrated with the requirement assessments and
historical dispositions. The full independent result review must assess it
alongside MC07/G12; earlier MC25/G18/MC34 acceptance remains confined to its
recorded scope.

## Integrated assessment against the four P15 criteria

The audit supplies a current assessment and a remaining design obligation for
all 35 requirements and 18 gaps. All 53 remain **partial as whole-product design
requirements** in `coverage.json`. Completing this audit does not change that
assessment. The current matrix is the row-level record; this note explains its
sources, interactions and consequences. The source index and matrix pin the
inspected files and locate the supporting passages, including evidence that
supersedes an older gap description without closing the wider obligation.

| P15 criterion | Completed audit contribution | Acceptance still required |
| --- | --- | --- |
| Every MC01–MC35 and G1–G18 assessed | One matrix row per requirement/gap, with assessment, located evidence, specific remaining work and design consequence; the substantive sections explain source coverage, histories, uncertainty, accounting, sectors, language, research and evaluation. | Independent review of these assessments and their interactions; later specification and method evidence remain required. |
| All P00–P14 classified honestly | Fifteen rows match the retained prior-work register. The historical synthesis distinguishes source evidence, exploratory probes and unexecuted phases, and reconciles actual review scope. | Review of whether the proposed consequences follow from that evidence; historical acceptance is not architecture approval. |
| Initial profiles and decisions explicit | Four candidates share ten obligation groups; accounting scope is held fixed for the authoring comparison and scope differences are disclosed for instruments/sectors. E01–E14 retain proposed answers, alternatives, consequences and next steps. | P16 must justify a proposed selection; P17 must support admitted methods. No candidate has been selected or ranked here. |
| Evidence and acceptance separated | The six evidence classes above distinguish specification, exploratory code, historical invariants, accounting validity, forecast validity and human acceptance. | Full P15 substantive review, later proposal review and actual human feedback each retain their own role. |

The most consequential interaction is between source coverage and history
completeness (MC01–MC09; G1/G11–G13). A preserved document, an accepted reading,
a declared history template and a feasible witness are different achievements.
Adding templates cannot repair an omitted contract unless its source obligation
and economic meaning are identified. Conversely, more acquired pages cannot
complete a history search. P16 must keep those populations and states distinct;
P17 must connect them in the real-company case required by MC28/G5. MC02's
rounding assumption and MC05's missing-ingestion/byte-vintage defaults remain
explicit E03/E04 decisions, rather than inherited admissions.

Mappings, aggregation and treatment constrain the same quantities (MC06–MC07,
MC11, MC13, MC16, MC19–MC22; G4/G7/G12/G16). A label mapping cannot perform
measurement conversion, a finite partition cannot establish a complete economic
population, and equal current balances cannot establish equal future exposure.
Control, perimeter, basis, event date and contract memory must survive those
operations together. P16 therefore needs common identity/context and capability
rules before selecting representation or storage. P17 needs applicable methods,
state changes and expected reports. The existing component arithmetic and
Northstar journals provide discriminating examples; they do not justify a
universal chart, general consolidation method or complete accounting package.

Corrections and uncertainty also meet at the history-family boundary (MC04–MC05,
MC08–MC12, MC14, MC18, MC25, MC27; G13–G18). A corrected extraction may invalidate
a constraint without changing the original source. A new issuer assertion may
change the eligible evidence view. Neither is automatically a probability update.
An admitted hypothetical scenario cannot reveal a future realised value to a
past decision, and an unsupported computation cannot disappear from the outcome
family. P16 must reconcile review layers, dated information, result identities,
partial-search states and retained mass; P17 must supply justified conditioning
and treatment examples. Replay equality through one engine is insufficient to
validate that combined semantics.

These interactions explain why neither the common representation nor the first
accounting domain is settled by historical code. MC23–MC26 and G2 require
specified meaning and failures across interfaces; MC29–MC31 and G8/G9 require
support for method and reuse choices. Shared-compiler agreement, metadata
screening and discovered tools cannot resolve those decisions. MC32–MC35 and
G10 require the resulting proposal to become a coherent, traceable and reviewed
manuscript while feasible internal preparation continues.

Historical limits remain unchanged in the assembled result. P08 has one bounded
Australian lifecycle and incomplete other-basis preparation; its later test pass
does not complete criterion 3. P09, P10, P13 and P14 remain unexecuted. P11's
AGREE accepts an honest bounded report with zero external integrations, while
P12's finite chronology/workload evidence supplies no scored extraction or
forecast validation. The MC25/G18 reconciliation and bounded MC34 reporting
repair retain their actual acceptance; MC07/G12 has no substantive acceptance
record. Full review must consider its existing composition/partition provisions
as well as its unresolved economic comparability, residual and dated-extension
obligations [S05–S17].

The next decision is whether independent review accepts this audit against all
four P15 criteria. After that acceptance, P16 can propose contracts and a staged
profile while retaining every later-domain obligation. P17 supplies the dated
methods, sources, competing interpretations and internally checked cases; P18
integrates and inspects the governing manuscript; P19 assesses proposal readiness.
All fourteen decisions still block the complete governing proposal. They do not
make the P15 audit unfinished merely because their assigned design work belongs
to a later phase. No architecture, product readiness, accounting opinion,
empirical forecast ranking or human acceptance follows from this submission.

## Source index

Source IDs identify the exact files and substantive anchors used above. The
retained claim ledgers also pin their underlying manuscript, code, fixtures and
historical results. Their hashes and anchors were checked against current files;
historical reports continue to describe their retained inputs. Checking a report's
identity does not rerun its old input set against today's mutable coverage.

| ID and retained source | SHA-256 | Substantive anchor |
| --- | --- | --- |
| [S01: accounting-mission-requirements.md](../accounting-mission-requirements.md) | `70806de8154b5a54b9c46d48801cbcc853bf451ac25d10d9fc534498742e2f01` | MC01–MC05, MC07, MC25, MC34–MC35 and their original acceptance obligations (lines 55–124) |
| [S02: gap-audit-2026-10-02.md](../../design/review/gap-audit-2026-10-02.md) | `ebd9edcc59b195c22ded6a1cb07a10ed8675a5ffc787f99a11f39d7571babcb5` | Question, baseline and skeptical audit; Findings G1–G10 |
| [S03: mission-gap-audit-2026-10-02.md](../../design/review/mission-gap-audit-2026-10-02.md) | `f42eba085886a9551d0a706c84945de4917f1abd8058a0080be7070f803e0d9c` | G11, G12, G13, G17 and G18; Completion consequences |
| [S04: p15-evidence-assessments-v2.json](p15-evidence-assessments-v2.json) | `a3d6b28f0c9c07621e85d684b5551b48fce6391cbdd49c42e3890aa9583077bb` | JSON Pointers /requirements, /gaps, /open_decisions; underlying sources have per-row hashes/anchors |
| [S05: p15-prior-work-v1.json](p15-prior-work-v1.json) | `779d8faffc5b74fa8567eb62a3b0639c969ebbe1949ff73f51e4397c11bc4396` | JSON Pointer /prior_work/0 through /prior_work/14; scope, limitations, design_consequence and evidence |
| [S06: p15-mapping-reconciliation-v6.json](p15-mapping-reconciliation-v6.json) | `d4ae4fb76f9fdfdba205875031c16583a5ea98045224495421a6ba3b98f3abc1` | JSON Pointers /claims, /row_assessments, /review_status, /test_provenance |
| [S07: p15-p07-reconciliation-v3.json](p15-p07-reconciliation-v3.json) | `5271dc109926a85422c0c4d7009534c6f61854bb13b48d9ffcc909f1821732c9` | JSON Pointers /claims, /remaining_obligations, /limitations |
| [S08: review_result-1.response.json](../../../data/accounting-master/runs/20261004T054134-68471e41/P15/execution-1/review_result-1.response.json) | `cd3067a48d7e3e1e03ac225b2dbe618776e359e9b59f226426883b7b270561d4` | JSON Pointers /summary, /assumptions, /residuals, /issues; bounded acceptance only |
| [S09: p15-mapping-historical-resolution-v7.json](p15-mapping-historical-resolution-v7.json) | `1ba919443a71170935f330558658a4f3df77bde813a702029bea810cdd5b0b1f` | JSON Pointers /entries, /resolution_rule; resolution of retained historical coverage |
| [S10: accounting-p15-execution-repair-20261004.md](../accounting-p15-execution-repair-20261004.md) | `d389d0e38822cea3a822545c3af8fb7b7db0b87e4a7a2be0b176e07633f3ca69` | P15 bounded substantive work; retirement of worker-created validator/completion prerequisites |
| [S11: checks.json](../../../data/accounting-master/runs/20261003T132627-949fe14f/P08/execution-1/checks.json) | `b09241082aef2699471e33b70fd219abdec724ee910fa996442a15ddd04e0fd0` | JSON Pointers /tests, /errors, /acceptance/criteria/criterion_3, /acceptance/phase_criteria_complete |
| [S12: applicability-disposition.json](../../design/research/p08-v6/applicability-disposition.json) | `6aa92a2d0891cba52b26cd5eb600380777f248e3464c70c44dec23594dafb223` | JSON Pointers /admission_allowed, /coverage |
| [S13: review_result-0.response.json](../../../data/accounting-master/runs/20261003T075910-81c6e8bb/P11/execution-0/review_result-0.response.json) | `a8fe514bd92e2df0e9f32f607af2ec3367fc0682e108409af6c278fb6e468def` | JSON Pointers /summary, /residuals, /verdict |
| [S14: integrations.json](../../../data/accounting-master/deliverables/P11/integrations.json) | `9995d01b1a9511ce23bf25b31e78207b824a3210ea037f2fc42f828b16721c28` | JSON Pointers /discovery_scope, /external_integrations_completed, /matched_frontends, /residuals |
| [S15: review_result-0.response.json](../../../data/accounting-master/runs/20261003T125342-ea7394f9/P12/execution-0/review_result-0.response.json) | `2ba825851f3c11401a60f6e9951a2c20f998c556e89aad3330b5184c9baccc10` | JSON Pointers /summary, /residuals, /verdict |
| [S16: benchmark.json](../../../data/accounting-master/deliverables/P12/benchmark.json) | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointers /preparation/protocol, /preparation/source_readiness, /runs/0/chronology_score, /repair_verification |
| [S17: p15-history-inspection-v1.json](p15-history-inspection-v1.json) | `e937f6880c4f5b5809d084e5e335ab5c36b9eb858c8b65ad7bb87d68afe7137a` | JSON Pointers /reviews, /unusable_captures, /scope; retained bounded review chronology |

Sources for Entity, control and perimeter (MC06) (current SHA-256; locators are substantive):

| Source | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 298-324 |
| `docs/design/fixtures/sectors.json` | `38c140d37b723bf908fc338d4fed9770273c68d593a002847f8ed807978df180` | JSON Pointer /consolidation |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 85-101 |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 191-258 |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 833-842 |
| `data/accounting-master/deliverables/P06/conformance.json` | `d6c81ba5296e856d6380c5abc561e6da0658b7e25079d44d37792ffbf0347a70` | JSON Pointer /observations/7 |
| `docs/design/spec/context-chronology-profile-v1.md` | `95eea33f44d40287a2f72b4adc68291fc3e0f864c7ffd48902e8e6a52c9e511b` | lines 1-23 |

Sources for Joint histories and the meaning of complete search (MC08–MC09; G1/G3) (current SHA-256; locators are substantive):

| Source | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/chapters/05-mathematics.tex` | `c0f4d7d9afe9256b0f26961423374c2fb7f897321ce5a1b0f43f0d0195e359b4` | lines 253-327 |
| `docs/design/chapters/07-execution.tex` | `33ed76b17a5e25cbc8dbf73945abec5318e37101f2d306f6648129f498296f28` | lines 28-63 |
| `docs/design/spec/core-contract.md` | `29b8195acfc2098312322731611baf9865a5c587b024e79d15a29ee346235c92` | lines 156-188 |
| `docs/design/spec/reconstruction-profile-v1.md` | `01936f104222bc635f7f20a8ca37c4ebb82aea139a403cb5b64a150739842df7` | lines 1-95 |
| `scripts/reconstruction_v1.py` | `ca38b7e6e96c005a96aaca080ff8a1ef4f57ab5e619f068a03173570e9d2fba8` | lines 56-176 |
| `scripts/rational_solver_v1.py` | `fd8b3c1cdf9cbdcef4650dddc422ff5ec321cd8e9dd69c2416bd529a1cdede3e` | lines 390-424 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/7 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/9 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/18 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/20 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /unsupported |

Sources for Uncertainty, aggregation and optional probabilities (MC10–MC12; G15/G16) (current SHA-256; locators are substantive):

| Source | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/spec/core-contract.md` | `29b8195acfc2098312322731611baf9865a5c587b024e79d15a29ee346235c92` | lines 227-274 |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 539-685 |
| `tests/test_accounting_p06.py` | `5bb66d65c3c7854a647d484baf4acb359f35c9d7fd06209a76a4bdb4a31dc1c9` | lines 171-219 |
| `data/accounting-master/deliverables/P06/conformance.json` | `d6c81ba5296e856d6380c5abc561e6da0658b7e25079d44d37792ffbf0347a70` | JSON Pointer /observations/4 |
| `docs/design/chapters/05-mathematics.tex` | `c0f4d7d9afe9256b0f26961423374c2fb7f897321ce5a1b0f43f0d0195e359b4` | lines 328-355 |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 746-831 |
| `tests/test_accounting_p06.py` | `5bb66d65c3c7854a647d484baf4acb359f35c9d7fd06209a76a4bdb4a31dc1c9` | lines 240-267 |
| `data/accounting-master/deliverables/P06/conformance.json` | `d6c81ba5296e856d6380c5abc561e6da0658b7e25079d44d37792ffbf0347a70` | JSON Pointer /observations/5 |
| `data/accounting-master/deliverables/P06/conformance.json` | `d6c81ba5296e856d6380c5abc561e6da0658b7e25079d44d37792ffbf0347a70` | JSON Pointer /observations/6 |
| `docs/design/chapters/05-mathematics.tex` | `c0f4d7d9afe9256b0f26961423374c2fb7f897321ce5a1b0f43f0d0195e359b4` | lines 357-386 |
| `scripts/reconstruction_v1.py` | `ca38b7e6e96c005a96aaca080ff8a1ef4f57ab5e619f068a03173570e9d2fba8` | lines 239-284 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/4/result/posterior |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /observations/4/result/mass |

Sources for Scenarios, available information and incomplete outcomes (MC14/MC18; G6/G14) (current SHA-256; locators are substantive):

| Source | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/chapters/07-execution.tex` | `33ed76b17a5e25cbc8dbf73945abec5318e37101f2d306f6648129f498296f28` | lines 285-315 |
| `docs/design/spec/core-contract.md` | `29b8195acfc2098312322731611baf9865a5c587b024e79d15a29ee346235c92` | lines 237-274 |
| `scripts/context_chronology_v1.py` | `64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62` | lines 688-712 |
| `tests/test_accounting_p06.py` | `5bb66d65c3c7854a647d484baf4acb359f35c9d7fd06209a76a4bdb4a31dc1c9` | lines 221-230 |
| `scripts/company_execution_v1.py` | `5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0` | lines 53-68 |
| `scripts/company_execution_v1.py` | `5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0` | lines 304-366 |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /obligations/information_access |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /runs/conditioning/summary |
| `docs/design/spec/core-contract.md` | `29b8195acfc2098312322731611baf9865a5c587b024e79d15a29ee346235c92` | lines 257-274 |
| `scripts/rational_solver_v1.py` | `fd8b3c1cdf9cbdcef4650dddc422ff5ec321cd8e9dd69c2416bd529a1cdede3e` | lines 390-424 |
| `scripts/company_execution_v1.py` | `5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0` | lines 104-128 |
| `scripts/company_execution_v1.py` | `5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0` | lines 198-210 |
| `scripts/company_execution_v1.py` | `5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0` | lines 339-366 |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /runs/joint_stress/summary |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /runs/branch_validation/summary |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /obligations/distinct_outcomes |
| `data/accounting-master/runs/20261003T024539-18803fb0/P05/execution-0/review_result-0.response.json` | `6f3cc89f86d5cb2bfa039e75c1cb6791ea12106f7483bb1778742bef0823ac0a` | JSON Pointer /residuals |

### Corporate operations, statements and group boundaries (MC13/MC15/MC16; G4) — inspected sources

| File | SHA-256 | Substantive anchor |
| --- | --- | --- |
| `docs/design/chapters/07-execution.tex` | `33ed76b17a5e25cbc8dbf73945abec5318e37101f2d306f6648129f498296f28` | lines 88-120 |
| `docs/design/chapters/07-execution.tex` | `33ed76b17a5e25cbc8dbf73945abec5318e37101f2d306f6648129f498296f28` | lines 226-284 |
| `docs/design/chapters/13-reference-company.tex` | `39377ec428ffb0188b9cf352aaab806c64ad4890862222a0ccd2694c34f5edee` | lines 6-63 |
| `docs/design/chapters/13-reference-company.tex` | `39377ec428ffb0188b9cf352aaab806c64ad4890862222a0ccd2694c34f5edee` | lines 99-161 |
| `docs/design/fixtures/northstar.json` | `3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e` | JSON Pointer /assumptions |
| `docs/design/fixtures/northstar.json` | `3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e` | JSON Pointer /historical_events |
| `docs/design/fixtures/northstar.json` | `3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e` | JSON Pointer /expected |
| `scripts/check_repair_conformance.py` | `bbaf540f38992bd9c10b8e809c79a87a28f3ddebfe10cf1df43d948f8da435f2` | lines 26-60 |
| `scripts/check_repair_conformance.py` | `bbaf540f38992bd9c10b8e809c79a87a28f3ddebfe10cf1df43d948f8da435f2` | lines 65-77 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/5 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/22 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 298-324 |
| `docs/design/fixtures/sectors.json` | `38c140d37b723bf908fc338d4fed9770273c68d593a002847f8ed807978df180` | JSON Pointer /consolidation |
| `scripts/check_repair_conformance.py` | `bbaf540f38992bd9c10b8e809c79a87a28f3ddebfe10cf1df43d948f8da435f2` | lines 179-182 |
| `docs/design/chapters/10-validation.tex` | `a4b9aa5846e0f694e888ba0a5cd3601994ce37ac4cadea0ffafdfd442e113e8a` | lines 52-55 |

### Instruments and dated reporting treatments (MC17/MC19) — inspected sources

| File | SHA-256 | Substantive anchor |
| --- | --- | --- |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 4-39 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 67-126 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 226-297 |
| `docs/design/chapters/07-execution.tex` | `33ed76b17a5e25cbc8dbf73945abec5318e37101f2d306f6648129f498296f28` | lines 173-208 |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /comparisons/economic_facts |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /comparisons/rows/0 |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /comparisons/rows/1 |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /comparisons/rows/2 |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /comparisons/criterion_status |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /acceptance |
| `docs/design/research/p08-v1/authority-register.json` | `db34b67c2b96d7c58e56e1094f1fb2358d9a0016933e0034ea34b892ad8193a9` | JSON Pointer /authorities |
| `docs/design/research/p08-v1/authority-register.json` | `db34b67c2b96d7c58e56e1094f1fb2358d9a0016933e0034ea34b892ad8193a9` | JSON Pointer /method_queue |
| `docs/design/research/p08-v2/source-inspection.json` | `1d6f201f382d5c459ca45f14ebd66876769069492d34b00a4a064b856833005d` | JSON Pointer /supported_finding |
| `docs/design/research/p08-v2/source-inspection.json` | `1d6f201f382d5c459ca45f14ebd66876769069492d34b00a4a064b856833005d` | JSON Pointer /missing_provisions |
| `docs/design/research/p08-v6/applicability-disposition.json` | `6aa92a2d0891cba52b26cd5eb600380777f248e3464c70c44dec23594dafb223` | JSON Pointer /admission_allowed |
| `docs/design/research/p08-v6/applicability-disposition.json` | `6aa92a2d0891cba52b26cd5eb600380777f248e3464c70c44dec23594dafb223` | JSON Pointer /coverage |
| `docs/design/research/p08-v6/applicability-disposition.json` | `6aa92a2d0891cba52b26cd5eb600380777f248e3464c70c44dec23594dafb223` | JSON Pointer /unresolved_groups |
| `scripts/corporate_financing_v1.py` | `3a9e0e64a0048e995ae1534de8e4e3d1da6cc3870d48d09637a1257ca4adb07d` | lines 126-145 |
| `scripts/corporate_financing_v1.py` | `3a9e0e64a0048e995ae1534de8e4e3d1da6cc3870d48d09637a1257ca4adb07d` | lines 148-193 |
| `scripts/corporate_financing_v1.py` | `3a9e0e64a0048e995ae1534de8e4e3d1da6cc3870d48d09637a1257ca4adb07d` | lines 239-275 |
| `docs/design/research/standards/aasb132.txt` | `aa280d780cc2020cef4d5f7220b4523fb7e68a6bf2e93b298c95929499e53a1a` | lines 6-12 |
| `docs/design/research/standards/aasb132.txt` | `aa280d780cc2020cef4d5f7220b4523fb7e68a6bf2e93b298c95929499e53a1a` | lines 1355-1375 |
| `docs/design/research/standards/aasb102.txt` | `fb83cfe516a411efa42440d081eb9eb6e00d39d5beb2d6489f0fb54e009b001d` | lines 319-333 |
| `docs/design/research/p08-v2/fasb-storage.txt` | `519247ddef09d13c42c663e7a413d9c6b5366d0408da8d724b63467389ed80dc` | lines 21-27 |
| `docs/design/research/p08-v2/fasb-storage.txt` | `519247ddef09d13c42c663e7a413d9c6b5366d0408da8d724b63467389ed80dc` | lines 1604-1617 |
| `data/accounting-master/runs/20261003T132627-949fe14f/P08/execution-1/checks.json` | `b09241082aef2699471e33b70fd219abdec724ee910fa996442a15ddd04e0fd0` | JSON Pointer /acceptance |

### Company extensions and bank methods (MC20/MC21) — inspected sources

| File | SHA-256 | Substantive anchor |
| --- | --- | --- |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 41-65 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 128-168 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 198-224 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 328-374 |
| `docs/design/chapters/06-language.tex` | `238aa4b5030a988de53d443fcf38fb78a6a39a4971b8e3951f29922369e6aea8` | lines 188-200 |
| `docs/design/chapters/06-language.tex` | `238aa4b5030a988de53d443fcf38fb78a6a39a4971b8e3951f29922369e6aea8` | lines 225-236 |
| `docs/design/fixtures/sectors.json` | `38c140d37b723bf908fc338d4fed9770273c68d593a002847f8ed807978df180` | JSON Pointer /bank |
| `scripts/check_repair_conformance.py` | `bbaf540f38992bd9c10b8e809c79a87a28f3ddebfe10cf1df43d948f8da435f2` | lines 164-170 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/38 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/39 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/40 |
| `docs/design/review/repair-conformance.json` | `f2b3fd3f987d074040abccb4f2bdb9f2794d42050f07d5eb5977318a67ab9136` | JSON Pointer /checks/41 |

### Insurance measurement and the remaining sector obligation (MC22; G7) — inspected sources

| File | SHA-256 | Substantive anchor |
| --- | --- | --- |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 170-195 |
| `docs/design/chapters/08-modules.tex` | `0233ce79b44029dde240bec32c960813ae3493ac2fa8a62435e7169d940a4b84` | lines 376-436 |
| `docs/design/fixtures/sectors.json` | `38c140d37b723bf908fc338d4fed9770273c68d593a002847f8ed807978df180` | JSON Pointer /insurer |
| `docs/design/review/accounting-dossiers/insurance.md` | `426960092c9c199eb3f5eb77596668585ac2208ded2d07e81da45a0a735eefb9` | lines 1-84 |
| `docs/design/research/standards/aasb17.txt` | `fbdab1cd07400226bf4cc312f2cecbef4d20ed78b131620c31217942b0d568fe` | lines 6-12 |
| `docs/design/research/standards/aasb17.txt` | `fbdab1cd07400226bf4cc312f2cecbef4d20ed78b131620c31217942b0d568fe` | lines 689-697 |
| `docs/design/research/standards/aasb17.txt` | `fbdab1cd07400226bf4cc312f2cecbef4d20ed78b131620c31217942b0d568fe` | lines 758-787 |
| `docs/design/research/standards/aasb17.txt` | `fbdab1cd07400226bf4cc312f2cecbef4d20ed78b131620c31217942b0d568fe` | lines 845-854 |
| `scripts/check_accounting_dossiers.py` | `de62d224e2ef9757161360bd25718d1be7577e4bb4c0c4eff23f44b5321d5709` | lines 69-94 |
| `docs/design/review/accounting-dossier-checks.json` | `d5581c67257877bced27535a699c5d13da930e52013ca7f1048997ea8a21dc0a` | JSON Pointer /scope |
| `docs/design/review/accounting-dossier-checks.json` | `d5581c67257877bced27535a699c5d13da930e52013ca7f1048997ea8a21dc0a` | JSON Pointer /calculations/insurance_base |
| `docs/design/review/accounting-dossier-checks.json` | `d5581c67257877bced27535a699c5d13da930e52013ca7f1048997ea8a21dc0a` | JSON Pointer /calculations/insurance_separate_transferred_risk |
| `docs/design/review/accounting-dossier-checks.json` | `d5581c67257877bced27535a699c5d13da930e52013ca7f1048997ea8a21dc0a` | JSON Pointer /calculations/insurance_nonperformance_loss |
| `docs/design/research/text/mack1993.txt` | `aeaf702772ab2904fb8374b2c7f33f572c0d76cd51f6a819d554e7fd258797ab` | lines 79-109 |
| `docs/design/research/text/mack1993.txt` | `aeaf702772ab2904fb8374b2c7f33f572c0d76cd51f6a819d554e7fd258797ab` | lines 181-207 |
| `docs/plans/accounting-proposal/p15-prior-work-v1.json` | `779d8faffc5b74fa8567eb62a3b0639c969ebbe1949ff73f51e4397c11bc4396` | JSON Pointer /prior_work/9 |
| `docs/plans/accounting-proposal/p15-prior-work-v1.json` | `779d8faffc5b74fa8567eb62a3b0639c969ebbe1949ff73f51e4397c11bc4396` | JSON Pointer /prior_work/10 |

### Language, solver and review contracts (MC23–MC27; G2/G17) — inspected sources

| File | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/chapters/04-architecture.tex` | `62f6ed2ad4c7e1f8cf2ae98ac65a3be3ebf915b53022a47d0a9fd02fb277dfe6` | lines 4-79 |
| `docs/design/spec/core-contract.md` | `29b8195acfc2098312322731611baf9865a5c587b024e79d15a29ee346235c92` | lines 20-156 |
| `docs/design/spec/core-ir.schema.json` | `fd45e425b4f47b0350a508fb5997874ca26af384fe174ef7544e746ee075461c` | JSON Pointer /$defs |
| `docs/design/spec/core0-lowering-profile-v1.md` | `cb1186c0b2b48d5ef61860dbb0b34443a4a3a1530572a682d8fbd8f1fc91c432` | lines 46-118 |
| `data/accounting-master/deliverables/P03/conformance.json` | `9010b3b3eeeb289e48a9624a661b6123a9cccde4e2ba2b28c869b7725d4151cd` | JSON Pointer /unsupported |
| `scripts/core0_frontends_v1.py` | `5bdf680b61ac2e9e726037cb1207c62f094aedfd24434a66444b3f8ff9be054f` | lines 265-292 |
| `docs/design/spec/reconstruction-profile-v1.md` | `01936f104222bc635f7f20a8ca37c4ebb82aea139a403cb5b64a150739842df7` | lines 66-95 |
| `data/accounting-master/deliverables/P04/conformance.json` | `6dfa1c4d232aa6ddbf14997ef69c23534cad224a52826d0c7865adcd82fcf551` | JSON Pointer /unsupported |
| `scripts/reconstruction_v1.py` | `ca38b7e6e96c005a96aaca080ff8a1ef4f57ab5e619f068a03173570e9d2fba8` | lines 58-87 |
| `docs/design/spec/review-persistence-profile-v1.md` | `84ac789c026ce68f81b30e7c148f08518d6404ef9a64bf0b05cc05b667ffd0aa` | lines 58-77 |
| `tests/test_accounting_p07.py` | `bbe3e8c1bc19e32740c3778a67998964d000685a57fe87d7dee3d41281025f0c` | lines 226-274 |
| `data/accounting-master/deliverables/P07/recovery.json` | `45bb362d7fc7df90d46ecc520e323fbdd0020c2b08ef0bf3978e7a73b1ca9f71` | JSON Pointer /obligation_coverage/review_and_invalidation |

### Research support and reusable software (MC29–MC31; G8/G9) — inspected sources

| File | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/research/catalog.json` | `cb80771a22a48678832430b2f26c1edaaa2ceb14f7d7dc9068d6a4e7fa3716f0` | JSON Pointer /0/status |
| `docs/design/research/catalog.json` | `cb80771a22a48678832430b2f26c1edaaa2ceb14f7d7dc9068d6a4e7fa3716f0` | JSON Pointer /2/sha256 |
| `docs/design/research/source-support.json` | `16944b733a25c2c9de3c0e573de7015e0de3a590dbb3ceffd36b205584dea3c7` | JSON Pointer /records/10 |
| `docs/design/research/claim-support.json` | `fe5d42d9c6fc4415ee69d3b1da049006d869ad1560519b99a40a15c062f670f1` | JSON Pointer /records/12 |
| `docs/design/research/forward-screening-decisions.json` | `8b9aac81d76710e4eeab380ccafd7a8baa6e209881ae1a113e3764752c7fa987` | JSON Pointer /scope |
| `docs/design/research/forward-screening-decisions.json` | `8b9aac81d76710e4eeab380ccafd7a8baa6e209881ae1a113e3764752c7fa987` | JSON Pointer /records/0 |
| `docs/design/research/backward-snowball.json` | `d73fb4cf98274f68aacb3466616b7cb0766b6067215ebf55bb26eca1a709f8a2` | JSON Pointer /records/0 |
| `docs/design/research/omissions.json` | `3730a76883669cac5fb1c2bea7e8c631174c14f0016448b30ca2252185a4dd2c` | JSON Pointer /records/0 |
| `docs/design/research/text/mernik2005.txt` | `2d415d8589931623a6d572ece8170a4e2d3e30c5261fef7ee026044d4306c53d` | lines 142-171 |
| `docs/design/research/tools.json` | `45c440709901e3e9c010aa495f97db4c1cdb1e5238a473c1e95d8fcbff5c86ef` | JSON Pointer /records/14 |
| `docs/design/research/software/Arelle_Arelle-arelle_ModelInstanceObject.py` | `097d4c252ea800c55c221eb67f9694ca689ee5c7bcd19ae38698941f966e8059` | lines 176-201 |
| `data/accounting-master/deliverables/P11/integrations.json` | `9995d01b1a9511ce23bf25b31e78207b824a3210ea037f2fc42f828b16721c28` | JSON Pointer /adapters |
| `data/accounting-master/deliverables/P11/integrations.json` | `9995d01b1a9511ce23bf25b31e78207b824a3210ea037f2fc42f828b16721c28` | JSON Pointer /external_integrations_completed |
| `data/accounting-master/deliverables/P11/integrations.json` | `9995d01b1a9511ce23bf25b31e78207b824a3210ea037f2fc42f828b16721c28` | JSON Pointer /residuals |
| `scripts/check_accounting_p11.py` | `f6602efb1f24793af4f4513c9694b3c0bd21fa72edbbbb887855e186b2adab0e` | lines 73-100 |

### Cases, manuscript and acceptance work (MC28/MC32–MC35; G5/G10) — inspected sources

| File | SHA-256 | Anchor |
| --- | --- | --- |
| `docs/design/chapters/13-reference-company.tex` | `39377ec428ffb0188b9cf352aaab806c64ad4890862222a0ccd2694c34f5edee` | lines 206-269 |
| `docs/design/fixtures/northstar.json` | `3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e` | JSON Pointer /forecast |
| `docs/design/chapters/10-validation.tex` | `a4b9aa5846e0f694e888ba0a5cd3601994ce37ac4cadea0ffafdfd442e113e8a` | lines 10-24 |
| `docs/design/chapters/10-validation.tex` | `a4b9aa5846e0f694e888ba0a5cd3601994ce37ac4cadea0ffafdfd442e113e8a` | lines 113-169 |
| `docs/design/chapters/10-validation.tex` | `a4b9aa5846e0f694e888ba0a5cd3601994ce37ac4cadea0ffafdfd442e113e8a` | lines 282-301 |
| `data/accounting-master/deliverables/P12/benchmark.json` | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointer /preparation/source_readiness |
| `data/accounting-master/deliverables/P12/benchmark.json` | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointer /preparation/protocol |
| `data/accounting-master/deliverables/P12/benchmark.json` | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointer /preparation/exposure |
| `data/accounting-master/deliverables/P12/benchmark.json` | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointer /runs/0 |
| `docs/design/review/author-review.md` | `a12c8e2087d217dbcbc2167bbf849e707c5b2a0c6f1dbc7e9bd550bc65e7a64d` | lines 47-81 |
| `docs/design/accounting-product-design.pdf` | `b5d955545fda1cce764f2efc09fdec2c51addeed8112a032f328c904a3027f8a` | PDF page 12 (printed page 7), sections 2.5–2.6 |
| `docs/design/accounting-product-design.pdf` | `b5d955545fda1cce764f2efc09fdec2c51addeed8112a032f328c904a3027f8a` | PDF pages 61 and 67 (printed pages 56 and 62), sections 11.1 and 11.9 |
| `docs/design/review/internal-before-expert.md` | `bd4bec863c8fbf54e131603ea403261044e63ecb1c17756a00a8190a20ef00f4` | lines 1-77 |
| `docs/plans/accounting-proposal/p15-prior-work-v1.json` | `779d8faffc5b74fa8567eb62a3b0639c969ebbe1949ff73f51e4397c11bc4396` | JSON Pointer /prior_work |
| `data/accounting-master/runs/20261004T054134-68471e41/P15/execution-1/review_result-1.response.json` | `cd3067a48d7e3e1e03ac225b2dbe618776e359e9b59f226426883b7b270561d4` | JSON Pointer /summary |
| `docs/plans/accounting-mission-requirements.md` | `70806de8154b5a54b9c46d48801cbcc853bf451ac25d10d9fc534498742e2f01` | lines 117-124 |

### Initial-profile comparison — source anchors

These are inspected proposal/prototype inputs, not new accounting authority or
measured profile rankings. The earlier source tables preserve the method details.

| File | SHA-256 | Substantive anchor |
| --- | --- | --- |
| `docs/design/chapters/04-architecture.tex` | `62f6ed2ad4c7e1f8cf2ae98ac65a3be3ebf915b53022a47d0a9fd02fb277dfe6` | lines 4-79 |
| `data/accounting-master/deliverables/P03/conformance.json` | `9010b3b3eeeb289e48a9624a661b6123a9cccde4e2ba2b28c869b7725d4151cd` | JSON Pointer /unsupported |
| `data/accounting-master/deliverables/P05/execution.json` | `6c972b6f52cbc13afb703a6a3008c5e12aa2e61317519d20241bbb251862f8e8` | JSON Pointer /obligations/distinct_outcomes |
| `data/accounting-master/deliverables/P08/authority-and-methods.json` | `babb354ec74c073421725ca23c882cced35b3b71b44ebd182d8fba9ed214de01` | JSON Pointer /acceptance |
| `data/accounting-master/deliverables/P11/integrations.json` | `9995d01b1a9511ce23bf25b31e78207b824a3210ea037f2fc42f828b16721c28` | JSON Pointers /matched_frontends, /external_integrations_completed |
| `data/accounting-master/deliverables/P12/benchmark.json` | `8a01ca7613116e58c7ad5e5ffbe1ab61ee7fa92dc47583a72a9e2e2effcfe9b3` | JSON Pointer /preparation/source_readiness |
| `docs/plans/accounting-proposal/p15-prior-work-v1.json` | `779d8faffc5b74fa8567eb62a3b0639c969ebbe1949ff73f51e4397c11bc4396` | JSON Pointer /prior_work |
