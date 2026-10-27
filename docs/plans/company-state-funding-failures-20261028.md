# Original financing-cap and dated-payment discriminators

28 October2026. C04; MC13/14/17/18/33/34. Target SIM-F022/023/024
using the unchanged refinancing teaching case and existing rational_solver_v1.

Question: do fee/cap and every dated cash-prefix constraint rule out the
apparent funding obtained by treating face as cash, borrowing without an
admitted offer, or spending a day5 issue on a day4 maturity? Comparator is
the exact chapter14 example in the retained5.52-R2 simulation source, plus
its preserved arithmetic.json. This is an explicit new finite constraint
encoding, not a claim that an existing production event engine supports it.

Primary criterion: the native exact solver and independently authored rational
cash-prefix sequences agree on each declared case; fee1/cap30 gives only29
cash for a need30; absent offers cannot create borrowing; term cash arrives
only day5. Full-sale H1 succeeds with bridge16 and closes cash1, whereas
delayed H2 fails without a later eligible offer. Half-sale H1/H2 need net term
cash6.5/24.5; price0.9 gives minimum faces85/9 and265/9. Inventory must remain
at least10 when term funding settles. Half-sale H2 is feasible at price53/80
and fails just below. These cases also examine the stated eligibility link.

Research intent: preserve dated constraints and offer rights in conditional
financing analysis. Expected failures are infeasible declared paths; these
reject those candidates, not the harness. Solver unknown/resource remainder
is a continuation veto for claiming infeasibility, not economic default.
Baseline/hash mismatch, oracle disagreement or incomplete exact coverage
vetoes the affected result and triggers a focused repair. Cash balances and
query counts explain results; they do not certify external offer admission.

Assumptions: amounts, fees, prices, dates, receipt alternatives and stock-sale
rights come directly from the synthetic chapter. Use exact rational values
and the existing finite linear solver budget; no numerical defaults change.
Within-day ordering is explicit: sale and bridge precede old payment on day4;
customer receipt precedes term issue on day5; bridge repayment is day6. No
overdraft and no additional flows. Unknown lead time, legal admission,
financial accounting, tax, later term maturity, preferences and market
probabilities are excluded. Per-history feasibility is not an implementable
nonanticipative policy. No policy ranking or empirical forecast follows.

Audit: a final cash total can pass while an earlier payment fails, so each
prefix is primary. A fee-free or unlimited-offer mutation can look successful
but changes the target; retain as a sensitivity control only. An eligibility
check using opening inventory is wrong after the sale; expose that mutation.
All amounts are CPU-only Fraction/SMT, no GPU or stochastic inference. Start
with the fee/cap discriminator before the larger fixed case list.

Artifacts: new company-state-funding-failures-20261028 under data/accounting-master,
exclusive attempts with inputs, complete solver results, constraints, checks
and run manifest. Preserve all original failure rows/statuses and frozen
releases. Run python3 -B in the current environment; no installation.
