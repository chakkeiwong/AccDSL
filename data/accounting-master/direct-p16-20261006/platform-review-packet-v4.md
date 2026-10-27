READ-ONLY, TOOL-FREE SUBSTANTIVE REVIEW. Review ONLY the actual self-contained specification and samples below. Do not fetch or request more files, do not execute, and do not launch agents. Missing exhaustive fixture coverage limits acceptance scope; it is not a reason to withhold concrete semantic review of supplied contracts. Earlier tool-reading reviews ended on turn limits without conclusions. Return a verdict in this single response.

Question: Is the supplied P16 architecture design coherent enough to govern later detailed methods, within its stated scope? Identify concrete semantic errors, unsupported claims or missing behavior preventing that. Distinguish P16 architecture defects from P17 accounting/sector/source methods, P18 manuscript and P19 readiness. Product runtime implementation is disabled. Counts (797 structural, 169 arithmetic, 2580 accounting assertions) show only finite document checks. 932 protected files are unchanged. Human/domain/forecast acceptance is not established.

Give at most six material findings with file/section, counterexample, repair and blocker status. State what you checked and what the evidence cannot establish. End VERDICT: AGREE or VERDICT: REVISE. Be concise but substantive.

Scope: portable records, persistence, typed interfaces, failures and company scope; preserve native accounting semantics.

FILE docs/design/proposal/architecture/language-ir-contract-v1.md
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

FILE docs/design/proposal/architecture/persistence-contract-v1.md
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
environment. Exact rational operations require exact equality. Approximate
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

FILE docs/design/proposal/architecture/interfaces-contract-v1.md
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
request fingerprint covers the exact portable request; accounting's historical
fingerprint is retained by an explicit legacy adapter, not recomputed as this one.

`OperationResult` has exactly `submission_ref`, `request_ref`, `operation`, `input_view_ref`,
`disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
`continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
References are typed. `submission_ref` identifies the preserved exact submitted
bytes and transport/decoder metadata; it always exists, even when decoding fails.
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
| `accounting.propose@1` | eligible assessment, exact request/opening, posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
| `accounting.commit@1` | validated commit request, eligible assessment, proposal/delta and expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; separate signature from assess-only |
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

FILE docs/design/proposal/architecture/failure-contract-v1.md
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

FILE docs/design/proposal/architecture/initial-profile-v1.md
# Proposed first implementation profile

The first implementation should connect a company's disclosures, alternative
histories, economic events and complete statements. A financing-only example
would leave the working-capital, operating-asset, tax and reporting interfaces
untested. The proposed domain is therefore a bounded corporate company; the
initial authoring interface is typed constructors into the portable IR, with a
matched, bounded textual notation. These are separate choices. This proposal
addresses MC01–MC35 without asserting that every requested method is now supplied.

## Scope and the alternatives compared

P15 compared four candidates. Corporate/shared-IR and typed-library-first can
have exactly the same domain and differ only in authoring. Instrument-first
would make financing lifecycle work earlier, but cannot meet the whole-company
goal until the operating-company continuation is added. Broad sector-first
would require bank, insurance, group and cross-standard methods at entry, with
more currently unresolved authority. The chosen order exposes interactions in
one connected company while specifying extension requirements now. It does not
establish that this order is cheapest, fastest or easiest to use.

The profile is `CorporateJointHistory/1`. It includes one legal entity and book
per branch, a declared domestic functional currency, annual/interim evidence,
multiple source vintages and reviewed alternatives. Context and schema design
retain multiple-entity/perimeter/currency fields so an unsupported operation
is explicit. “One book” is an execution scope, not a global uniqueness rule for
companies or future groups. A company with subsidiaries, leases or contingencies
cannot be admitted as a closed single-company model merely by omitting them.

Evidence preparation must account for the declared statement and note inventory,
incorporated references and unresolved source units. Readings, interpretations,+assumptions and treatment eligibility are separate layers. Investor-information,
system-as-of and exploratory archival questions use the time contract's distinct
admission rules. Exact financial quantities, source precision and conditional
rounding assumptions remain distinct. Source limitations accompany each dependent
query; there is no global “complete” flag inferred from pages parsed.

The initial economic methods must connect sales/delivery/collection, purchases/
inventory/cost of sales/payables, payroll, tangible-asset additions/depreciation,
simple debt/equity/dividends and a declared simple tax model. They produce profit,
balance sheet, cash flows and changes in equity from the same event histories.
The simple tax model is an authored teaching assumption; actual tax requires
P17's jurisdictional method. Northstar supplies a closed synthetic example,
not proof that these methods cover Apple or a representative real issuer.

The initial reconstruction method is the history contract's admitted-template,
rational affine family with finite choices and bounded integers. It preserves
unidentified debt mix, unknown payment timing and other query-relevant state.
The declared half-year event slots do not recover invoices or prove daily
liquidity. Querying a finer horizon requires refinement or an unresolved answer.
Exact bounds require whole-domain reasoning and endpoint attainability; search
witnesses and explored extrema are not promoted to complete families or bounds.

Scenario execution initially supports imposed exogenous paths with explicit
behavior and information restrictions. Joint finite rational probability is an
optional extension under the admitted-measure contract. Unweighted alternatives
remain valid initial results. Continuous inference, causal interventions,
calibration and empirically validated forecasts require P17 methods and later
execution evidence. An imposed interest-rate stress does not reweight historical
contract alternatives or become a probability forecast.

Typed constructors must express all included records without embedding opaque
Python functions. The bounded text frontend initially covers the matched debt
and constraint fragment; unsupported declarations produce located diagnostics.
Textual whole-company authoring is a later frontend obligation, with the same
domain semantics and validation. Deferring that parser does not defer the
whole-company typed model, the DSL design or the portable representation.

## Acceptance examples and limits

