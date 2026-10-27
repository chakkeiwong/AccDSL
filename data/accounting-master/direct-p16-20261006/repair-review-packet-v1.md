READ-ONLY FINAL REVIEW OF REPAIRS. No tools or further file requests. Review the supplied original findings, dispositions and complete repaired contract texts. Earlier independent domain review returned AGREE with six boundary clarifications; platform returned REVISE with two blockers and four clarifications. Those substantive reviews and finite arithmetic remain the baseline; this task only verifies the grouped repairs and checks for new contradictions they introduce. Product runtime remains disabled; P17 methods/source work and P18/P19 remain. Return at most five unresolved material findings, if any, and one terminal VERDICT: AGREE or VERDICT: REVISE. Do not repeat packet/tool/governance loops.


ORIGINAL REVIEW platform-review-v5.md
**Checked (by hand, no tools):** Northstar opening balance (sums to 0), every 2024H1/H2 posting roll-forward (cash 65/74.6, receivables 20/35, inventory 25/20, plant net 85/91, prepaid 2/0, payables 25/30, profit 6/23.6, equity 72/90.6, cash-flow classes, FY 260/29.6/45.6/−22/−9/14.6), the original-vs-corrected H1 reading (120→110, tax 3.5→1.5+2 prepaid, profit 14→6, equity 80→72), the 2025 derivation (purchases 170, dep 13, receivables 55, payables 40, PBT 82−2x, tax 16.4−0.4x, profit 65.6−1.6x, op cash 48.6−1.6x, cash 95.2−1.6x, equity 148.2−1.6x, assets 288.2−1.6x, floating endpoint 93.6/146.6/286.6), LX01/LX02 expansion (5+2x, 5+4x, slope −3.2 at 9%), FX01 bounds ([104,116]), the four exchange projections (X007 derivation of C09/C10 unresolved, X008/K01/K04 rejection codes, stage, statuses and unchanged four domains), and cross-contract consistency of key/fingerprint/replay order, status vocabularies, stage orders, invalidation and export rules.

**Cannot establish:** runtime behavior, durability, SHA digests listed in fixtures, source truth of AASB 9 facts, human/domain/forecast acceptance, or P17 method validity.

**Findings**

1. *architecture-integration-v1 §Status mapping* — The table has no row for native accounting `status=assessed` with assessment `unresolved`/`outside_scope`/`ineligible` and `computation_status=specified_exact` + `mathematical_status=unresolved`. Counterexample: X007 is exactly that combination; by the rule "unknown combinations return STATUS_MAPPING_UNSUPPORTED" the canonical valid assess-only exchange is unmappable. Repair: add explicit accounting rows (disposition `completed`, structural `valid`, computation `complete`, math `not_applicable` or `defined`, accounting_validity copied native). Blocker for the mapping table being governing; bounded text fix.

2. *interfaces-contract-v1 I2* — `accounting.commit@1` is declared, but no native request schema can supply its argument: v1 requests lack C01–C10 eligibility; v2 requests fix `operation="assess_only"` and "cannot commit". Counterexample: a commit citing a v2 eligibility Ref is contradicted by its own schema. Repair: mark the signature declared-only/unsupported pending a reviewed v3 commit request, or specify it now. Blocker for the I2 table as stated; not for the architecture.

3. *interfaces I1 vs persistence P2/P4* — Two idempotency keys for one call: envelope `(operation_kind, workspace_key, request_id)` and the event tuple. Counterexample: same `request_id`, new `business_event_id` → P4 says conflict, P2 says fresh event. Repair: state that accounting operations are keyed solely by the P2 tuple (request_id advisory) or define a request_id check stage before lookup. Non-blocking.

4. *I1 `expected_head` vs I2 arguments/replay fingerprint* — Head appears both in the envelope `{owner_key,state_ref,generation}` and in arguments ("expected branch head/generation", "expected review view/revision", "expected selection revision"); P2 also renames `branch_id`→`branch_key`. Counterexample: a retry after `unknown` commit with a refreshed generation changes the fingerprint and yields `EVENT_ID_CONFLICT` rather than replay. Repair: one location, state whether generation is in the fingerprint, map view/selection revisions to the head shape, unify naming. Non-blocking.

5. *L1 `Unknown{reason,obligation_refs}` / `Ref` vs native fixtures* — Native packets encode unknown as null value + inner/outer `unknown_reason` (X007 valid, X008 invalid) with no stated adapter mapping to L1 `Unknown`; the X008 rule exists only by example. `submission_ref` targets raw bytes, but L1 `Ref` digests only records. Repair: declare a BlobRef kind and the native-unknown→Unknown mapping with the inner/outer rule. Non-blocking.

6. *I1 `execution.budget` elapsed-time vs P5 replay* — Elapsed-time budgets make completed/unresolved partitions environment-dependent, so "exact equality" replay of a partial result is unachievable as written. Repair: condition replay equality on coverage/partition identity; recommend operation-count budgets for reproducible checkpoints. Non-blocking.

Core semantics (stable key, lookup-before-freshness, all-or-none, continuous shared x, status independence, invalidation) are coherent and arithmetically verified. Findings 1–2 are text-level contradictions in supplied contracts, not P17/P18/P19 matters.

VERDICT: REVISE

ORIGINAL REVIEW domain-review-v5.md
**Checked (by hand, from supplied text only):** finite posterior arithmetic in UC01/UC02/D_then_E/UC08 and the matched lazy/joint identity (Z_D=7/12→(3/7,4/7,0); Z_E|D=5/7 and joint Z=5/12 both →(3/5,2/5,0); A∘A normalizer 1; corrected (1,1/2,1) on prior →Z=5/6,(3/5,1/5,1/5)); MA03 union 5/6+1/2−1/3=1; §5 completed-mass 35/3 and conditional mean 14; H2 E05 ratios 3 and 11/4; H4 grouping 5/2; E3 ties-to-even endpoint claims for 120/121; T3 date-interval rule; T5 150 vs 140; Northstar opening (190=190), H1, H2, FY, 2025 fixed/floating balances, cash roll-forwards and the affine table (slopes 2, −0.4, −1.6; 9% control → 4, −3.2); rejection receipt state/status fields against uncertainty §2 and the integration mapping. All arithmetic reconciles; no numeric error found.

**Findings (all P16 architecture; none accounting-authority):**

1. **uncertainty-contract-v1 §3/§4 vs chaining §2/§4 — repeat-condition disposition undetermined.** §3: reapplying A is idempotent, "records no new information factor"; §4 table: new request on same information block → `DUPLICATE_INFORMATION`. Chaining resolves A_then_A only by treating A as an authored condition (consumed atoms `[]`). Counterexample: A defined from observation block D, resubmitted — one rule yields `SPECIFIED_RESULT`, the other `REQUEST_INVALID`. Repair: state that re-conditioning on an identical consumed condition identity is accepted-idempotent (new receipt, no new atom), while `DUPLICATE_INFORMATION` applies to likelihood factors or a condition submitted as a new block; tag UC01's A explicitly as authored. Non-blocking.

2. **Chaining §3–4 / evidence E4 — selection pointer after correction undefined.** After UC08, `state_after` still selects `CH.view.UC02@1` (rev 1), a view the new evidence view marks superseded. Chaining says "requests for the current view must match the current revision" but gives no rule for a current-view request whose selected view is superseded in a newer evidence view, nor whether selection is keyed per evidence/time view. Repair: scope selection revisions to (family, evidence/time view) or require correction to emit an explicit re-selection obligation and a `SELECTION_SUPERSEDED`-type unresolved result for current-view requests. Non-blocking for method governance; must precede the persistence contract.

3. **attachment-v2 §F vs rejection-status §2 — `structural_validity` meaning diverges.** Attachment: "concerns the representation, not normalization", stale model → `RETAINED_ONLY`. Chaining/rejection: stale law binding → `REQUEST_INVALID` with `structural_validity=invalid` ("including semantic binding"). Integration copies this field into platform mapping, so a consumer cannot infer meaning uniformly. Repair: define `structural_validity` once as request-validation outcome (envelope + binding) or add a separate `binding_validity`; amend §F wording. Non-blocking.

4. **uncertainty-contract-v1 §2 request schema not amended.** The "exact" field list omits `admission_receipt_ref` (required by chaining §3 and present in `CH.request.D_then_E`) and `target_time_ref/target_evidence_view_ref/target_admission_ref` (chaining §5, `CH.request.UC08`). Repair: version the request schema (v1→v1.1) listing operation-specific fields. Non-blocking.

5. **interfaces I1 vs uncertainty §5 — coverage vocabulary unmapped.** Platform `coverage` partitions into completed/unresolved/unsupported/infeasible/cancelled; native partition is completed/unsupported/numerical_failure/solver_unknown/cancelled/unexplored. Integration maps statuses but not regions (where do `numerical_failure`, `solver_unknown`, `unexplored` go; does "unknown mass" survive?). Repair: add a region/mass mapping row with `STATUS_MAPPING_UNSUPPORTED` fallback. Non-blocking.

6. **`CH.evidence.corrected@1` — dependency list conflates inputs with affected records.** It lists `CH.view.D_then_E@1`, its law/candidate as `dependencies` while also naming themas `invalidated_descendant_refs`. If dependency closure is also identity-defining (chaining §2), the corrected evidence view's identity depends on whether an optional descendant was ever created, contradicting chaining §4's conditional "if the D,E descendant is present". Repair: split `dependencies` (mathematical/semantic inputs) from `affects`/`invalidates` edges; exclude affected records from identity-defining closure. Non-blocking.

