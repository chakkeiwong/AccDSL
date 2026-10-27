# Joint-measure attachment and event identity v2

This document specifies the next bounded part of the P16 uncertainty contract.
It attaches a declared joint measure to an already versioned history family and
evaluates events against that one measure. It does not select a measure from
data, infer independence, condition on observations, update likelihoods, run a
solver, or produce financial statements. The examples are synthetic design
fixtures; they establish no probability for an actual company and no
accounting permission.

This version repairs the saved examples only. Systematic matched-alternative
assessment and remaining failure-case coverage remain the next bounded task.

The contract is needed for MC08--MC14, MC18, MC25 and MC27 and for G1, G15 and
G16. It consumes the evidence, time, history-family and admission records
already described in this directory. Accounting validity, empirical forecast
validity, implementation correctness and human acceptance remain separate
questions.

## A. Request, result and identity

`MeasureAttachmentRequest` is an immutable, versioned record with these fields:

| Field | Required meaning |
| --- | --- |
| `request_id`, `version`, `predecessor` | Stable request identity and an explicit predecessor; changing the bytes creates a new version. |
| `family_id`, `family_version`, `view_id`, `view_version` | Exact history family and named view to which the measure applies. A measure never silently follows a successor family. |
| `model_id`, `model_version` | Version of the declared measure representation and its evaluator. A model label alone is not a law. |
| `coordinates` | Ordered typed coordinates, including entity/perimeter, concept, dimensions, units, time and any shared drivers. Coordinate identity is semantic, not an array position chosen by a caller. |
| `sample_space` | Explicit elementary outcomes or a declared continuous/mixed domain, with support and measurability metadata. Missing support is unresolved. |
| `event_representation` | Versioned selectors for elementary outcomes, measurable cells or symbolic predicates. A display label is never an event key. |
| `measure_kind`, `purpose` | `finite_joint`, `discrete_joint`, `continuous_joint` or `mixed_joint`; purpose is one of scenario, pricing, risk, or another declared use. Purposes cannot be mixed implicitly. |
| `mass_or_density` | Exact masses, a versioned density, or a symbolic measure expression. Finite examples use rational strings; unsupported evaluation retains the expression. |
| `support_restrictions`, `dependence` | Restrictions and all declared cross-coordinate dependence. Empty dependence means “unspecified”, not independence. |
| `provenance`, `justification` | Source/model record versions, author, rationale, assumptions and whether the law is synthetic, stipulated, estimated or empirically supported. |
| `information_cutoff`, `evidence_cutoff` | Time views used to justify the model and to admit its inputs. Later information cannot silently enter an earlier view. |
| `dependencies` | Exact versioned family, evidence, time, category and model dependencies. A missing or stale dependency blocks current reuse. |

The result is a `MeasureAttachmentResult` with the request and record identity,
old and proposed view, a disposition, reason codes, preserved records,
support references, unresolved obligations, structural validity, attachment
status, mathematical obligations, empirical-justification status,
capability status, computation status and permitted next operations. These
fields are separate. A syntactically valid finite law can be attached as an
assumption while its empirical justification remains `not_established`.

The dispositions are:

* `ATTACHED_ASSUMPTION`: the declared law is structurally valid and explicitly
  admitted as a model assumption; no empirical claim follows.
* `ATTACHED_SUPPORTED`: a separately inspected source/model record supports the
  law for this purpose and scope. This status is not created by a fixture.
* `RETAINED_ONLY`: the submission is preserved but not selected.
* `REQUEST_INVALID`: identity, version, support or representation is malformed.
* `UNSUPPORTED`: the requested evaluator or measure representation is outside
  declared capability; the expression and domain remain intact.
* `SCOPED_CONFLICT`: restrictions or attached records are incompatible in the
  named family/view. It is not a claim of global infeasibility.

## B. Attachment invariants

1. The family/view, model version, coordinate order, purpose and information
   cutoffs are part of the identity. A law attached to `F@1/V@1` cannot be
   reused for `F@2/V@1` merely because the labels look alike. A changed support
   invalidates reuse until an explicit alignment or update operation records
   what changed.
