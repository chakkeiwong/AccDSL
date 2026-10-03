# AccDSL Core 0 contract, revision 1

Normative companions: `core-0.lark`, `core-ir.schema.json` and
`../fixtures/demo-debt-package.json`. The authored expected lowering is
`../fixtures/core-ir-demo.json`; it is not compiler-generated. The LaTeX chapters teach the semantics;
these files settle serialisation and the complete demonstration dependency set.
No general compiler or product runtime is asserted to exist.

## Lexical and static meaning

Input is UTF-8 with LF or CRLF accepted. Identifiers are ASCII, case-sensitive;
all literal words in the grammar and `true/false/or/and/not/per/year` are
reserved. Strings use JSON escaping, reject unpaired surrogates and are NFC
normalised for semantic identity; original bytes remain evidence. No exponent,
thousands separator, percent literal, implicit multiplication or host-language
escape is supported. Negative numbers use unary minus; decimals become reduced
rationals directly. Dates must be valid Gregorian dates (the token shape alone
does not validate them). Currency/name suffixes are resolved before typing.

Operators follow grammar precedence, arithmetic associates left, comparisons
cannot chain, `and/or` are logical connectives over a joint formula. No
three-valued source missingness is coerced to Boolean. `not` may recursively
apply to a Boolean/formula; arithmetic sign applies to a numeric expression.
No declaration identifier may repeat in a namespace. Imports expose qualified
exports; short names must resolve uniquely. Fields must exist on the declared
record, argument counts/types must match, no implicit money or calendar cast.
Records reject duplicate keys and unknown fields. Arrays are homogeneous unless
their declared type is an explicit tuple. Cyclic let/reference definitions are
rejected before solver dispatch; event dependencies are checked separately.

The schema fixes all IR node fields, forbids extra fields and distinguishes
nullable optional links from empty collections. Every reference resolves in
the frozen package/evidence closure. Schema validation precedes semantic
validation: reference kind, acyclic graphs, type compatibility, context
compatibility, numeric canonical form, units, rules and capability admission.
An enum value permitted by JSON Schema is not evidence that its requested
operation is implemented. Schemas and semantic rules are jointly normative.

Expression arities are fixed: `literal` and `ref` have no arguments; `negate`,
`not` and `field` have one; arithmetic, comparison, `and` and `or` have two.
A `call` matches its registered signature. `array` has its declared element
type and any permitted length; `record` has one argument per distinct
`field_names` entry, in that order. A literal has exactly one rational or text
payload consistent with its type; a reference has a target ID; a field has its
field name in `text`; a call has a qualified function ID in `target`. Unused
payload fields are null and unused `field_names` is empty. Arithmetic and
ordering require compatible numeric types/contexts; equality requires matching
types; logical operators require Boolean values or Boolean formulas. Field
selection and record construction use the registered record type. No schema
success bypasses these semantic checks.

External identifiers such as `builtin:Core0@1`, `DemoCalendar@1`, package
operations and `fixture:` reading/view/witness IDs resolve through a frozen
registry with declared kinds, versions and content digests. The demonstration
package describes these exports and its calendar periods. They are not all
embedded as top-level IR nodes. The reference checker validates structure and
selected evaluated expressions; complete registry resolution and compiler
validation remain implementation obligations. A missing export is an error,
not authority to invent a value or load mutable network content.

SourceSpan locators use `pdf:<1-based-page>:<x0>,<y0>,<x1>,<y1>` with PDF
points from the top-left of the rotated visible page, or `html:<element-id>`
with a retained node ordinal fallback in the frozen parse. A text-extract
character range is a derived locator and retains the extractor version; it
does not pretend to be an original page bounding box. Monetary Context has
non-null currency and a compatible unit. Posting amount is nonnegative in the
book's functional currency; optional original_quantity/original_unit retain
foreign money or commodities and require a valuation when converted.
Journal assumptions and accrual_period preserve the measurement's conditions
separately from its cash posting date. The schema's nullable fields are always
present; null is permitted only under these stated semantic conditions.

A decimal `100 USD` lowers to `literal` with rational `{n:"100",d:"1"}`,
type `Money<USD>` and no hidden scale multiplier. `alpha` lowers to a `ref` to
the same symbol ID on every use. `0.05 per year` has type `Rate<annual_simple>`.
Source references and origin offsets are kept in the evidence binding, outside
the semantic expression digest. A program with source observations cannot run
until its evidence registry and accepted review decisions are supplied.

