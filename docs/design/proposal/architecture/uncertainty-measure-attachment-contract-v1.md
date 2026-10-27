# Joint-measure attachment and event identity v1

This document specifies the next bounded part of the P16 uncertainty contract.
It attaches a declared joint measure to an already versioned history family and
evaluates events against that one measure. It does not select a measure from
data, infer independence, condition on observations, update likelihoods, run a
solver, or produce financial statements. The examples are synthetic design
fixtures; they establish no probability for an actual company and no
accounting permission.

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
   malformed representation, not extra mass. A zero-mass outcome may be
   retained only when the support contract says it is part of the declared
   space.
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

Two credible representations receive the same fixtures:

* **Family-linked record (provisional choice).** The attachment stores the exact
  family/view and references the model record. Revisions and invalidation are
  straightforward, and a reader can trace a probability back to the joint
  history family. Portability requires a stable family identity service.
* **Self-contained joint-model record.** The attachment carries a complete
  joint model and an explicit projection to a family. It is easier to export,
  but duplicated family definitions can drift and a correction must reconcile
  two version graphs.

The family-linked design is proposed for the initial profile because preserving
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
| Family-linked identity | Preserves revisions and dependency closure. | Export/import may lack family registry. | Version-mismatch and changed-support fixtures. | Provisional profile choice |

All fixture outputs are specified behavior only. They do not show that a
runtime, accounting treatment, company probability or forecast is correct.
