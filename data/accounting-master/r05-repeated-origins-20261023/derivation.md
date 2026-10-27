# Fixed companies retain serial and cross-company forecast uncertainty

This local deduction assumes fixed company identities and deterministic
weights chosen before test outcomes. It does not select those weights, an
origin calendar or a future-data law. Let d_it be candidate-minus-comparator
loss for company i at protocol origin t, with identical target/information
and score definitions for the pair. The index t must refer to a declared
grouping of actual origins; fiscal-year labels alone do not define one.

Write g_t=sum_i w_i d_it and D=sum_t a_t g_t, with nonnegative weights summing
to one at each level. Assume the required conditional second moments exist
under a stated law Q for future outcomes, information and fitting. Conditioning
fixes the panel and any design quantities declared fixed under that law.
Expanding the centered sums gives

    E_Q[D] = sum_t a_t sum_i w_i E_Q[d_it],

    Var_Q(D) = sum_t sum_s a_t a_s Gamma_ts,
    Gamma_ts = sum_i sum_j w_i w_j Cov_Q(d_it,d_js).                 (1)

Equation (1) follows from linearity of expectation applied to the finite
double product. No stationarity or cell independence is needed. Treating g_t
as a scalar process retains cross-company covariance in Gamma_ts; it does not
make those covariances vanish. If the company weights or eligibility depend on
observed losses, this fixed-weight derivation no longer supplies the claimed
formula without including that randomness.

The expectation in (1) is a weighted mean of the expectations at those origins.
The selected future-origin target Delta_Q need not equal it. A justification
relating historical and future origins is a separate assumption or result.
Even if equality is justified, (1) does not yield a central limit theorem,
confidence interval or valid resampling method. Those require their own
conditions. CRPS finite first-moment conditions do not alone guarantee the
second moments assumed here for paired losses.

To expose the effect of fixing company means, consider the explicitly fictional
model with n fixed companies and K origins,

    d_it = mu_i + V_t + e_it.

The mu_i are fixed constants in this illustration. V_t and e_it are mutually
independent symmetric signs with mean zero and variance one. They are new
future shocks, not sampled company identities. With equal origin weights,

    g_t = sum_i w_i mu_i + V_t + sum_i w_i e_it,
    E[D] = sum_i w_i mu_i,
    Var(D) = [1 + sum_i w_i^2] / K.                                (2)

Independence across t is an explicit property of this example only. The shared
V_t gives cross-company covariance one at the same origin. With equal company
weights equation (2) is 1/K + 1/(nK). Falsely treating all cells as independent
would use 2/(nK). For the earlier illustrative n=9,K=8 these values are 5/36
and 1/36. The factor five is fictional, not an estimated effective sample size.

The older synthetic model also sampled a permanent U_i with variance one.
That model's 1/n term was correct under its stated unconditional law. In the
present example the company effects are fixed, so there is no such sampling
term. This does not imply that parameter estimation, time-varying company
shocks or uncertainty about company means disappear in an actual study.
If Q includes them, their covariance contributions must be retained. The two
models answer different conditional questions; the earlier derivation is not
being retracted.

For a complete finite check set n=2,K=2, mu=(1,3). Six independent signs
(V_1,V_2,e_11,e_12,e_21,e_22) give 64 equally likely fictional worlds. Equal
company weights yield mean 2 and variance 3/4. Weights (1/4,3/4) yield mean
5/2 and variance 13/16. The wrongly independent-cell variance is respectively
1/2 and 5/8. These expectations are supplied before enumeration. The unequal
weights change both the objective and variance; they are not preferred weights.

Serial dependence is separate. For two origins let g_1=Z_0+Z_1 and
g_2=Z_1+Z_2, where the three Z values are independent symmetric signs.
Then Var(g_1)=Var(g_2)=2 and Cov(g_1,g_2)=1. The equal-origin mean has

    Var((g_1+g_2)/2) = (2+2+2)/4 = 3/2.                           (3)

The false independent-origin variance is one. Direct enumeration of eight
worlds verifies (3). This example models a possible shared-shock mechanism;
it does not derive a block length, lag cutoff or law for the named companies.

The practical consequence is narrow: fix the chosen issuer population and
declare the future-origin law before selecting uncertainty theory. Aggregate
under predeclared substantive weights when appropriate, retain all covariance
mechanisms, and preserve failed/missing cells. Neither a source-file count nor
these exact illustrations provides a forecast-performance bound.