**What the evidence cannot establish:** fixture-wide reference closure, hashes and the omitted registry records; F1/F2 failure-contract vocabulary referenced by interfaces; L1/P2–P5 persistence and IR semantics; the E05 real-source conflict (still absent, acknowledged); any runtime enforcement, accounting authority (P17), manuscript integration (P18) or readiness (P19); human/domain/forecast acceptance. The 797/169/2580 counts and 932 unchanged files are finite document checks only.

**Distinction:** Findings 1–6 are P16 boundary/vocabulary gaps, not accounting/sector/source methods (P17), not manuscript (P18), not readiness (P19). No supplied arithmetic, admission rule or correction semantics is wrong; the defects are unstated or divergent behavior at boundaries that later methods will consume.

VERDICT: AGREE

DISPOSITIONS: Platform finding 1 maps completed accounting assessment while preserving unresolved math (we do not adopt the suggested invented defined/not_applicable value). Finding 2 gets a separate acyclic basis/authorization/commit schema with explicit unsupported-profile behavior. Findings 3–4 have one head location, one event lookup namespace, stable branch alias and original fingerprint/head retries. Finding 5 defines BlobRef/Submission plus native Unknown/NotApplicable mapping. Finding 6 distinguishes receipt replay, equal matched exact values and environment-dependent partial search coverage. All six domain findings are explicitly amended in A2–A6, without modifying protected native fixtures. Malformed outer requests additionally retain raw Submission while validated request/view/coverage may be null. Failed mathematics now retains native failed verdict.

REPAIRED FILE docs/design/proposal/architecture/cross-contract-amendment-v1.md
# P16 interaction amendments after independent review

This supplement resolves the material cross-contract findings from the direct
platform and domain reviews. It applies to the named fields/operations below,
not to all older records by date. Historical fixture bytes and identities remain
unchanged. The architecture index pins this amendment with the other contracts.
It addresses MC04, MC08–MC14 and MC24–MC27/MC33–MC35. All exchanges described here
are proposed behavior; P17 supplies actual domain methods and authority.

## A1. A commit request that cannot promote assess-only permission

Native accounting request v2 remains exactly `operation=assess_only`. Its
assessment has posting_permitted=false and is not an authorization to commit.
Changing that field or attaching its eligible finding to a commit is invalid.
The portable commit path uses the following separate closed records; no native
request schema is extended silently. Every Ref has the L1 kind/schema/digest,
all referenced records/blobs resolve, and additional fields are rejected.

`AccountingEventBasis/v1` has exactly `identity`, `event_ref`, `opening_ref`,
`context_ref`, `branch_ref`, `time_ref`, `chart_ref`, `authority_refs`,
`method_ref`, `evidence_refs`, `admission_refs`, `assumptions_ref`, `view_ref`.
`identity` has exactly entity_id, book_id, branch_key and business_event_id,
all nonempty ASCII identifiers. Each `_ref` is a nonnull typed Ref; plural
Refs are schema-declared sets. Evidence/admissions may be explicitly empty only
when the method's admitted assumption scope allows that and records why.
Authority_refs must identify actual applicable support or a specifically typed
SyntheticAuthority for a declared synthetic example; it cannot be an untyped
claim of compliance. The economic event contains its payload/version/date,
not a reference to a future commit request. All identity/context/branch/time/
chart/method/authority/admission bindings are checked as in the domain contracts.

`PostingAuthorization/v1` has exactly `basis_ref`, `posting_profile_ref`,
`method_ref`, `authority_refs`, `status`, `findings`, `posting_permitted`,
`evidence_level`, `view_ref`. Status is eligible, unresolved, ineligible or
outside_scope. Findings retain each method precondition and its reason/source;
no early summary suppresses other material findings. posting_permitted is an
exact Boolean, true only for eligible status under a posting profile that
explicitly supports this event/treatment/method in this view. All other statuses
require false. Evidence level states source-supported or authored-synthetic
scope; synthetic eligibility cannot authorize a real-book posting. A method
without a complete posting specification returns outside_scope and false.
`accounting.authorize@1` produces this record from the EventBasis and profile;
it does not mutate a book or reuse native assess-only permission.

`AccountingCommitArguments/v1` has exactly `basis_ref`, `authorization_ref`,
`journal_ref`, `delta_ref`. All are nonnull typed Refs to EventBasis,
PostingAuthorization, JournalProposal and EconomicDelta respectively. The
proposal and delta each name the same basis and authorization and contain the
domain journal lines/independent state effects. Their types, signs, contexts,
rounding and roll-forwards obey the accounting contract. Their dependency graph
ends at the immutable basis/authorization, not at the later final commit request.

The outer `OperationRequest` has operation accounting.commit@1 and a nonnull
expected_head whose owner matches the basis's entity/book/branch and state_ref
matches opening_ref. Its generation is the original expected branch generation.
The P2 lookup key is derived solely from basis.identity. A `Ref` to a native v2
assessment in authorization_ref fails INVALID_REFERENCE_KIND; a portable record
with false posting permission fails POSTING_NOT_AUTHORIZED. No flag edit can
pass the recomputed profile/method/admission checks. For a genuinely supported
profile, verify all proposal/authorization/basis bindings before receipt lookup,
then follow exact replay/conflict, absent-key freshness and atomic recheck/commit.
The final receipt refers back to the request/proposal and new state. None of
those earlier records refers forward to that receipt, so L1's graph stays acyclic.

The profile package and domain schema lock define the JournalProposal and
EconomicDelta payload for that operation, including expected account and
economic-state effects. An unknown schema or missing eligible profile yields
UNSUPPORTED_PROFILE_OPERATION, no commit. This is a defined commit interface,
not a claim that P16 supplies every corporate or sector posting method. Existing
R01–R06 remain legacy replay examples under their original schemas. `A1-positive`
is a specified request under an authored equal-price example profile with the
100 asset/2 expense/102 cash candidate; `A1-negative` substitutes the native
assess-only record and must reject before lookup. Equal arithmetic alone does
not satisfy the authorization.

## A2. Accounting results and coverage mapping

These explicit rows extend the integration status table. They consume the full
tagged native response and assessment, not a selected string in isolation.

| Native accounting combination | Platform result |
| --- | --- |
| status=assessed, assessment eligible, computation specified_exact, math unresolved | disposition completed; structural valid; mathematical unresolved; computation complete; native assessment retained; no new commit |
| status=assessed, assessment unresolved, computation specified_exact, math unresolved | completed assessment operation; structural valid; mathematical unresolved; computation complete; no journal or permission |
| status=assessed, assessment ineligible or outside_scope, computation specified_exact, math unresolved | completed assessment operation; structural valid; mathematical unresolved; computation complete; adverse assessment retained; no journal or permission |
| native input rejection invalid/unresolved/not_computed | rejected; same status meanings; request_ref and payload null; submission retained |

`completed` answers whether the assessment request was processed. It says neither
that the proposed treatment is eligible nor that its mathematics was established.
Native accounting_validity=not_assessed remains not_assessed. All specified_exact
examples retain evidence_mode=specification_example and capability
specified_only_no_runtime. X007 therefore maps successfully as a completed
assessment with an unresolved treatment, without inventing `defined` mathematics.
Unknown combinations return STATUS_MAPPING_UNSUPPORTED with the native record
retained and no asserted platform completion.

Coverage mapping preserves every native region predicate and its original
reason/subtype. Native completed → platform completed; unsupported → unsupported;
numerical_failure, solver_unknown and unexplored → unresolved; cancelled →
cancelled. Native proved-empty model regions → infeasible only with their proof
and original model scope. A service failure does not establish such emptiness.
The source partition/overlap relation, parent domain, mass value or explicit
unknown-mass obligation and law/view/admission Refs travel with every region.
Mapping does not merge records solely because they have the same platform label.
Any label without an explicit mapping returns STATUS_MAPPING_UNSUPPORTED.

For mass 3/5 completed and 2/5 numerical_failure, platform output retains both
regions, unresolved subtype numerical_failure and mass 2/5. No normalizing by
3/5 occurs. A region with unknown mass remains unknown, not zero. A read-only
assessment's singleton coverage can be completed even when its treatment is
unresolved; that denominator describes assessment work, not all financial
histories. The financial obligations remain in the typed assessment/unresolved
fields and cannot disappear into the singleton count.

## A3. Repeated conditions and information reuse

The native update operation distinguishes an authored event condition, an
observed likelihood block and a condition proposed as a new observation. Repeating
the identical admitted condition identity in a descendant law is idempotent:
new request ID may produce a new derivation receipt, with denominator one,
unchanged masses, no new atom and the original condition's information lineage
retained. This includes a condition whose lineage traces to an already consumed
observation. It does not multiply that observation's likelihood a second time.

DUPLICATE_INFORMATION applies when the caller submits an already consumed
observation as an incremental likelihood block, or falsely presents the repeated
condition as new information. Matching member sets alone does not establish
matching condition identity. Changed meaning/coordinates/evidence must be bound
and reviewed under their own request. UC01's A and A_then_A are authored
conditions, with no observed-information atoms; D and E are observed blocks with
the specified conditional kernel. This amendment resolves the apparent overlap
between uncertainty §3's idempotence rule and §4's new-information table.

## A4. Selection after correction

Selection owner identity is `(family_ref, target_evidence_view_ref,
target_time_ref, purpose)`. Every owner has its own immutable selection revisions
and mutable selected pointer. A historical query naming an old evidence/time
view reads that view's selection and exact lineage. A correction creating a new
evidence view does not mutate the old pointer or implicitly admit/select its
new candidate posterior. UC08's unchanged state_after therefore refers to the
old owner, not a current pointer in the newly corrected evidence view.

