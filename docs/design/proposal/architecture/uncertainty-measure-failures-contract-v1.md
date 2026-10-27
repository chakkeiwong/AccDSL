# Joint-measure prerequisite failures: bounded supplement v1

This supplement supplies five missing rejection examples for MC12/G15, with
MC08, MC10, MC14, MC18 and MC25 interactions. It clarifies the v2 attachment
contract, not a running product. The companion fixtures pin that contract and
its registry by SHA-256. All examples are synthetic. The uncertainty contract,
attachment assessment and P16 remain incomplete; independent review is pending.

## Scope and relation to v2

The baseline is `uncertainty-measure-attachment-contract-v2.md`: section A's
`dependencies` field; B.2's explicit finite masses (including zeros); C's event
identity; D's failure list; and F's paragraphs beginning “Every request”,
“These examples validate”, “Every result”, and “Rejections leave”. This
supplement makes their prerequisite failures and result precedence explicit.
It neither changes the eighteen saved examples nor treats registry presence as
admission. Earlier mathematical failures such as a negative mass retain their
v2 meaning. Stale-but-available dependencies, malformed field types and complete
partition/projection failure coverage require a later assessment.

For the five cases the pre-state contains an already admitted synthetic law.
A rejected attachment candidate has no attachment of its own; a rejected event
request still names the old attachment. In either case the old law's finite
axioms remain satisfied. The requested computation remains unresolved. These
are different questions and appear in separate result fields.

## Ordered validation and atomic rejection

Validation uses exact `id@version` references. It never chooses another version
because its ID prefix matches. For this bounded supplement the order is:

1. Validate the request envelope, operation fields and immutable registry
   identities. Reject conflicting definitions of an existing key before
   interpreting any candidate. These are prerequisites checked on all fixtures;
   additional malformed-envelope examples are outside this slice.
2. Resolve directly named semantic records, including event references. A
   missing event yields `EVENT_REFERENCE_UNRESOLVED`, even when the same key
   also occurs in `dependencies`. Do not report that secondary occurrence as
   a second primary failure or invent a selector.
3. Resolve every declared dependency at its exact version. An unavailable
   version yields `DEPENDENCY_VERSION_UNAVAILABLE`; an available predecessor
   cannot satisfy it. Then compute required dependency closure from semantic
   references and the explicitly named time/admission context. A required
   available record absent from the declared list yields
   `DEPENDENCY_NOT_DECLARED`. Availability and declaration are separate tests.
4. Validate family/view/model/attachment bindings, purpose, coordinate order
   and cutoffs as in v2. Candidates with changed contents require new IDs or
   versions. This slice preserves those bindings; it does not redefine stale
   attachment behavior.
5. For finite laws, reject duplicate elementary IDs, then require the mass-key
   set to equal the declared sample space. A missing key yields
   `FINITE_MASS_COVERAGE_INCOMPLETE`. Only after coverage may nonnegativity and
   unit total establish the candidate's finite-law obligations. A diagnostic
   sum of supplied entries is allowed but is not a probability or a law test.
6. For finite-ID events, require the selector set to be a subset of the
   family's sample space. An outside member yields
   `EVENT_SELECTOR_OUTSIDE_SAMPLE_SPACE`. Do not intersect with the space to
   repair it, infer a new outcome, or interpret the outside ID as a missing
   registry record. Evaluation and partition/projection checks follow.

Return the earliest failing stage, with sorted offending references within
that stage. Later stages are not certified by a rejection. No event probability
is emitted and no family, view or attachment is replaced. An exact list of
unresolved references is retained separately from existing records. Retaining
a submission is append-only evidence, not admission of its model or event.
Full transactional implementation belongs to the unfinished persistence contract.

## Complete receipt and registry convention

The fixture imports all 49 baseline registry records under a pinned file hash.
`records` contains only new candidate keys; overlap with any baseline key is
forbidden, even if the proposed replacement is equal. Each new key matches the
record's `id` and `version`. Models/events with changed contents use new keys;
family/view and unchanged model identities are reused exactly. Case requests
and results are complete, with no implicit overrides. Two successful controls
are kept separately from the exactly five new rejection cases: the existing
MA03c request/result, and a complete valid attachment request constructed from
MA02a's operation shape and MA04c's diagonal law. The latter adapts the operation
explicitly before its candidate is constructed; omission of one zero is the
only semantic difference between its valid and rejected submissions.

`validation_context` explicitly supplies `time_ref` and `admission_ref` for
these fixtures. Required dependencies are the transitive closure of request
family/view/model, coordinates, provenance, justification, attachment and event
references plus these context records. Traverse the corresponding typed
reference fields of resolved records, including coordinate references inside
symbolic selectors. Sample outcome IDs are members of a declared domain, not
registry references. The declared dependency list must contain that closure;
additional declared dependencies must also resolve. This supplies a checkable
interpretation of v2's “every direct semantic reference” plus transitive
requirements without silently adding absent entries to the submitted list.