The primary integrated example is the protected Northstar disclosure fixture
and chapter, interpreted through the new contracts. Its opening and half-year
events support independently calculable statements and a continuous debt family.
For the 2025 stress, let x be the floating fraction. The common joint result is:

| Quantity | Conditional value in currency units |
| --- | --- |
| Debt interest | 5 + 2x |
| Profit before tax | 82 − 2x |
| Tax at the stipulated 20% rate | 16.4 − 0.4x |
| Profit | 65.6 − 1.6x |
| Operating cash flow | 48.6 − 1.6x |
| Closing cash | 95.2 − 1.6x |
| Closing equity | 148.2 − 1.6x |
| Closing assets | 288.2 − 1.6x |

Here 0 ≤ x ≤ 1, payables plus debt are 140, receivables 55, inventory 40 and
net plant 98. Every row uses the same x. The endpoints are not equiprobable
scenarios, and the output is not a rectangular box of independently selectable
amounts. Changing the floating rate to 9% changes the interest slope to 4 and
the cash/profit/equity slopes to −3.2; independent arithmetic must detect that
change even if both frontends share an erroneous constant.

Acceptance of the specification requires exact expected exchanges for the
following connected cases, with preserved sources and explicit assumptions:

1. Annual/interim source inventory, missing incorporated reference, alternative
   narrative translation, rounding unknowns and separately admitted constraints.
2. Joint working-capital reconstruction and unidentified fixed/floating debt
   mix, with known aggregate movements and unknown intraperiod timing.
3. Conditional 2025 events, eligible treatments, balanced proposals, reconciled
   complete statements and debt-mix dependence, plus a changed-rate control.
4. Original versus corrected interim information views without later-information
   leakage; no automatic source-derived accounting permission.
5. Partial or unsupported region preservation, unavailable methods, exact versus
   approximate capabilities and unweighted versus admitted-measure queries.
6. Valid replay, changed-payload conflict, concurrent stale-head rejection,
   unknown commit recovery, review correction/invalidation and failed migration.

The shared platform examples exercise these connections alongside retained
evidence/time/history/uncertainty/accounting examples. A bounded real filing
case must retain its full declared inventory and all unformalized disclosures;
Apple's partial source preparation cannot satisfy that case by itself. E05's
real source-backed conflict and P17's dated accounting methods remain proposal
work. A document calculation satisfies only the finite arithmetic part of this
list. Runtime acceptance additionally needs implemented source/typed lowering,
solver/simulator, transaction fault tests and adapter checks. Human understanding
and accounting/forecast validity have separate evidence.

## Dependencies and retained later work

Implementation should proceed in dependency order, after the proposal has been
completed and the user has authorized implementation:

1. Versioned record definitions, exact values/context, source byte retention,
   dependency closure and pinned package/schema loading.
2. Review and time selection, provenance/invalidation, immutable views and the
   initial transaction store's receipt/replay behavior.
3. Typed constructors and validation; the matched debt text fragment and source
   maps; independent expected IR and adverse input cases.
4. Admitted history templates, joint affine constraints, finite-choice search,
   partial checkpoints, typed capability failures and query-dependent refinement.
5. The connected corporate economic and accounting methods with their actual
   authority, event scheduling and information boundaries; statement mapping.
6. The integrated company case, source corrections, replay/recovery and bounded
   real-filing coverage; then optional justified measure operations and adapters.

P17 must complete actual source-grounded methods for corporate operations,
bonds/equity, groups/FX, IFRS/US GAAP/ASBE, banks and insurers. The extension
records in I4 make dependencies visible; they do not count as method completion.
Examples must include a changed group perimeter, intercompany elimination and
FX translation, credit loss and credit-risk memory, and insurance service/
measurement memory. Imported official rules and software interfaces require
located inspected sources and explicit limits. General nonlinear inference,
calibrated forecasting, multiwriter throughput and distributed durability are
later implementation/evaluation obligations, not inferred from prototype tests.

P18 integrates the completed methods and contracts into the governing LaTeX
manuscript and inspects its actual rendering. P19 assesses the full proposal
against MC01–MC35 and G1–G18. The current architecture may be judged specified
within its scope while those later proposal blockers remain open. Neither that
judgment nor a successful PDF build authorizes product implementation.

FILE docs/design/proposal/architecture/architecture-integration-v1.md
# Integration of the nine proposed contracts

The active contract list in P16 architecture.json is the document index. This
supplement resolves interactions among those contracts without altering earlier
evidence or treating saved fixture outcomes as executed product behavior. It
addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
prototypes, not automatic defaults.

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

FILE docs/design/proposal/architecture/accounting-complete-exchanges-v1.md
# Accounting exchange and context reconciliation

The field controls for C09/C10 distinguish missing, malformed, unknown and
not-applicable values. This supplement carries those controls through complete
requests, dependency closure, assessments and publication. It also supplies the
remaining source/context predicates and an independently derived disposition for
V01–V16. It addresses MC08, MC13, MC25, MC27, MC34 and MC35, with G4/G18.
No accounting engine or product endpoint is implemented.

## Comparator, evidence and audit

The comparators are the seventeen corrected integration-v2 exchanges, the
accepted C03/C05/C07 supplements, the saved 260 C09/C10 field controls and
the sixteen V-series input/output mutations. Source claims and method flags
remain synthetic assumptions. The check must derive findings from supplied
fields, verify newly pinned source packets and all transitive record references,
then compare authored expected results. Matching a copied outcome alone would
not test the defect. Earlier evidence remains unchanged.

The skeptical audit passes for this finite specification task. Reject stale
pins, unintended changed facts, incorrect reference closure, disagreement between
price and route requirement, guessed Boolean controllers, premature receipt
lookup or publication of defective output. Fixable failures trigger correction
of this draft. Source-authority gaps remain P17 work; no deterministic check
promotes stipulated facts into inspected entity facts. No backend, solver,
timing or statistical comparison is attempted.