For a current-view query in the new owner, an inherited selection whose
dependencies are superseded returns SELECTION_SUPERSEDED, no usable probability
result, and an explicit re-admission/re-selection obligation. If no inherited
selection exists, return SELECTION_REQUIRED. Resolving either requires an
admissible new attachment and the owner's expected revision; it cannot fall
back silently to an older evidence owner. Historical requests remain valid in
their frozen scope. Numeric correction, admission and selection remain three
distinct effects. This also governs descendants created after the correction.

## A5. Native request versions and validation meanings

For uncertainty attachment storage, `representation_validity` assesses record
shape separately from normalization and reuse. The historical attachment-v2
text's structural_validity label is interpreted as that record-level field.
For an operation result, structural_validity is request validation, including
shape, exact reference binding and admission in the requested view. Retaining
a well-shaped old attachment as RETAINED_ONLY does not make a stale-law request
valid. Platform adapters name their source schema and target field, preserving
both meanings. A malformed supplied record stays invalid at both boundaries;
no status is silently reinterpreted without its record/operation discriminator.

`UncertaintyRequest/chaining-1.1` extends the §2 base request list explicitly.
Base fields remain required and unchanged. A request using a derived admitted
bundle additionally requires admission_receipt_ref, bound to its attachment,
law, view, purpose and admission. Operation `correct_and_rebase` additionally requires
target_time_ref, target_evidence_view_ref and target_admission_ref, each bound
to the corrected inputs and proposed output view. Base law/view/attachment
refer to the frozen calculation input; target fields refer to the revised
authorization context. A target field is not required to equal its base field.
For `likelihood_update`, the three target fields are optional only as an
all-or-none tuple authorizing a proposed changed observation; they do not permit
reuse of a consumed atom. Thus the retained correction submitted incorrectly
as an incremental update passes that shape rule and then fails
CORRECTION_REQUIRES_REBASE. Other operations reject these target fields.
Unknown extra fields and a partially supplied target tuple reject.

The existing CH fixture registry explicitly selects this request profile through
its import adapter; stored native bytes/digests are preserved as historical
examples. New wire requests must advertise the profile in the enclosing
signature/schema lock, never rely on implementation inference from a CH prefix.
No old uncertainty v1 exact field list accepts these extra fields by accident.

## A6. Semantic correction input versus affected descendants

Portable correction uses two separate records. `CorrectionBasis` depends on
the unaffected base law, superseded reading/semantic atom, corrected source,
target time/evidence admission, replacement rule and calculation method.
It does not depend on which optional descendants happen to have been computed.
`InvalidationReport` depends on that CorrectionBasis plus the inspected store
snapshot, and lists affected descendants and why they cannot be reused. Adding
a stored descendant changes the report identity, not the corrected calculation
or its semantic family/law identity. Reverse-dependency discovery and query-time
ancestor checks enforce invalidation for descendants absent from that report.

L1 still requires every typed Ref in each portable record to be listed among
that record's dependencies. Affected descendant Refs are dependencies of the
audit report, not inputs to the corrected mathematical model. This split avoids
both dangling audit references and semantic dependence on optional work.
The native `CH.evidence.corrected@1` is a combined historical audit/context
record. Its LegacyImport retains its ID and maps its corrected inputs to
CorrectionBasis and invalidated_descendant_refs to InvalidationReport. Its old
audit digest is not asserted to be the portable correction's semantic identity.
No retained fixture is rewritten or claimed to have this portable encoding.

REPAIRED FILE docs/design/proposal/architecture/language-ir-contract-v1.md
# Portable financial records and authoring, proposed version 1

The portable representation is the meaning exchanged between extraction,
reconstruction, accounting and reporting. Text notation and typed constructors
are two ways of proposing those records. Neither authoring path can create an
accepted source reading, an accounting permission or a probability merely by
constructing a value. This contract addresses MC02–MC14 and MC23–MC27, especially
G2/G3/G12/G15/G18. `platform-contract-examples-v1.json` supplies specified examples;
the companion calculation checks finite consequences, not a compiler.

## L1. Representation and version boundary

A `Record` has exactly `kind`, `schema`, `key`, `revision`, `body`, and
`dependencies`. `kind` and `schema` name a registered, versioned record
definition; `key` is its stable, schema-scoped logical name; `revision` is a
nonnegative JSON integer (never Boolean). `body` conforms to that exact schema.
`dependencies` is a set of typed `Ref` values. A `Ref` has exactly `kind`,
`schema`, `digest`; its target digest covers the entire target record. Links
inside a body are also typed Refs and must occur in dependencies. Additional
dependencies are permitted only with a declared role in the body's schema.
The dependency graph of a submitted closure must be finite and acyclic. A new
receipt refers to its request and prior state; the prior state never refers
forward to that receipt. Stable business keys may refer to one another as names
without creating content-reference cycles.

Each schema declares required, optional and nullable fields separately, and
rejects unknown fields. Omission and null are not synonyms. Unknown scientific
or accounting content uses `Unknown {reason, obligation_refs}`; an absent required
field is an invalid record. A record with unknown content can be retained but
cannot satisfy an operation that requires that content. A `Candidate<T>` is
distinct from `Admitted<T, view_ref, decision_ref>`. Admission requires checking
the referenced decision in the requested immutable view, including ancestors;
possession of the wrapper alone is insufficient.

Quantities use reduced exact `Rational {n,d}` with signed base-ten numerator
text and positive denominator text: no leading plus or zeroes, `gcd(|n|,d)=1`,
zero `0/1`. Decimal source tokens are converted by their base-ten value, never
through binary floating point. Integer metadata and integer counts remain JSON
integers. This separates the old Core 0 phrase “all numeric values are rational”
from record revisions, ordinals and bounded counts. Approximate results instead
use `Approximation {decimal_text, method_ref, error_description, environment_ref}`;
they cannot be substituted into an exact operation without an explicit
approximation policy and its provenance.

New record digests use `SHA256(UTF8("accdsl.portable.v1/" + schema) || 0x00 ||
canonical(record))`. Canonical JSON is UTF-8, sorted ASCII object keys, no
insignificant whitespace and no floats, NaN, infinity, duplicate keys or invalid
Unicode scalar values. Strings retain their decoded code points; JSON escapes
and literal Unicode for the same code point are equivalent. Composed and
decomposed Unicode are distinct unless a named transformation explicitly maps
them. Identifiers are ASCII; financial labels and quoted source text may be
Unicode. This deliberately replaces implicit global NFC normalization in the
exploratory Core 0 proposal: source spelling must not be silently changed.
Raw source identity always hashes original bytes, outside this record encoding.

A `BlobRef` is a distinct tagged object with exactly `kind="blob"`,
`algorithm="sha256"`, `digest` (64 lowercase hexadecimal digits), and
`byte_length` (nonnegative integer, never Boolean). It resolves to exact bytes,
not to a portable record. A `Submission` record has body exactly
`{blob_ref, media_type, transport, decoder_ref}`, with decoder_ref null when
decoding is unavailable. An OperationResult.submission_ref is a typed Ref to
this record; it is not a record digest falsely assigned to raw bytes. Record
dependencies list record Refs; schema-declared BlobRefs are a separate required
byte-closure obligation checked alongside them.

Native unknowns are decoded through a named LegacyImport adapter. A nullable
value with a required explanatory reason maps to an Unknown carrying that
reason and its source/obligation Refs, while retaining the original native
packet/inner/outer reasons in the import. A non-applicable null remains an
explicit NotApplicable variant, never Unknown or zero. Under native C09,
required=true with a null route requires both nonblank inner and outer reasons;
neither replaces the other. A contextual reason on a known value is annotation,
not an unknown. Missing or malformed native fields reject before conversion.
This mapping preserves source statements without giving the converted value
admission in a new view.

Array order is meaningful except for schema-declared sets. In this version,
`dependencies`, module declarations by key, context dimensions by axis key, and
the explicit IR `all_of`/`any_of` operand sets are canonical sets; reject duplicate
keys or members before sorting by canonical UTF-8 bytes. All other arrays,
including event schedules, journal lines, source spans and diagnostic priority
sequences, retain order. Rational reduction and set sorting occur during typed
construction; a purported canonical wire record violating them is rejected.
There is no general algebraic simplification, alias folding or equivalence proof
in hashing. Hash equality supports byte identity under the chosen encoding, not
economic equivalence or source truth.

For byte-level interoperability the serializer emits literal valid non-ASCII
Unicode scalars in UTF-8. Escape only quotation mark, reverse solidus and control
characters U+0000–U+001F: use `\b`, `\t`, `\n`, `\f`, `\r` for their five named
controls and lowercase `\u00xx` for the remainder. Do not escape solidus. Integers
use minimal base-ten text, with no leading plus, zeroes or negative zero. Input
escapes are decoded before canonical output. Object keys are ASCII and ordered
by unsigned ASCII bytes. These rules, set normalization and rational reduction
fix one byte string for every valid typed record; arbitrary JSON writer defaults
are not part of the definition.

Existing `accdsl.replay.v1/*`, uncertainty fixture and Core 0 digests retain
their original encodings. `LegacyImport {format, original_bytes_ref,
original_id, decoder_ref, portable_ref, comparison_ref}` connects them to a new
record. A migration must prove the stated field/value correspondence and retain
both IDs. A two-decimal acquisition fixture is not a general two-decimal money
rule. No historical digest or receipt is rewritten to fit this proposal.

## L2. Financial types and context

