# F2 — signed time value in a fully aligned zero-cost collar

17 October 2026. MC16/17/24/26/29/30/32–35, G2/G3/G7/G8/G10.
Baseline Version 3.39; preserve AlignedOptionComponents/1 and its deliberately
restricted purchased-call domain. Original operation P17-05 hedging and the
finite F2 signed-component residual. Evidence:
`data/accounting-master/zero-cost-collar-20261017/`.

## Skeptical audit and evidence contract

The next useful signed-component method is explicitly supplied by IFRS
9.B6.5.31: the time-value changes of an eligible purchased/written option
combination with zero net time value at designation enter OCI, even though
the cumulative time change over the entire relationship is zero. For a
transaction-related item, the final time-value basis adjustment is zero.
B6.5.32 still limits this to aligned time value; the general unmatched,
opposed-change reading of B6.5.33 is not inferred from it.

Question: can a fully aligned purchase collar retain signed interim component
reserves and separate actual call/put cash while closing to the independently
derived bounded purchase price? Use a purchased call at upper strike K_U and
a written put at lower strike K_L, K_L < K_U, both for quantity q and the same
expiry/underlying as the forecast purchase. Opening spot lies between the two
strikes, initial intrinsic is zero, and both nonnegative premiums are equal.
They are still two gross premium flows, not absent cash flows. Supplied findings
admit the combination's eligibility, continuing qualification, matching item
risk/terms, transaction-related nature and complete values. No pricing or legal
qualification is inferred.

Comparator: directly derive final inventory and net cash cost as
q*min(max(S_expiry,K_L),K_U), independently of the chronological journals.
Primary criteria: exact agreement at below/at/between/at/above strike prices;
every date's option assets/liabilities, intrinsic reserve, signed time reserve,
cash and equity reconcile; final cost reserve is zero. Include an interim
positive and negative net-time-value reversal. Zero net initial cost is not a
reason to drop the two premiums or subsequent signed time value.

Hard vetoes: mismatched quantity/term/underlying, unequal initial premiums,
nonzero expiry time values, wrong component or settlement, future facts,
missing eligibility/valuation findings, unsatisfied funding order or partial
results after refusal. Explain-only diagnostics: counts, build success and
intermediate reserve size. A local error triggers bounded repair; missing
source support blocks only its dependent method. No stochastic comparison,
current-law admission, tax treatment or production compliance follows.

Defaults: strikes 9/11, q10, opening spot10, equal premiums6 and capital300
are authored synthetic amounts, chosen to make both payoff signs inspectable.
Both legs are fully aligned as a combined collar; do not describe each single
leg as an independent hedge of the whole purchase. No time-value monotonicity
or common cumulative-loss assumption is imposed. All marks are supplied,
nonnegative per-leg time values; the signed net amount follows subtraction.
The supplied measurement profile has zero discount and no carry/basis/credit
effects, with explicitly supported opposite hedged-item risk measures. These
are finite measurement assumptions, not a general commodity/option valuation
model. In particular, synthetic quotes must be plausible under those declared
terms; nonnegative time values alone do not prove arbitrage-free pricing.
Before freezing cases, improve that cheap diagnostic: at each date supply an
auxiliary positive-weight distribution over terminal prices 6,9,10,11,14 whose
mean is the quoted spot and whose option-payoff means are the quoted values.
Equal inception weights imply equal premiums6. Intermediate weights
(1/10,1/10,1/10,1/5,1/2) imply spot11.7, call15 and put3; reversing those weights
implies spot8.3, call3 and put15. These are local convex-combination witnesses
for synthetic marks, not inferred probabilities, forecasts or a joint model
across dates. This replaces the arbitrary premium10 before any fixture freeze.
Funding order is supplied for the finite example: pay call premium, receive
put premium; at expiry pay supplier, receive call payoff, pay put payoff.
Insufficient intermediate cash refuses rather than inventing finance.

## Execution

Inspect IFRS9.6.2.1/4–6,6.4.1,6.5.11/15,B6.5.5/29–33 and relevant existing
contracts. Freeze exact authored expectations; derive net-price and component
identities; write/check the read-only reference; integrate a successor section,
build and read affected pages; preserve all original obligations and refresh the
next phase. No installation, product runtime, controller or empirical run.

Heterogeneous stopped-item reserve attribution remains another named F2 question.
The collar does not answer it. Do not apply an aggregate nominal fraction or
sum independent lower-of reserves without proving the designation permits that
operation. Inspect that source/derivation boundary next. Pending independent
and human acceptance does not halt internal work.
