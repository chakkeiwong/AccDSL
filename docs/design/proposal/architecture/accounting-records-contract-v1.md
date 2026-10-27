# Accounting requests, receipts and observable failure — proposed supplement v1

This supplement completes the finite acquisition exchange described in
accounting-contract-v1.md §§2–4. It preserves accounting-replay-contract-v1.md's
accepted identity lookup order and immutable receipts. It replaces AC01 and
AC03 only as field-complete exchange examples; their source-scoped arithmetic
and all predecessor files remain evidence. AC02 is not expanded here. AR01–AR05
remain the accepted replay examples, referenced by exact file hash and case ID.
These are proposed requirements, not executable product interfaces. MC13, MC25
and MC34 are addressed, with MC08 branch preservation, MC35 internal preparation
and G4/G18 interactions. Full accounting eligibility and lifecycle methods remain
unfinished.

## Question, evidence and stopping boundary

Can a consumer reconstruct the submitted facts, assessment, proposed postings
and commitment outcome without conflating arithmetic with eligibility or an
unreceived response with rollback? Compare a typed exchange with a direct
balanced journal on the identical A03 unresolved-treatment and A01 delta-mismatch
inputs. Acceptance requires complete reference closure, explicit missing-value
semantics, independently reconciled event/journal/state amounts and the six
specified before/after outcomes. Corrupt source bindings, unresolved record
references, a posting on rejection or a changed original receipt veto the
fixture. Balance is an explanatory diagnostic only. Stop after this supplement,
six concrete exchanges, finite calculations, P16 records and structural check.
No authority research, production code, database selection or new test suite is
part of this slice.

Skeptical audit: the comparator receives the same facts and authority limits.
Neither a prototype nor a checker count defines the desired behavior. The
examples are deterministic and synthetic; no statistical ranking is attempted.
The inherited A01 classification is stipulated, not inferred from a balanced
entry. A03's missing observable-valuation evidence must survive every response.
Commit uncertainty must survive until authoritative lookup resolves it. The
existing whole-architecture failure is expected while four contracts and the
initial profile remain unfinished; it cannot certify this subsection either.

## Record notation and ownership

The adjacent fixture registry contains `{kind, content}` under actual SHA256
keys. A `Ref<K>` is the 64-character lowercase hex digest of a record of kind K
in that registry. Verify content digest and expected kind before use; a digest
is not evidence of truth. `FileRef` is `{path: repository-relative ASCII string,
sha256: digest}` and resolves exact retained file bytes. External provenance
uses `{file: FileRef, locator: nonempty string}`. Record dependencies are acyclic.
Records are immutable; owners publish new versions, never edit retained bytes.

Unless marked nullable below, every field is required and null is invalid.
Unknown extra fields are rejected for this version, preventing silent loss from
the fingerprint. Strings are nonempty ASCII; identifiers are opaque and scoped
as stated. Versions/sequences are nonnegative integers (booleans are not
integers); arrays are ordered, contain no duplicate references and may be empty
only where stated. Dates are ISO calendar dates; instants are ISO UTC timestamps.
Money is a signed decimal string with exactly two places, no exponent or negative
zero. Journal debit/credit amounts are nonnegative Money. No float is permitted.
`KnownBool` is exactly `{status: "known", value: boolean}` or
`{status: "unknown", reason: string}`. Absence is malformed; explicit unknown
is a valid retained fact and can block treatment. Null means the particular
result does not exist, never an unknown monetary zero.

Use the accepted replay encoding (sorted JSON keys, compact separators,
ensure_ascii=True, allow_nan=False, ASCII bytes). New complete records use domain
`accdsl.accounting.records.v1/<kind>` followed by NUL and encoded content. The
stable key alone uses `accdsl.replay.v1/key`, preserving its accepted tuple;
the complete request digest is its fingerprint within the new record version.
The new domain avoids falsely identifying incomplete predecessor requests as
complete requests. A future migration must retain the original encoding version;
cross-version equivalence is not presumed. Mutable transport metadata is outside
the request. Collision resistance is assumed, not proved.