Source symbol-domain intervals are closed; strict bounds use explicit
constraints. Choice members resolve within their choice namespace. The
surface syntax has no unbounded loops, recursion, dynamic code evaluation or
host calls; finite schedules/collections come from typed packages. Report
fields bind supported mapping expressions and cannot override recognition.
Every assumption constraint or conditional model input has an Assumption
record carrying its expression, scope, rationale, origin, evidence, validity
period, information cutoff and role (Baseline, Hypothesis, Convenience or
ReviewedDefault). An authored baseline is not automatically a reviewed
default. Conditional example endpoints are hypotheses, not inferred facts.

## Exact values, contexts and built-ins

Rationals use base-10 signed numerator strings and positive denominator strings,
lowest terms; zero is `0/1`. Money adds only within one currency and compatible
context. Real times money is money; rate times money must also supply a
YearFraction through `simpleInterest`. Rate alone is not a dimensionless Real.
No rate basis is implicitly coerced. The demonstration's accrual rule uses
`simpleInterest(principal,rate,fraction)` explicitly. Integer counts stay integer.
Division by a symbolic value
requires nonzero proof and is outside the rational-linear solver fragment.

Context equality compares entity, perimeter version, measurement basis,
currency/unit, instant/period/calendar and dimensions. A sum may discard a
dimension only through a valid partition mapping. Reference fields and source
spans may differ without changing financial comparability. Observation
precision is a domain, not a tolerance argument. Unknown rounding convention
is an unresolved reading, not an assumed half-unit interval.

Domain `display` preserves the disclosed spelling, unit/scale and sign when
available; `rounding_rule` identifies the declared convention or is null for
an unrounded mathematical symbol. The SourceSpan retains the original text.
An exact numeric domain has equal closed bounds; an interval has ordered bounds
and explicit endpoint inclusion (a null endpoint is unbounded and open).
Finite-domain `values` are distinct typed expression IDs and use null bounds.
A missing domain has null bounds, no values, and a non-null `missing_reason`;
other domain kinds have null `missing_reason`. Empty or contradictory admitted
domains return an explicit consistency error. Display text alone never supplies
an unknown rounding convention.

The complete built-in set is:

| Name | Signature and effect |
| --- | --- |
| external | String -> SourceRef; resolves a frozen registry key; never fetches network content during evaluation |
| value | Observation<T> -> contextual T or shared constrained Symbol<T>; missing raises MissingEvidence |
| constant | T -> dated exogenous Driver<T>, all dates in the explicit scenario horizon |
| simpleInterest | Money<C>, Rate<annual_simple>, YearFraction -> Money<C>, exact product; symbolic classification happens after expansion |
| yearFraction | start, end, CalendarRef, ConventionRef -> YearFraction; supported conventions `one_year` and `half_year_fixture` require exact named periods; others require a registered calculator |
| currencyScale | CurrencyRef -> Int from the frozen currency registry, USD=2 in demonstration |
| roundMoney | Money<C>, Int, String -> Money<C>; only half_even supported in DemoDebt; rounding at posting boundary, rational ties exact |
| sumOver | PartitionRef, array of contextual T -> contextual T with that dimension removed; disjoint/exhaustive population proof required |
| convert | Money<C1>, Measurement<Rate<C2/C1>> -> Money<C2>; valuation date and purpose must match, source amount retained |
| balance | StateRef, AccountRef -> signed Money<C>; read-only committed state at information date |

All other functions must have a package-registered pure signature and versioned
implementation digest; their capability is explicit. Rules may bind values,
check requirements and propose postings. They cannot sample, mutate state or
access I/O. Contract and behaviour plugins produce proposed events/state
changes through the typed interfaces below. Zero-posting contract changes need
an explicit non-recognition operation.

## Reconstruction model and finite coverage

A ModelScope lists templates, slots per entity/period, books, account roles,
timing/calendar resolution, allowed choices, bounds, and forbidden/unsupported
operations. A slot is a possible aggregate event, with an active flag and
nonnegative amount; inactive implies zero. A template declares both its posting
incidence vector and economic-state change. Sales and collections are different
slots; issue and reset are different slots. Debt states retain F/V, rates,
reset calendar, maturity and hedge links even when historical incidence agrees.

Instantiate every declared slot once, then share variables by economic IDs and
observation IDs. Compile roll-forwards and report mappings into constraints;
add each accepted evidence domain once. Match source observations by exact
context/mapping, never by label similarity. Attach source/assumption IDs to
constraints. Branch on finite choices only, with mutually exclusive guards;
continuous families remain formulas. Count completed, infeasible and unresolved
choice cells. `ExactWithinScope` requires every cell decided and each matching
source obligation resolved or explicitly outside simulation scope. A satisfied
witness alone does not establish coverage. Real-world completeness is never
inferred from this finite result.

