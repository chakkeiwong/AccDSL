# Forecasts retain their eligibility, timing and failure history

This proposed documentary contract refines the records in the 18 October E3
specification for the user's selected fixed-company, future-origin question.
It supplies no production schema, forecast runner or empirical admission.
Forecast period and company-weight preferences remain unanswered. The rules
below work with any subsequently admitted target and weighting objective.

## Identity and ordering

An eligibility row identifies the protocol version, named issuer, target
concept, actual flow interval or stock date, perimeter/basis/currency versions,
information cutoff, origin grouping and original weight rule. Freeze eligibility
and its exclusions before model success or test losses are inspected. A rule
may be scheduled before future data exist; admission of the resulting rows
requires a reproducible, outcome-independent application of that rule.
An unsupported input, failed forecast, missing scale or missing outcome stays
attached to its eligible row. A discovered protocol error requires an explicit
invalidated version and successor design; it cannot silently delete the row.

Keep protocol lock, model/refit lock, forecast creation, forecast lock, issue
deadline and outcome release distinct. The information cutoff defines permitted
information, while creation and lock say when an actual prediction existed.
The deadline is an operational policy choice, not automatically the cutoff or
target start. Prediction bytes, law/set status, scenario/economic assumptions,
training rows, feature/scale dependencies and candidate/comparator identities
must be bound to the forecast lock. A hash calculated today proves no earlier
existence. Earlier existence and scope of exposure require retained dated
evidence with its own reliability assessment.

Use conservative interval comparisons when timestamps have limited precision.
For closed time bounds A=[a_l,a_u], B=[b_l,b_u], A<=B is established if
a_u<=b_l, contradicted if a_l>b_u, and otherwise unverified. For A<B, use
a_u<b_l and a_l>=b_u respectively. Null or inadequately supported evidence is
unverified. Contradiction and lack of evidence both prevent timing admission;
only the former proves that the stated ordering was violated. Bounds use a
common timezone/time convention and must be finite and ordered.

For the proposed prospective chronology screen require:

1. Every predictor and training-label availability precedes or equals the
   information cutoff. Derived inputs inherit every upstream availability
   requirement. A publication day for another version is insufficient.
2. The cutoff precedes or equals forecast creation; creation precedes or
   equals lock; lock precedes or equals the predeclared issue deadline.
3. Forecast lock strictly precedes the earliest supported public availability
   of the specified target outcome. Equal timestamps do not establish this.

These are necessary ordering checks on supplied evidence. They do not prove
absence of private knowledge, complete provenance, correct accounting mappings
or an untouched test. Preserve exposure separately as declared and verified,
known exposed, or unverified. A reconstruction created after outcome release
may still have a correctly computed retrospective score; it gains no
prospective status. A partly elapsed target is labelled as such even when its
first public outcome release is later. A new outcome-release discovery can
invalidate a prior timing assessment without changing the old forecast bytes.

## Orthogonal statuses

| Axis | Meaning and separate record |
| --- | --- |
| Eligibility | Included under the locked rule, or excluded with a pre-outcome reason. Preserve the complete included set and original weights. |
| Chronology | Supported, contradicted, or unverified, with every individual timing predicate and evidence reference retained. |
| Exposure | Separately reviewed exposure status; a timing pass alone cannot establish an untouched evaluation. |
| Candidate attempt | Complete admitted law, unweighted set, incomplete law, refused/unsupported, numerical failure, or not attempted. Retain all attempts and unresolved mass. |
| Comparator attempt | The same fields for the locked comparator; its failure cannot erase candidate failure or change the comparator after outcomes. |
| Outcome | Admitted first release, not yet observed, disputed/unknown, or sensitivity-only later version. Record exact target/version, evidence and derivation. |
| Scale | Admitted positive as-of assets, missing, nonpositive, unverified or available too late. Both arms use the same amount. |
| Score | Per-arm raw and scaled status; paired status and reasons; exact/approximate method and numerical error. Domain validity and evaluation-design eligibility are separate. |
| Service policy | Original attempt and any prospectively declared fallback activation; compare the defined combined service separately from the original model. |

Store sets of reasons rather than one overriding error. If a candidate fails
numerically and the outcome is missing, both facts remain. Raw scoring can be
possible when scaling is not. A mathematically defined score on a late or
exposed forecast remains a retrospective/development calculation; it is not a
valid prospective comparison. A valid candidate law cannot be paired when the
locked comparator is unavailable. An unweighted set remains eligible for its
separate inclusion/width protocol and does not receive a probability score.

Completeness, finite first moments and joint-law validity need substantive
support. Labels alone establish none of them. The examples use point laws
so their CRPS is exactly absolute error; no fitted law is asserted to pass.
The secondary energy-score task separately requires a joint cash/debt law,
common target identity and fixed component scales; passing scalar examples
does not admit that vector task.

## Outcome revisions and retries

Lock the policy of first-release evaluation before test outcomes; the identity
and hash of future outcome bytes are recorded only when they become available.
First release refers to the specified target, not the earliest convenient file.
Keep revisions of the evidence assessment append-only, with the earlier
assessment, reason and changed evidence. A later restatement is a distinct
sensitivity branch. It cannot overwrite the primary first-release value.
If earlier release evidence is discovered, invalidate the former first-release
assessment explicitly and recompute under a versioned analysis; do not retain
a false label just to preserve an old result.

