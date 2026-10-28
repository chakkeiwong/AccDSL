# Numerical correctness starts with the stated target

28 October 2026. C04; SIM-F056–060. Attempt01 passes138 checks, including11
direct polynomial SMT queries and verification of five retained pricing results.
No neural training, empirical probability estimation or solver promotion occurs.

For F056, the finite epsilon=±1 example reproduces the chapter's mean-zero,
unit-variance premise. The desired squared expected residual is(theta-1)^2,
uniquely minimized at1. Averaging the single-draw squared residual instead
gives2(theta-1/2)^2+1/2, minimized at1/2 with expected residual-1/2. Exact
independent two-draw enumeration recovers the intended objective; reusing a
draw recovers the wrong objective. Negative individual two-draw products are
possible and do not contradict the expectation identity.

For F057, f(a)=(a+1)^2 on a>=0 has the unique constrained optimum0. Its
derivative2 is balanced by multiplier2; complementary slackness holds.
The interior stationary point-1 violates feasibility. Algebra and direct SMT
exclude any feasible lower objective or positive action attaining the minimum.
These checks establish this convex polynomial case, not general clipping or
nonconvex KKT sufficiency.

For F058, the explicitly supplied policy pi(a)=2-a and price a*pi(a) produce
total derivative2-2a. Freezing the policy gives partial derivative2-a. Exact
central differences at three rational actions and three step sizes reproduce
both quantities under their respective dependencies. At a=1 the total derivative
is0 while the partial is1. The true price is maximized at1, and the partial-zero
boundary a=2 has price0. The local policy relation is a deliberate discriminator,
not a fitted lender response or an admitted economic equilibrium.

F059 reuses the already checked financing-tail counterexample. All29 source
hashes in that retained run match. Whole-domain records preserve capacity100
and no face can fund110 in the stipulated channel. The invented positive tail
100+(F-140)/1000 predicts110 at face10140, while the original two-asset payoff
still gives100 and leaves shortfall10. Five saved solver records are checked
and the state-payoff arithmetic recomputed. Reuse is evidence correspondence,
not another independent benchmark or a trained-surrogate experiment.

For F060, the supplied polynomial(u-1)(u-3)=0 has exactly two roots,1 and3.
Factorization and direct SMT exclude a third real root. Eight exact Newton
steps from0 and4 approach the different roots with small residuals. Starting
at2 encounters zero derivative and nonzero residual, so that attempt is
unresolved. Its failure does not erase the two exact solutions. Neither local
convergence nor the complete mathematical root set selects an economic branch.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F056 target mismatch | Exact expectations and unique minimizers agree | Same-draw objective differs | Real residual/conditional law | Match implemented expectation to declared target | A training loss proves economic equations |
| Retain F057 boundary case | Global polynomial comparison and KKT agree | Interior root infeasible | General constraints/nonconvexity | Preserve active-set and feasibility conditions | Universal KKT/clipping correctness |
| Retain F058 dependency case | Total and frozen differences match separate algebra | Detached derivative differs from total | Actual policy dependence and regularity | Retain dependency meaning | Actual equilibrium derivative calibrated |
| Reuse F059 capacity evidence | Original hashes, five solver results and payoff arithmetic agree | False tail leaves shortfall10 | Other funding channels and model applicability | Validate approximations under original payoff | Learned method evaluated or company insolvent |
| Retain F060 branch case | Exact two-root set and distinct local attempts | Zero derivative remains unresolved | Economic selection and broader root geometry | Preserve alternatives and local status | Newton globally converges or selects equilibrium |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Wrong objective, infeasible action, detached total-derivative claim, false funding and false uniqueness exposed |
| Statistically supported ranking | None; exact finite/polynomial diagnostics |
| Descriptive-only differences | Counts and local Newton residuals describe these cases |
| Default readiness | No numerical or model defaults change |
| Next evidence needed | Broader coupled services, admitted economic laws and independent validation |

Post-run red team: the strongest alternative explanation for any future
failure is a mismatch between this small model and the claimed economic target.
The local affine policy and two-root polynomial are explicit premises. They
establish counterexamples to unrestricted claims, not a general financing solver.
Continue unit/horizon/evaluation distinctions, source research and ordered
reading. E3 forecasting remains deferred; no global continuation veto fired.

Final verification passes all1,179 protected hashes, including997 frozen-release
files. The original task/acceptance populations and prior statuses persist.