The primitive types are Bool, Int, Rational, Text, Date, Timestamp, Ref<T> and
explicit tagged Unknown. Containers are Option<T>, homogeneous List<T>,
schema-declared Set<T>, records and tagged unions. Bool is not Int. Dates use
valid Gregorian days; timestamps require an offset and retain the original
precision. Timestamp comparison uses the time contract's interval interpretation.

The financial types include `Money<currency>`, `Quantity<unit>`,
`Rate<convention>`, `YearFraction<calendar, convention>`, `InstantValue<T>` and
`Flow<T, [start,end)>`. Every contextual value carries a Context Ref identifying
legal entity, book, perimeter version, basis, currency/unit, economic instant
or reporting interval, calendar and a set of dimensions. Source locators,
reported display scale and reading provenance are retained alongside the value;
they do not silently change its arithmetic magnitude.

Addition, subtraction and comparison require equal financial types and
compatible contexts. A source scale is applied once during reading, while its
original value and spelling remain available. Entity, perimeter, basis,
currency, time or dimension changes require a named transformation with input
and output contexts, method, assumptions and evidence. `sumOver` removes an
axis only under a pinned disjoint/exhaustive partition. `convert` requires a
dated rate, purpose and measurement method. No label similarity converts IFRS
into US GAAP; the standards method must supply a transformation or report that
the comparison is unresolved.

An opening and closing stock cannot be added as flows. Deriving an interim
flow by annual-minus-prior-interim requires compatible interval endpoints,
perimeter, basis and revision view. Precision does not create an error tolerance:
nearest-rounding intervals require source support or an explicit admitted
rounding assumption. A displayed 100 at unit scale may conditionally denote
`[199/2,201/2)` only under the declared tie convention; unknown convention
remains unknown, and different tie rules have different endpoint inclusion.

## L3. Expression and model records

An Expression has `key`, `type`, nullable `context_ref` and one discriminated
operator payload. Literal carries one typed value; ref names one declaration;
negate/not take one operand; add/subtract/multiply/divide/comparisons take two;
`all_of`/`any_of` take nonempty operand sets; field takes a record and field key;
call carries a pinned operation Ref and ordered arguments. Each operator's
payload excludes the other payloads. Boolean expressions remain formulas when
their shared symbols are unknown; Unknown values are never coerced to false.

Multiplication by a dimensionless scalar preserves a financial type. A rate is
not dimensionless: simple interest requires principal, annual rate and an
explicit year fraction. Division requires a nonzero denominator; inability to
establish nonzero is an unresolved precondition, while an established zero
gives undefined mathematics. Backend admission classifies the expanded formula,
not the spelling of a function call. Symbolic products are not rational-linear
merely because the surrounding function has an accounting name.

A Module contains declaration sets for contexts, sources, readings,
interpretations, assumptions, symbols/domains, constraints, choices,
contracts/events, measurements, rules, scenarios and reports, plus a package
lock. Every symbol has one uncertainty category, type, domain and admission
dependencies. Reusing its key means the same unknown in every linked expression.
Global constraints apply to every alternative; a choice-local constraint stays
inside that named choice. Alternatives are joined under the history contract's
specified union/intersection, not silently intersected or independently selected
account by account. No declaration automatically creates a probability measure.

An OperationSignature declares input/output types, context relationships,
preconditions, postconditions, failure codes, effects, capability and method/
authority dependencies. Effects are one of pure calculation, candidate
construction, source acquisition, review proposal or requested transaction.
An accounting rule proposes an assessment/journal/delta; it cannot commit.
Opaque callbacks or arbitrary host-language execution are not portable IR.
Extension packages must declare record schemas and signatures, export hashes
and the unsupported-operation response; unknown required semantics cannot be
ignored. Names are qualified by package and version; no mutable “latest”.

The portable initial exact fragment permits rational affine constraints over
real unknowns plus explicitly finite discrete choices and bounded integers.
Negative rates are permitted when the operation's economic domain permits them;
the P03 nonnegative-rate restriction is not inherited globally. Unsupported
nonlinear, unbounded discrete, distribution or calendar methods return the
requested operation and missing capability. Partial linearization is a new
assumption-labelled model, never an exact solution of the original formula.

## L4. Compilation and matched authoring

`CompileRequest` supplies source kind (text or typed construction), source bytes
or typed Module, schema/profile refs, full package lock, evidence/time view and
requested capability target. Compilation performs, in order: strict decode and
source spans; name/import resolution; dependency/cycle checks; static types and
context checks; admission-layer checks; expanded-operation capability analysis;
canonical record production. Each stage returns all independently decidable
diagnostics in stage/path/code order. Dependent checks are `not_evaluated` with
their blocking diagnostic; they are not additional guessed type errors.

`CompileResult` returns candidate IR, source map, unresolved input obligations,
capability analysis and a validation receipt bound to every input. Invalid
structure/types produce no executable IR. A well-typed module can have unresolved
financial inputs: return a retained candidate and `execution_admitted=false` for
affected targets. Compilation does not call a solver, choose a history, post a
journal or turn source acceptance into method eligibility.

The bounded text notation retains Core 0 lexical/precedence rules and its
registered declarations. Unsupported syntax is diagnosed; textual support is
advertised per declaration/signature. Typed constructors produce the same
abstract declarations; arbitrary Python objects or lambdas are not accepted.
Both frontends pass through the same typed IR admission rules. Text positions
are Unicode code-point half-open ranges in retained source bytes after a named
decode; typed positions are constructor paths. Source maps are outside model
semantic identity, but their own content hashes bind the exact authored source.
Formatting and comments may change a source-map ID without changing the model.

LX01 specifies matched text and typed declarations for debt 100, shared unknown
floating share x in [0,1] and interest `100*((1-x)*1/20+x*7/100)`. Both propose
the same financial expression and its explicitly conditional stress assumption.
Its expanded interest is `5+2x`; endpoints are 5 and 7 and x=1/2 gives 6.
The shared domain is continuous, not two equally probable cases. LX02 changes
7/100 to 9/100, so the upper endpoint becomes 9: frontend agreement alone would
miss a shared wrong constant, hence the independent arithmetic. LX03–LX08 reject
currency/context mixing, absent admission, symbolic nonlinearity at an exact
linear backend, duplicate keys and unknown imports. These are proposed expected
exchanges; the document calculation is not evidence of a completed compiler.

## L5. Alternatives and consequences

The old small text compiler and typed library are useful feasibility evidence,
but neither settles the portable representation. JSON records are proposed
because they are inspectable and already match retained evidence; a binary
encoding is permissible as a lossless transport with a specified decoder.
Embedding executable Python is rejected as the governing representation because
it leaves side effects, evaluation order and unknown handling outside a shared
contract. XBRL remains an evidence interchange, ledgers carry concrete postings,
and inference languages implement selected methods; none by itself preserves
all the required evidence, joint histories and accounting admission layers.
No authoring, performance or maintenance superiority has been measured.

REPAIRED FILE docs/design/proposal/architecture/persistence-contract-v1.md
# Persistence, correction and recovery, proposed version 1

A completed accounting transition is one committed fact about a particular
book and branch. A lost network response must not post it again; a correction
must not rewrite what an earlier information view contained. This contract
addresses MC04–MC06, MC18, MC25, MC27 and MC33–MC35, especially G17/G18. It
specifies observable storage behavior. The examples are transaction traces,
not an implemented database or a durability experiment.

## P1. Ownership and retained objects

One transactional store owns immutable portable records, dependency edges,
review snapshots, branch heads, committed journals/state deltas, operation
receipts and continuation checkpoints. Original source bytes live in immutable
content-addressed storage. A metadata transaction may reference a blob only
after its exact bytes are durably available and verified. A crash between blob
creation and metadata commit can leave an unreferenced blob; it cannot leave an
accepted source reference to absent bytes. Existing originals are retained.
Exports, caches, Parquet tables and rendered reports are derivatives of a named
store snapshot, not additional writable truth. An export failure does not undo
a committed transaction or justify posting again.

Each branch has a stable `branch_key`, an immutable branch definition Ref and a
mutable head `(state_ref, generation)`. The branch definition names its family,
evidence/model/scenario versions and projection namespace. A separately
commissioned hypothetical run uses a new projection namespace/branch key;
reopening the same run uses its original key. A branch revision, renamed run or
retry cannot evade an event conflict inside that namespace. Aggregating branches
requires the declared family/view semantics and never counts projections as
multiple realized transactions.

The initial local implementation is proposed to have one logical transaction
writer. Multiple clients may submit requests, but the store serializes commits.
Other implementations must provide the same atomic comparisons and isolation;
“single writer” is not permission to omit stale-state checks. SQLite is an
implementation candidate based on P07's bounded probe. Distributed consensus,
specific filesystem durability and physical media failure guarantees require
their own implementation and evidence; no document calculation establishes them.

## P2. Event commit and replay

The stable accounting lookup key remains the tuple `(entity_id, book_id,
branch_key, business_event_id)` from accounting-replay-contract-v1. Event version,
payload and expected opening state belong to the complete request fingerprint,
not the lookup key. The generic Core 0 run/event key is historical exploratory
evidence and does not override this rule. Legacy fixture digests are retained
through the import mapping in L1, never silently compared with portable digests.

For one requested event the store performs:

1. Validate the request's decoding, field shapes, exact reference closure,
   internal bindings and admissible historical context. Corrupt or inconsistent
   input fails before any receipt lookup. Validate independent fields in the
   declared stage order; do not derive fresh accounting assumptions here.