Supported solver fragment: rational linear equalities/inequalities, strict
bounds, finite enums and Boolean combinations lowered to finite disjunctions.
Money quantisation either occurs after continuous analysis or uses integer
minor-unit variables with a separately declared bounded integer solver. Integer
and nonlinear constraints may not be silently submitted as continuous LPs.
Unknown-by-unknown products, symbolic discount rates/exponents, arbitrary
functions and unbounded integer search return UnsupportedFragment/Unknown.
Fixed proportions times known totals are linear; variable F,V with F+V=D is
linear even when D is rounded. A fixed constraint F/D >= a with known a and
proved D>0 becomes F>=aD; an unknown a restores bilinearity.

Feasibility results are sat+exact witness, unsat+constraint/source core or
unknown+reason+undecided formula. Bounds include lower/upper rational value,
attainment flags, proof/certificate reference, rounding stage and scope. Strict
inequalities require infimum/supremum semantics. An unbounded result is neither
unknown nor a finite extreme. Resource budgets are explicit request fields;
timeout preserves undecided cells rather than deleting them.

## Temporal selection and local review

An EvidenceView first filters by availability cutoff and (if requested)
ingestion cutoff. Day-only availability maps to the next local midnight using
the named timezone; finer availability requires evidence. Selective explicit
supersession removes only the targeted assertions in the same context. A
superseding assertion must be eligible itself. Transitive successors follow
the acyclic supersession graph. Competing maximal assertions form a conflict
set, never a last-row-wins result. Original view chooses initial assertions in
each chain from a declared filing, not arbitrary earliest ingestion. A filing
with no prior version supplies its original itself. Harmonisation derives new
observations, preserves originals and records all transformation rules.

Intervals are [start,end_exclusive) in a calendar; balance instants refer to
the end-of-day boundary. Cumulative subtraction requires same start, nested
end, units/basis/perimeter and revision group, or an explicit compatibility
assertion supported by review. A restatement of one flow does not restate every
note. Prospective estimate changes affect events from their effective date;
retrospective corrections generate a new view and an explicit opening bridge.

Review states are Proposed, Accepted, AcceptedAlternative, Rejected and
Superseded. Accept requires verified locator/literal, context, rationale,
reviewer/date, applicability checks and a reconciliation result. Acceptance
of an extraction is separate from acceptance of an accounting interpretation.
Several accepted alternatives need a choice group. Reject never deletes source
bytes. Correction creates a new reading linked to the old one; replacing an
accepted reading requires a supersession action. An unresolved contradiction
sets conflict, even if each extraction was accepted. No LLM confidence becomes
a hypothesis weight. Derived formulas, mappings, measurements and runs record
dependency IDs; a changed decision makes their descendants stale for new
views. Historic frozen runs remain replayable, labelled with their old view.

## Uncertainty, scenarios and results

Uncertainty kinds are ExtractionReading, HistoricalFact, AccountingElection,
MeasurementEstimate, BehaviourPolicy and FutureInnovation. Each has scope,
domain, evidence, dependencies and admission rule. An election needs a dated
permitted treatment and evidence of eligibility; a balanced but prohibited
treatment is UnsupportedTreatment. Estimates need a method/date/inputs; future
innovations need a joint law and measure. New observations constrain facts;
corrections replace evidence views; likelihoods update probability models;
hypothetical stresses alone do none of those.

ExogenousStress supplies named driver paths without updating historical weights.
ObservationalConditioning supplies observed events, a joint model and positive
event probability/likelihood; finite enumeration computes normalised joint
weights exactly. Zero probability yields UndefinedConditioning, not equal
weights. Continuous density conditioning requires an explicit conditional
model/regular conditional distribution adapter. StructuralIntervention replaces
specified equations in a named acyclic structural model, retaining exogenous
noise; absence of that model yields UnsupportedScenario. Risk-neutral pricing
and real-world simulation measures have different IDs and cannot be mixed
without an explicit justified transformation.

InformationView(date, observer, role, evidence_view, committed_prefix,
announced_scenario_inputs, forecast_model) exposes past/current facts and
permitted forecasts. Future realised innovations and future event outcomes
are unavailable. A scenario may announce an entire stress path to management
only when its visibility is `announced`; otherwise management sees current and
past driver values. Valuation uses an inner expectation conditional on this
view, with an independent stream domain from outer realised defaults.

