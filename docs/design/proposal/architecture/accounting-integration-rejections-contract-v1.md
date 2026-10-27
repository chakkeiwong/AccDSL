# Rejection before receipt lookup — bounded proposal supplement v1

This specification addresses MC08, MC13, MC25, MC34 and MC35 and G4/G18.
It supplements the records, bindings, integration and accepted typing contracts.
It specifies finite synthetic exchanges; it neither implements an endpoint nor
accepts the integration or the whole P16 architecture.

## Question and evidence contract

Does an invalid submission preserve diagnostic evidence and stop before receipt
lookup, freshness checks or accounting assessment? The comparators are the
unchanged integration-v2 I01 assessment, an existing unresolved-condition case,
and the exact retained R06 committed-replay state and receipt. Single-defect
variants retain their comparator facts except the declared mutation. Passing
requires input-derived detection at the specified stage, precise diagnostics,
null unvalidated outputs, and unchanged identity index, committed journals,
selected state and committed receipts. Invalid acceptance, receipt disclosure,
source-version substitution, changed predecessors or invented posting permission
veto this slice and require repair. The known whole-architecture failure is not
a continuation veto. Counts and hashes explain preservation; they do not prove
accounting eligibility, current authority, runtime enforcement or forecast quality.

The pre-run skeptical audit found no unresolved objection to this bounded task:
corrected v2 is the comparator; R06 supplies an already committed world that can
expose premature lookup; no performance or stochastic ranking is sought; the
standard-library finite calculation matches the available CPU environment. Stop
after this supplement, complete exchange material, finite checks, registered
structural check, integrity record and P16 checkpoint. Remaining field coverage,
source/method-context assessment and lifecycle research are separate tasks.

## Submitted bytes and validation order

Each fixture imports its comparator by exact file hash and case ID, preserves
raw request text, and supplies a dependency bundle. Each dependency has its
claimed digest, original record domain, kind and exact canonical content text.
These are **candidate bytes**, outside the validated-record registry. A candidate
digest is an assertion for diagnosis, never an accepted request fingerprint.
The receiver retains raw request and available dependency bytes even on failure.
The submission record identifies raw request bytes under the comparator domain;
the enclosing exchange and its pinned fixture identify the supplied bundle.
A retained committed receipt remains in the before/after world; null response
receipt means no receipt is disclosed by this invalid submission.

Validation has the following ordered stages. Within a stage, findings sort by
(field path, reason code); all independently decidable findings at that stage
are retained. Stop before subsequent stages after any finding. Do not derive
binding or accounting findings from missing, malformed or unverified material.

1. `parse`: parse ASCII JSON with duplicate-key detection, including nested
   objects. Duplicate keys are invalid even when both values are identical;
   retaining the first or last value silently is forbidden.
2. `dependencies`: traverse the request's referenced candidate records. Require
   availability, parse each, and recompute its digest under its original domain.
   Check pinned file bytes when resolving source references. Never substitute
   current/latest bytes for a missing pinned version. Invalid dependency bytes
   remain diagnostic material and cannot enter the validated registry.
3. `shape`: apply the inherited closed field sets. Numeric record versions and
   sequences are nonnegative integers excluding booleans. Eligibility conditions
   contain exactly one C01–C10 in that order. Missing and duplicate IDs are
   malformed, not unknown facts. This finite supplement exercises representative
   fields; the full integration schema remains a separate acceptance obligation.
4. `source_versions`: resolve each ConditionRef through its pinned file, case
   and condition ID, then compare its opaque value_version exactly with the
   source condition's version. No trimming, coercion or chronological inference.
5. `bindings`: compare complete eligibility bindings with the request and retain
   the existing B1–B5 invariants. No identity/receipt lookup occurs until all
   validation stages succeed. Then the retained ordering applies: committed
   replay before freshness; new identities face freshness before assessment.

A source version mismatch is `CONDITION_SOURCE_VERSION_MISMATCH`, not
`STALE_OPENING_STATE`. The latter concerns a validated new transaction's opening
state after identity lookup. An explicit unknown in a resolvable source packet
is structurally valid and proceeds to semantic assessment as unresolved.