2. Read the committed receipt index under the stable key. An equal fingerprint
   returns the original immutable receipt with `additional_commit=false`.
   A different fingerprint yields `EVENT_ID_CONFLICT`, including when its event
   version differs. Replaying a valid historical request is not reassessment
   against today's source or method version.
3. For an absent key, compare both expected opening state and expected head
   generation. A mismatch returns `STALE_OPENING_STATE`. Assess treatment and
   construct the candidate journal, economic delta and closing state outside
   mutation. Arithmetic/balance alone cannot authorize a treatment.
4. In one transaction, recheck absent key and the same head comparison, validate
   the candidate dependencies, then insert the journal, delta, closing state,
   dependency edges and immutable committed receipt, and advance the head.
   Commit all or none. A competing identical commit returns the original
   receipt; a different fingerprint conflicts; a competing different event
   advancing the head makes this request stale. No speculative candidate is
   published as committed while the comparison is unresolved.

The observation returned with replay may identify today's branch head, but the
receipt's original opening/closing states, assessment and journal never change.
The four accounting domains in the existing fixtures—state, journal registry,
delta registry and committed receipt index—remain identical on rejection/replay.
Candidate scratch data and diagnostics are not members of those domains.
Rejected requests may append a separately typed audit record after validation;
it cannot appear in the committed event index or count as an economic transition.
If an operation promises an audit receipt and its audit write fails, report that
failure explicitly while retaining the established unchanged-domain outcome.

## P3. Crash ambiguity, resume and exports

A response has `commit_observation` equal to `committed`, `not_committed` or
`unknown`. A crash before the atomic commit leaves the old head and no new
receipt. A crash after commit but before acknowledgement leaves the complete
new head and receipt. The client's timeout alone cannot distinguish those cases;
return `unknown` with the original key/fingerprint and query/retry that identity.
Do not retry under a fresh event ID. Once storage recovers, receipt lookup
resolves the ambiguity. Missing/corrupt committed dependencies are an integrity
failure, not a reason to reconstruct an apparently similar receipt.

A search checkpoint atomically records the semantic manifest, partition identity,
completed/explored cells, preserved unresolved formulas/regions, frontier order,
budget used and resulting objects. A cell is not complete before its evidence
and frontier transition commit together. Resume requires the original semantic
manifest and partition/traversal identity. An increased explicitly supplied
budget is a new scheduling request linked to the old checkpoint, not a new
financial model. Changed source, context, method, scenario, family or ordering
requires a new applicable manifest and a stated reuse relation; it cannot reuse
an old suffix by position. Cancellation preserves the last committed frontier.

Immutable export manifests name every record/blob, format/decoder, digest,
root query/view and required reference closure. Stage an export in a temporary
location, verify its closure, then publish its manifest atomically. An incomplete
export is explicitly incomplete and cannot be loaded as a closed bundle. Import
verifies all referenced bytes before committing metadata; an unavailable
optional attachment remains a located coverage obligation. Missing required
closure rejects dependent use, even if the manifest itself hashes correctly.

## P4. Review, correction and invalidation

Source and review requests have their own idempotency namespace
`(operation_kind, workspace_key, request_id)` and fingerprints. A repeated exact
request returns its immutable receipt; changed payload conflicts. A new review
uses an expected prior view and generation. It records reviewer, rationale,
accepted layer, referenced evidence and operation (propose, accept,
accept-alternative, reject or supersede). Legal state transitions follow the
evidence contract. Self-supersession and mismatched replacement scope reject
before mutation. Only review admission records can advance a reading's layer.

A new immutable view records its parent, changed decisions and dependency
selection revisions. It never mutates the old view. Invalidation follows the
reverse dependency graph transitively, including dependencies on candidate-set
membership, not only on the previously chosen members. Therefore adding a newly
eligible filing can stale a selection that formerly had one member. Newly
created descendants must check all ancestors against their requested view;
they cannot escape invalidation by being created after the invalidation scan.
Unrelated dependency closures remain usable. `explain` always uses the output's
frozen view; a current-view query explicitly reports stale dependencies.

A correction to an economic event is a new business event linked to its
predecessor and a specified correction method (reversal/replacement or a dated
adjustment, as applicable). It does not overwrite the original receipt and a
version bump alone does not post it. Corrected historical disclosure creates a
new evidence/model projection; it does not retroactively change what an investor
or the system knew. P17 supplies the accounting treatment of each correction;
missing treatment authority remains unresolved rather than a generic reversal.

## P5. Migration and reproducibility

Migration input is `(old_schema, new_schema, migration_method_ref, source_snapshot,
expected_head, declared_semantic_relation)`. Output retains original bytes/IDs,
new bytes/IDs, a complete mapping and the comparison evidence. A
representation-only migration must preserve decoded typed quantities, contexts,
uncertainty categories, references, admission states, event identities and exact
reference-query outcomes. Invertibility over the retained source domain or an
explicit lossless retained original is required. Changed model meaning, rounding,
calendar, probability or operation order is a new model/version, not a successful
representation-only migration. Failed mapping or comparison leaves all prior
heads and objects usable; migration never silently fills missing metadata.

Replay locks the model, view, package/calculator versions, scenario, requested
outputs, numeric/calendar policies, algorithm/capability manifest and relevant
environment. Exact rational operations on the same evaluated domain require
exact equality. Receipt replay returns the original recorded partition and
values. Re-executing a partial search with a wall-time limit need not visit the
same cells on another machine: compare answers on matched cells, retain both
frontiers and make no claim that partial coverage is identical. Reproducible
prefix comparisons use a pinned traversal and operation-count budget;
elapsed-time limits are resource stops, not semantic equality criteria.
Resume uses P3's exact saved frontier. Approximate
operations require predeclared method-specific error comparisons and retain both
values; a generic float tolerance cannot establish financial equivalence.
Random-stream identity names seed, coupling group, economic owner, date,
shock-kind and draw index, with pinned generator and transforms. Branch traversal
position is absent. The retained SHA-based reference primitive remains only an
identity illustration; no production generator or calibration is selected here.

PX01–PX08 in the shared examples specify lost acknowledgement, exact replay,
changed payload, two writers at one head, correction invalidation, branch
isolation, incomplete export and migration outcomes. Their finite traces make
the expected behavior reviewable. The future implementation must additionally
pass crash/reopen/fault-injection tests on the selected storage/environment.

## P6. Alternatives and tradeoffs

Mutable documents with periodic checkpoints cannot establish the atomic
receipt/state relation above without an additional transaction protocol.
An event log with deterministic projections is viable if its commit marker,
projection visibility and replay checkpoints obey the same contract. The
proposed transactional metadata store plus immutable blobs separates large
source bytes from small atomic changes and fits existing local probes. Its
single-writer throughput and crash guarantees are unmeasured. Analytics engines
and storage libraries remain replaceable behind these observable semantics.

REPAIRED FILE docs/design/proposal/architecture/interfaces-contract-v1.md
# Operations across the financial model, proposed version 1

The interfaces connect an acquired disclosure to a proposed reading, an admitted
financial model, alternative histories and conditional statements. Each operation
names the version it consumes and the authority it needs. In particular, an
extraction service cannot accept its own interpretation, a valuation service
cannot authorize accounting, and a report cannot commit journals. This contract
addresses MC01–MC27 and MC33–MC35, with the software obligations of MC29–MC32.
It specifies exchanges; it does not provide runtime endpoints.

## I1. Common request and response

`OperationRequest` is a portable L1 record with schema
`accdsl.operation.request.v1`. Its body has exactly:

| Field | Required type and meaning |
| --- | --- |
| `operation` | Qualified operation name from I2; no implicit version selection |
| `request_id` | ASCII identifier, stable across retries of the same request |
| `workspace_key` | ASCII identifier for the store namespace |
| `profile_ref`, `signature_ref` | Exact profile and operation-signature Refs |
| `view_ref` | Immutable evidence/review/time view Ref; never a mutable `current` alias |
| `arguments` | Closed tagged record for the named signature, with fields in I2 |
| `execution` | `{mode, budget, environment_ref}`; mode is `specification_example` or `runtime`; budget explicitly states operation count and elapsed-time limits or a reason each is inapplicable |
| `expected_head` | Null for a read, or `{owner_key, state_ref, generation}` for a requested mutation |

All fields are present. Null is allowed only where stated. A caller asking for
the current view first resolves it and receives its revision; mutation compares
that revision again. Arguments contain typed Refs and typed values, never
arbitrary host-language objects. Required closure is the transitive closure of
request dependencies plus schema/package definitions in its lock. A missing
optional source attachment remains a named coverage obligation; a missing
required rule, record, admission or decoder rejects affected use. Schema version,
argument type or unsupported operation is diagnosed before calculation. A
request fingerprint covers the exact portable request, including expected head,
generation, request_id and execution settings; accounting's historical
fingerprint is retained by an explicit legacy adapter, not recomputed as this one.

`expected_head` occurs only in the common envelope. References to an expected
head or revision in the signature table below mean that envelope field, not a
duplicate argument. For accounting its owner is the entity/book/branch and
state_ref is the opening state; for review its owner is the review namespace
and state_ref is the review view; for uncertainty selection its owner is the
family/evidence/time selection and state_ref is the selection record. In each
case generation is that owner's monotone revision. Retry after unknown commit
resubmits the original expected head/generation and all original request bytes.
Refreshing the expected head constructs a different request and must never be
used to disguise a retry. Lookup precedes current-head freshness.