## Binding and semantic predicates

Use the native sequence parse, recognizable dependencies, shape, source_versions,
bindings, lookup, freshness, assessment, output validation. A shape-valid but
internally inconsistent source packet is a binding failure, not a legitimate
economic alternative. Unknown economic content must use the named unknown
representation. The existing 299-path field matrix governs types/presence; the
later reason and C03/C05/C07/C09/C10 amendments prevail for their exact fields.

| Conditions | Required consistency and remaining meaning |
| --- | --- |
| C01 | Annual start equals request context; `within_retained_window` equals `2023-01-01 <= annual_start < 2026-07-01` for the pinned Compilation 5. False consistently represented is outside_scope; a contradictory flag is SOURCE_CONTEXT_MISMATCH. The edition, reporting basis and actual entity applicability still need source-supported assessment. |
| C02 | Holder/instrument/exception facts remain independently admitted. A synthetic scope-exceptions string is a stated assumption, never executable proof that exceptions are absent. Unsupported feature gives outside_scope; missing required real-world assessment gives unresolved. |
| C03/C04 | Preserve the accepted C03 date/party rules. Recognition date equals the event's economic date; trade/settlement and valuation dates must be valid dates. Conditional policy eligibility does not override nonparticipation. No universal equality of contractual and recognition dates is imposed. Regular-way/policy eligibility is a distinct admitted method judgment. |
| C05 | Category agrees with the event category. Classification rationale and designation/OCI choices remain the accepted explicit conditional rules; descriptive cash-flow prose is not a completed SPPI analysis. |
| C06/C07 | Exact decimal price/fair value/fee equal the event values; valuation date equals the event's date for this immediate-acquisition profile. A different valuation date needs a named bridging method/new profile. C07 incrementality and purpose obey the saved predicates; contextual reason text never changes them. |
| C08 | Source entity/book/branch labels match the declared synthetic aliases; aliases match request identity and pinned context/branch. Currency/unit/scale equal context. Cash settlement and no separate FX/tax/other-asset treatment are profile assumptions, not universal accounting rules. |
| C09 | With valid exact source amounts, required is exactly `price != fair_value`. Under equal price the retained profile has two null, not-applicable routes and branch not_applicable. Under unequal price either true route gives branch a, both false give b, and all other valid pairs give unknown. Both route values and both reasons survive even when one true route suffices. A stored branch inconsistent with those values is SOURCE_CONTEXT_MISMATCH. |
| C10 | Method availability comes from the pinned method/profile, not a supplied true flag or reason. This retained profile has neither unequal-price posting method. A true availability flag contradicts its pinned capability and fails METHOD_CAPABILITY_MISMATCH. A different supported package requires a new method/profile Ref and full reassessment. C10 contextual reason remains nullable; unknown C09 does not itself require C10 text. |

The single KnownBool `observable_valuation` in the request's evidence record is
only the derived qualifying OR of C09. Under required=false it is unknown/not
required; with a true route it is known true; with two false routes known false;
otherwise unknown. The source's two route values are never reconstructed from
this lossy projection. A contradictory convenience field fails
SOURCE_CONTEXT_MISMATCH. Assessment preconditions retain their coarse historical
projection, while findings and valuation_routes retain the precise results.

These rules distinguish a malformed controller from an internally inconsistent
but typed packet, and both from a legitimate unresolved treatment. C01/C02/C04/
C05 actual authority, economic facts and permitted methods remain admissibility
requirements. A real input cannot acquire `synthetic_only` admission by copying
an example label. The interfaces require an explicit mapping and reviewed
applicability decision in its own scope.

## Complete exchanges and output discipline

The companion fixture imports the exact native record registries. Every changed
source packet is stored separately with its comparator and change explanation;
the changed eligibility source/ConditionRefs, request, submission, assessment and
response are rehashed. Each exchange resolves the complete record closure.
File hashes are file references, never mistaken for record digests. Imported
records retain their original digest domains.

Valid contextual-reason changes preserve all economic facts, treatment findings,
method flags and evidence statuses of their comparator. Invalid shape/context
changes return no validated request, assessment, diagnostic journal/delta,
receipt or observed-state publication reference. Lookup, freshness and assessment
are false. Every exchange has additional_commit=false and identical before/after
values for identity index, committed journals, selected state and committed
receipts. Valid assess-only exchanges can look up and assess without posting.

The sixteen retained V cases are active adverse examples, not completed runtime
tests. V01–V04 and V08/V09 fail shape; V05–V07 fail bindings; V10 fails dependency
kind. V11–V16 retain a validated request but reject a defective produced
assessment/response as ASSESSMENT_OUTPUT_INVALID. Derive these outcomes from the
candidate operation/profile/version/aliases/conditions/bindings and published
assessment content. Output checking requires one ordered finding per C01–C10,
summary consistency, correct route projection and diagnostic-example scope,
posting_permitted=false for assess-only, and no additional commit. The rejection
does not imply that the company's acquisition is ineligible.

The finite diagnostic establishes these specified distinctions and preservation
properties. It does not implement arbitrary request validation, prove the truth
of the underlying source statements, establish standards compliance or accept
P16. Integrated independent review must assess its scope with the other eight
contracts and the initial profile.

FILE docs/design/proposal/architecture/accounting-replay-contract-v1.md
# Accounting replay and event identity — proposed supplement v1

This supplement repairs the replay semantics in accounting-contract-v1.md,
sections 2–4. It supersedes AC04 and AC05 as reproducible retry/staleness
examples, and clarifies invariant 5: event version belongs to the fingerprint,
not the stable lookup key. AC01–AC03 and all predecessor files remain historical
source-scoped evidence. This slice addresses MC13, MC25 and MC34 with MC08
branch preservation and G4/G18 interactions. It specifies behavior, not software.

