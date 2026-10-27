# Paired panel loss: target and covariance

This is a project derivation, not an estimate from company outcomes. Let
d_it = L(candidate_it,y_it) − L(comparator_it,y_it), evaluated against the same
target, origin, information set and score. Fix weights a_it before test outcomes,
with sum a_it=1. For a declared repeated-sampling population, define
Delta_a = sum a_it E[d_it] and D_a = sum a_it d_it. Finite second moments give

    E[D_a] = Delta_a,
    Var(D_a) = sum_(it) sum_(js) a_it a_js Cov(d_it,d_js).

To derive the second identity, subtract E[D_a], distribute the product of the
two weighted sums and take expectations term by term. Row-independent variance
retains only identical-cell terms. Pairing removes neither serial covariance
nor cross-issuer covariance. Outcome-dependent weights would require a new
derivation. Without a defended repeated-sampling law, D_a is a weighted
description of the specified finite cells; this identity does not create a
population interval for it.

For a counterexample, take a complete n-by-T grid with equal weights and
d_it = mu + U_i + V_t + e_it. Let all U, V and e be mutually independent,
mean zero and variance one. Independent symmetric +/-1 variables suffice.
Then Cov(d_it,d_js)=1{i=j}+1{t=s}+1{i=j,t=s}. Summing the weighted covariances
or collecting coefficients of U, V and e gives

    Var(D_a) = 1/n + 1/T + 1/(nT).

The false independent-cell formula is 3/(nT). With illustrative n=9,T=8,
the true variance is 1/4 and the false value 1/24: a factor of six. These
72 synthetic cells are not a reinterpretation of the 192-report inventory.
The model illustrates a possible failure; it does not estimate actual firm
or calendar dependence. If a further common shock C has unit variance,
the true variance increases by one, whereas falsely treating it as a separate
independent shock in each cell adds only 1/(nT).

For arbitrary fixed weights the same example gives
sum_i(sum_t a_it)^2 + sum_t(sum_i a_it)^2 + sum_it a_it^2.
The checker compares this coefficient expression with the covariance double
sum and independently enumerates the 256 +/-1 assignments for a 2-by-2 case.
Those exact arithmetic checks verify the example, not a panel inference method.

E3 asks for a favorable paired effect beyond a justified margin m, with
candidate-minus-comparator orientation. A defensible one-sided upper bound U
would need U < -m, alongside all validity checks. Rejecting E[d]=0 two-sided
does not establish that condition: the effect could have the wrong sign or be
smaller than m. No m, confidence level, weighting or upper-bound procedure is
selected here. ForeComp's two-sided polynomial is not silently repurposed as
a one-sided panel confidence bound.

Missing outcomes also change the computed quantity. For the illustrative
differences (2, missing), the observed-cell mean is 2; replacing missing by zero
and dividing by two yields 1. Neither number identifies the unknown two-cell
mean without an additional missingness assumption. The example explains the
code-reuse hazard; it does not endorse complete-case deletion as a solution.