Accounting idempotency uses only P2's business-event lookup namespace.
request_id is correlation metadata, not a second accounting lookup index, though
it remains part of the complete fingerprint. Reusing it for a different
business-event key does not alias the events; changing it for an already
committed event changes the fingerprint and conflicts. Source/review/selection
mutations use their separately specified operation/workspace/request namespace.
The new branch_key maps to the native branch_id value through an explicit
LegacyImport binding, preserving the original entity/book/branch/event tuple.

`OperationResult` has exactly `submission_ref`, `request_ref`, `operation`, `input_view_ref`,
`disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
`continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
References are typed. `submission_ref` identifies the preserved exact submitted
bytes and transport/decoder metadata through L1's Submission record and BlobRef;
it always exists when submission retention succeeds, even when decoding fails.
If the retention store itself fails before writing it, return an out-of-band
transport failure carrying the original client correlation and no purported
OperationResult or committed outcome. The caller still retains its submission.
`request_ref` is null until a typed request passes validation. `operation` and
`input_view_ref` are null when the corresponding validated identities are not
available; a diagnostic may quote the untrusted submitted values. Continuation
and receipt references may also be null. `payload` is a tagged
union selected by the signature; rejected input has null payload. `diagnostics`
and `unresolved` are ordered lists (possibly empty). `coverage` contains the
requested domain Ref and completed/unresolved/unsupported/infeasible/cancelled
region Refs, with their partition/overlap relation. Reads may use one singleton
request region; they cannot invent an economic-family denominator. When request
validation prevents establishing the requested domain, coverage is null with
the blocking diagnostic; it is not an empty completed domain. `statuses`
and disposition obey F1. `evidence_mode` repeats specification/runtime, so an
expected `complete` in a document never asserts runtime execution.

`commit_observation` describes the mutation requested by this operation:
`committed`, `not_committed`, or `unknown`. A read returns `not_committed` even
when it inspects an earlier committed receipt. Accounting's replay payload may
say the original event is committed while the outer result says this invocation
made no new commit. The payload must carry `additional_commit=false`; this is
not a contradiction. A successful review or checkpoint mutation has its own
receipt and is never described as an accounting posting.

Transport status and financial status are independent. An HTTP error or client
timeout is not evidence of noncommit. A local Python, CLI or service binding
must preserve the same argument values, input versions and result union. There
is no required network deployment, server framework or user interface in P16.

## I2. Operation signatures and ownership

In this table each listed input is required unless explicitly marked optional.
Lists are explicit even when empty. Domain records retain the detailed fields
in their named contracts; the table does not replace them with untyped prose.

| Versioned operation | Arguments → payload | Effect and controlling contract |
| --- | --- | --- |
| `source.prepare@1` | package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation → ExtractionPreparation | Acquires/preserves sources and constructs candidates under extraction-v1; no semantic admission |
| `review.propose@1` | target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null → ReviewProposal | Candidate construction; accepts no layer |
| `review.commit@1` | ReviewProposal, expected review view/revision → immutable ReviewDecision and new view | Review transaction under evidence E4/persistence P4; admissible action/layer required |
| `time.select@1` | package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy → selected assertions, conflicts and temporal obligations | Pure selection under time T1–T6; no invented ingestion or publication time |
| `model.compile@1` | CompileRequest from L4 → candidate Module, source map, diagnostics and target admission/capability report | Candidate construction; no solver or posting |
| `history.construct@1` | admitted Module, opening, scope, template registry, query/horizon, resource budget → HistoryFamily, partition, witnesses and unresolved formulas | H1–H7; witnesses are examples within the family, not its definition |
| `history.refine@1` | frozen family, additional admitted constraint or refinement, dependency view, budget → child family and inclusion relation | Candidate construction; record whether correction replaces constraints instead of intersecting them |
| `history.query@1` | family, typed joint observable, bound/feasibility request, capability manifest → symbolic/partial/exact answer, coverage and endpoint attainability | Pure; unsupported expressions remain explicit |
| `uncertainty.evaluate@1` | exact native uncertainty request, law/attachment/admission and operation-specific event or observation block → native UncertaintyResult and candidate derived bundle | Native admission/attachment/chaining rules; never selects its result automatically |
| `uncertainty.admit@1` | candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision → admitted attachment and decision | Admission transaction; author-stipulated measures keep that label |
| `uncertainty.select@1` | admitted attachment/receipt, rationale and expected selection revision → new selected-view revision | Selection transaction; no probability recomputation |
| `scenario.project@1` | family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget → conditional event/journal/state proposals by history and scenario | Candidate construction; budgets preserve unresolved regions; no historical-book commit |
| `accounting.assess@1` | native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions → TreatmentAssessment | Pure accounting assessment; inherited `assess_only` profile cannot post |
| `accounting.authorize@1` | AccountingEventBasis and posting-profile Ref → PostingAuthorization | Pure evaluation under a separately supported posting profile; an assess-only result cannot grant posting permission |
| `accounting.propose@1` | PostingAuthorization, AccountingEventBasis and posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
| `accounting.commit@1` | AccountingCommitArguments/v1 and envelope expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; schema in cross-contract-amendment-v1, separate from native assess-only |
| `report.build@1` | frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy → joint statement family, reconciliation and coverage | Pure; derive from retained state/journals, no balancing plug or hidden branch selection |
| `record.explain@1` | output Ref, its frozen view, requested lineage depth → source/method/assumption/decision paths and unresolved dependencies | Pure; depth truncation is explicit; cannot substitute today's view |
| `work.resume@1` | checkpoint Ref, original semantic manifest, scheduling budget → operation-specific resumed result | Resume the original operation; checkpoint ownership/atomicity in P3; no model change hidden as resume |
| `store.export@1` | snapshot/root Refs, format/decoder, destination → closed manifest or explicit incomplete export | Derivative publication under P3; no domain mutation |
| `store.import@1` | closed manifest, exact blobs/records, decoder and target namespace → import receipt and original-to-local mappings | Verify before metadata transaction; import alone grants no financial admission |
| `store.migrate@1` | migration request from P5 → preserved originals, new representation, comparison/mapping and receipt | Transaction only after required semantic comparisons; no changed-model-as-format claim |

Compilation and history queries may be pure with respect to committed accounting
state while producing immutable candidates in a scratch or candidate store.
Persisting those candidates requires the named owner and receipt. The effect
classification is not a promise that no bytes are written anywhere.

## I3. Scenario information and joint statements

The initial `ExogenousScenario` specifies dated values or formulas for named
drivers, their domains, units, admissibility assumptions and dependencies. An
`InformationView` exposed to a policy or measurement operation contains only
admitted historical information up to its decision instant and permitted
simulated past. Future simulated values are withheld, even when the scheduler
already knows the full imposed path. Deterministic stress does not by itself
authorize perfect-foresight decisions; a separate assumption must do that.
Observational conditioning uses the uncertainty interface. A causal intervention
requires a specified causal model/replacement operation and is unsupported by
the initial exogenous profile.

The result remains indexed by history, admissible treatment and scenario. Every
statement amount refers to that common index, opening and event sequence.
Cash flow, profit, balance sheet and equity movement are reconciled jointly.
Reporting may return separate conditional answers or a pushforward of an
admitted law. It cannot create one statement from independent minima/maxima
that occur in incompatible histories. Aggregating an axis requires a pinned
disjoint/exhaustive partition or returns an unallocated residual with a reason.
An unsupported tax/lease/FX method makes dependent lines unresolved; unaffected
amounts remain available with their dependence stated.

## I4. Extension boundary and adapters

An `ExtensionPackage` declares `{package_key, version, record_schemas,
operation_signatures, supported_contexts, state_requirements, authority_refs,
method_refs, capability_requirements, migration_refs, example_refs}` and pins
every member. Empty authority lists mean no accounting-authority claim, not
universal eligibility. Callers verify the method's dated entity/instrument/basis
scope and uncertainty admission separately from schema loading.

Corporate records retain receivable/payable terms, inventory lots and cost
method, assets and depreciation memory, tax bases, leases, debt/equity rights
and contingencies. Groups retain legal entity, control evidence, dated perimeter,
ownership/NCI, functional/presentation currencies and elimination links. Banks
add cash-flow terms, effective rate, credit-risk stage, default/cure history,
collateral/guarantees and prudential-rule context; prudential capital is not
accounting equity. Insurers add coverage units, cohort/group eligibility,
fulfilment cash-flow assumptions, discount/risk adjustment, CSM/loss component,
reinsurance and service history. These are structural obligations; P17 must
specify their method fields, transitions, authority and matched cases before an
operation using them becomes supported.

An extraction adapter returns located candidates; a contract scheduler returns
dated contractual events; a valuation adapter returns a quantity with method,
currency/date and numerical evidence; an accounting method returns an assessment
and proposed entries; a ledger adapter exchanges concrete entries/receipts.
None inherits another's authority. Each adapter manifest identifies upstream
version/license, supported subset, input/output schema mapping, calendar/unit/
rounding transformations, preserved lineage, information loss and unavailable-
backend behavior. Lost economically relevant fields veto that exchange. Retaining
raw upstream output permits inspection but does not repair lost meaning.
P17 owns pinned official-interface/license inspection and executable adapter
feasibility; existing exploratory tool presence is not completed integration.

## I5. Precedence and versioning

The active P16 architecture index pins its contracts. Domain-specific validation
and accounting/uncertainty vocabulary take precedence within their versioned
native interfaces. Platform v1 adds explicit wrappers and cross-contract rules;
it does not rewrite saved native receipts. `architecture-integration-v1.md`
records status mapping and the precise historical rules that are superseded.
A later amendment prevails only for the fields and profile it expressly names;
date alone or a file named “latest” grants no precedence.