## Question, evidence and stopping rule

Can the same recorded acquisition be retried after later transactions without
posting twice, while changed requests conflict and genuinely new stale requests
are rejected? Compare identity lookup before freshness with freshness before
identity lookup, using the identical request and committed state. The primary
criterion is the derived response and absence/presence of a further domain
transition in each specified case, including branch isolation. Wrong source
hashes, inconsistent dependencies or non-reconciling arithmetic invalidate the
fixture calculation. Journal balance is an explanatory arithmetic check, not
proof of eligibility. No statistical ranking, runtime durability, accounting
validity or complete IR selection follows. Preserve the result in
accounting-replay-verification-v1.json and stop after this bounded slice.

Skeptical audit: these are matched deterministic cases, not a comparison of
prototype test counts. Failure of the whole P16 checker is expected while four
contracts and the initial profile are unfinished. It does not invalidate a
correctly scoped retry example. Conversely, passing these examples cannot
complete the accounting contract. Remaining input/receipt, eligibility, atomic
failure and architectural-alternative obligations require a subsequent task.

## Identity and record encoding

The stable event key is the tuple (entity_id, book_id, branch_id,
business_event_id). Book identifiers are scoped by entity; branch identifiers
are scoped by book. Branch IDs reference explicit branch records and their
common family. The same event label in a different branch is a distinct posting
identity; it neither inherits a receipt nor grants economic admissibility.
A version change under the same key conflicts. An intentional correction needs
a new business-event ID linked to the superseded event and a separately
specified correction method; a version bump alone never authorizes a second
posting. Correction workflows are outside this slice.

The request fingerprint covers the complete request record: stable key, event
version and payload, expected opening-state digest, context, time/cutoff,
branch record, and authority/method/evidence/assumption record digests. Mutable
transport metadata (arrival time, tracing token) is outside this request. Every
transitive record is immutable and checked against its digest. Thus equal
fingerprints mean equal retained request bytes under this encoding, assuming
SHA256 collision resistance; they do not assert economic equivalence.

For these finite fixtures only, serialize JSON with sorted keys, compact
separators, ensure_ascii=True and allow_nan=False, encoded as ASCII. Objects
have unique string keys; arrays preserve order; numeric amounts are decimal
strings with exactly two fractional digits; versions are nonnegative integers.
Floats, NaN, duplicate keys and non-ASCII text are excluded from this fixture
profile. UTF-8 interoperability, arbitrary dimensions, migrations and a general
language encoding remain open. The digest is SHA256 of the ASCII domain,
a NUL byte and serialized bytes. Domains are accdsl.replay.v1/key,
accdsl.replay.v1/request and accdsl.replay.v1/<record kind>. A receipt references
request, assessment, journal, delta and opening/closing records without a cycle.
The registry stores kind, full content and digest, not symbolic digest labels.

These are proposed convenience choices. SHA256 follows existing immutable
source references; exact two-decimal amounts follow the synthetic A01 example;
branch IDs and monotonically numbered states expose isolation and stale inputs.
Their failure modes are omitted request fields, accidental aliases, precision
loss and mistaken cross-branch reuse. The bounded calculation checks all
request dependencies, changes payload and branch separately, uses Decimal and
checks distinct opening/closing digests. These checks do not promote the
choices to a general persistence or IR default.

## Order, receipts and concurrency obligations

1. Check structure, resolve all pinned records and validate internal context:
   entity/book/branch, currency/unit/basis, event time and source cutoff. An
   exact retry uses its retained historical context, not today's method or
   cutoff. Missing/corrupt dependencies are an invalid request, not a replay.
2. Under that branch/book identity, look up the stable key in committed receipts.
   If found, compare the complete request fingerprint. An equal fingerprint
   returns the original immutable receipt; a different fingerprint returns
   EVENT_ID_CONFLICT before any freshness check. Neither creates a new domain
   transition. Changed payload cannot evade conflict by changing its version.
3. Only for an absent key, compare the expected opening digest with the current
   state of that branch. Mismatch returns STALE_OPENING_STATE without a posting.
4. For a fresh new event, assess eligibility and construct/check the journal
   and independent delta. Only then may one atomic operation insert identity,
   journal, closing state and committed receipt. Recheck absence of the key and
   opening state atomically to prevent a concurrent writer racing these checks.
   Persistence must later specify isolation, crash recovery and audit storage.

The immutable receipt always retains status=committed and commit=true for the
original transaction. A retry response has status=replayed,
additional_commit=false and the same receipt digest; it must never rewrite
that receipt as replayed or return a newer closing state as its original result.
Its response separately identifies the current observed state. A conflict may
identify the existing receipt for diagnosis, without claiming it belongs to the
submitted fingerprint. A stale or conflicting response preserves the submitted
request and known facts; journal and delta are null, additional domain writes
are zero and before/after state and committed-receipt index are identical.
Optional audit logging is separate from domain writes and is not required or
modeled by these fixtures. Replay retrieval is not a fresh eligibility verdict.

Freshness-first on the specified retry sees the original opening state differ
from the now-current state and incorrectly reports STALE_OPENING_STATE. Both
orders reject the genuinely new stale request. Stable-key-only replay without
a fingerprint would incorrectly accept a changed payload. Including payload
or version in the lookup key would instead hide the conflict. These comparisons
justify the proposed order under the stated retry contract; they establish no
speed or storage advantage.

## Concrete inputs and consequences