For result ingestion, a stable event identifier plus identical payload is an
idempotent retry. The same identifier with different bytes is a conflict, not
an overwrite. A correction requires a new event linked to the earlier event
and review; the materialized analysis selects one stated revision per eligible
cell. Neither multiple attempts nor duplicate ingestion multiplies its weight.
A snapshot retains all eligible IDs, including unavailable cells. Changing a
target, origin, model lock or comparator requires a new analysis identity.
The finite replay illustration checks only this bookkeeping, not durable
storage, concurrency, timestamp authentication or tamper resistance.

A fallback is part of a service only if its trigger, information access,
model and version were declared before the affected outcomes. Score the actual
locked fallback forecast, retain the original failure and fallback usage, and
name the service explicitly. The right to attempt an alternative after failure
does not make an after-outcome forecast prospective. No fallback model,
penalty or missingness assumption is selected in this proposal.

## Denominators and what the sums mean

For a finite eligible set E, let a_c>=0 be deterministic original weights with
sum_E a_c=1. This is symbolic notation, not the pending actual-company choice.
For a separately labelled scorable subset A, define

    W_A = sum_(c in A) a_c,
    S_A = sum_(c in A) a_c d_c,
    D_A = S_A/W_A, when W_A>0.

Always report the eligible count, scorable count and W_A. When A is empty,
the conditional mean is unavailable. S_A is the contribution of observed
cells under the original weights; it is not the full effect D_E. If all
remaining positive-weight losses are defined and observed,
D_E=S_A+sum_(c outside A, a_c>0) a_c d_c. A predeclared zero-weight cell
contributes zero by definition of this weighted target, even if its loss is
undefined; retain its eligibility and failure/veto records. This makes no
performance claim for excluded-weight cells and permits no post-result
reweighting.
Otherwise D_E stays unavailable. When a forecasting algorithm has supplied
no law, its CRPS is undefined rather than an unobserved numeric value; a
full-service definition is needed before any missing-score model is coherent.

The same problem remains in the future-origin target. With scorable indicator
R and an integrable, otherwise well-defined difference d,

    E[d] = P(R=1)E[d|R=1] + P(R=0)E[d|R=0]

when both conditional events have positive probability (zero-probability
terms are omitted). This follows by partitioning the expectation. Observing
coverage and the first conditional mean does not identify the second term.
No missing-at-random assumption, numeric penalty or finite CRPS loss bound
is supplied. Conditioning on model success can therefore change the target.
More source files do not identify the missing part.

Do not recompute equal-company or exposure weights on the surviving rows and
call them the original weights. If an A-only descriptive table is useful,
its normalization and population are explicit. Also report per-company,
origin, critical-stratum and failure counts. The fixed-panel process g_t
is unavailable for an origin if its positive-weight required losses are
undefined, absent an admitted service/missingness rule. Dropping that origin
conditions on success rather than automatically preserving the selected Q.

## Expected fictional examples

Six cells have illustrative weights (1/4,1/4,1/8,1/8,1/8,1/8). They are not
the nine-company weights. Each complete arm uses point predictions10 and11
for outcome10. Raw differences are -1; with assets10 the scaled difference
is -1/10. A has full supplied timing/exposure evidence. B has incomplete
candidate mass. C has both candidate numerical failure and no outcome.
D has missing scale. E locks after the outcome release. F has unknown input
availability. All six remain eligible.

Raw score-domain coverage is A,D,E,F: count4, weight5/8, contribution-5/8,
conditional mean-1. Scaled score-domain coverage is A,E,F: count3, weight1/2,
contribution-1/20, conditional mean-1/10. Supplied prospective chronology and
exposure support only A among scaled pairs: count1, weight1/4,
contribution-1/40, conditional mean-1/10. These last checks still do not admit
an actual experiment. The full eligible effect remains unavailable in all
three tables. The same conditional means across subsets do not repair missing
service coverage.

Timing examples cover exact and uncertain inclusive cutoffs; definitely late
and overlapping availability; strict lock before release; equality, overlap,
unknown bounds and invalid intervals. The first-release illustration has
outcome10 and a later sensitivity value12: differences-1 and+1 respectively.
Changing which one is primary changes the answer, so the version stays explicit.
Repeated identical events count once; a conflicting retry is refused. Omitted,
extra or duplicate eligibility rows, incomplete-law zero-filling, a replaced
first-release version and nonpositive scale acceptance are rejected controls.

Two aggregation boundaries are also prescribed. If no candidate is attempted,
all three conditional means and full effects are unavailable. If A alone has
predeclared weight1 and all others weight0, the raw effect is-1 and the scaled
effect is-1/10 with all six eligibility rows and other failures retained. Those
weights are a separate illustrative objective, never a repair for observed
missingness or a selection of the pending actual-company weights.

The claimed result is a precise proposed record/aggregation contract and exact
finite examples. Actual source availability, exposures, target mappings,
complete forecast laws, weights, future law, confidence, margin and empirical
execution remain unadmitted. No human or independent acceptance is inferred.
