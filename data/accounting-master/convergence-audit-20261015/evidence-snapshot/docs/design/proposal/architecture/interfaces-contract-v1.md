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
`request_ref` is null until a typed request passes all input validation, including
binding/admission/authorization before lookup. An input rejection, including
AX02's false posting permission, therefore keeps request_ref null even if typed
decoding succeeded. A separate optional audit record links the retained
Submission and diagnostic candidate bytes, never a purported validated request.
Output-producer rejection after successful input validation retains request_ref.
`operation` and
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
