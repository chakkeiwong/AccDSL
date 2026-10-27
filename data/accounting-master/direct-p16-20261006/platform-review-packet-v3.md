READ-ONLY P16 SUBSTANTIVE REVIEW. Codex executes; do not edit, run shell/network, or launch agents. Read/Glob/Grep are available. Review the following actual draft contracts and inspect exact references as needed. Product implementation is disabled. These are governing design specifications, not evidence of runtime conformance. P17 source/accounting/sector method obligations, the E05 real conflict and a complete real-package case remain proposal blockers; do not invent closure, and do not mistake those explicit later tasks for a missing P16 architectural answer.

Find material semantic defects: identity/replay, native status mapping, information/admission loss, math, incomplete-result claims, hidden defaults and omitted bindings. Return concrete findings with file/section, counterexample, smallest repair and whether blocking P16 architecture acceptance. Report inspected scope. End VERDICT: AGREE or VERDICT: REVISE. Check counts are not acceptance evidence: current finite checks are 797 structural, 169 arithmetic, 2580 accounting-exchange assertions and 932 unchanged protected files. Read data/accounting-master/deliverables/P16/architecture.json for current index/decisions (ignore historical bounded-work status as current authority). The active plan is docs/plans/accounting-p16-direct-execution-20261006.md.

FOCUS: New four contracts and their native accounting interactions. Inspect representative complete exchanges when judging closure/shape/publication.

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

`OperationResult` has exactly `request_ref`, `operation`, `input_view_ref`,
`disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
`continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
References are typed. The last two references may be null. `payload` is a tagged
union selected by the signature; rejected input has null payload. `diagnostics`
and `unresolved` are ordered lists (possibly empty). `coverage` contains the
requested domain Ref and completed/unresolved/unsupported/infeasible/cancelled
region Refs, with their partition/overlap relation. Reads may use one singleton
request region; they cannot invent an economic-family denominator. `statuses`
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
mathematical status is `defined`, `undefined`, `unresolved`, `infeasible` or
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
| failed mathematics, such as an invalid proposed law | rejected; mathematical_status=unresolved at platform level with the exact native `failed` finding retained; never `infeasible` without proof of an empty family |

For the last row a platform diagnostic names the failed mathematical predicate
and preserves the native result; the requested probability result remains
unresolved. `structural_validity` is copied from the native request validation,
not inferred from the law's failure. A proof of infeasibility is a different
tagged result and maps to `infeasible`. Numeric/service failure has computation
`failed` and math `unresolved`, not mathematical infeasibility. These rules
prevent the platform's deliberately smaller vocabulary from changing a claim.

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


