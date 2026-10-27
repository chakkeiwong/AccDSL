# Expected accuracy and a finite observed comparison

The selected research question concerns future dates for the fixed nine
companies. For issuer i at an eligible origin t, let Y be the reported
consolidated full-year OCF outcome and A the identical strictly positive,
as-of total-assets scale supplied to both arms. Candidate and comparator
predictive laws must describe that same target, currency and unit, with finite
first moments. Write

    d(i,t) = [CRPS(F_candidate(i,t), Y(i,t))
              - CRPS(F_comparator(i,t), Y(i,t))] / A(i,t).

Negative d means lower candidate loss. The fixed-interpretation comparator
must be locked without test-outcome selection and use the same permitted
information and economics. This comparison sits within the existing baseline
ladder; it does not waive the naive, runoff and tuned-classical comparisons.

For a joint future process Q governing origins, information, reporting,
outcomes, fitting and failures, define the expected target

    Delta = (1/9) sum_i E_Q[d(i,O_i)].

This expression requires integrability of the scaled differences. Finite
unscaled CRPS alone does not prove integrability if random as-of assets can
approach zero. The fixed company list selects neither Q nor stability across
future reporting or economic regimes. Linearity needs no independence across
companies. Their dependence still matters for inference.

For a finite planned collection E_i with nonnegative, predeclared rational
weights b(i,t) summing to one within each company, the realised estimator is

    D = (1/9) sum_i sum_(t in E_i) b(i,t) d(i,t).

Q, the sampling design and any transport assumptions must justify using D to
estimate Delta. This is not a definition making them equal. With deterministic
weights, finite second moments give

    Var(D) = (1/81) sum_(i,t) sum_(j,s)
                    b(i,t)b(j,s) Cov(d(i,t), d(j,s)).

This follows by expanding the variance of the finite linear combination.
Conditioning on random design weights instead requires the conditional
variance plus variance of the conditional mean. Common shocks, different
fiscal intervals, shared fits and serial dependence cannot be discarded by
calling the nine firms independent replicates.

The exact reference includes a two-world example: all nine differences are
-1 in one world and +1 in the other, each with probability one half. Delta
is zero, while the one-origin realised D is either -1 or +1. That complete
fictional law illustrates the distinction and supplies no evidence about Q
for the actual companies.

An undefined score with positive original weight leaves D unavailable. The
weighted sum of observed contributions and its covered weight remain useful
diagnostics; their quotient answers a conditional, survivor question. A
zero-weight cell contributes zero even when its score is undefined, and the
undefined score is still recorded. Origin weights cannot be changed after
failure to manufacture that exception. Every issuer retains one ninth; an
issuer with no eligible score cannot be silently removed.

For a complete finite law with rational atoms (x_k,p_k), the authored reference
evaluates

    CRPS(F,y) = sum_k p_k |x_k-y|
                - (1/2) sum_(k,l) p_k p_l |x_k-x_l|.

To recover the usual squared-CDF definition, write H_y(z)=1{y<=z} and
|x-y| as the integral of (1{x<=z}-H_y(z)) squared. Taking expectations gives
the integral of F(z)(1-F(z))+(F(z)-H_y(z)) squared. For independent X,X'
with law F, half of E|X-X'| is the integral of F(z)(1-F(z)); subtraction
leaves the CRPS integral of (F-H_y) squared. Finite support makes these
integrals finite. For a point mass the result is absolute error.
Scaling x and y by positive A divides both
absolute-distance terms by A, proving the common-scale equivalence in this
domain. An unweighted set supplies no p_k and is refused. The reference does
not restrict the wider proposed method to finite laws or invent probabilities
for history sets.

For the user's predictive-accuracy research purpose, the proposed directional
claim is Delta < 0, supported only by a justified uncertainty procedure with
an upper bound below zero and all validity checks satisfied. Zero is a
research equality boundary, not an economic threshold. A positive material
margin is a separate conditional claim and is not a prerequisite for this
internal research design. Confidence, multiplicity, sample size, future law,
service policy and inference remain unresolved. A negative realised D or a
passed arithmetic test establishes no future-performance ranking.