2. For a finite joint law, each elementary outcome ID is unique, each mass is
   finite and non-negative, and the exact total is one. A duplicate ID is a
   malformed representation, not extra mass. The declared sample space S is
   distinct from positive-mass support {s in S: m(s)>0}. Every member of a finite
   S has an explicit mass, including zero. Omitting a member is an error, not an
   assertion of zero mass. An event may include zero-mass members. A partition
   must cover S, not merely its positive-mass subset.
3. No mass is inferred from solver counts, branch counts, labels, extraction
   confidence, reviewer preference, successful-run frequency or a convenient
   equal-weight default. An unweighted future domain remains unweighted until a
   separate attachment is explicitly accepted.
4. Dependence is joint information. Identical marginal summaries do not permit
   an independence assumption. Shared drivers, entity links, dates, lots and
   contract states stay in the coordinate and dependency records.
5. A real-world scenario measure and a pricing or risk measure are different
   records. Changing `purpose` requires a new attachment and justification; it
   is not a unit conversion.
6. An attachment may be conditional on admitted evidence, an authored
   assumption, or a future-domain restriction. It cannot turn an unsupported
   accounting election into authority or turn a reported value into an economic
   fact.
7. Every accepted operation is append-only. A correction creates a new measure
   version and records the predecessor, changed support and affected results.
   Old views remain readable as historical records but are not current by
   default. Failed writes leave the old view current and return a failure
   receipt.

The historical Core 0 probe required a joint law for future innovations and
therefore rejected an unweighted future domain. This proposal supersedes that
probe restriction for the whole product: an unweighted domain is admissible as
an explicit scenario assumption, but probability, expectation, likelihood and
quantile operations require this attachment contract and an attached law. The
older restriction remains evidence about the prototype, not a universal
semantic rule.

## C. Event identity and evaluation

An `EventIdentity` contains an event ID/version, the exact family/view and
measure identity, coordinate bindings, selector kind, selector expression,
projection metadata and provenance. A named event may be an overlapping view;
it need not be a cell in a partition. Distinct elementary outcomes that map to
the same displayed coordinate remain distinct IDs. A duplicate event
description with the same identity is an idempotent reference; a new selector
version is a new event.

For a finite space `S` with masses `m(s)`, a selector `E` evaluates as

\[
  P(E)=\sum_{s\in S:\,E(s)}m(s).
\]

For events `A` and `B`, evaluation uses the same joint law:

\[
P(A\cap B)=\sum_{s:\,A(s)\land B(s)}m(s),\qquad
P(A\cup B)=P(A)+P(B)-P(A\cap B).
\]

The subtraction is required when views overlap; summing named-view masses
without the intersection double-counts shared outcomes. A finite partition must
carry coverage and pairwise-disjointness evidence before a caller may treat its
cell masses as an exhaustive decomposition. For continuous or mixed spaces,
the request preserves the declared domain and measure expression. If no
validated evaluator is available, the result is `UNSUPPORTED` with the
symbolic event and unresolved numerical obligation; it never fabricates a
grid, density normalization or probability.

Projection is explicit. If two elementary outcomes `(region=A, rate=1)` and
`(region=B, rate=1)` both project to `rate=1`, the projected display has mass
one but the elementary outcomes remain two distinct members of the joint
space. Collapsing them is allowed only through a named measurable projection
that records the lost coordinate and the resulting event algebra.

## D. Failures and interactions

The evidence and admission contracts supply immutable records, category
dispositions and selected assumptions. The time contract supplies information
cutoffs, byte vintages and review views. Histories consume an attached law and
return family-scoped events; they must retain unweighted domains and unresolved
branches when no law is attached. Accounting receives a measure only as a
scenario/model input and must perform its own recognition, measurement and
journal checks. Language/IR must encode exact versions, selectors, domains and
reason codes. Persistence owns atomic append, stale-version detection and
reverse dependencies. Interfaces expose the purpose, conditions, cutoffs,
support, dependence and unresolved obligations. Failure semantics preserve
partial records on resource or evaluator failure.

The following are explicit failures: negative or non-unit finite mass;
duplicate elementary IDs; omitted support; stale family/model version;
incompatible purpose; implicit independence; event references outside the
declared space; a partition advertised without coverage/disjointness evidence;
and unsupported continuous evaluation. None of these failures authorises
discarding mass, renormalising successful branches, or replacing an unresolved
outcome with a default.

Conditioning, likelihood updates, measure conversion, calibration and
conditional statement/outcome payloads are future operations. They must name a
denominator/event identity, information set and resulting family version and
will be specified in a separate reviewed task.