The fixture registry includes complete branch-scoped opening balances, pinned
context and request dependencies. A01 has price=fair value=100.00 and fee=2.00.
Eligibility is explicitly stipulated under the retained S9 5.1.1 source scope;
this task does not re-establish classification or jurisdiction applicability.
Cash starts at 1000.00, asset and expense at zero, and equity at -1000.00 in
debit-positive notation. The event directly implies cash -102.00, asset +100.00,
expense +2.00, equity zero change. Separately, debit asset 100.00, debit expense
2.00 and credit cash 102.00 aggregate to the same delta. Closing cash is 898.00.
A second separately identified acquisition advances this branch to cash 796.00,
asset 200.00 and expense 4.00; its full request and receipt are retained as setup.

AR01 commits the control. AR02 retries AR01 after the second acquisition and
returns AR01's original receipt without changing either receipt or current
state. AR03 changes the fee to 3.00 under the same key and conflicts, preserving
that submitted fact without posting it. AR04 uses a new event ID with the old
opening digest and is stale. AR05 uses the original event label in another
explicit branch with its own opening state: it commits there while branch A
and both of its receipts remain unchanged. Branch B is a synthetic stipulated
alternative, not a newly inferred economically admissible history.

The calculation independently derives A01 deltas from event amounts and from
journal lines, checks complete receipt references and every source binding,
and derives outcomes before comparing authored expectations. It is an offline
finite document calculation, not a reusable runtime evaluator or product test
suite. Full lifecycle eligibility, general record typing, atomic failure modes,
interfaces, language/IR, persistence and initial-profile selection remain open.

FILE docs/design/proposal/architecture/accounting-integration-contract-v1.md
# Acquisition request and assessment integration — proposal v1

This supplement binds the independently reviewed acquisition dossier and decision
supplement to immutable request and assessment records. It addresses MC08, MC13,
MC25, MC34 and MC35, with G4/G18 interactions. It is a proposed specification,
not a runtime API. The terminal bounded AGREE in
`data/accounting-master/runs/20261005T150545-71a70996/P16/execution-0/review_result-0.response.json`
accepts those source examples only. This integration requires its own review.

## Question and evidence boundary

Can a recipient recover every reviewed condition, individual unknown and combined
adverse finding from the request and assessment, with reproducible identity?
The comparator is the existing records-plus-bindings specification on the same
synthetic facts, before it binds the ten conditions. Primary acceptance requires
complete C01–C10 references, matched results for E01–E17, all nine valuation pairs,
correct context and version bindings, and unchanged committed state. Lost findings,
unknown-to-false coercion, changed predecessor files, cross-version receipt aliases
or a diagnostic assessment granting posting permission veto acceptance. Hashes
and balance are explanatory checks, not accounting validation. There is no
scientific ranking, historical evidence admission or runtime claim.

The skeptical audit found a material date difference: the records illustrate
January acquisitions, while the eligibility facts use June. The new examples
therefore create new time/event/admission records, with June economic dates and
matching reporting intervals. They do not attach June facts to January requests.
C01 period-start variations E04/E16/E17 change the new context's annual-period
start; the event's reporting interval remains the explicitly stipulated 2024
interval. Those adverse examples already lie outside this authority profile;
no calendar-valid historical book is asserted. This is not a migration of a
committed transaction. Source labels such as “synthetic purchaser” are explicitly
mapped to opaque entity/book/branch identifiers; no real-company identity is inferred.

Stop after this contract, fixtures, finite calculation, integrity record, P16
checkpoint and one registered check. Language/IR is the next separately scoped
contract after review. Lifecycle methods and profile selection remain separate.

## Versioned input contract

Use the predecessor ASCII canonical JSON encoding: sorted keys, compact
separators, ensure_ascii=True, allow_nan=False. Each new record has a SHA256 of
`accdsl.accounting.integration.v1/<kind>` + NUL + canonical content. Imported
records retain their original domain and bytes. The stable identity key retains
`accdsl.replay.v1/key`; a request fingerprint always includes its schema version,
operation and complete precondition references. Identical economic amounts do
not establish cross-version request equivalence. No old receipt may be relabelled.

The request preserves every v1 request field: identity, event, opening, context,
branch, time, chart, authority, method, evidence, admissions, assumptions and
lineage. Its schema_version is 2. It adds exactly `operation="assess_only"` and
`eligibility: Ref<eligibility_input>`. The operation cannot commit. A future
posting operation requires a separately reviewed extension and new fingerprints.
This explicitly limits the new examples without changing the retained R01–R06
posting, rejection, abort or acknowledgement-loss examples.

An eligibility_input has exactly schema_version=1, profile="acquisition-conditions-v1",
dossier and decision_rules FileRefs, source_case CaseRef, bindings, aliases and
conditions. CaseRef is `{file:{path,sha256},case_id}`; a ConditionRef is
`{case:CaseRef,condition_id,value_version}`. It resolves precisely the complete
input at cases[id=case_id].complete_inputs[condition_id], including value,
unknown_reason, provenance, scope and version. It never resolves an expected
assessment. All ten condition IDs are required once, in C01–C10 order. Pin both
the file bytes and value_version; a new version changes the request. The evidence
owner publishes new records rather than editing inputs in place.

Bindings contains the exact request references for context, branch, time, chart,
authority, method, assumptions, evidence and admissions. Every equality must hold;
context/branch versions are compared by complete reference, not names alone.
The existing five bindings remain mandatory: event.branch=request.branch,
opening.branch=request.branch, event.time=request.time,
opening.chart=request.chart and method.authority=request.authority. All existing
context, identity, account membership and admission/evidence/time checks remain.
Aliases maps the source C08 entity/book/branch labels to the request's identity
IDs and to the pinned context and branch references. It is a synthetic mapping
assertion with scope `synthetic_only`, not historical entity resolution.