Two conflicts are resolved explicitly. The stable accounting event key is P2's
entity/book/branch/business-event key, not an event-version or transient-run key.
For native assessment validation, the established parse → recognizable
dependencies → shape → source versions → bindings sequence prevails over a
generic platform ordering. A wrapper may reject its own malformed envelope
first; it cannot expose a receipt before native validation. New portable-only
operations use F2's order. This preserves historical outcomes without letting
the old generic Core 0 contracts silently select defaults for new domains.

IX01–IX06 in the shared example file cover a connected company, changed stress,
an unresolved operating input, later-information rejection, overlapping report
classes and a sector call without an eligible method. Together with the native
complete accounting exchanges they make the contracts' interaction inspectable.
They specify results; the document calculation verifies only finite arithmetic
and reference consistency. Compatible implementations still require actual
frontend, backend, storage and recovery conformance evidence.

REPAIRED FILE docs/design/proposal/architecture/failure-contract-v1.md
# Results, incomplete work and failures, proposed version 1

A missing source, an insolvent company and a crashed solver are different
outcomes. Combining them into “failed” would either lose admissible histories or
publish results with stronger meaning than the evidence permits. This contract
addresses MC08–MC14, MC18, MC25 and MC33–MC35 and integrates the existing
uncertainty and accounting status rules.

## F1. Independent result dimensions

Every public operation returns an `OperationResult` bound to its request and
input snapshot. It contains a disposition, status envelope, typed payload,
diagnostics, unresolved obligations, domain coverage, nullable continuation and
commit observation. Disposition is one of `completed`, `partial`, `rejected`,
`unsupported`, `cancelled`, `internal_failure`, `commit_unknown` or `replayed`.
It is not an accounting conclusion. Successful completion within a declared
scope does not imply that scope describes every real history or disclosure.

The existing uncertainty envelope remains normative: structural validity,
mathematical status, computation status, empirical justification, capability
status, accounting validity and human acceptance have separate fields. An adapter preserves
the exact domain-native vocabulary in the payload; it does not invent a Boolean
“passed” from them. In particular, a pre-evaluation rejection uses
`structural_validity=invalid`, `mathematical_status=unresolved` and
`computation_status=not_computed`, as the rejection-status supplement requires.
Mathematical status cannot be `not_computed`. Empirical/capability/accounting/
human fields are copied from the governing operation evidence in their native
vocabulary, never assumed accepted.

For new platform envelopes, structural validity is `valid` or `invalid`;
mathematical status is `defined`, `failed`, `undefined`, `unresolved`, `infeasible` or
`not_applicable`; computation status is `complete`, `partial`, `not_computed`,
`cancelled` or `failed`. Domain-native subreceipts keep their own named schema
and vocabulary. The platform does not rewrite historical receipts to these
labels: its explicit versioned adapter maps their stated meaning. New platform
envelopes additionally retain `empirical_justification`, `capability_status`,
`accounting_validity`, `forecast_validity`, `product_readiness` and
`human_acceptance`. The first three copy a supported native value or use
`not_established`, `specified_only_no_runtime`, `not_assessed` respectively;
the last three are `not_assessed`, `not_implemented`, `pending` in these examples.
No map turns `specified_exact` into a claim of runtime execution: evidence mode
remains `specification_example`. The explicit mappings and unsupported cases
are in architecture-integration-v1.md.

Mathematical `infeasible` requires established emptiness of the declared model;
solver silence gives `unresolved`. Conditioning on a zero-probability event
under the specified finite law is `undefined`, even if computing its zero
normalizer completed successfully. A feasible symbolic family may have a
partial search. An economically defined default event is an outcome of a
successfully evaluated scenario when its default method is supported; it is not
a solver failure. A positive balance check establishes none of the accounting,
forecast, product or human acceptance fields.

## F2. Diagnostic and rejection order

`Diagnostic` has code, stage, record Ref or submitted-byte Ref, source locator,
field path, affected query/branch IDs, dependency path, observed value/category,
expected rule, retry advice and blocking diagnostic IDs. No fabricated numeric
substitute appears in place of an unavailable observation. Diagnostic prose
explains a typed code but cannot supply missing economic facts.

For new portable-only operations the stages are decode; field shape; reference integrity; cross-record
binding/context/time admission; capability/admission; requested calculation;
transaction comparison; publication. An operation may refine these stages,
but cannot reverse a required domain ordering. Existing native accounting uses
parse → recognizable dependencies → shape → source versions → bindings, as
specified in the field-validation supplement. For accounting, all specified
source field/binding checks precede receipt lookup; lookup precedes new-event
freshness and treatment calculation. Retried historical requests use their
pinned historical context, not today's review view. Domain profiles identify
which preconditions are checked before lookup and which only for a new event.

Return all independently decidable diagnostics within the earliest failed stage,
sorted by schema-defined stage rank, canonical field path and code. Later stages
are explicitly not evaluated. A malformed parent/controller suppresses its
dependent child predicates; it does not suppress independent sibling findings.
This incorporates the guarded C03/C05/C07/C09/C10 reason rules without turning
an unknown route into false or promoting contextual prose into evidence.
Invalid requests return no candidate result that could be used as admitted
output. Retained submitted bytes and separate audit receipts remain available.

## F3. Preserve the requested domain

Every aggregate identifies the full requested family/view/scenario domain and
partitions its work into completed, unresolved, unsupported, infeasible and
cancelled regions. Regions are predicates with identities and coverage relations,
not just counts. Overlap is explicitly represented or removed under a proven
partition; unexplored formulas remain available. A partial result states which
queries depend on unresolved regions and which are unaffected. “No completed
regions” is not an empty family.

With an admitted joint law, retain assigned mass for all regions, including
unsupported or failed evaluations. Do not renormalize successful regions.
Example FX01 assigns mass 3/5 to a path returning cash 120 and 2/5 to a path
whose calculation is unavailable. The returned known cash mass is 3/5 and
unresolved mass 2/5; neither mean 120 nor a complete cash distribution is
authorized. If the unresolved path has independently established cash bounds
[80,110], the unconditional mean is bounded by [104,116]; without those bounds
even that interval is unsupported. Computing a conditional mean given successful
evaluation is a different estimand and requires an explicitly requested,
meaningful conditioning event; computational success is not economic evidence.

Without an admitted law, return joint feasible regions or per-history conditional
results, never weights derived from witness/branch counts. Interval endpoints
from partial exploration are explored-only. An exact bound must identify the
full formula, proof/certificate or checked exact method, endpoint attainability
and numerical policy. A supremum of 1 for x<1 is not an attained maximum.
Approximate bounds retain method, error description and missing coverage.

## F4. Retry, cancellation and integrity

Retry advice distinguishes `same_request_after_service_recovery`,
`inspect_commit_then_retry_same_identity`, `new_request_after_input_repair`,
`new_model_or_capability_required` and `no_automatic_retry`. A model-input repair
gets a new fingerprint; it cannot reuse an existing business-event key to hide
a conflict. Availability failures preserve input and work checkpoints; an
unknown commit must first be reconciled under its original identity.

Caller cancellation stops new work at the next interruptible boundary and
returns the last committed checkpoint. Already committed events are not rolled
back by a cancelled response. Cancellation during a storage call may yield
unknown commit observation until recovery. A callback that cannot be interrupted
requires an external resource limit and a recoverable process boundary; a
cooperative progress report is not proof that a commit did or did not occur.

A mismatched required digest, invalid dependency cycle, corrupted committed
record or inconsistent checkpoint is an integrity veto on affected use. Preserve
the invalid bytes and report the mismatch. Do not resume, fabricate replacement
evidence or relabel the error as financial infeasibility. An unrelated corrupt
source does not block a query whose complete dependency closure excludes it.

FX02–FX07 specify zero conditioning mass, unsupported nonlinear bounds, economic
default, a timed-out worker, malformed source fields and unknown commit. They
make both allowed and forbidden conclusions explicit. The checks are finite
examples of the proposed semantics; accounting authority, empirical forecast
quality and production recovery remain separate evidence obligations.

## F5. Alternatives

A single success flag is simpler to transmit but conflates mathematical meaning,
computation, admission and acceptance. Throwing an exception for every partial
branch loses useful unaffected results and encourages selection bias. The
proposed typed result plus diagnostics preserves partial work while making
invalid or unsupported calculations unusable as complete results. Exceptions
may still signal implementation faults internally, but the public boundary
must retain the submitted identity, commit uncertainty and last durable work.

REPAIRED FILE docs/design/proposal/architecture/architecture-integration-v1.md
# Integration of the nine proposed contracts

The active contract list in P16 architecture.json is the document index. This
supplement resolves interactions among those contracts without altering earlier
evidence or treating saved fixture outcomes as executed product behavior. It
addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
prototypes, not automatic defaults.

`cross-contract-amendment-v1.md` A1–A6 is the active named amendment for the
portable commit schema, accounting/coverage mappings, repeated conditions,
corrected-view selection, native uncertainty schema/validation meanings and
semantic-versus-audit dependencies. It takes precedence for those exact
interactions while retaining original native bytes and their evidence limits.

## Meaning carried between contracts