NORTHSTAR ORIGINAL INPUTS:
{"schema":"accdsl-design-fixture/1","entity":"Northstar Components (synthetic)","currency":"USD","units":"one currency unit","basis":"DemoCorporate/1; not GAAP certification","disclosure_scope":"Closed synthetic goods company; the listed source package is complete by construction","assumptions":{"historical_resolution":"half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices","inventory":"one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5","sales":"delivery transfers control; no returns, services, variable consideration or foreign currency","tax":"20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax","plant":"opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals","debt":"100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast","time":"half-year accrual fractions 1/2, annual 1; explicit teaching convention","closing":"temporary accounts closed after each H1/H2; annual income uses movements excluding closing","universe":"no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package"},"accounts":{"cash":"asset","receivables":"asset","inventory":"asset","plant_cost":"asset","accum_depreciation":"contra_asset","tax_prepaid":"asset","payables":"liability","debt":"liability","capital":"equity","retained":"equity","revenue":"income","cost_of_sales":"expense","payroll":"expense","depreciation":"expense","interest":"expense","tax":"expense"},"opening":{"cash":"60","receivables":"20","inventory":"30","plant_cost":"100","accum_depreciation":"-20","tax_prepaid":"0","payables":"-20","debt":"-100","capital":"-50","retained":"-20"},"historical_events":[{"id":"2024H1.sale","date":"2024-06-30","period":"2024H1","postings":[{"account":"receivables","signed_amount":"110"},{"account":"revenue","signed_amount":"-110"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.collect","date":"2024-06-30","period":"2024H1","postings":[{"account":"cash","signed_amount":"110"},{"account":"receivables","signed_amount":"-110"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.buy","date":"2024-06-30","period":"2024H1","postings":[{"account":"inventory","signed_amount":"70"},{"account":"payables","signed_amount":"-70"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.supplier","date":"2024-06-30","period":"2024H1","postings":[{"account":"payables","signed_amount":"65"},{"account":"cash","signed_amount":"-65"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.deliver","date":"2024-06-30","period":"2024H1","postings":[{"account":"cost_of_sales","signed_amount":"75"},{"account":"inventory","signed_amount":"-75"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.wages","date":"2024-06-30","period":"2024H1","postings":[{"account":"payroll","signed_amount":"20"},{"account":"cash","signed_amount":"-20"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.plant","date":"2024-06-30","period":"2024H1","postings":[{"account":"plant_cost","signed_amount":"10"},{"account":"cash","signed_amount":"-10"}],"cash_class":"investing","state_changes":{}},{"id":"2024H1.depreciate","date":"2024-06-30","period":"2024H1","postings":[{"account":"depreciation","signed_amount":"5"},{"account":"accum_depreciation","signed_amount":"-5"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.interest","date":"2024-06-30","period":"2024H1","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.tax","date":"2024-06-30","period":"2024H1","postings":[{"account":"tax","signed_amount":"1.5"},{"account":"tax_prepaid","signed_amount":"2"},{"account":"cash","signed_amount":"-3.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.dividend","date":"2024-06-30","period":"2024H1","postings":[{"account":"retained","signed_amount":"4"},{"account":"cash","signed_amount":"-4"}],"cash_class":"financing","state_changes":{}},{"id":"2024H2.sale","date":"2024-12-31","period":"2024H2","postings":[{"account":"receivables","signed_amount":"150"},{"account":"revenue","signed_amount":"-150"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.collect","date":"2024-12-31","period":"2024H2","postings":[{"account":"cash","signed_amount":"135"},{"account":"receivables","signed_amount":"-135"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.buy","date":"2024-12-31","period":"2024H2","postings":[{"account":"inventory","signed_amount":"85"},{"account":"payables","signed_amount":"-85"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.supplier","date":"2024-12-31","period":"2024H2","postings":[{"account":"payables","signed_amount":"80"},{"account":"cash","signed_amount":"-80"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.deliver","date":"2024-12-31","period":"2024H2","postings":[{"account":"cost_of_sales","signed_amount":"90"},{"account":"inventory","signed_amount":"-90"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.wages","date":"2024-12-31","period":"2024H2","postings":[{"account":"payroll","signed_amount":"22"},{"account":"cash","signed_amount":"-22"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.plant","date":"2024-12-31","period":"2024H2","postings":[{"account":"plant_cost","signed_amount":"12"},{"account":"cash","signed_amount":"-12"}],"cash_class":"investing","state_changes":{}},{"id":"2024H2.depreciate","date":"2024-12-31","period":"2024H2","postings":[{"account":"depreciation","signed_amount":"6"},{"account":"accum_depreciation","signed_amount":"-6"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.interest","date":"2024-12-31","period":"2024H2","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.tax","date":"2024-12-31","period":"2024H2","postings":[{"account":"tax","signed_amount":"5.9"},{"account":"tax_prepaid","signed_amount":"-2"},{"account":"cash","signed_amount":"-3.9"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.dividend","date":"2024-12-31","period":"2024H2","postings":[{"account":"retained","signed_amount":"5"},{"account":"cash","signed_amount":"-5"}],"cash_class":"financing","state_changes":{}}],"expected":{"2024H1":{"cash":"65","receivables":"20","inventory":"25","plant_net":"85","tax_prepaid":"2","assets":"197","payables":"25","debt":"100","equity":"72","revenue":"110","profit":"6","operating_cash":"19","investing_cash":"-10","financing_cash":"-4"},"2024H2":{"cash":"74.6","receivables":"35","inventory":"20","plant_net":"91","tax_prepaid":"0","assets":"220.6","payables":"30","debt":"100","equity":"90.6","revenue":"150","profit":"23.6","operating_cash":"26.6","investing_cash":"-12","financing_cash":"-5"},"2024FY":{"revenue":"260","profit":"29.6","operating_cash":"45.6","investing_cash":"-22","financing_cash":"-9","cash_change":"14.6"},"2025_fixed":{"cash":"95.2","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"288.2","payables":"40","debt":"100","equity":"148.2","revenue":"300","profit":"65.6","interest":"5","tax":"16.4","operating_cash":"48.6","investing_cash":"-20","financing_cash":"-8"},"2025_floating":{"cash":"93.6","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"286.6","payables":"40","debt":"100","equity":"146.6","revenue":"300","profit":"64","interest":"7","tax":"16","operating_cash":"47","investing_cash":"-20","financing_cash":"-8"}},"forecast":{"start":"2025-01-01","end_exclusive":"2026-01-01","demand_units":"30","price":"10","unit_cost":"5","target_inventory_units":"8","current_sales_collection_fraction":"0.9","legacy_receivable_collections":"10","old_payables_paid":"30","new_purchases_paid":"130","payroll":"50","capex_at_period_end":"20","dividend":"8","tax_rate":"0.2","funding_limit":"0"},"coverage_units":[{"id":"NS.opening","kind":"statement","disposition":"structured","content":"Opening balance sheet and account balances"},{"id":"NS.h1.original","kind":"statement","disposition":"superseded_reading_preserved","content":"Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80"},{"id":"NS.h1.correction","kind":"note","disposition":"structured","content":"Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6"},{"id":"NS.fy","kind":"statement","disposition":"structured","content":"Annual and revised interim statements derived from listed events"},{"id":"NS.operations","kind":"policy","disposition":"structured","content":"Goods, inventory, asset and working-capital assumptions above"},{"id":"NS.debt","kind":"note","disposition":"alternative_family","content":"Principal 100, interest 5; fixed/floating composition undisclosed"},{"id":"NS.equity","kind":"note","disposition":"structured","content":"Capital 50; original retained 20; dividends H1 4, H2 5"},{"id":"NS.reference","kind":"cross_reference","disposition":"resolved","target":"NS.debt","content":"Financing note applies to debt and interest in every statement"}]}

Supporting inspection paths (all relative to repo):
- docs/design/proposal/architecture/accounting-complete-exchanges-v1.json: exchanges X002, X007, X008, X188, X202, X241, K01 and K04; resolve their records and imports.
- docs/design/proposal/architecture/accounting-complete-source-packets-v1.json: matching cases; compare original source refs.
- docs/design/proposal/architecture/accounting-integration-field-validation-fixtures-v1.json: V01–V16 actual adverse candidates and expected outcomes.
- docs/design/proposal/architecture/accounting-complete-exchanges-diagnostic-v1.py: context_findings and adverse_outcome independently classify these finite inputs.
- docs/design/proposal/architecture/uncertainty-chaining-fixtures-v2.json: cases, mappings, bundles, admissions, active_rejection_receipts; requested refs resolve in records.
- docs/design/proposal/architecture/platform-contract-examples-v1.json and platform-contract-calculation-v1.py: joint company outcomes, changed-rate control and finite arithmetic.
- docs/design/proposal/architecture/evidence-contract-v3.md; time-contract-v2.md; history-families-contract-v1.md; uncertainty-admission-contract-v1.md; uncertainty-measure-attachment-contract-v2.md: controlling domain rules.
- docs/design/proposal/architecture/accounting-replay-contract-v1.md and accounting-integration-contract-v1.md: native key, assess-only effects and validation order.

Tools may inspect these exact files. Do not claim exhaustive coverage if sampling; substantive architecture review with disclosed sample coverage is the intended result. Do not demand another packet approval cycle.