## E. Matched alternatives and default audit

Two credible representations are proposed for a future matched assessment
against the same fixtures. That assessment has not been completed:

* **Family-linked record (provisional choice).** The attachment stores the exact
  family/view and references the model record. Revisions and invalidation are
  straightforward, and a reader can trace a probability back to the joint
  history family. Portability requires a stable family identity service.
* **Self-contained joint-model record.** The attachment carries a complete
  joint model and an explicit projection to a family. It is easier to export,
  but duplicated family definitions can drift and a correction must reconcile
  two version graphs.

The family-linked design remains a provisional candidate because preserving
shared history identity and revision lineage is a stated mission requirement.
This is a design rationale, not a performance or usability ranking; both
alternatives remain implementation candidates until the language, persistence
and interface contracts are reviewed. The material defaults have the following
audit:

| Choice | Provenance and justification | Failure mode | Smallest diagnostic | Status |
| --- | --- | --- | --- | --- |
| Rational finite masses in fixtures | Exact arithmetic makes overlap and normalization inspectable. | Decimal parsing could hide rounding. | Recompute with `Fraction` and compare exact strings. | Synthetic diagnostic convention |
| Explicit elementary IDs | Needed to distinguish equal projections. | Callers may use labels as IDs. | Duplicate-ID and projection-collision fixtures. | Proposed invariant |
| No implicit independence | Required by joint-history dependence. | Marginal-only input may be treated as independent. | Same-marginal/different-joint fixtures. | Proposed invariant |
| Separate purpose | Scenario and pricing measures answer different questions. | A converter may relabel a measure. | Purpose-mismatch rejection fixture. | Proposed invariant |
| Family-linked identity | Preserves revisions and dependency closure. | Export/import may lack family registry. | Version-mismatch and changed-support fixtures. | Candidate; profile unselected |

All fixture outputs are specified behavior only. They do not show that a
runtime, accounting treatment, company probability or forecast is correct.


## F. Operation-specific records and fixture convention (v2)

The companion v2 JSON stores complete request/result records in each case. There
are no implicit case overrides or defaults. `records` is an immutable registry:
its key equals `id@version`, and references always use that complete key.
`family_ref`, `view_ref`, `model_ref`, coordinate references and dependency lists
resolve there. An explicitly null model denotes an unweighted domain, not a
missing field. A stored malformed model remains a submitted candidate; registry
presence is not admission. The same key must never describe different bytes.
Family and view versions are independent; a view identifies exactly one family
version. Model versions bind the family, view, coordinate order, sample space,
purpose, dependence and mass/density representation. A new law requires a new
key. These examples use explicit references rather than duplicating id/version
pairs that could disagree.

Every request has `request_id`, `version`, `predecessor`, `operation`, exact
family/view/model references, ordered `coordinates`, `sample_space`,
`measure_kind`, `purpose`, `mass_or_density`, `dependence`,
`support_restrictions`, `event_representation`, `provenance`, `justification`,
`information_cutoff`, `evidence_cutoff`, and `dependencies`. Coordinates resolve
to typed concept/entity/perimeter/dimension/unit/time metadata. Dependencies
include every direct semantic reference and the time/admission/evidence records.
Transitive dependencies follow the registry references. Cutoffs here are both
2026-03-01T00:00:00Z; fixture records were authored for this synthetic time view.
No claim about the information available for a real company follows.

`MeasureAttachmentRequest` uses `operation=attach_measure`. The deliberately
invalid branch-count request uses `infer_from_branch_count`; its rejection is
specified even though this is not an admitted operation. Marginal-only inputs
are retained as constraints on possible laws, with no attached joint measure.
For finite laws, masses cover the declared outcomes exactly and joint outcome
assignments cover every coordinate. `support_restrictions=[]` means no added
restriction, not permission to discard an outcome. A density is expressed
relative to its declared base measure; missing normalization remains explicit.

`EventEvaluationRequest` uses `operation=evaluate_event` and also requires
`attachment_ref`, `event_refs`, and `query`. The attachment is either an admitted
synthetic precondition or a retained symbolic candidate with explicit status.
Each event binds its own model/family/view and coordinates, selector kind,
selector expression, projection metadata and provenance. Queries are one-event
probability, two-event overlap, finite partition validation, or finite
projection. MA03c repeats one event reference; it does not request an evidence
update and proves nothing about semantic duplicate likelihoods. Symbolic
requests retain expressions when the proposed evaluator cannot compute them.

