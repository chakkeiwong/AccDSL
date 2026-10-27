# C05/C07 conditional unknown representation — proposal amendment v1

This bounded specification addresses MC08, MC13, MC25, MC34 and MC35,
with G4/G18 interactions. It amends only F211, F219, F243, F248 and F253
of the retained 299-path field inventory. The accepted six-row source-reason
type amendment remains unchanged. Product implementation is disabled.

## Question, baselines and skeptical audit

Can a submitted classification or fee packet distinguish an explicit unknown
from malformed representation, while preserving known false values? E01/E02/E05
and their I01/I02/I05 integration exchanges are exact preservation comparators.
They are synthetic examples, not authority or an approved product architecture.
The passing evidence is explicit conditional rules, local positive and negative
controls, complete representative exchanges and candidate-derived diagnostics.
Changed predecessor bytes, stale pins, lost unknowns, contradictory controls,
ambiguous diagnostics or publication of rejected input veto this bounded result.
Counts and hashes are explanatory structural evidence; accounting validity,
forecast quality and human acceptance are not inferred from them.

The pre-edit skeptical audit passes for this scope: the approved comparators
retain the actual known and unresolved cases; no weak-baseline ranking, hidden
runtime, new dependency or scientific experiment is involved. The historical
calculator recognizes unknown C07.incremental but does not cover every nullable
C07 combination. Therefore all nine combinations are checked only for
representation. Their accounting outcomes must not be copied from that calculator.
Stop after the five-field amendment, local controls, representative exchanges,
preservation and document checks. Remaining source rules and V01–V16 are later tasks.

## Fields and precedence

The companion matrix separates observed JSON types from allowed JSON types.
It governs the five named rows' requiredness, types and conditional predicates;
all other retained field rules and source provenance requirements continue to apply.
Each packet and its value must be objects. Each of the three named fact leaves
and both unknown_reason properties is required. Missing is malformed; present
null represents an explicitly unknown fact. A Boolean false is known, just as
true is known. No numeric, string or other coercion is permitted. Preserve source
bytes, opaque packet versions, rationale_status and provenance exactly.

C05/value/rationale_available permits boolean|null. C07/value/incremental and
C07/value/would_incur_without_acquisition each permit boolean|null. For C05,
a null rationale_available requires a nonblank C05 unknown_reason. For C07,
null in either named leaf requires a nonblank C07 unknown_reason. A single reason
explains the packet; this rule does not claim that its prose substantiates each
fact or supplies missing facts. No complement relationship between the two C07
Booleans is imposed by representation validation. In particular, true/true and
false/false are representable and may require substantive reconciliation later.
No rationale_status text or reason prose overrides a fact leaf.

Both reasons permit null|string as JSON types. Null is conditionally admissible
only when every scoped controlling leaf is a known Boolean. If a controlling
member is malformed, that member is rejected; it does not become an unknown.
Every string must contain a character outside this explicit whitespace set:
U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A,
U+2028–U+2029, U+202F, U+205F and U+3000. There is no trimming or Unicode
normalization. The same set is used by the accepted six-row amendment.

A nonblank contextual reason is permitted when all facts are known. This keeps
explanatory source text without converting it into uncertainty or rejecting a
packet solely for carrying additional explanation. Requiring null in that case
would discard useful text; inferring a fact from the explanation would change
the evidential boundary. Automatically replacing a missing reason or false fact
with null is rejected because it changes the submission.

## Ordered findings and dependency guards

All scoped predicates run at shape, after parse and dependency integrity and
before source_versions, bindings, receipt lookup and accounting assessment.
Presence precedes type; string content follows only a successful string type
check. A missing member yields INVALID_CONDITION_PACKET. A wrong JSON type
yields INVALID_FIELD_TYPE. A blank string yields INVALID_UNKNOWN_REPRESENTATION.
A well-typed null reason with at least one well-typed null controlling leaf also
yields INVALID_UNKNOWN_REPRESENTATION at source/C05/unknown_reason or
source/C07/unknown_reason. The expected rule and observed presence/type/value
must be returned, with null's presence explicitly true and missing's false.