| Kind and publishing owner | Complete content fields |
| --- | --- |
| `context`, caller | `entity_id`, `book_id`, `currency="CU"` (synthetic unit, not an ISO currency claim), `unit="units"`, `scale=0`, `basis="synthetic-A01-FVTPL"`, `annual_period_start: Date`, `schema_version=1` |
| `branch`, history-family producer | `context: Ref<context>`, `branch_id`, `family_id`, `version`, `admissibility="stipulated"`; no probability implied |
| `time`, caller with evidence admission producer | `economic_date: Date`, `reporting_start: Date`, `reporting_end: Date`, `source_cutoff: Instant`, `review_cutoff: Instant`, `view: "historical_as_known" or "restated"`, `basis="synthetic_scenario"`; interval is closed and contains economic_date |
| `authority`, method author | `version`, `source: provenance`, `paragraphs: nonempty string array`, `application_scope: string`, `applicability: "stipulated" or "unresolved"`; these anchors support the retained example, not a general standards claim |
| `method`, method author | `version`, `name`, `authority: Ref<authority>`, `rounding="exact_two_decimal_reject_extra_precision"`, `formula: string`, `scope: string` |
| `assumptions`, scenario author | `version`, `eligibility: "stipulated" or "unresolved"`, `cash_settlement: boolean`, `no_other_flows: boolean`, `branch_admissibility="stipulated"`, `balance_sign="debit_positive"` |
| `evidence`, evidence producer | `version`, `source: provenance`, `source_case: "A01" or "A03"`, `nature="synthetic"`, `observable_valuation: KnownBool` |
| `admission`, admission producer | `evidence: Ref<evidence>`, `time: Ref<time>`, `status="synthetic_only"`, `known_at: Instant|null`, `reviewed_at: Instant|null`, `reason: string`; null instants explicitly mean no historical availability claim |
| `chart`, accounting method author | `context: Ref<context>`, `version`, `accounts: nonempty array<Account>`; Account has `account_id`, `concept_id`, `normal_side: "debit" or "credit"`, `dimensions: object<string,string>`; empty dimensions means no sector/geographic breakdown, not an unknown breakdown |
| `state`, accounting state publisher | `context: Ref<context>`, `branch: Ref<branch>`, `chart: Ref<chart>`, `sequence`, `balances: object<account_id,Money>`; exact chart account keys, no omitted accounts |
| `event`, caller/economic model | `business_event_id`, `version`, `kind="cash_acquisition"`, `context: Ref<context>`, `branch: Ref<branch>`, `time: Ref<time>`, `price: Money`, `fair_value: Money`, `fee: Money`, `category="FVTPL"`; all three monetary inputs nonnegative |
| `request`, caller | `schema_version=1`, `identity: Identity`, `event: Ref<event>`, `opening: Ref<state>`, `context: Ref<context>`, `branch: Ref<branch>`, `time: Ref<time>`, `chart: Ref<chart>`, `authority: Ref<authority>`, `method: Ref<method>`, `evidence: nonempty array<Ref<evidence>>`, `admissions: equally sized array<Ref<admission>>`, `assumptions: Ref<assumptions>`, `lineage: array<provenance>` (empty allowed) |
| `assessment`, accounting assessor | `request: Ref<request>`, `status: "eligible" or "unresolved" or "ineligible" or "outside_scope"`, `reason_codes: array<string>`, `preconditions: nonempty array<Condition>`, `authority: Ref<authority>`, `method: Ref<method>`; Condition is `{name, status: "satisfied" or "unknown" or "failed", support: string}` |
| `journal`, accounting proposer | `request: Ref<request>`, `assessment: Ref<assessment>`, `context: Ref<context>`, `branch: Ref<branch>`, `chart: Ref<chart>`, `purpose="candidate"`, `lines: nonempty array<Line>`; Line is `{account_id, concept_id, dimensions: object<string,string>, debit: Money, credit: Money}` |
| `delta`, accounting calculator | `request: Ref<request>`, `context: Ref<context>`, `branch: Ref<branch>`, `chart: Ref<chart>`, `changes: object<account_id,Money>` (all chart keys, including zeros), `derivation="independent_event_formula"` |
| `receipt`, commit coordinator | `request: Ref<request>`, `assessment: Ref<assessment>`, `journal: Ref<journal>`, `delta: Ref<delta>`, `opening: Ref<state>`, `closing: Ref<state>`, `identity_key: digest`, `status="committed"`, `commit=true`, `sequence: integer`, `encoding_version="accdsl.accounting.records.v1"` |

