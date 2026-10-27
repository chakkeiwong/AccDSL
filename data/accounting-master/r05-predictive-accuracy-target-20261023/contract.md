# Predictive-accuracy comparison contract

The first E3 study is a research comparison of predictive accuracy. Its
primary outcome is the expected difference in operating-cash-flow CRPS between
the alternative-history candidate and a comparator whose fixed interpretation
is locked before test outcomes. The sign is

`d(i,t) = [CRPS(candidate(i,t), Y(i,t)) - CRPS(comparator(i,t), Y(i,t))] / A(i,t)`.

Here `A(i,t)` is the same strictly positive as-of total-assets amount for both
arms. Lower candidate loss therefore gives a negative `d`. The zero boundary
`Delta = 0` separates equal expected predictive accuracy from a candidate with
negative expected loss. This is the directional research criterion implied by
the selected purpose. It is not a business-value threshold. The frozen E3
promotion rule remains stricter: a material-improvement claim needs a
defensible uncertainty bound below a separately justified negative margin.

For issuer `i` and eligible future origin `t`, let `b(i,t)` be predeclared
within-issuer origin weights summing to one. The selected equal-company target
is

`Delta = (1/9) sum_i sum_t b(i,t) d(i,t)`.

The nine issuer shares remain one ninth when origin counts differ or cells fail.
An observed survivor mean is a conditional diagnostic; it is not the full
effect. If an issuer has an undefined positive-weight cell, the full effect is
unavailable until a declared service or law supplies that component. No
renormalisation, zero imputation or representation-count weighting is allowed.

The future-origin statement is `Delta = (1/9) sum_i E_Q[d(i,O_i)]`, where Q is
an explicit joint process for origins, information, outcomes, fitting and
refitting. Repeated historical rows do not define Q. Any variance or interval
must include serial, cross-issuer, overlapping-fiscal-interval and common-fit
covariances. An independent-company bootstrap or a scalar package default is
not admitted by analogy.

The candidate, comparator, target, cutoff, preprocessing, positive scale,
scenario information, refit cadence, tuning cap, fallback and output bytes are
locked before each affected outcome. Complete finite probability laws are
required for CRPS. An unweighted set remains an explicitly set-valued result;
it receives no invented probability score. The joint closing-cash/financial-
debt task still requires a separate admitted joint law and fixed component
scales.

The exact fixtures in `reference.py` establish arithmetic boundaries only:
point-law CRPS sign, asset scaling, unequal-origin equal-company aggregation,
missing-cell denominator preservation, comparator-lock chronology and refusal
of invalid weights/scales. They provide no uncertainty estimate, forecast
performance, source admission or default policy.
