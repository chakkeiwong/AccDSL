# POCI interest and subsequent lifetime-loss changes

16 October 2026. R03 bank method residual, R07 manuscript and R08 evidence.
MC02/04/05/11/13/16/19/20/21/24/25/28/30/32/33/34/35;
G2/G4/G7/G12/G13/G17/G18. Documentary reference calculations only.

## Gap and skeptical audit

The P17 bank method explicitly promises ECL/SICR/POCI. The current residual
audit leaves POCI open. The retained standards example A07 supplies amortised
cost 60 and credit-adjusted EIR 20% and checks interest 12; its source note
explicitly excludes the full allowance/asset lifecycle. Repeating a rate/base
selection would not close this gap. Specify a bounded POCI purchase-to-collection
method with independent annual roll-forwards, subsequent lifetime-loss changes,
favorable revisions, adverse collection and the original credit-adjusted rate.

The existing non-POCI gross121/allowance60.5 example is not an interchangeable
comparator: a POCI asset incorporates initial expected losses in its initial
credit-adjusted rate. Charging that initial loss again as a day-one allowance
would be wrong. High risk or discount alone does not prove POCI status.
Inspect the historical EU 2023/1803 original 5.1.1, 5.4.1(a), 5.5.13–14,
Appendix A, B5.4.7 and B5.5.45; preserve the earlier AASB rate example as
bounded arithmetic evidence, not automatic EU applicability.

## Intent and evidence contract

Main question: can the method preserve initial loss-adjusted yield, calculate
interest on amortised cost, and recognize only subsequent changes in lifetime
credit losses, including favorable changes beyond the initial expectations?
Expected failures: duplicate initial impairment; change to an ordinary EIR or
gross interest after improvement; clip favorable loss adjustments at zero;
put allowance discount unwind into impairment twice; erase surviving legal
rights merely because the carrying amount is derecognized.

Use a synthetic single fixed terminal claim 121 due after two annual periods,
acquired for admitted fair value 50 with initial expected receipt 60.5. No
fees, coupons, FX, modification or other cash flows. The original credit-adjusted
rate is exactly 10%, verified by `60.5/(1.1)^2=50`; this rate is a numerical
example, not an inherited estimation default. Initial credit shortfall PV50
is already incorporated in price/rate and is not an additional allowance.

At year one before new information, carrying/interest are 55/5. Revising
expected terminal receipt to88 gives PV80 and impairment gain25. The next
year's interest is8 on80, so carrying becomes88. A final adverse revision
to actual collection70 produces loss18; total interest13 plus net impairment
gain7 equals total profit20 and net collection70 minus purchase50. Continue
also unchanged expectations, deterioration, later full recovery and an A07
rate/base limiting case. Freeze all annual asset, signed allowance, interest,
impairment, cash and equity targets before calculation.

For this fixed schedule, retain a before-allowance carrying amount G and a
signed loss allowance L, with amortised cost N=G−L. Before the next credit
revision, accrete G at the original credit-adjusted rate r, recognize interest
rN, and attribute rL to allowance unwind, so N grows by rN. At a revision,
new N is the PV of expected remaining receipts at r; set L=G−N and recognize
the difference as impairment, not as a new rate. This signed bookkeeping
decomposition must be derived and checked against the Appendix A definitions;
it is not a claim that a negative allowance is a contractual liability. It
preserves favorable lifetime-loss changes required by5.5.14. A terminal
collection and any financial write-off must keep contractual uncollected
amount and legal-release status separately visible.

Primary criterion: independent exact stage/journal/cash targets and direct
discounting agree, with initial allowance zero, unchanged rate and complete
net-asset/equity bridge. Comparator: direct PV and cash conservation, plus the
protected A07 one-period12 interest check. Vetoes: invalid initial-rate equality,
wrong classification or source/valuation/time bindings, impossible collection
or expected cash, omitted required findings, wrong allowance/profit signs,
double-counted discount unwind or non-atomic failure. Counts and speed are
explanatory, not scientific promotion criteria. No stochastic ranking applies.

## Default and assumption audit

| Choice | Provenance/status | Justification | Risk and early check |
|---|---|---|---|
| Fixed annual terminal claim | New bounded method hypothesis | Separates initial credit loss from later revisions without day-count/root-solver ambiguity | Explicitly refuse other schedules; preserve arbitrary-schedule residual |
| Price50/receipt60.5/rate10% | Authored exact example | Original discounted expectation equals admitted acquisition measurement | Require equality, do not accept a convenient supplied rate |
| POCI, amortised-cost classification and acquisition fair value | Supplied findings under inspected source | Method needs all three independently | False/unknown refusal; discount or high risk alone cannot establish POCI |
| Expected receipts and revised credit facts | Supplied forecasts, no calibrated probability model | Isolate accounting treatment | Keep information dates and actual receipts separate; no predictive accuracy claim |
| Signed loss component | Local derived representation | Preserve favorable changes and exact net interest | Independently check each gross/net/allowance movement and reject a zero floor |
| No fees, coupons, modification, FX, tax or sale | Scope hypothesis | Keeps the mechanism identifiable | Refuse altered scope; no general bank or current-law readiness |

Pre-mortem: a balanced asset can still contain the initial loss twice, while
favorable revisions can be suppressed by a nonnegative-allowance default.
Freeze both counterexamples. A direct final cash check alone cannot distinguish
wrong interest-versus-impairment classification, so freeze those categories
separately. Clarify final write-off and legal-rights treatment before freezing
the terminal events; do not silently treat partial collection as legal release.

Continuation vetoes: conflicting required source, corrupt protected evidence or
work outside documentary authorization. Failed candidates trigger retained
repair (three focused attempts before replanning). A missing application fact
blocks that application, not the ready documentary method. No calibration,
empirical banking conclusion, public filing advice, runtime or current-law
compliance is inferred.

## Execution and reader contract

Use existing CPU-only Python/Fraction with `CUDA_VISIBLE_DEVICES=-1`, no
installations or controller. Preserve sources, original/frozen inputs, attempts,
manifests and result at `data/accounting-master/bank-poci-rollforward-20261016/`.
First finish the exact source/representation/collection audit, then freeze the
independent cases. Integrate only after the financial checks pass, preserving
all124 Version3.24 sources and all53 obligations/six interactions.

The reader knows the ordinary loan/allowance example. Start with a purchase
price already reflecting expected credit losses. Derive its rate, distinguish
interest from a later forecast revision, and show why improvement can produce
a signed favorable allowance. Follow cash to the closing profit and keep
legal rights separate. Human voice remains provisional; inspect affected
pages and refresh the master before continuing the next audited residual.