Identity is exactly `{entity_id, book_id, branch_id, business_event_id}`. Entity
scopes book; book scopes branch; branch scopes event. These fields agree with
context, branch and event records. Version belongs in the event/fingerprint,
not the stable key. Every journal line matches its chart concept and dimensions;
context supplies currency/unit/scale/basis for every amount without conversion.
A line has exactly one positive debit or credit. States use debit-positive signed
balances, including negative equity. With opening cash 1000 and equity -1000,
asset and expense zero, the acquisition gives cash 898, asset 100, expense 2,
equity -1000. Sum of balances remains zero. This is an unclosed trial balance;
expense is not silently closed into equity, and no financial-statement package
is implied. Rounding never plugs a discrepancy: extra precision is rejected.

Assessment authority/method must equal request references. Journal and delta
must name the same request, context, branch and chart; receipt opening equals
request opening, closing sequence is opening sequence + 1, and all receipt
links belong to that transaction. Assessment eligible is necessary but not
sufficient for commitment. For this finite A01 method, independent changes are
asset=price, expense=fee, cash=-(price+fee), equity=0, conditional on fair value
matching price and the stipulated treatment. For A03, no measurement/posting
formula is selected until the unresolved valuation condition is resolved.

## Submission, status and response records

`submission` is caller-retained `{wire_format="ASCII_JSON", raw_text: string}`.
Its digest identifies received bytes, including malformed content; it is never
a valid request fingerprint by implication. For the finite examples raw_text
contains the request object and all references resolve in the bundled registry.
The bundle is the caller's immutable dependency submission; the receiver retains
it for diagnosis. Invalid JSON or missing dependencies preserve raw_text and
available bytes and reject; they cannot acquire a canonical request digest.

`response` is produced by the accounting endpoint. Its complete fields are
`submission: Ref<submission>`, `request: Ref<request>|null`, `status` (enum below),
`reason_codes: array<string>`, `assessment: Ref<assessment>|null`,
`diagnostic_journal: Ref<journal>|null`, `diagnostic_delta: Ref<delta>|null`,
`receipt: Ref<receipt>|null`, `observed_state: Ref<state>|null`,
`commit_status: "committed"|"not_committed"|"unknown"`,
`additional_commit: boolean|null`, `statuses: Status`,
`metadata: {response_id: string, operation: "submit"|"lookup"}`.
The metadata is outside the immutable receipt and request fingerprint.

Status has seven required fields. Structural validity is `valid` or `invalid`;
mathematical status is `satisfied`, `unresolved`, `undefined` or `failed`;
computation status is `specified_exact`, `specified_partial`, `symbolic` or `not_computed`. The other fields
in every example are `empirical_justification="not_established"`,
`capability_status="specified_only_no_runtime"`, `accounting_validity="not_assessed"`
and `human_acceptance="pending"`. Eligibility is a separate assessment: even an
eligible synthetic acquisition has no established accounting validity.

| response.status / reason | Other fields and consequences |
| --- | --- |
| `committed` / empty | Valid request; eligible assessment; receipt required; mathematical=satisfied, computation=specified_exact; commit_status=committed, additional_commit=true |
| `replayed` / empty | Same immutable committed receipt; commit_status=committed, additional_commit=false; current observed state separate; no new assessment of eligibility |
| `rejected` / `MALFORMED_REQUIRED_FIELD` (also malformed JSON, missing dependency, context/admission error) | request=null when canonical validation failed; assessment/journal/delta/receipt null; structural=invalid, mathematical=unresolved, computation=not_computed; commit_status=not_committed, additional_commit=false |
| `rejected` / `TREATMENT_UNRESOLVED`, `TREATMENT_INELIGIBLE`, `OUTSIDE_SCOPE` | Valid request and retained corresponding assessment; no journal/delta/receipt; mathematical=unresolved, computation=not_computed; no commitment |
| `rejected` / `DELTA_MISMATCH`, `UNBALANCED_JOURNAL`, `ROUNDING_MISMATCH` | Valid request and eligible assessment; diagnostic candidate journal/delta may be retained, never a receipt; mathematical=failed, computation=specified_exact for the evaluated mismatch; no commitment |
| `aborted` / `COMMIT_ABORT_CONFIRMED` | Valid request, eligible assessment and computed diagnostics; mathematical=satisfied, computation=specified_exact; receipt=null; authoritative confirmation of no domain writes; commit_status=not_committed, additional_commit=false |
| `commit_unknown` / `ACKNOWLEDGEMENT_LOST` | Client-side observation; valid retained request; receipt and observed_state=null; mathematical=satisfied, computation=specified_exact if proposal had completed; commit_status=unknown and additional_commit=null; no assertion of rollback |

