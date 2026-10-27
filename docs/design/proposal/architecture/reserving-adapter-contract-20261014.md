# Reserving adapter: proposed evidence-preserving exchange

14 October 2026. P17-10; optional specification supplement. Existing
OperationRequest/OperationResult and portable identity rules remain unchanged.
This adds an optional signature, reserving.evaluate@1, only to its declared
documentary profile. No runtime endpoint, R installation or distribution is
provided.

## Decision on the inspected native candidate

The audit baseline is mages/ChainLadder source commit
5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728, DESCRIPTION0.2.17 dated
2023-01-09. These identify retained bytes, not the latest release.
R/BootstrapReserve.R, BootChainLadder lines5–155, sampleResiduals/randomClaims
and rpois.od around409–447 were inspected. The static routine takes cumulative
Triangle, R, process.distr and seed, returning simulated pasts, process
triangles/totals, fitted-mean distributions and one-year arrays.

The source requires equal row/column counts although its error message and
help describe a broader rectangular case. The first proposed adapter profile
therefore supports square triangles only; broader shapes are unsupported until
a different inspected method is named. Its mask identifies every observed,
future and out-of-profile cell independently of an NA value.

The source replaces all NA process values by0 before aggregation and returns
no corresponding failure mask. A returned0 can therefore mean a valid zero,
a structural placeholder or a failed draw converted to zero. Those three
states cannot be reconstructed from the final numeric array alone. Even a
complete input mask does not recover failures in future cells.
Unmodified native output is retained as raw evidence but is **unsupported**
for a complete AccDSL predictive result. A wrapper that merely inspects the
post-coercion arrays cannot repair this information loss.

A later instrumented implementation could preserve cell status and RNG
provenance before coercion. Such an implementation needs a new source digest,
dependency lock and method identity; it is not the inspected unmodified
package. Its values must be checked against the intended method. This
document supplies authored fixtures for that boundary, not an implementation.
No actual code fork or correctness/performance comparison is claimed.

The returned ParamDist.ByOrigin contains fitted conditional means and
IBNR.ByOrigin/IBNR.Triangles/IBNR.Totals contain process outcomes after
coercion. Never substitute the former for the latter. NYCost outputs are
outside this lifetime profile: a separate one-year contract must specify
payments, closing re-estimation, information cutoff and center.

## Law and source identity

The process-law record names algorithm, support, parameters and units.
For positive mean m and dispersion phi:

| Native selection | Inspected mathematical law | Profile consequence |
|---|---|---|
| gamma | Gamma(shape=m/phi,scale=phi) with sign/absolute-value handling in native code | Optional positive m,phi law; signed handling excluded from this profile |
| od.pois,phi=1 | Poisson(lambda=m) | Nonnegative integers in the declared base payment unit |
| od.pois,phi>1 | NegativeBinomial(mu=m,size=m/(phi−1)) | Nonnegative integers; differs from phi*Poisson(m/phi) |
| od.pois,0<phi<1 | Negative size in inspected helper | Unsupported by that helper; does not invalidate an explicitly specified gamma law |

Gamma and negative-binomial paths have equal mean/variance under appropriate
parameters, but different supports and tails. A scaled-Poisson request must
not be silently satisfied by the negative-binomial helper.
Rescaling a continuous monetary amount and choosing an integer payment unit
are different model choices. Zero process payment is valid for Poisson/
negative-binomial laws; an absent or failed draw is never a valid zero.
Unsupported zero/negative fitted mean or unidentified dispersion is diagnosed
before a complete process result. Do not infer positivity from observed
cumulative amounts alone.

DESCRIPTION's GPL(>=2) is retained as source evidence. Transitive R/package
versions, compiled dependencies, concrete license election, redistribution
and instrumented-fork terms are not cleared. Local documentary inspection
requires neither installing nor distributing the package. All remain explicit
preconditions to any later selected runtime or distribution.

The native routine reinitializes its seed for residual sampling and process
generation. Record that behavior under its own RNG-policy identity. Do not
describe it as independent streams. A proposed replacement must identify
the generator/version, stream derivation, residual/process labels, replicate
mapping and restart state; labels alone do not prove independence.
The present fixtures declare authored values and no RNG execution.

## Complete exchange

The supplied schemas in the dossier close every record body. Use the common
portable record wrapper, typed references, complete dependency closure and
schema-prefixed canonical SHA256. A separate schema lock retains the schemas
and this semantic contract as exact blobs. Diagnostic/status strings have
their own declared finite values in the supplied schema.

