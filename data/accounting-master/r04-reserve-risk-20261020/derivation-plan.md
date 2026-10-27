# Exact diagnostics after technical source inspection

20 October 2026. Addendum to `accounting-r04-reserve-risk-20261020.md`.
No random experiment, fitted claims model, accounting calibration or empirical
promotion is planned. Each case has an independent mathematical expectation.

1. Appendix 2, paper page 34 (physical 35), prints ascending-order weights
   `w1 = 1 - t(S1)` and `ws = t(Ss) - t(S(s-1))` for `s >= 2`, then says
   their sum is one. For the permitted `rho=1`, two equally weighted losses
   0 and 4 give printed weights 1/2 and -1/2. The denominator is zero and
   the unnormalised sum is -2; the declared integral equals the mean, 2.
   Derive positive masses from the transformed survival function, giving
   `ws = t(S(s-1)) - t(Ss)` with `S0=1`. Test the rho=1 mean and telescoping
   mass against exact fractions, including repeated values and a constant loss.
   For rho=2 use a nonuniform finite law with losses 0,4,10 and masses
   5/9,1/3,1/9. Tail probabilities 1,4/9,1/9,0 have rational square roots
   1,2/3,1/3,0. Both corrected mass and survival-interval integration give
   14/3, versus the ordinary mean 22/9. No floating approximation is needed.

2. Reconstruct Appendix 3 using square-integrable terminal ultimate U,
   nested information F_t, adapted paid amount A_t, remaining payments
   L_t=U-A_t, and true conditional means M_t=E[U|F_t]. Source CDR uses the
   profit sign, D_t=M_(t-1)-M_t. Distinguish E[sqrt(Var(L_t|F_t))|F_0],
   sqrt(E[Var(L_t|F_t)|F_0]), and sqrt(Var(L_t|F_0)).
   Use a four-outcome exact law: U=0,2,8,14, probabilities 1/4 each;
   time 1 reveals which pair contains U; no payments until time 2.
   Expected conditional SD=2, expected conditional variance=5, initial
   variance=30. First and second CDR variances are 25 and 5, covariance 0.
   The second increment's squared size depends on the first, so orthogonality
   does not establish independence. Future SD=3 on the second branch exceeds
   sqrt(5): the expected-risk upper bound is not a pathwise upper bound.
   No extension to quantiles, arbitrary refitted forecasts or stochastic
   discounting is licensed by this exact martingale argument.

3. Make the finite-tail convention explicit. For losses 0,4,10 with masses
   1/2,1/4,1/4 and alpha=3/5, the left quantile is 4. Quantile-integral
   expected shortfall is (10/4 + 4*(3/20))/(2/5)=31/4. The conditional
   means above and at-or-above that quantile are 10 and 7; neither computes
   that target. These expose atom handling, not a defect in the source's
   particular simulation implementation. An exact VaR-equivalent alpha for
   31/4 does not exist in this discrete law. Quantile 4 instead corresponds
   to alpha in (1/2,3/4]. Report the CDF coverage separately from exact
   quantile equivalence; do not invent a unique percentile by interpolation.

The checks compare different formulations: survival intervals versus weights,
direct terminal variance versus conditional decomposition, and integrated
quantile segments versus tail mass at the quantile. Reject wrong signs,
normalisations, omitted covariance conditions and naive atom exclusions.
Use Python Fraction and exact square-root recognition only. Retain evaluated
values and explicit source/derivation scope in `comparison.json` and method
notes. Passing these fictional examples verifies these identities, not a
general risk engine or empirical uncertainty model.

Skeptical audit: the sign error is visible in the actual accepted-manuscript
render; no claim about the published edition is made. The variance conditions
are stronger than arbitrary plug-in forecasting and remain explicit. These
examples address target/implementation distinctions without choosing a risk
measure, probability law or confidence level for any real insurer.