C01 annual-period start must equal context.annual_period_start. C04 recognition
date must equal event.time.economic_date. C06 price/fair value and C07 fee must
equal event amounts exactly after decimal-string normalization. C08 units,
currency and scale must equal context. The old single observable_valuation
KnownBool is a derived convenience for the qualifying OR, never the evidence
source for the two routes; equal-price examples use explicit unknown/not-required.
The authoritative Q/O values remain individually accessible through C09.
Null route values mean unknown only where the reviewed condition specifies it;
C09.required=false means not applicable. Missing fields are malformed, never
unknown or zero. All v1 lexical/type rules remain, with these explicit additions.

## Output and non-lossy assessment

The assessment retains request, status, reason_codes, preconditions, authority
and method. It adds schema_version=2, eligibility, findings, valuation_branch,
valuation_routes, method_applicability, source_assessment, evidence_level,
posting_permitted=false and diagnostic_example. Preconditions retains the v1
{name,status,support} shape: satisfied_conditionally/not_applicable maps to
satisfied; unresolved to unknown; ineligible/outside_scope to failed. This coarse
projection is for compatibility only. The exact finding, its reason and all
child route findings remain in findings; valuation_routes additionally exposes
both raw values and unknown/qualifies/does_not_qualify/not_applicable statuses.
No consumer may use the coarse projection to discard an outside-scope reason.

source_assessment pins the reviewed example as comparative provenance; the
calculation derives statuses from input facts and compares them with it. It is
not an input to eligibility inference. Summary precedence remains ineligible,
outside_scope, unresolved, eligible. Evaluate all ten conditions before selecting
a summary; retain every adverse reason in condition order. This precedence is a
reporting convention, not an accounting rule. method_applicability is conditional
for the equal-price example, unavailable for known unequal-price branches, and
unresolved for an unknown branch. It does not override recognition failures.
The conditional eligible control remains synthetic and grants no posting right.

The response retains submission, request, assessment, diagnostic_journal,
diagnostic_delta, receipt, observed_state, commit_status, additional_commit,
statuses and metadata. The new successful assessment response has status=assessed,
commit_status=not_committed, additional_commit=false and all journal/delta/receipt/
observed_state references null. diagnostic_example is a CaseRef only for E01's
existing explanatory arithmetic; it is not a journal reference. No assessment
constructs a journal, state delta or receipt. Accounting validity remains
not_assessed, empirical justification not_established, capability specified_only_no_runtime,
and human acceptance pending. The four committed domains are exactly the
identity index, committed journals, selected state and committed receipts.

## Failure and replay order

First retain submission bytes; validate JSON, types, digests, all references,
versions and bindings before identity lookup. Duplicate keys, extra fields,
missing condition IDs, an unavailable pinned file or a value-version mismatch
are structural rejections. Canonical-byte/digest disagreement is corruption,
not a new assessment. Structural rejection returns request=null and
assessment=null, all candidate/receipt/state references null and a precise code;
no canonical request is admitted. Preserve the exact submitted bytes and failed
references in diagnostics. Never repair a version mismatch silently.

After validation, lookup precedes freshness. A same-key different fingerprint
is an identity conflict, even if its amounts or condition summaries match. A
matching committed request returns its original receipt without a fresh
assessment; a diagnostic assessment is never placed in the commit index.
A genuinely absent key checks freshness before assessing. Stale opening state
returns a rejection without assessment or writes. Unknown facts produce valid
unresolved findings; disproved recognition produces ineligible; an authority
outside the retained window produces outside_scope. These are semantic outcomes,
not malformed requests. Combined findings survive summary precedence.

Repeated assess_only submission has the same request and deterministic assessment
digests but no receipt. Its outcome is assessed again, not replayed committed.
The fixtures also reference exact R06 matching-receipt replay, preserving its
original fingerprint and receipt, and demonstrate that a v2 fingerprint cannot
retrieve that v1 receipt. R01–R06 are all retained by immutable CaseRefs; no
v2 committed receipt is invented merely to furnish a positive replay example.
An in-flight posting lookup remains unknown until authoritative finality; this
read-only operation is definitively not_committed because it cannot publish.
Rejection or assessment leaves all four domains byte-for-byte unchanged.

## Alternatives, defaults and remaining decisions

Embedding mutable condition prose in request identity fails reproducibility.
Embedding complete immutable condition values can satisfy the same contract, but
would duplicate the reviewed packets; typed references are chosen here because
they preserve one inspectable source and explicit versions. A reference-only
design must retain resolvable bytes: a missing source is a veto, not permission
to use the latest file. The old category/one-Boolean input cannot represent both
valuation routes or ten separate obligations. A richer upstream classification
could satisfy this contract if it preserves the same facts and authority.
No storage or execution architecture is selected by these examples.

| Choice / provenance | Status and reason | Failure / early diagnostic |
| --- | --- | --- |
| Existing v1 field shapes and B1–B5 | Reviewed bounded baseline | Schema drift; compare retained keys and binding equalities |
| New domain and request version | Proposed convention to prevent aliases | Reused receipt; compare v1/v2 digests with the same identity |
| Ten typed condition references | Proposed representation of accepted dossier | Stale/missing source or lost unknown; resolve every field and pinned version |
| CU two-decimal amounts, synthetic mapping | Convenience from existing examples | False real-world precision/identity claim; exact Decimal and explicit aliases |
| Summary precedence | Accepted bounded reporting convention | Lost lower-priority finding; E15–E17 retain every finding |
| assess_only boundary | Conservative proposal scope | Eligibility mistaken for permission; all four domains and receipt stay unchanged |

The retained authority is AASB 9 Compilation 5, not a general current IFRS,
US GAAP or ASBE determination. The reviewed dossier supplies paragraph anchors
and limits; this integration adds no authority claim. Actual classification,
historical admission, lifecycle methods and wider company/sector support remain
open. The full MC01–MC35/G1–G18 mission survives this bounded representation.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit integration for independent review | Finite report records preservation and linkage checks | Any failed binding or changed predecessor blocks slice acceptance | Generalized schemas and actual facts remain unvalidated | Inspect new contract and fixtures | Runtime or accounting validity |
| Keep P16 partial | Four architecture groups/profile/decisions remain open | Whole-architecture structural failure remains expected | Language, persistence, interfaces, failure semantics | Scope language/IR after review | Product readiness or human acceptance |

