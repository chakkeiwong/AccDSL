# Rejecting a scalar event list

This bounded proposal supplement asks whether the family-linked and self-contained
joint-law representations reject a string-valued `event_refs` before interpreting
it as a list. Each has a valid control with the same law, event, available model
versions, admission records and cutoffs. It addresses MC12/G15 and their
interactions with MC08, MC10, MC14, MC18 and MC25. All MC01–MC35/G1–G18 remain
active. Product implementation is disabled.

## Question and evidence contract

The exact comparator is `SC01_old_version_control` at `/pairs/0` in
`uncertainty-stale-fixtures-v1.json`. Attachment contract v2, the prerequisite
failure contract v1 and the representation comparison v1 remain provisional
specifications. The new fixture pins their files and exact locators. Historical
prototype behavior does not decide the proposed semantics.

Success for this slice requires complete paired requests and receipts: both valid
controls specify the probability 5/6; both malformed requests reject the scalar
at the operation-field check and specify no probability. Exact arithmetic checks
the controls only. Pin failures, unintended input differences, incomplete
dependencies in a control, unequal event meanings or a receipt claiming later
validation require repair before interpreting the comparison. These are
continuation vetoes for the document diagnostic, not evidence against either
architecture. Representation size and performance are not compared.

The candidate is strict array typing with an explicit field-type receipt. Its
expected failure is a request error despite the existence of an otherwise valid
event and attached law. No architecture preference, general equivalence, runtime
correctness, atomic persistence, accounting validity or forecast validity follows.
The fixture and verification JSON preserve the result; the result note separates
specified behavior from author checks. Stop after two controls, two malformed
requests, verification and partial registration. The next task is malformed
envelopes, missing fields and registry identities, considered separately.

## Assumptions and skeptical audit

| Choice and status | Provenance and reason | Failure mode | Early diagnostic |
|---|---|---|---|
| Synthetic masses; baseline only | SC01 masses 1/2, 1/3, 1/6 isolate syntax from calibration | Successful arithmetic mistaken for empirical support | Calculate each law independently with exact fractions; retain not_established |
| Exact v1 bindings with both versions available; comparator | SC01 preserves old attachment and event | Selecting v2 adds a stale-binding error | Compare each control input with SC01 except request identity |
| Bijective owned mapping; hypothesis | Retained explicit mapping makes this finite comparison interpretable | Missing outcome or mismatched coordinate changes the event | Check both versioned maps, assignments and event selectors |
| Array of exact reference strings; proposed rule | The operation takes an event list and later resolves its members | Implicit wrapping hides a malformed submission | Inspect the actual JSON type before traversing references |
| Earliest failed stage; provisional rule | Failure contract's ordered validation | A type error is misreported as a missing event | Receipt marks later stages not_checked and validated references empty |
| Canonical JSON content hashes; diagnostic convention | Deterministic preservation within these fixtures | Confusing value identity with wire-byte or storage guarantees | Hash resolved records and submitted request separately; make no storage claim |

The skeptical audit supports this matched comparison: one semantic mutation,
identical availability and bindings, explicit stopping conditions and no proxy
promotion. The smallest distinguishing check reads the submitted field type;
it must succeed before diagnostic reference traversal is attempted. No new
authority research or numerical experiment is needed for this document example.

## Four complete submissions

`MF01_array_control` reuses every SC01 input field except its request identity.
The linked request has `event_refs=["event:A@1"]`; the owned request has
`event_refs=["local-event:stale-A@1"]`. Both explicitly select the old compatible
model. Both model versions, both owned mappings, all provenance, admission and
cutoff records remain available. The event consists of the first two outcomes,
so its probability is 1/2 + 1/3 = 5/6 in each representation. The third outcome
has mass 1/6; the total is one. The probability is conditional on this synthetic
assumed law, with no empirical justification established.

`MF02_scalar_rejected` contains the same complete inputs. Only `/event_refs`
changes from the one-element array to that element as a string; request/result
identities change mechanically. A machine-readable delta identifies exactly this
change. The owned request continues to contain its complete immutable records;
external records use exact pinned JSON pointers. No selector, dependency, model
version, purpose, cutoff or mapping is changed to manufacture a failure.

## Stage-one rule and receipt

For these `evaluate_event` requests, `event_refs` must be an array whose members
are exact versioned reference strings. A string in place of that array yields
the newly proposed refinement `REQUEST_FIELD_TYPE_INVALID`, with
`field_path=/event_refs`, `expected_type=array` and `actual_type=string`.
The receipt specifies `REQUEST_INVALID`, `structural_validity=invalid`,
`mathematical_status=unresolved`, `computation_status=not_computed`,
`probability=null`, `empirical_justification=not_established` and
`capability_status=specified_only_no_runtime`.

Within stage one, a usable envelope precedes operation-field checking; this
example stops there. Registry-identity checking is recorded as not checked by
the rejected operation. Stages two through six and event evaluation are also
not checked. This specifies a local precedence refinement, not complete
compound-error ordering. The operation neither wraps the scalar into an array,
iterates its characters, nor looks it up as a missing event. It emits no
`EVENT_REFERENCE_UNRESOLVED` finding. General element syntax, empty lists,
duplicate elements, invalid envelopes, missing fields and conflicting registry
definitions are outside this slice.

All original receipt fields remain present. `support_references` and, in the
owned form, `audit_references`, identify retained references; on rejection they
do not assert that those records were resolved or validated. The added
`validated_dependency_refs` is empty. The scalar value, complete request,
request identity and canonical content hash are retained. Canonical hashing here
means SHA-256 of UTF-8 JSON with sorted keys, compact separators and ASCII
escaping. It identifies the fixture's JSON values, not original transport bytes.

The receipt's attachment status is `unchanged_not_revalidated`. Separately,
`pre_state_assessment` records the old attachment's `attached_assumption` status
and satisfied finite-law obligations from the valid control. The author
diagnostic checks that pre-state independently; the failed operation does not.
Pre/post hashes specify identical family, view and attachment records. Hashes
for every supplied external and owned record, plus the complete request, make
preservation checkable at the document level. They do not prove an implemented
transaction, storage write, or crash recovery property.

## Correspondence, alternatives and correction

Direct status fields correspond exactly. Request/result and attachment
identities translate through the retained encoding map; local model/event
references translate to the linked ones, and local mapping identities have no
linked counterpart. Dependency roles remain those in SC01: numerical law and
event, family bindings, admission/provenance, audit-only references, and the
available newer versions. These roles describe supplied records, not work
performed after rejection. The fixture explicitly lists every receipt field as
direct, translated, dependency-related or encoding-specific; state manifests
are compared to their own resolved pre-state rather than requiring equal hashes
for different encodings.

Implicitly wrapping the scalar would let an implementation guess the author's
intent, but would lose the distinction between an admitted request and a repaired
one. Treating the characters as references would produce irrelevant lookup
errors. The proposed strict rejection preserves the submission and permits a
corrected, newly identified request with the array. `submit_corrected_request`
is a proposed user action in this receipt, not an implemented API. Correction
must re-enter validation; this fixture does not execute a fifth request or promise
its acceptance without those checks. The old malformed request remains retained.
No automatic repair, admission, migration or probability computation occurs.

The baseline's deferred `model_migration` dependency is retained. Conditioning,
duplicate-evidence protection, likelihood updates and conditional outcomes still
need specification after the remaining input, binding and partition/projection
failures. Six whole-product contracts, the initial profile, integrated acceptance
criteria and dependency order, and fourteen decisions remain unresolved. E05
source limits, P17 research/authority/real-company work, independent substantive
review and human acceptance remain open.
