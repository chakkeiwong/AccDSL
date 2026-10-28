# Numerical targets and claims: SIM-F056/057/058/059/060

28 October 2026. C04; MC09/11/13/14/18/28/33/34.

Question: does the numerical calculation answer its declared objective,
constraint, dependency and solution-scope question? Baselines are the original
rows and simulation/11-numerics.tex and26-finite-finance.tex. This is exact
finite arithmetic and counterexample verification, not neural training or an
equilibrium performance benchmark.

Skeptical audit: single-draw squared residual adds a parameter-dependent
variance; independence is required for the two-draw product. An interior
derivative is not a constrained optimum condition. A detached policy omits
part of a total derivative. A positive extrapolated tail slope changes the
funding model. One successful local root is not uniqueness or economic
selection. Existing F029 evidence already checks the same positive-tail
counterexample required by F059; verify its source hashes and reuse it instead
of presenting a duplicate benchmark as additional independent evidence.

F056 explicitly supplies epsilon=+1/-1 with equal mass, a convenient finite
realization of the chapter's zero-mean/unit-variance premise. Enumerate single,
same-draw and independent two-draw expectations. Compare with the separately
expanded polynomials and their exact minimizers1 and1/2. Negative individual
two-draw products do not invalidate the expectation identity.

F057 verifies f(a)=(a+1)^2 on a>=0: optimum0, derivative2 and multiplier2;
interior root-1 is infeasible. Algebra f(a)-f(0)=a(a+2) proves the global
comparison on this domain; check a counterexample formula with direct Z3.
This convex polynomial example does not validate clipping or general KKT
sufficiency for nonconvex company problems.

F058 adds the explicitly local affine policy pi(a)=2-a and price P(a,pi)=a*pi
on[0,2] to instantiate the source's chain-rule failure. Full derivative2-2a
differs from partial2-a. Exact central differences at interior rational points
independently check the full derivative; partial dependence is also checked
with pi frozen. The equation pi+a-2=0 has policy Jacobian1. No actual lender
or equilibrium policy is calibrated or claimed.

F059 reads and hash-verifies the retained pricing-policy attempt01 and its
whole-domain records: true capacity100; false tail100+(F-140)/1000 invents
need110 root10140. Recompute original two-asset payoffs and shortfall10.
An invented affine tail is an explicit surrogate mutation, not a trained net.

F060 uses an openly supplied polynomial (u-1)(u-3)=0 as a branch discriminator.
Exact algebra/direct Z3 verifies both roots and excludes any third root. A
fixed eight-step Newton diagnostic from0 and4 approaches different roots;
residual and distance checks classify those local outputs, while initialization2
has zero derivative and remains unresolved. No numerical failure can erase the
two established solutions or select one as an economic equilibrium.

Primary pass is agreement with independent algebra, explicit full-domain
counterexample queries and specific negative-control behavior. Z3 is used
directly for these small polynomial identities, not advertised as an expanded
rational_solver_v1 fragment. Per-query timeout10seconds is a convenience cap;
Unknown is a promotion veto and repair trigger. Incorrect target or discarded
solution invalidates the affected candidate, not the research direction.
Corrupted preserved inputs or invalid harness stops the unit until repair.
Counts, timing and Newton residuals explain scope; no stochastic ranking occurs.

Premortem: a passing symbolic example can be mistaken for economic model
validity or general convergence. Preserve all premises and non-claims. Record
source hashes, exact commands/environment, formulas, outputs and manifests in
company-state-numerical-targets-20261028/attempt-01. Run CPU-only python3 -B.
All original statuses and frozen releases remain; no default changes, forecast
claims, native accounting admission or broad requirement closure follow.