Post-run red team: hashes can preserve a wrong assertion perfectly. The strongest
alternative explanation is a deficient synthetic classification or context
mapping. A contradictory contract, source paragraph or binding would overturn
the affected assessment. Independent input-derived checks address representation
consistency only; they cannot validate the source facts or a production engine.

ACTUAL ACCOUNTING EXCHANGE PROJECTIONS:
{"id":"X007","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"expected_diagnostics":[],"lookup":true,"freshness":true,"assess":true,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"source_values":{"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"inner: valuation input unresolved","branch":"unknown"},"unknown_reason":"outer: route evidence absent","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"response":{"submission":"f6c80db388b4bbf5dae424ee449e2b31f706f0c8135578a0f9d294c7ede03059","request":"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1","status":"assessed","reason_codes":["C09:unresolved","C10:unresolved"],"assessment":"3e71df06c1f530037f53937018977b28a27ba1f04bde42f2f8b5025cfc224035","diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"valid","mathematical_status":"unresolved","computation_status":"specified_exact","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"assessment":{"schema_version":2,"request":"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1","status":"unresolved","reason_codes":["C09:unresolved","C10:unresolved"],"preconditions":[{"name":"C01","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C02","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C03","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C04","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C05","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C06","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C07","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C08","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C09","status":"unknown","support":"unequal price; valuation routes unknown"},{"name":"C10","status":"unknown","support":"branch evidence missing; method decision pending"}],"authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","eligibility":"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c","findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"unresolved","reason":"unequal price; valuation routes unknown"},{"condition":"C10","status":"unresolved","reason":"branch evidence missing; method decision pending"}],"valuation_branch":"unknown","valuation_routes":[{"field":"identical_instrument_active_market_quote","value":null,"status":"unknown"},{"field":"technique_only_observable_market_data","value":null,"status":"unknown"}],"method_applicability":"unresolved","source_assessment":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"evidence_level":"conditional_synthetic_only","posting_permitted":false,"diagnostic_example":null}}
{"id":"X008","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"expected_diagnostics":[{"stage":"shape","path":"source/C09/unknown_reason","code":"INVALID_UNKNOWN_REPRESENTATION"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"source_values":{"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"response":{"submission":"2890f182341d858eb68c26d8ff06c876e99279a852b21039a1dcc225cf2dc3fb","request":null,"status":"rejected","reason_codes":["INVALID_UNKNOWN_REPRESENTATION"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}}}
{"id":"K01","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"expected_diagnostics":[{"stage":"bindings","path":"source/C09/value/required","code":"SOURCE_CONTEXT_MISMATCH"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"source_values":{"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":false,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":"neither route assessed","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"response":{"submission":"c1c98853cc8192823fe353068c70d760328faa4834c0404e02c4065148c08719","request":null,"status":"rejected","reason_codes":["SOURCE_CONTEXT_MISMATCH"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}}}
{"id":"K04","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"expected_diagnostics":[{"stage":"bindings","path":"source/C10/value/unequal_price_a_method_available","code":"METHOD_CAPABILITY_MISMATCH"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"source_values":{"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":"neither route assessed","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":true,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"response":{"submission":"c21fc6ae5892c5cb088cc6eb290bf7821a4b4841e8fa847d62e5682f97787810","request":null,"status":"rejected","reason_codes":["METHOD_CAPABILITY_MISMATCH"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}}}

ACTUAL NORTHSTAR FINANCIAL INPUTS AND EXPECTATIONS:
{"schema":"accdsl-design-fixture/1","entity":"Northstar Components (synthetic)","currency":"USD","units":"one currency unit","basis":"DemoCorporate/1; not GAAP certification","disclosure_scope":"Closed synthetic goods company; the listed source package is complete by construction","assumptions":{"historical_resolution":"half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices","inventory":"one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5","sales":"delivery transfers control; no returns, services, variable consideration or foreign currency","tax":"20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax","plant":"opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals","debt":"100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast","time":"half-year accrual fractions 1/2, annual 1; explicit teaching convention","closing":"temporary accounts closed after each H1/H2; annual income uses movements excluding closing","universe":"no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package"},"accounts":{"cash":"asset","receivables":"asset","inventory":"asset","plant_cost":"asset","accum_depreciation":"contra_asset","tax_prepaid":"asset","payables":"liability","debt":"liability","capital":"equity","retained":"equity","revenue":"income","cost_of_sales":"expense","payroll":"expense","depreciation":"expense","interest":"expense","tax":"expense"},"opening":{"cash":"60","receivables":"20","inventory":"30","plant_cost":"100","accum_depreciation":"-20","tax_prepaid":"0","payables":"-20","debt":"-100","capital":"-50","retained":"-20"},"historical_events":[{"id":"2024H1.sale","date":"2024-06-30","period":"2024H1","postings":[{"account":"receivables","signed_amount":"110"},{"account":"revenue","signed_amount":"-110"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.collect","date":"2024-06-30","period":"2024H1","postings":[{"account":"cash","signed_amount":"110"},{"account":"receivables","signed_amount":"-110"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.buy","date":"2024-06-30","period":"2024H1","postings":[{"account":"inventory","signed_amount":"70"},{"account":"payables","signed_amount":"-70"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.supplier","date":"2024-06-30","period":"2024H1","postings":[{"account":"payables","signed_amount":"65"},{"account":"cash","signed_amount":"-65"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.deliver","date":"2024-06-30","period":"2024H1","postings":[{"account":"cost_of_sales","signed_amount":"75"},{"account":"inventory","signed_amount":"-75"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.wages","date":"2024-06-30","period":"2024H1","postings":[{"account":"payroll","signed_amount":"20"},{"account":"cash","signed_amount":"-20"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.plant","date":"2024-06-30","period":"2024H1","postings":[{"account":"plant_cost","signed_amount":"10"},{"account":"cash","signed_amount":"-10"}],"cash_class":"investing","state_changes":{}},{"id":"2024H1.depreciate","date":"2024-06-30","period":"2024H1","postings":[{"account":"depreciation","signed_amount":"5"},{"account":"accum_depreciation","signed_amount":"-5"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.interest","date":"2024-06-30","period":"2024H1","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.tax","date":"2024-06-30","period":"2024H1","postings":[{"account":"tax","signed_amount":"1.5"},{"account":"tax_prepaid","signed_amount":"2"},{"account":"cash","signed_amount":"-3.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.dividend","date":"2024-06-30","period":"2024H1","postings":[{"account":"retained","signed_amount":"4"},{"account":"cash","signed_amount":"-4"}],"cash_class":"financing","state_changes":{}},{"id":"2024H2.sale","date":"2024-12-31","period":"2024H2","postings":[{"account":"receivables","signed_amount":"150"},{"account":"revenue","signed_amount":"-150"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.collect","date":"2024-12-31","period":"2024H2","postings":[{"account":"cash","signed_amount":"135"},{"account":"receivables","signed_amount":"-135"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.buy","date":"2024-12-31","period":"2024H2","postings":[{"account":"inventory","signed_amount":"85"},{"account":"payables","signed_amount":"-85"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.supplier","date":"2024-12-31","period":"2024H2","postings":[{"account":"payables","signed_amount":"80"},{"account":"cash","signed_amount":"-80"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.deliver","date":"2024-12-31","period":"2024H2","postings":[{"account":"cost_of_sales","signed_amount":"90"},{"account":"inventory","signed_amount":"-90"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.wages","date":"2024-12-31","period":"2024H2","postings":[{"account":"payroll","signed_amount":"22"},{"account":"cash","signed_amount":"-22"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.plant","date":"2024-12-31","period":"2024H2","postings":[{"account":"plant_cost","signed_amount":"12"},{"account":"cash","signed_amount":"-12"}],"cash_class":"investing","state_changes":{}},{"id":"2024H2.depreciate","date":"2024-12-31","period":"2024H2","postings":[{"account":"depreciation","signed_amount":"6"},{"account":"accum_depreciation","signed_amount":"-6"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.interest","date":"2024-12-31","period":"2024H2","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.tax","date":"2024-12-31","period":"2024H2","postings":[{"account":"tax","signed_amount":"5.9"},{"account":"tax_prepaid","signed_amount":"-2"},{"account":"cash","signed_amount":"-3.9"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.dividend","date":"2024-12-31","period":"2024H2","postings":[{"account":"retained","signed_amount":"5"},{"account":"cash","signed_amount":"-5"}],"cash_class":"financing","state_changes":{}}],"expected":{"2024H1":{"cash":"65","receivables":"20","inventory":"25","plant_net":"85","tax_prepaid":"2","assets":"197","payables":"25","debt":"100","equity":"72","revenue":"110","profit":"6","operating_cash":"19","investing_cash":"-10","financing_cash":"-4"},"2024H2":{"cash":"74.6","receivables":"35","inventory":"20","plant_net":"91","tax_prepaid":"0","assets":"220.6","payables":"30","debt":"100","equity":"90.6","revenue":"150","profit":"23.6","operating_cash":"26.6","investing_cash":"-12","financing_cash":"-5"},"2024FY":{"revenue":"260","profit":"29.6","operating_cash":"45.6","investing_cash":"-22","financing_cash":"-9","cash_change":"14.6"},"2025_fixed":{"cash":"95.2","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"288.2","payables":"40","debt":"100","equity":"148.2","revenue":"300","profit":"65.6","interest":"5","tax":"16.4","operating_cash":"48.6","investing_cash":"-20","financing_cash":"-8"},"2025_floating":{"cash":"93.6","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"286.6","payables":"40","debt":"100","equity":"146.6","revenue":"300","profit":"64","interest":"7","tax":"16","operating_cash":"47","investing_cash":"-20","financing_cash":"-8"}},"forecast":{"start":"2025-01-01","end_exclusive":"2026-01-01","demand_units":"30","price":"10","unit_cost":"5","target_inventory_units":"8","current_sales_collection_fraction":"0.9","legacy_receivable_collections":"10","old_payables_paid":"30","new_purchases_paid":"130","payroll":"50","capex_at_period_end":"20","dividend":"8","tax_rate":"0.2","funding_limit":"0"},"coverage_units":[{"id":"NS.opening","kind":"statement","disposition":"structured","content":"Opening balance sheet and account balances"},{"id":"NS.h1.original","kind":"statement","disposition":"superseded_reading_preserved","content":"Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80"},{"id":"NS.h1.correction","kind":"note","disposition":"structured","content":"Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6"},{"id":"NS.fy","kind":"statement","disposition":"structured","content":"Annual and revised interim statements derived from listed events"},{"id":"NS.operations","kind":"policy","disposition":"structured","content":"Goods, inventory, asset and working-capital assumptions above"},{"id":"NS.debt","kind":"note","disposition":"alternative_family","content":"Principal 100, interest 5; fixed/floating composition undisclosed"},{"id":"NS.equity","kind":"note","disposition":"structured","content":"Capital 50; original retained 20; dividends H1 4, H2 5"},{"id":"NS.reference","kind":"cross_reference","disposition":"resolved","target":"NS.debt","content":"Financing note applies to debt and interest in every statement"}]}