Guard descendants on a present object parent. Emit only the parent finding when
that parent is malformed; continue independent sibling checks. A malformed fact
cannot trigger the conditional reason finding. A different, well-typed null fact
can trigger it independently: C07.incremental missing with
would_incur_without_acquisition=null and unknown_reason=null yields both the
missing-leaf finding and the reason finding. If the only unresolved control is
malformed, do not manufacture a conditional finding from it. Missing, wrong-type
or blank reasons already have their own finding; do not duplicate it with a
conditional finding. Retain all independently decidable shape findings sorted
by (path, code), regardless of which condition was visited first.

Diagnostics have stage, path, code, expected and observed fields, matching the
retained rejection diagnostic contract. Candidate values, not mutation labels,
determine findings. The fixture separately records why earlier stages pass and
which null paths activate each conditional predicate. The finite diagnostic must
recompute those derivations from the candidate source file.

## Complete exchanges and evidence limits

Unchanged I01, I02 and I05 are retained controls. A changed source case is saved
as a new file with complete_inputs; only the declared leaves differ. Exact
FileRefs and CaseRefs identify it. Dependent eligibility, request, submission,
assessment and response records are materialized with refreshed identities;
unchanged records are imported by exact file hash under their original domains.
No asserted candidate request digest is a validated request fingerprint before
validation succeeds. Original opaque source versions remain exact strings;
version alone is not source identity because the enclosing file hash changes.

Contextual-reason changes on known controls preserve their stipulated assessment.
For every valid exchange, identity lookup finds no key in the retained empty
identity index; freshness is then checked before assessment, as required by the
integration contract. Retained valid unknowns reach unresolved assessment. Invalid reason candidates
stop at shape before lookup and assessment. They return rejected/not_committed,
additional_commit=false, null request, assessment, diagnostic_journal,
diagnostic_delta, receipt and observed_state. The seven statuses are invalid,
unresolved, not_computed, not_established, specified_only_no_runtime,
not_assessed and pending in their inherited named fields. Response reason codes
follow diagnostic order, with first-occurrence deduplication for repeated codes.
The diagnostic array retains every affected path. All committed domains and
selected state remain unchanged for both valid assess_only and rejected exchanges.
No broader Boolean-combination accounting result is specified by local controls.

## Defaults, alternatives and continuation

| Choice and provenance | Status and reason | Failure mode and early check |
| --- | --- | --- |
| Retained E/I controls and original record domains | Preservation baseline | Stale or changed comparator; exact hashes |
| Explicit whitespace set from accepted amendment | Reviewed local rule | Host-dependent blank classification; scalar-range controls |
| Context strings on known packets | Proposed extension consistent with six-row amendment | Prose interpreted as a fact; unchanged-fact and assessment controls |
| All nine C07 combinations | Representation coverage only | Shape pass mistaken for eligibility; local-only labels |
| Finite document diagnostic, standard library | Convenience check | Authored expectations echo checker; separately authored failures plus mutation isolation |

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit this bounded amendment | Fresh finite checks and explicit exchanges | Any mismatch requires repair | Exhaustive source/context semantics remain open | Independent bounded review | P16 acceptance or runtime correctness |
| Retain wider proposal work | Four groups/profile/decisions incomplete | Whole architecture remains incomplete | C03/C09/C10 and V01–V16 remain | Remaining source condition group, then V diagnostics | Accounting/forecast validity or human acceptance |

Strongest alternative explanation: finite fixtures can agree while missing a
control combination or a dependency path. Check all nine combinations, raw
submitted values, complete dependency closure and exact mutation isolation;
a contradictory preserved control overturns that example. This does not replace
independent substantive review. All MC01–MC35/G1–G18 obligations remain.
