# Continuous uncertainty, information and contractual guards

26 October 2026. W04; MC11/26/28/33/34, G16, P17-08.04 and L01.

## Research intent and scope

Can a small exact representation share computations across continuous rate
families while preserving observations, contractual eligibility, feasible
policies, journals and cash bounds? The comparator is an independently written
enumeration of every discrete mode and every point/open interval of a known
one-dimensional piecewise-affine model. It is not a finite random grid.

Use the existing chapter 17 coupon example: face100, one year, zero spread,
floor3%, cap6%, rate in [2%,8%], and a strict liquidity trigger at interest5.5.
Add an alternative fixed coupon5 and an independently specified committed or
unavailable facility. Both alternatives can match the earlier interest5 and
debt100 reports. They are synthetic admissible premises, not inferred company
facts. All four discrete alternatives and the entire rate interval remain.
Opening cash is5.5, other assets94.5, old debt100, equity0. Interest is accrued
before the decision, reducing equity and creating interest payable. Refused
payment preserves this payable, the accrual journal and the due-claim memory;
it cannot make the obligation disappear. This is a supplied accounting example.

At one decision date the actor chooses pay or draw. Pay is feasible iff cash
covers interest. Draw borrows1, pays a fee0.25 and then interest; this stipulated
facility may be drawn only when committed and interest strictly exceeds5.5.
Draw also requires nonnegative ending cash. Actions are indivisible orders,
not contingent programs. A coarse observation reveals only rate<=4%; a refined
observation additionally reveals whether the liquidity trigger has occurred.
The signal is available before the order. Neither mode nor hidden facility
rights may be used by a policy unless explicitly added to its observation.
No probability is supplied; feasibility is required throughout the retained
family. A family with unavailable facilities can have no feasible total policy.

## Sequence and evidence contract

1. Implement exact rational affine expressions and disjoint point/open cells,
   splitting at coupon knots, observation changes and action-guard roots.
   Share equal calculation nodes but retain every original mode/cell identity.
2. Compare complete symbolic transitions with a separately authored closed-form
   oracle on a common refinement. Equality of affine coefficients throughout
   each cell, plus exact guard classification, is the primary criterion.
   Compare all journals, balances, claims, observations and refusal states.
3. Enumerate observation-measurable policies and compare feasible sets. The
   committed-only family with the refined signal must admit pay-before-trigger/
   draw-after-trigger; the coarse signal must not acquire hidden information.
4. Check limited budgets preserve every unresolved region and valid outer
   bounds. Derive and test guard/observation error margins; never infer a
   uniform bound from samples. Test scope invalidation and counterexamples.
5. Save results, derivations, manifests and remaining work. Refresh the master
   and full gap records, preserving concurrent funding and frozen predecessors.
   Integrate the explanation in a protected manuscript successor if the active
   manuscript is stable; otherwise leave an explicit integration task.

Promotion is only to a checked bounded reference, not production or whole-W04
closure. A different affine coefficient, boundary inclusion, feasible action,
observation partition, journal, joint identity or missing region vetoes it.
Controls must discriminate rights erasure, clairvoyant policies, threshold
rounding, marginal dependency loss, stale scope and budget truncation. Counts,
runtime, node sharing and page count are explanatory, not acceptance criteria.

Continuation vetoes are corrupted predecessors, changing live pointers during
promotion, invalid exact arithmetic or a comparator that shares the defect.
Ordinary candidate failures trigger a preserved attempt and targeted repair.
Do not rerun successful one-shot writers. At most three execution attempts,
each with a 120-second CPU budget; no installation, GPU, stochastic sweep,
external worker, publication or professional engagement.

## Defaults and skeptical review

Rational arithmetic is the chapter's proposed bounded profile; it avoids
rounding at strict guards but does not implement monetary quantisation. The
one-rate, one-date model is a deliberately small scope, not evidence that
general continuous company states are tractable. Fixed-rate and facility
alternatives are hypotheses; infeasible families and unknown regions are
valid answers. Explicit roots are the oracle baseline; point sampling alone
would miss intervals and is rejected as a proof method.

The first proposed comparison risked treating equal coupon values as equal
states and allowing a policy to inspect the hidden right. Revised plan: retain
mode/right identities, compare complete states, and intersect feasible actions
over each actual observation class. Adding contingent orders changes the
policy class and invalidates the cache; no universal policy-equivalence claim
is made. Open-cell extrema can be unattained and must retain this distinction.

Audit passes for this revised bounded question: the comparator covers the full
interval analytically, failure controls target information and rights as well
as amounts, stopping conditions are explicit, and no timing/capacity/default
claim is based on a smoke test. Exact local derivations support the new claims;
the existing literature dossier remains the source for broader theory.

Artifacts: data/accounting-master/continuous-guards-20261026/. CPU only with
CUDA_VISIBLE_DEVICES=-1; standard Python, no ML imports. Record actual command,
git commit, source hashes, environment and wall time. Preserve the accepted
dated-funding attempt and all existing manuscript editions.

Reader-facing treatment: accounting/risk researchers familiar with affine
functions should reconstruct the payment choice, guard split, information
restriction and exactness proof in order. Use the scholarly narrative and
natural analytical prose skills; retain all premises and mathematical steps.
Human comprehension remains pending and does not stop provisional drafting.
