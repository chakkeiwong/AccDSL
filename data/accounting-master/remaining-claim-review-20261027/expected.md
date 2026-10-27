# Independent expected calculations before execution

These are exact authored examples, not estimates for an issuer. Fractions are
used throughout; no stochastic sampling, solver, old writer or framework runs.
The new verifier reads retained results and calculates the following quantities
independently. Generic algebra below establishes the claims; finite checks
detect transcription and implementation errors in the displayed examples.

## C06 and C_PMMCMC_AUX

Set intersection narrows the same historical scope. Replacing a constraint
requires reconstruction from active premises, not intersection with the old
restriction. For equal prior weights, old likelihood (1,0) gives (1,0); replacing
it with (1/4,3/4) gives (1/4,3/4). Multiplication into the old posterior remains
(1,0). The new law is not absolutely continuous with respect to that posterior.

For a fixed type with probability p and likelihood ratio four, posterior
4p/(1+3p) is increasing since its derivative is 4/(1+3p)^2. Prior bounds
[1/4,3/4] give [4/7,12/13]. This is not independent choice of each period's
marginal. Under independent multinomial sampling the probability of losing
a type of weight 1/100 in 100 draws is (99/100)^100, strictly greater than 1/3.
No inference about other resampling schemes follows.

For the retained-estimate example the three joint states are
(0,1/2),(0,3/2),(1,1). Equal type priors and auxiliary masses (1/2,1/2;1)
produce target (1/8,3/8,1/2). Proposing the other type gives transition
[[0,0,1],[0,1/3,2/3],[1/4,1/2,1/4]]. Detailed balance holds. Refreshing both
estimates changes type switching rates to 5/6 and 3/4, giving stationary
type-one probability (5/6)/(5/6+3/4)=10/19 and bias 1/38.

For the representation-exchange example, the new auxiliary values are
(1/4,7/4;1). The correct joint law is (1/16,7/16,1/2). Unweighted refresh
gives (1/4,1/4,1/2). The correct PMMH kernel is
[[0,0,1],[0,3/7,4/7],[1/8,1/2,3/8]]. It preserves the correct law, but takes
the wrong law to type-one mass 65/112, a one-step discrepancy of 9/112.
This is not stationary bias of that valid kernel. Weighting each exchange by
Z_new/Z_old cancels the old likelihood tilt and gives the desired new joint
law after marginalizing the old auxiliary variable. Estimates here are positive.

## C07, C09 and C17

With face100, solvent probability9/10, recovery40 and gross discount21/20,
expected payoff is94, proceeds1880/21 and yield11/94. The inconsistent printed
equation gives yield11/90 and proceeds9000/101. Payoff minus accumulated
proceeds is44/101. The old opposite residual is -44/101; neither sign is an
arithmetic discrepancy.

For estate70 and senior/junior faces60/50, strict priority pays60 and10.
Paying70% of both faces pays77 and exceeds the estate. For homogeneous shares,
100 old shares plus20 at price10 and no fee changes value1000 to1200 while
preserving old value1000. Price8 changes total value to1160, old value to2900/3,
and new value to580/3; cash160 plus transferred value100/3 equals new value.
Conversion of face100 into10 shares extinguishes that obligation and creates
10 shares; no principal cash payment is authorized by these stipulated terms.
These identities do not admit an accounting treatment or a legal priority rule.

The combined path starts cash16. Coupon5/7 and operating payment6 leave5/3.
A pre-financing covenant of5 admits borrowing only in the first path. Maximum
face5 with solvency4/5 and recovery2 has expected payoff22/5 and proceeds88/21.
At a fixed per-face quote88/105, face315/88 raises3. In the other path the
required net equity5 plus fee1 gives gross6. Fair subscription into post-issue
value25 gives new fraction6/25, old value19, price19/100 and new shares600/19.
Both closing cash balances are8; the debt and ownership states differ.
The already reviewed typed runtime has final balances112/103/9 and112/100/12.
This check adds no new runtime acceptance or equilibrium claim.

## C10, C11 and C12

Equal priors and disclosure probabilities9/10 versus1/10 yield good-type
posterior9/10 after disclosure and1/10 after silence. Missingness can be
ignored in the stated factorization only under the source's specified
likelihood/parameter/prior conditions and positive normalization.

With uniform value and independent probability1/2 of knowing it, silence at
cutoff a has mass(1+a)/2 and unnormalized value(1+a^2)/4. Indifference gives
a^2+2a-1=0. The polynomial is strictly increasing on[0,1], changes sign at
rational bounds4142/10000 and4143/10000, and has the unique root sqrt(2)-1.
Below that root silence pays more; above it truthful disclosure pays more.
This local example is distinct from Suijs's conditional reverse-selection result.

For a fair binary U, models(X=U,Y=U) and(X=U,Y=X) both put mass1/2 at
(0,0) and(1,1). Setting X=1 leaves Y=U in the first, mean1/2, and forces
Y=1 in the second, mean1. No observed joint distribution distinguishes them.

## C13, C14, C15 and C16

C13 is a source/implementation-boundary claim. Read-only checks bind the
historical spec and dictionary, selected service code and24 retained fixture
rows. No runtime result is expected or generated. A file ending .json that
contains a retained404 response is not a dictionary or successful metadata.

For r(theta,e)=theta-1+theta e with fair e in{-1,1}, E[r]=theta-1 and
E[r^2]=(theta-1)^2+theta^2. Their minima occur at1 and1/2 respectively;
the second objective equals2(theta-1/2)^2+1/2. Independent paired draws
give E[r(e1)r(e2)]=(theta-1)^2. As a local derivative check, choose P(a,p)=a p,
p(a)=a: the total derivative is2a, whereas holding p fixed gives a. At a=2
the values are4 and2. These are not accusations about an uninspected code path.

For a Bernoulli outcome with true probability q, expected squared probability
loss is q(1-p)^2+(1-q)p^2=(p-q)^2+q(1-q). Thus p=q uniquely minimizes expected
loss. This exemplifies proper scoring; it is not empirical calibration or an
executed forecast study. Vintage correctness and policy comparability remain
protocol requirements. E3 stays deferred.

For C16, under each fixed-type law Q_i a fair independent signal X matches
theta with probability1/2. Selecting theta=X after observing X gives loss1.
No convex mixture of Q_0,Q_1 gives that joint law: each has uniform X
independent of theta, so every mixture still has matching probability1/2.

Conditional expected shortfall at level1/2 on uniform losses(0,1,2) is
(1/3*2+1/6*1)/(1/2)=5/3. Equivalently minimize t+2E[(Z-t)_+] at the three
breakpoints; the minimum is5/3. The six-state envelope has masses bounded by1/3.
The vector(0,0,1/6,5/18,5/18,5/18) is feasible; conditioning on its first
three states concentrates at loss2. Since2 is that group's maximum, the
conditional envelope supremum is exactly2. This changes the conditional risk
definition, not merely a numerical approximation.
