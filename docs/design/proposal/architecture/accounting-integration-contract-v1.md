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
