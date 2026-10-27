# R05 — inference for prospective expected performance

23 October 2026. P17/P19; MC05/08/10/12/14/18/26/33–35; G6/G10/G13/G15/G17.
Output: `data/accounting-master/r05-inference-options-20261023/`.

## Research question and evidence boundary

The selected estimand is expected candidate-minus-locked-comparator CRPS for
the same nine named companies at future full fiscal years, each company
contributing one ninth after the common positive as-of asset scaling. First
release is the primary outcome. The exact future-origin law, within-company
time weights, and a confidence procedure remain open. This unit compares
inference choices; it does not evaluate forecasts or admit data.

Skeptical audit: nine issuers are purposively named, share shocks, and have
asynchronous fiscal intervals. Treating them as nine independent clusters is
not justified by equal company weights. Repeated annual origins share history,
refits and future shocks. The chosen target is an expectation under a declared
future process, not simply the finite realised average. The 2018–2025 source
panel is too short to establish a stable dependence law or a useful prospective
sample size. The matched conditional-predictive-ability source read does not
supply E3's one-sided expected-loss bound; no test is adopted from it. These
risks preclude a default confidence procedure today.

## Evidence contract for the comparison

Define the per-cell loss difference `d_ik` as scaled candidate CRPS minus
scaled fixed-comparator CRPS for issuer i and eligible start-year cohort k.
Use the same positive as-of assets for both arms and preserve the full one-ninth
issuer weights. Let `X_k = (1/9) sum_i d_ik` only for a complete paired cohort;
missing cells remain unresolved and do not change other weights. The future
expected target is `Delta_K = E_Q[(1/K) sum_k X_k]` under a prospectively
declared joint law Q for origins, issuer outcomes, common shocks, asynchronous
intervals and the locked sequential fitting policy.

The primary directional boundary is `Delta_K < 0`; an economic margin is a
separate decision. A promotion interval must be one-sided, valid for the
selected Q/estimand, and have its upper bound below zero (or below a separately
justified negative margin if economic materiality is later selected). All
methods must retain prospective protocol locks, complete denominators, failure
status, forecast versions and first-release outcomes. Descriptive finite means,
small-sample p-values, calibration diagnostics and sensitivity analyses cannot
be upgraded to a ranking. The artifact must state assumptions and what is not
concluded.

## Candidate inferential routes

1. **Finite-horizon report only.** Fix a finite future cohort set, report its
   complete realised average and cell table, and make no confidence or expected-
   performance ranking. This is valid as a finite-sample description but does
   not answer the selected expectation claim.
2. **Time-series long-run-variance inference.** Aggregate all nine companies
   within each complete start-year cohort to `X_k`; estimate the mean and
   long-run variance with a predeclared HAC procedure and one-sided upper bound.
   This retains contemporaneous cross-company dependence. It requires a stable
   mean/weak stationarity or a justified local-stationary target, suitable
   mixing/dependence, finite moments, and enough cohorts for the asymptotic
   approximation. Fiscal asynchrony and the 2027 reporting transition make
   these assumptions substantive. Annual observations and the current source
   horizon provide no adequacy evidence. It is a candidate for later
   prospective validation, not a current default.
3. **Predeclared joint longitudinal model.** Specify time-varying means, shared
   shocks, issuer dependence, asynchronous intervals, sequential refits and
   reporting-regime effects; derive a model-conditional interval for `Delta_K`.
   This can represent finite-grid heterogeneity but shifts validity to model
   specification and requires target-specific calibration and sensitivity.
4. **Bounded sequential inference.** A distribution-free martingale/e-process
   would need an appropriate conditional null and bounded or controlled-tail
   loss differences. No such bound or conditional null is established. Clipping
   the loss difference changes the estimand unless separately justified; it is
   not a free repair. Do not use this route without a new derivation.
5. **Block bootstrap sensitivity.** Resample common temporal blocks of the
   nine-company cohort vector, not issuers independently. This preserves
   within-cohort co-movement but still requires adequate temporal length and
   dependence assumptions; with few prospective years its tail bound is not
   reliable and cannot rescue an invalid HAC primary analysis.

## Assumption audit and diagnostics

| Choice | Provenance/status | Failure mode | Earliest diagnostic |
|---|---|---|---|
| Equal issuer contribution | Direct user decision | Missing firms reweighted away or shared shock ignored | Assert complete nine-cell denominator; inspect cohort vectors and covariance |
| Equal cohort weights | Prior design proposal only; not user-selected | Overweights dense years or changes the expected target | Compare exact target under alternative predeclared time weights before lock |
| Start-year cohort | Calendar proposal, not selected | Asynchronous windows obscure common exposures | Print actual interval bounds and overlap graph by cohort |
| HAC long-run variance | Candidate, not default | Short series, breaks, dependence misspecification | Predeclare simulation/size diagnostics using plausible dependence and regime cases |
| 95% one-sided confidence | Convenience convention only; unselected | Overstates certainty or mismatches decision | Ask the user before confirmatory protocol lock |
| Prospective stopping horizon | Unselected resource/design choice | Optional stopping inflates error or yields no power | Fix duration or alpha-spending rule before first outcome |
| 2027+ OCF mapping | Source-dependent unknown | Accounting transition changes target across issuers | Adjudicate issuer policy, target versions and first-release mapping before inclusion |

## Decision and stop conditions

Continue only as protocol design until Q, cohort/time weights, cutoff schedule,
source policy, fitting locks, inference assumptions, confidence level,
sequential-look rule and resource horizon are stated together. The specific
continuation veto is a design that cannot represent the selected expected
quantity or silently treats dependent issuers/origins as independent. A short
or noisy result is candidate evidence, not a reason to abandon the idea. If no
valid uncertainty method or enough future cohorts is feasible, report the
finite result descriptively and do not make an expected-performance ranking.

No model training, simulation ladder, benchmark, forecast collection, or
inferential test is authorized by this design note. No manuscript or source
admission changes. The plan survives skeptical review only as a comparison of
routes; the HAC route is explicitly a conditional proposal whose assumptions
and sample adequacy remain to be settled.