A receipt retains all v2 result fields. The five receipts specify
`REQUEST_INVALID`, `structural_validity=invalid`,
`mathematical_status=unresolved`, `computation_status=not_computed`,
`probability=null`, `family_effect=unchanged`, empirical justification
`not_established`, and capability `specified_only_no_runtime`.
`attachment_status` is `not_attached` for the rejected candidate and
`attached_assumption` for an event request using the preserved old attachment.
The additional `existing_attachment_law_status` names that old attachment and
separately records its valid structure and satisfied finite mathematics.
These statuses do not assert empirical or accounting validity.

`old_view` and `proposed_view` both identify the existing view. `state_before`
and `state_after` contain identical family/view/attachment pointers and SHA-256
values of their canonical registry contents. They specify unchanged state;
the author diagnostic checks the specified equality, not a runtime transaction.
`submission_sha256` hashes the fixture's exact UTF-8 `submission.bytes` string;
parsing that string must reproduce `input` exactly. `preserved_records` lists
that request's ID/version plus existing reachable records. `support_references`
lists existing records only, not unavailable placeholders and not the request
itself. “Support” here means records consulted, not accounting authority.
Unresolved keys remain in the submitted bytes and `unresolved_references`.
Out-of-space members appear in `observations.outside_outcomes` instead.

Both retained lists include resolved references reachable from the request,
its declared dependencies, validation context and pre-state. Traversal skips
unavailable keys without manufacturing records. Missing declarations can
therefore appear in support: resolution does not repair the request's list.
Receipt arrays are unique and sorted except that the preserved request is first.
`unresolved_obligations` and `mathematical_obligations` state the repair needed
before the requested computation can be decided. Only `revise_request` is
advertised after rejection; conditioning, likelihood update and conditional
outcomes remain future dependencies. No rejected result contains a partial
numerical event answer hidden in observations.

## Five discriminating examples

| Case | Single semantic defect relative to control | Required consequence |
| --- | --- | --- |
| MF01 | Delete `bin:01@1`'s explicit zero from the four-outcome diagonal law; use a new candidate model ID and a matching request. | Coverage fails although the three listed masses sum to one. Preserve the valid diagonal attachment; do not infer the omitted zero. |
| MF02 | Replace MA03c's event reference, including its dependency occurrence, with unavailable `event:unavailable@1`. | Return unresolved-event receipt. Preserve the submitted key, without claiming its event record exists. |
| MF03 | Create a new event from A with an added `tri:outside@1` selector member; keep the same law/family bindings. | Resolve the event successfully, then reject its selector. The old tri law remains valid. |
| MF04 | Remove `justification:fixture@1` only from MA03c's dependency list. | The directly referenced record is available but undeclared; reject without silently augmenting the request. |
| MF05 | Add unavailable `evidence:synthetic@2` to MA03c's declared dependencies; version 1 remains available. | Reject the exact-version dependency; do not substitute version 1. |

Identifier changes needed to preserve immutability are bookkeeping consequences
of these defects, not additional semantic defects. MF02 retains MA03c's repeated
references; unresolved-event validation precedes idempotent lookup. MF03 retains
the same repetition and does not make any likelihood-update claim.

## Audit, alternatives and stop

Explicit coverage follows B.2; inferring zero would conflate an omitted input
with a stipulated probability. Exact-version rejection follows v2 identity;
substitution would change the information used. Rejecting incomplete dependency
lists makes missing reproducibility information visible; auto-completion would
hide what was actually submitted. Ordered rejection is a proposed engineering
choice for deterministic receipts, not a prototype-derived product requirement.
A collect-all-errors alternative remains possible in a later interface design,
provided it distinguishes checked failures from unperformed validations.

The baseline, one-defect comparisons and stop condition were independently
reviewed in plan 59837457ef465a7b2b9abdf6f3627322799994af7cb28db24b369887ac323a95.
Exact rational arithmetic and canonical JSON hashing are document-diagnostic
conventions. The smallest check compares actual outcome/mass sets, resolves
exact keys, derives dependency closure and evaluates the valid controls. The
risk is that an author and diagnostic share an unstated assumption; independent
substantive review remains necessary. Counts cannot promote the proposal.

Stop after the five cases, input-derived diagnostic, partial registration and
fresh structural receipt. Next separately review the matched comparison of
family-linked and self-contained joint models and the remaining failure
inventory. Optional bounded result review stays pending without blocking that
freshly reviewed drafting task. Full independent P16 review remains mandatory.
Six contracts, initial profile, integrated acceptance/dependency order and all
fourteen decisions remain open; the wider MC01–MC35/G1–G18 mission is preserved.
