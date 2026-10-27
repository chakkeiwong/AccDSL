# R05 — conditional and unconditional targets in a shared-regime diagnostic

23 October 2026. P17/P19; MC05/08/10/12/14/18/26/33–35; G6/G10/G13/G15/G17.
Output: `data/accounting-master/r05-martingale-estimand-20261023/`.

## Question and baseline

The target is expected candidate-minus-locked-comparator score under a declared
joint law Q for future dates, company outcomes, shared shocks and sequential
refitting. Whether the expectation conditions on a starting information set
remains unresolved. With equal company weights and complete start-year
cohorts, write `X_k = (1/9) sum_i d_ik` and
`Delta_K = E_Q[(1/K) sum_k X_k]`. A martingale residual method often controls
`sum_k (X_k - E[X_k | F_{k-1}])`; that is an error around a realized
information-conditional path, not automatically a confidence interval for
`Delta_K`.

Skeptical audit: common regimes can make nine firms and many years nearly one
observation. Conditioning on the realized common regime changes the estimand.
Optional stopping or bounded residuals do not repair that mismatch. The smallest
meaningful check is an exact finite shared-regime model with rational
probabilities, comparing marginal target, predictable conditional means,
martingale residuals and an invalid iid calculation.

## Evidence contract

Construct a fully enumerated toy: one latent regime `R` has values 0 and 1 with
probability one half; all nine issuers and all K=3 future cohorts have loss
difference `d_ik=R`. Compute exactly: (1) marginal `Delta_K`; (2) the realised
average; (3) each conditional mean given the regime; (4) martingale residuals;
(5) cross-company and cross-time correlation; and (6) compute the iid sample
variance and its invalidity. Compare two filtrations: R known at the start,
and initially trivial information with R revealed by the first cohort. In the
second case the first residual is R-1/2 and subsequent residuals are zero.
Compare each conditional target with the unconditional target. Pass requires
exact arithmetic and the stated equality
relations. The toy illustrates a failure mode only; it does not estimate E3
power, sample size, or actual issuer dependence.

## Plan and limits

Use `Fraction` full enumeration over the two regimes; no RNG, solver, model fit,
ML, or empirical data. The key validity veto is presenting a pathwise or
conditional bound as marginal expected performance without the derivation and
assumptions connecting them. A direct conditional forecast-accuracy estimand
may be scientifically meaningful. The user's settled choice does not itself
select the starting conditioning set. This toy cannot reject martingale
inference generally: validity depends on the target, filtration and assumptions.
No actual interval, confidence level or sampling law is promoted.

Deliver exact result, decision/inference tables, manifest and read-only replay
under a fresh versioned directory. Update the four active controls afterward.