| Boundary | Meaning that must survive | Rejection or unresolved consequence |
| --- | --- | --- |
| Evidence → time | Original bytes, source occurrence, review layer, economic/reporting/publication/ingestion clocks | Missing clocks cannot support stronger historical-knowledge claims |
| Evidence/time → history | Scoped admitted interpretation/assumption, joint symbols, conflicts and exclusions | Faithful reading alone cannot become an admitted accounting constraint |
| History → uncertainty | Full family/view, partition, dependence and query-relevant economic memory | No weights from witness counts; missing law gives a symbolic/unweighted result |
| Scenario/history → accounting | Branch opening, exact event identity, date/context, permitted information and eligible method | Unresolved or unsupported treatment produces no posting |
| Accounting → persistence | Validated request, source/method versions, proposal/delta and expected head | Exact replay before freshness; all-or-none transition; unknown commit reconciled under original identity |
| Calculation → report | Common history/scenario index, native statuses, unresolved regions/mass and unit/time semantics | No successful-subset renormalization or independent selection of line extrema |
| Correction → all descendants | Immutable old view, replacement scope, candidate-set membership and transitive dependency | Current reuse invalidated even for descendants created after the correction |
| Any contract → IR/interface | Versioned type, lineage and admission requirements | Unknown schema or required semantics cannot be ignored or coerced |

## Explicit amendments and precedence

L1's portable encoding applies only to new portable records. Existing native
record digests, original files, source byte hashes and receipts stay unchanged.
Integer metadata remains integer; financial quantities use exact rationals.
There is no global NFC normalization. A named legacy import retains both IDs
and checked decoded correspondence. Source-map identity is separate from model
identity, so formatting changes do not alter a model's financial meaning.

P2 resolves the early accounting contract's ambiguous “event/version” language:
the stable lookup key excludes version and payload. A correction uses a new
business-event identity with an explicit treatment/lineage; merely changing a
version under an existing key conflicts. Branch identity includes an explicit
projection namespace, distinguishing separately requested hypotheticals from
retries of the same projection. No double counting of hypothetical projections
is permitted when reporting realized transactions.

Native accounting retains its established validation order and assess-only
boundary. New portable wrappers validate their own envelopes and then delegate
to that native order. Dependency recognition is guarded by reference shape;
malformed refs are not followed. A shape error cannot be masked by finding an
old receipt. Output defects are distinguished from ineligible economic events:
reject publication as ASSESSMENT_OUTPUT_INVALID while retaining the validated
request and diagnostic candidate. All four committed accounting domains remain
unchanged for assess-only, rejection and replay.

Uncertainty fixture v2 rejection receipts supersede only their explicitly named
v1 predecessors. Their valid requests, joint laws, calculation payloads and
unchanged successes remain evidence. Derived law/view bundles require separate
admission and selection; a numerical posterior does not admit itself. No
platform wrapper changes an existing domain's status values in place.

## Status mapping at the new platform boundary

The native uncertainty schema has seven distinct statuses. The new platform
schema preserves the full native result and applies these mappings only with
the operation's tagged disposition and payload. Unknown combinations return
`STATUS_MAPPING_UNSUPPORTED`; they are not guessed.

| Native meaning | Platform interpretation |
| --- | --- |
| REQUEST_INVALID with invalid/unresolved/not_computed | rejected; invalid/unresolved/not_computed; no usable payload |
| satisfied + specified_exact, with a valid finite calculation payload | completed; valid/defined/complete; evidence_mode=specification_example |
| undefined, with established zero normalizer | completed; valid/undefined/complete; no posterior |
| specified_partial with retained unresolved regions | partial; valid/unresolved/partial, even when some local values are defined |
| symbolic without a requested executable evaluator | partial with retained formulas; valid/unresolved/not_computed |
| UNSUPPORTED operation/capability | unsupported; valid/unresolved/not_computed; retain input family |
| failed mathematics, such as an invalid proposed law | rejected; mathematical_status=failed, preserving the native finding; never `infeasible` without proof of an empty family |

For the last row a platform diagnostic names the failed mathematical predicate
and preserves the native result; no probability value is published.
`structural_validity` is copied from the native request validation,
not inferred from the law's failure. A proof of infeasibility is a different
tagged result and maps to `infeasible`. Numeric/service failure has computation
`failed` and math `unresolved`, not mathematical infeasibility. These rules
preserve the failed mathematical verdict without conflating it with an empty
financial model or a service failure.

Native accounting `assessed` with `eligible` means the requested assessment was
specified, not that a journal was committed. Outer disposition is completed,
commit observation not_committed; its native accounting-validity field remains
not_assessed for the synthetic examples. `unresolved`/`outside_scope`/`ineligible`
remain explicit assessment results, with no JournalProposal. Input rejection
maps as above. A replay payload carries the original committed receipt and
additional_commit=false; outer disposition replayed, commit observation
not_committed. A lost acknowledgement of a requested write maps to commit_unknown
with unknown observation until the original identity is reconciled.

Empirical justification and capability values are preserved. Forecast validity,
product readiness and human acceptance cannot be inferred from any mapping.
All platform examples are specification examples; their finite arithmetic is
checked separately, and product_implemented remains false.

## Continuous company family and insufficient summaries

The protected Northstar example has one shared unidentified floating fraction
x∈[0,1]. Historical interest of 5 does not identify it when both loan types
charged 5%. The 2025 scenario changes floating interest, profit, tax, cash and
equity together. I3's statement payload must therefore retain their common x,
not just independent endpoint lists. The source package's closed synthetic
scope, teaching tax model, assumed intraperiod ordering and aggregate event
resolution all travel with the result.

Grouping two instruments with the same currency, rate/reset schedule, maturity,
seniority, collateral/guarantee rights and relevant accounting memory may preserve
a specified linear interest query by adding principals. Grouping fixed and
floating instruments only by their historical interest loses the stress exposure
and fails that query. Even the safe grouping must be reconsidered for a new
default, prepayment or instrument-specific tax question. This is a query-scoped
sufficiency rule, not a general compiler proof of economic equivalence.

The real source-backed conflict requested in E05 is still missing: seven inspected
candidates did not establish one. The fourteen synthetic conflict cases specify
behavior but cannot supply that source evidence. P17 must complete the exact
authority/method and real-source obligations. The initial-profile choice and
interface decisions are proposed answers now, with actual evidence and owning
phase in P16's decision records. Open source/method decisions remain proposal
blockers through P19; they are not closed by writing this integration document.

SPECIFIED INTERACTION CASES (not runtime)
[{"id":"AX01","operation":"accounting.commit@1","arguments_kind":"AccountingCommitArguments/v1","authorization_kind":"native assess_only assessment","expected":{"disposition":"rejected","code":"INVALID_REFERENCE_KIND","lookup":false,"commit":false}},{"id":"AX02","operation":"accounting.commit@1","authorization_kind":"PostingAuthorization/v1","posting_permitted":false,"expected":{"disposition":"rejected","code":"POSTING_NOT_AUTHORIZED","lookup":false,"commit":false}},{"id":"AX03","operation":"accounting.commit@1","declared_basis":"synthetic equal-price FVTPL acquisition","supported_posting_profile":"authored example only","authorization":"eligible; all named bindings/admissions satisfied","journal":[{"account":"asset","debit":"100","credit":"0"},{"account":"expense","debit":"2","credit":"0"},{"account":"cash","debit":"0","credit":"102"}],"expected":{"candidate_balance":"0","commit":"specified only if unchanged absent-key/head recheck succeeds","accounting_authority":"authored synthetic; not actual-entity compliance"},"limit":"Specified schema/transaction conditions; no record compiler/store executed"},{"id":"AX04","native_response":"assessed","native_assessment":"unresolved","native_math":"unresolved","native_computation":"specified_exact","expected":{"disposition":"completed","math":"unresolved","computation":"complete","evidence_mode":"specification_example","journal":null}},{"id":"AX05","regions":[{"native":"completed","mass":"3/5"},{"native":"numerical_failure","mass":"2/5"}],"expected":[{"platform":"completed","mass":"3/5"},{"platform":"unresolved","native_subtype":"numerical_failure","mass":"2/5"}]},{"id":"AX06","regions":[{"native":"unexplored","mass":null,"obligation":"measure of symbolic region unknown"}],"expected":[{"platform":"unresolved","native_subtype":"unexplored","mass":null,"obligation":"measure of symbolic region unknown"}]},{"id":"AX07","operation":"condition_event","same_semantic_condition":true,"already_consumed_observation_lineage":["D"],"submitted_as_new_block":false,"expected":{"normalizer":"1","new_atoms":[],"masses":"unchanged"}},{"id":"AX08","operation":"likelihood_update","submitted_incremental_atom":"D","already_consumed":["D"],"expected":{"code":"DUPLICATE_INFORMATION","new_posterior":null}},{"id":"AX09","old_selection_owner":["family","evidence-v1","time-v1","scenario"],"query_owner":["family","evidence-v2","time-v2","scenario"],"inherited_selection":"superseded","expected":{"code":"SELECTION_SUPERSEDED","old_owner_usable_in_frozen_scope":true,"fallback_to_old_owner":false}},{"id":"AX10","same_correction_inputs":true,"different_optional_descendants":true,"expected":{"same_correction_basis":true,"same_corrected_law":true,"same_invalidation_report":false}},{"id":"AX11","original_head":["s0",0],"current_head":["s1",1],"original_event_and_fingerprint":true,"expected":{"retry_expected_head":["s0",0],"result":"replayed","additional_commit":false}},{"id":"AX12","partial_run_limit":"wall_time","environment_changed":true,"expected":{"require_equal_matched_exact_values":true,"require_equal_explored_domain":false,"retain_both_frontiers":true}}]

Current checks: 171 finite arithmetic/reference checks and 2580 full accounting exchange assertions passed after edits. The new interaction cases are specified expected consequences, not executed store/frontend tests. Registered structural and final preservation hashes will be refreshed after review.