RunResult preserves rows by hypothesis/continuous condition, scenario, path and
date. Cells carry Context and Exact/Symbolic/Samples/CertifiedBounds/ExploredRange/
Unresolved tags. Path failure has an enum: EconomicDefault, Unsupported,
NumericalFailure, SolverUnknown, Cancelled. Default retains the legal obligations
and usable state; an unsupported required treatment stops affected descendants.
Unaffected outputs may survive through the dependency graph. No unweighted
family has a mean. Weighted runs preserve successful, unresolved and default
mass; missing outcomes block unconditional means/quantiles. Conditional-on-success
results require an explicit separate request and show their denominator.

Finite joint measures attach to disjoint economic hypotheses, not alternative
labels. Overlapping views cannot be summed; reparameterisations require a
pushforward measure, with Jacobian where densities are used. Priors and
likelihoods list information blocks so totals/components do not duplicate
evidence. Exact finite inference is the reference optional method. Continuous
inference requires a declared density/parameterisation, numerical validity,
multiple-chain/seed and downstream checks; no sampler default is selected here.

## Identity, replay, migration and storage

Canonical bytes are UTF-8 JSON, NFC strings, sorted ASCII keys, separators `,`/`:`
without whitespace, no floats, NaN, duplicate keys or negative zero. All numeric
values are reduced rational records. Arrays preserve order except schema fields
declared sets: dependencies, source IDs and constraint conjunctions sort by ID.
No general algebraic equivalence rewriting is implied. Evidence identity hashes
raw documents, locators, extraction/review versions and context. Model identity
hashes normalised IR, assumptions, rule/calculator locks and resolution contract,
excluding source byte offsets/formatting. Run identity additionally hashes
evidence view, scenarios, horizon, outputs, numeric/calendars, stream scheme and
environment profile. Every digest is SHA-256 with a domain/version prefix.

Event ID hashes run-independent economic owner, schedule version, date, phase,
operation and occurrence ordinal. Idempotency keys pair run ID and event ID;
same payload returns the committed result, changed payload yields conflict.
Independent events may reorder only if their read/write sets are disjoint or
the package proves commutation, including cash/funding constraints. Otherwise
explicit dependencies decide order or expose ambiguity. Atomic commit includes
economic state, journals, measurements and explanation edges.

The reference random primitive hashes the canonical tuple (stream-v1, seed,
coupling-group, entity, contract/cohort, economic-date, shock-kind, draw-index),
takes the first unsigned 64 bits in big-endian order, and maps to the open-unit
rational (integer+1/2)/2^64. Branch enumeration order is absent. Coupling groups
declare shared uniforms; marginal transforms and correlation construction are
versioned. This is a deterministic reference primitive, not a claim of validated
Monte Carlo quality. Research runs must name an assessed counter-based generator
and preserve the same keying contract. Gaussian/transcendental transforms require
a numerical environment and comparison tolerance; rational examples are exact.

SQLite owns immutable source/readings/review rows and transactional execution
metadata; content-addressed files own raw bytes and frozen JSON; DuckDB reads
versioned Parquet exports for analytics. No independent mutable copy owns truth.
Foreign keys must resolve before commit. Schema migration is original payload +
new payload + mapping + before/after IDs. Representation-only migration needs
conformance equivalence on the supported node set; changed semantics creates a
new model. A major version is never relabelled as compatible merely because its
JSON parses. Restart requires exact locked identities and the last committed
state; changed inputs require a new run.

## APIs and adapter boundaries

All methods accept immutable referenced records and return either the typed
success record or Diagnostic(code, message, source_ids, entity/period, dependency
path, retryable, capability). No method modifies its inputs. A request_id makes
mutating import/review operations idempotent. The normative operations are:

| Operation | Required arguments | Success |
| --- | --- | --- |
| ingest | bytes/hash, filing_id, availability, extractor_lock, request_id | SourceDocument, source units, proposed readings, coverage obligations |
| review | reading_ids, action, evidence, reviewer, reason, prior_view, request_id | ReviewDecision, new EvidenceView, invalidated descendants |
| compile | source/typed-IR, schema_version, package_lock, evidence_view | validated IR, unresolved simulation inputs, diagnostic list |
| reconstruct | IR, ModelScope, view, solver_lock, budgets | HistoryFamily and cell coverage, witnesses/conflicts/unknowns |
| simulate | family/conditions, initial_state, scenarios, horizon, InformationPolicy, packages, numeric and stream settings, outputs, budgets | RunResult with committed state/journals and branch manifest |
| report | committed run/date/period, mapping, view, queries | contextual joint cells and explanation references |
| bound | formula, query expression, domain, quantisation mode, solver/budget | certified bound/attainment or explicit Unknown/Unbounded |
| explain | output_id, frozen run_id | typed dependency graph, no latest-source substitution |
| replay | run_id, checkpoint_id, lock/environment | equal exact outputs or explicit numerical comparison report |