The operation is pure with respect to financial books and law admission.
Its arguments name the triangle, method/law lock, requested draw plan and
producer evidence. A real implementation would generate producer evidence;
the documentary profile consumes authored evidence to specify interpretation.
Common execution mode is specification_example and expected_head is null.
Returned candidate payments do not authorize journals, select a probability
measure or admit real-company data.

The triangle records entity/portfolio, currency/base unit/scale, valuation
date and information view; ordered origin/development labels and payment-date
mapping; exact observed cumulative amounts; and the explicit structural mask.
No missing observed amount is zero-filled. The method lock names native
snapshot or proposed instrumentation, model target, law parameters, support,
shared-fit rules, version and unexecuted environment/terms limitations.

The draw plan names the complete requested replicate IDs. Producer evidence
retains raw output bytes and the pre-coercion statuses, when available. For
each replicate it names the fit ID and one joint vector of future cells.
Each cell has location, fitted mean, process value or null, status and reason.
All cells of one replicate use its fit ID; fitted means and payments remain
different fields. Missing/duplicate cells, repeated draw IDs, mixed fits,
wrong currency/scale and a method/law mismatch reject the affected result.
Validated input with unsupported native evidence retains request_ref but
publishes no admissible predictive payload.

For instrumented documentary evidence, completed draws aggregate all expected
future cells in their specified payment periods. Any failed cell makes that
replicate's total null. Do not discard the replicate or replace its failed
cell with0. Retain successful cells for diagnosis and the failure with its
source location. A summary carries requested, attempted, completed, failed
and pending counts and each replicate outcome. A mean over the full requested
sample is null if any replicate is failed or pending.

A diagnostic mean over completed draws must be explicitly labeled as such.
It is not an unconditional prediction. Count fractions such as1/2 describe
execution coverage of planned draws, not known probability mass of economic
histories. Bootstrap draws do not create a defensible probability for solver
failure. Any finite bound for missing process values requires separately
supported bounds and is withheld by this profile.

The outer coverage domain is the requested set of computational draw IDs,
with disjoint completed, unresolved and cancelled regions. It is not the
company's economic-family domain. The result preserves separate structural,
mathematical, computational, empirical, accounting, forecast, product and
human statuses. Completed output means complete under the finite exchange
rules only; empirical/forecast validity remains not_assessed.

## Cancellation, identity and continuation

A stop request is not proof of termination. Confirmed cancellation preserves
completed draws and identifies unattempted draws as cancelled. An attempt
whose worker status is unknown returns partial with unresolved termination;
do not publish a complete result or start a competing resumed worker.
The current fixture has no durable checkpoint, so continuation_ref is null.
Later resume requires the existing P3 checkpoint transaction, semantic
manifest, original draw IDs and RNG state; a native routine without these
capabilities is unsupported for resume. Repeating native seed initialization
is not a checkpoint implementation.

Common request identity includes request_id, view, all arguments and execution
settings. Exact resubmission has the same content fingerprint; changing the
law, IDs, budget or request identifier changes it. A new scheduling request
may reference an unchanged semantic checkpoint only under P3, never by
silently changing the old request. This pure operation makes no accounting
commit; commit_observation is not_committed even if immutable diagnostic
records are retained. No storage durability claim follows from this fixture.

## Acceptance examples and remaining execution

Authored possible negative-binomial payments for three future cells are
(0,4,8) and (2,6,10); joint totals are12 and18, sample mean15. These are
chosen values for exchange checking, not fitted to the triangle or random
draws from an executed generator. If the first draw's last cell fails, its
total is null; the completed-only mean18 is diagnostic and the requested
sample mean is withheld. If cancellation leaves the first draw only,
diagnostic mean12 also cannot stand in for the missing full sample.

The decisive contrary case has future values (0,4,0). One pre-coercion
world contains a valid final0; another contains a failed final draw. The
native coercion maps both to the same array/total4. No post-hoc arithmetic
or hash can tell them apart. This information-loss result justifies the
unsupported disposition without running R.

Later runtime work must test the pinned implementation, actual numerical
generation, dependency/terms closure, pre-coercion capture, termination,
restart and checkpoint crash behavior before claiming compatibility.
The specification and 2.86's conditional-target safeguards remain independently
useful while those obligations are open.