For canonical conflict/staleness, preserve the accepted replay rules: request is
retained, journal/delta null, no additional writes. An existing conflicting
receipt is diagnostic only and cannot be assigned to this request. Lookup carries
`{identity: Identity, expected_request: Ref<request>}`; it returns `replayed` only
on matching fingerprint. A missing entry while commitment could still be in
flight remains unknown. `not_committed` requires authoritative finality (the
commit is terminated and cannot later publish). How persistence proves finality
remains a required later design decision, not an assumed timeout rule.

## Atomic boundary and failure traces

The domain view has four jointly published parts: stable identity→receipt index,
committed journal set, selected closing state for this branch and committed
receipt set. Candidate records may be computed outside this boundary; their
presence in a fixture registry or diagnostic store is not commitment. Optional
rejection/audit storage is separate and must not create an index entry, select a
closing state or publish a journal/receipt as committed. Its failure cannot undo
a committed transaction. This slice permits audit storage to be disabled.

Validate dependencies and context, then look up the stable key before checking
freshness. Equal fingerprint returns the original receipt. Different fingerprint
conflicts. Only an absent key compares opening state with current state, assesses
treatment and computes/reconciles candidates. At commitment recheck both absence
and freshness atomically; a racing identical event returns its receipt, a changed
one conflicts, and another event advancing state makes this request stale. There
is no successful outcome with only some of the four domain parts changed.

The six examples reset to the same complete initial world unless explicitly
chained. R01 publishes all four parts; R02 malformed input, R03 A03 unknown
valuation, and R04 balanced-but-wrong asset allocation leave all four unchanged.
R05 completes candidates but the stipulated commit abort leaves all four
unchanged; no committed receipt exists. R06 publishes the same complete R01
transition but loses acknowledgement. The client's first response says unknown;
a subsequent authoritative matching receipt lookup resolves committed, returns
the original receipt and adds no transition. Never allocate a new event ID to
escape an unknown outcome. Runtime isolation, torn-write prevention and crash
recovery are obligations for the persistence contract, not results of these
finite traces.

## Matched alternatives and assumptions

On A03 the known facts are price 100, fair value 105, fee 2 and unknown evidence
for the valuation condition. A direct balanced candidate (asset 100, expense 2,
cash -102) balances but cannot determine whether that measurement is eligible.
On R04 both paths receive an otherwise stipulated eligible A01 and a journal
asset 99, expense 3, cash -102. It balances, but disagrees with the event's
asset 100 and expense 2. A direct-posting design can satisfy this contract if it
also retains the assessment, exact dependencies, independent delta and atomic
receipt boundary. The comparison favors retaining that information; it does
not establish a speed, storage, framework or general IR winner. Event sourcing
can also satisfy the contract if projection and receipt visibility are atomic
at the stated boundary; event-log durability alone does not answer this question.

| Choice / provenance | Status and reason | Failure and early diagnostic |
| --- | --- | --- |
| Exact two-decimal CU, inherited A01 | Convenience for finite arithmetic | Cannot represent FX/interest precision; reject extra decimals and reconcile using Decimal; no global default |
| Replay serialization and SHA256 | Convenience consistent with retained immutable examples | Omitted dependencies or cross-version aliases; full reference closure, distinct domains and exact-byte hash verification |
| A01 eligibility / retained example | Stipulated hypothesis | Balance could conceal missing authority; retain applicability and assumptions as stipulated, preserve A03 unknown control |
| Optional audit storage / replay supplement | Proposed independent diagnostic channel | Audit mistaken for commitment; enumerate four domain parts before/after and keep audit writes separate |
| Synthetic time/admission | Explicit scenario choice | 2024 economic dates could be mistaken for evidence available then; admission has null known/review instants and synthetic_only, never historical-as-known evidence admission |

Time-contract-v2's economic time, reporting interval and separate source/review
cutoffs are represented explicitly. The examples use a restated scenario view;
the source fixture assembled in 2026 is not admitted as a historical 2024 fact.
A real historical request must replace synthetic admission with reviewed source
availability and applicability under the governing evidence/time contracts.
That broader admission type, accounting lifecycle and authority/precondition
coverage remain the next accounting task. P17 retains corporate operations,
financing, groups/FX, banks, insurers and IFRS/US GAAP/ASBE obligations. P16 still
needs language/IR, persistence, interfaces, failure semantics, integrated initial
profile, dependency order and fourteen open decisions.