Contract methods are schedule(terms,start,end,calendar), observe(terms,date,info),
payoff(terms,event,state,market), transition(state,event). Behaviour is
decide(state,information,policy) -> actions. Measurement is measure(state,event,
information,method) -> value/basis/error/method annotations. Accounting is
recognise(event,state,measurement,rule) -> postings+proposed state patch.
Reporting is map(state,journals,period,perimeter,policy) -> contextual cells.
Every adapter advertises exact supported operations and input dimensions.

Arelle is selected for tagged filing proposals: read QName, contextID, entity,
period, dimensions, unitID, scale/decimals, nil flag and raw locator. Preserve
duplicate facts; validations are diagnostics, not a chosen truth. Docling
provides layout/table proposals with page bounds and conversion status; a table
cell without a verified header/context is unresolved. Z3 receives named rational
linear assertions and finite choices, returns status/witness/core; validate
witnesses exactly and preserve unknown reasons. ACTUS receives locked contract
terms, calendars and dated risk factors; returns events/payoffs, never automatic
accounting entries. QuantLib receives explicit evaluation date, curves, fixings,
calendar/day-count, instrument and measure; returns approximate valuations and
numerical metadata, never historical probabilities. These are adapter designs
grounded in archived interfaces. Only Z3 is exercised by the reference checks.

Beancount is an optional concrete-journal export/check comparator; unsupported
symbolic families stay in AccDSL. Catala is a rule-language comparator. Stan,
Pyro/PyMC are possible later inference adapters, not required core dependencies.
Licences and inspected source hashes are in tools.json; deployment linking and
redistribution must be checked for the selected version. Python constructors
and the text frontend must emit the same IR and receive identical diagnostics.
Usability and maintenance comparisons remain empirical questions.

### Concrete adapter exchanges

The following are expected exchanges at the AccDSL boundary, not captured
outputs of unrun libraries. Upstream wire formats must be translated by a
version-pinned adapter before these records are accepted.

* The acquired Apple interim fact `f-112` has QName
  `us-gaap:CashAndCashEquivalentsAtCarryingValue`, literal `30,299`, scale 6,
  decimals -6, USD unit, context `c-17`, CIK `0000320193` and instant
  `2024-12-28`. Its nominal value becomes rational USD `30299000000/1`;
  the original display remains `30,299` in millions. The source locator is
  `html:f-112` in the frozen interim document; dimensions are empty. Accuracy
  metadata is retained separately from that nominal value. An uncertainty
  interval additionally needs the declared rounding convention; scale alone
  does not create an exact economic amount. Reapplying scale to an Arelle
  value already transformed by inline-XBRL is an error. A nil fact returns
  missingness, never zero. Two copies with conflicting values remain two
  readings, not an averaged amount. The source fields are in the Apple
  manifest; the inspected Arelle interface snapshot hash is recorded in
  `research/tools.json`. No Arelle integration was run.
* A normalized borrower interest event has contract `loan-1`, USD principal
  100, annual simple rate `1/20`, year fraction 1, payment date `2026-12-31`,
  payoff `-5/1` from the borrower's perspective, no fees and no unpaid prior
  accrual. A supported accrue-and-pay operation consumes this economic event
  and proposes debit interest expense 5 / credit cash 5, subject to available
  cash and book/context checks. A rate-reset event changes the contract's
  future rate and emits no posting under its declared non-recognition rule.
  The adapter must state whose payoff sign is returned and cannot infer
  liability carrying value or an accounting election from a schedule alone.
  This is an ACTUS-oriented boundary example; an actual ACTUS service request
  and returned event must be tested against a selected service version later.
* A normalized valuation request supplies evaluation date `2025-12-31`, one
  USD cash flow of 110 at `2026-12-31`, a declared one-year fraction, annual
  effective yield `1/10`, no options/default and discount factor `10/11`.
  Its exact reference present value is USD 100. A numerical QuantLib result
  must retain date, curve/engine/calendar locks, units, measurement purpose,
  status and justified error/tolerance against this reference. It is a
  valuation of the stated cash flow, not a historical weight or an automatic
  journal amount. Changing the evaluation date creates a distinct request;
  stale process-global settings must not contaminate the next branch.

These examples specify success meanings and the principal rejection cases.
Pinned integration, exceptional-event coverage and empirical cost remain
separate acceptance work.
