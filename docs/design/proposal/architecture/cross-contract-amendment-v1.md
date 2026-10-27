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
The branch definition has required `book_mode`, exactly `synthetic` or `real`,
and the posting profile has required nonempty `supported_book_modes`, a set of
those literals. Authorization verifies membership and the following evidence
scope. A synthetic branch requires evidence_level=authored-synthetic
and cannot be committed into a real branch. A real branch requires a
source-supported posting authority and separately admitted real-workspace
facts/assumptions; an admitted assumption retains its assumption label. Copying a
synthetic label into a real branch is a binding failure. This discriminator is
checked by `accounting.authorize@1`, which produces this record from the
EventBasis and profile;
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