Every result includes `result_id`, `version`, `request_ref`, `operation`,
`old_view`, `proposed_view`, `disposition`, `reason_codes`, `preserved_records`,
`support_references`, `unresolved_obligations`, `structural_validity`,
`attachment_status`, `mathematical_status`, `mathematical_obligations`,
`empirical_justification`, `capability_status`, `computation_status`,
`next_permissible_operations`, `future_dependencies`, `family_effect`,
`probability`, and `observations`. Attachment success additionally identifies
`attachment_ref`; evaluated results retain the input attachment. `probability`
is populated only for a single defined event; multi-event/projection answers
are named in `observations`. Invalid total mass is an observation about a
candidate, not an event probability. Unsupported or rejected evaluations return
no numerical probability. Receipt preservation is not an attached law.

Attachment dispositions retain section A meanings. Event results add
`EVALUATED` for a computed, mathematically valid query under the named law;
`REQUEST_INVALID` for incompatible identity/purpose or malformed selectors;
`RETAINED_ONLY` for a stale model that needs explicit migration; and
`UNSUPPORTED` for a retained symbolic request without a validated evaluator.
`structural_validity` concerns the representation, not normalization;
`mathematical_status` is independently `satisfied`, `failed`, or `unresolved`.
An unavailable evaluator can leave structure valid and mathematics unresolved.
All empirical statuses here are `not_established`. `capability_status` means
capability proposed by this document, never an installed runtime capability.
All results are specified expectations, not executed product responses.

An attachment appends a measure record referencing its existing family/view;
it does not change the history family or select a probability for unweighted
alternatives. `old_view` and `proposed_view` therefore match in these examples.
Rejections leave the old view/attachment current. Stale-model and changed-family
requests preserve that original view and require a new explicitly reviewed
attachment; they cannot silently redirect it. Atomic persistence remains a
separate unfinished contract.

The currently specified next operations are revise_request, attach_measure,
evaluate_event, and retain_symbolic. These names describe the proposal only.
Conditioning, likelihood updates, model migration, evaluator installation and
conditional financial outcomes occur only in `future_dependencies`. No example
advertises condition_or_update as a presently permissible operation.

## G. Repaired examples and exact local deductions

MA01 preserves an unweighted continuous domain and rejects branch counting as
a law. MA02 uses one three-atom family and separately identified valid,
negative-mass, non-unit and duplicate-ID submissions. MA03 evaluates the valid
law with masses 1/2, 1/3, 1/6: for A={a,b} and B={b,c}, P(A)=5/6,
P(B)=1/2, P(A intersection B)=1/3, hence P(A union B)=5/6+1/2-1/3=1.
A partition omitting c fails even though its listed cells are disjoint.

MA04a retains Bernoulli marginals without inventing a coupling. MA04c and MA04d
use the same four assignments (0,0), (0,1), (1,0), (1,1). The first law places
1/2 on each diagonal assignment and explicit zeros elsewhere; the second puts
1/2 on each off-diagonal assignment and zeros on the diagonal. Summing over Y
or X gives the same Bernoulli(1/2) marginals under each law. Summing the diagonal
masses gives P(X=Y)=1 and 0. Thus these marginals cannot determine that event.
These are local finite-sum deductions, not claims from an external source.

MA04b has its own two-outcome family and law: (A,1) and (B,1), each mass 1/2.
The explicit rate projection sums both preimages to mass 1 while preserving
both elementary IDs. This law never reuses the three-atom model identity.
MA05 rejects changed family/support and changed purpose, and retains a stale
model request without migrating it. MA06 uses distinct compatible continuous
and mixed domains/models. Both preserve their symbolic expressions and missing
mathematical/evaluator obligations, with null numerical probability.

The finite fixture convention is exact rational arithmetic, not a proposed
restriction on all real implementations. The local diagnostic recomputes from
inputs, checks identity/reference/domain compatibility, and compares specified
outputs. It is an author consistency check, not an engine or prose acceptance
test. Comprehensive failure coverage, matched alternatives and uncertainty
integration remain open; independent substantive review is pending.