| Example | Exact defect | Stage | Reason |
| --- | --- | --- | --- |
| J01 | Duplicate request operation key, same value | parse | DUPLICATE_JSON_KEY |
| J02 | Request unexpected `extra_field` | shape | UNEXPECTED_FIELD |
| J03 | Eligibility conditions omit C10 | shape | MISSING_CONDITION_ID |
| J04 | Eligibility conditions repeat C10 | shape | DUPLICATE_CONDITION_ID |
| J05 | Request schema_version=true | shape | INVALID_RECORD_VERSION_TYPE |
| J06 | Request time digest has no supplied record | dependencies | MISSING_DEPENDENCY |
| J07 | C01 value_version differs from pinned source | source_versions | CONDITION_SOURCE_VERSION_MISMATCH |
| J08 | Eligibility time binding names the retained January time, request names June | bindings | ELIGIBILITY_BINDING_MISMATCH |
| J09 | Event price bytes change without changing claimed digest | dependencies | RECORD_DIGEST_MISMATCH |
| J10 | R06 replay request/fingerprint unchanged, supplied event price corrupted | dependencies | RECORD_DIGEST_MISMATCH |

J02–J05, J07 and J08 recompute affected candidate record identities and request
text. They must not fail merely because a mutation accidentally left a stale
hash. J09/J10 deliberately retain the false digest assertion. J10 starts from
R06's committed after-state and preserves its receipt identity and record domains;
it must reject even though the original fingerprint would retrieve a receipt.
No integration-v2 committed receipt is fabricated. The positive R06 control is
the unchanged retained lookup exchange, not a new commit.

## Response and alternatives

Every invalid exchange returns status rejected, commit_status not_committed,
additional_commit false, and null request, assessment, diagnostic_journal,
diagnostic_delta, receipt and observed_state. Structural validity is invalid,
mathematical status unresolved, computation not_computed, accounting validity
not_assessed, empirical justification not_established, capability
specified_only_no_runtime, human acceptance pending. The seven-field status and
response shapes remain those of the records contract. Precise stage/path/expected
and observed diagnostics reside in the retained exchange diagnostic record;
reason_codes in the response preserve their deterministic order. Rejection does
not assert that no prior transaction committed: it states that this attempt did
not commit, while receipt lookup was not performed.

Lookup-first would return the R06 receipt on J10 despite corrupt submitted
material, violating the validation contract. Silent repair of duplicate keys,
versions or missing records could turn a different submission into an apparently
valid request. Validation-first is proposed because it preserves what was
submitted and makes rejection reproducible. Valid explicit unknowns still reach
assessment, so validation is not a rule that all accounting facts must be known.

| Default and provenance | Status / justification | Failure and early diagnostic |
| --- | --- | --- |
| Sorted compact ASCII JSON, ensure_ascii=True, allow_nan=False; records/typing contracts | Reviewed bounded encoding baseline | Wrong domain/digest; recompute each candidate |
| Integer record versions; opaque source versions; accepted typing repair | Reviewed bounded type baseline | Boolean coercion or silent latest; J05/J07 |
| Ordered validation above | Proposed deterministic failure precedence | Hidden downstream inference; stage/path checks and J10 |
| Ten conditions and I01/R06 controls; reviewed synthetic packets | Convenience finite coverage, not exhaustive schema | Happy-path bias; unknown and committed-world controls |

| Decision | Primary criterion | Veto | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit rejection slice for bounded review | Input-derived checks in fresh verification record | Any incorrect stage, disclosure or mutation blocks slice | General schema still incomplete | Independent review of exchanges and derivation | Runtime or accounting validity |
| Keep integration/P16 partial | Four groups/profile/decisions remain unfinished | Whole-architecture check remains incomplete | Source/method-context and later domains | Separate next integration task | Product readiness/human acceptance |

Strongest alternative explanation: a narrow validator and authored fixtures may
agree while omitting important fields. The finite calculation must derive the
named failures from raw input and compare them with separately authored expected
responses. This reduces circularity but cannot establish exhaustive validation.
A contradictory binding, source packet or retained receipt overturns the affected
example. All MC01–MC35/G1–G18 obligations remain in force.
