# F2 successor — actual and aligned option components through settlement

16 October2026. MC02/04/05/11/13/16/17/19/24–28/30/32–35;
G2/G4/G7/G12/G13/G17/G18. Documentary methods only. Evidence:
`data/accounting-master/aligned-option-components-20261016/`.

## Skeptical audit and scope

The manuscript already explains actual/aligned time-value declines and the
cumulative lower-of reversal. Repeating those isolated examples would not
answer F2's remaining component-join question. The missing method must keep the
actual option, the hypothetical option matching the hedged item, the designated
intrinsic gain, time-value cost reserve, mismatch profit and actual cash apart.

Use the retained EU2023/1803 original IFRS9.6.2.4(a),6.5.11/15,
B6.5.5/29–33. The older AASB-profile examples remain their own baseline; this
finite method is explicitly historical-EU and does not silently convert their
authority. B6.5.5 forbids importing features of the actual instrument into the
hedged item. B6.5.32 determines aligned time value from the hypothetical option
matching the item's critical terms. B6.5.33 has different branches according
to the inception time-value comparison.

The model uses one purchased call and a transaction-related inventory purchase,
equal quantities and currencies, an original spot price below both strike
levels, zero initial intrinsic value and supplied complete component valuations.
The hypothetical call's strike equals the one-sided hedged price level; the
actual strike can differ. Current intrinsic values are q*max(price−strike,0).
This payoff identity does not value time value. Both time values are positive
at inception and remain between zero and their own inception values; this
keeps cumulative time-value changes in the source-inspected common-loss case.
Signed collars, opposed cumulative changes and a general option-pricing model
remain explicit source/valuation obligations.

## Evidence contract and hand-derived expectations

Question: how do mismatched actual/aligned components alter reserve, profit and
inventory basis without creating hypothetical cash?

Higher-actual case: quantity1, initial price90, actual strike100, hedged/aligned
strike110, initial actual/aligned time values6/4. Premium cash6 is paid only for
the actual option. At price115, actual intrinsic15 and aligned intrinsic5;
actual/aligned time values3/3 imply actual total18 and hypothetical total8.
Intrinsic reserve5 and intrinsic profit10; cost reserve−1 and mismatch profit−2.
Combined reserve4/profit8 reconcile the actual option's gain12 from cost6.
At expiry price130, intrinsic30/20 and time values0/0 give intrinsic reserve20,
cost reserve−4 and profit8. Opening cash/capital200 becomes cash94 after
premium6, supplier130 and actual settlement30. Inventory is130−20+4=114;
cash+inventory208=capital200+profit8. Using actual intrinsic30 as the hedged
item would wrongly give inventory104 and profit−2, although the final sum
would still balance. This is a target error, not a bookkeeping failure.

Lower-actual case: actual strike110, hedged/aligned strike100, initial times2/3.
At price105, intrinsic0/5, actual time1 and aligned time5/2 give actual total1, hypothetical15/2;
cost reserve−1/2 and profit−1/2. At expiry price120, intrinsic10/20, zero times,
intrinsic reserve10, cost reserve−2, mismatch profit0. Opening cash200 becomes
88 and inventory112, with equity200. A second intermediate observation must
show reversal of the prior mismatch from cumulative, not period-only, changes.

Also freeze matched critical terms, expiry out of the money, both zero intrinsic
values, intermediate reversals and counterexamples to booking the hypothetical
option or scaling it from the actual option. Primary pass criteria: exact
component/classification targets, every reserve/earnings movement, premium/
supplier/settlement cash, both direct basis transfers and complete equity.
Missing valuations, incorrect critical-term binding, omitted premiums, mixed
profiles, unsupported signed changes and partial output on refusal veto the
affected method. Counts and build success are explanatory only.

The hypothetical derivative is a measurement device, never a second asset or
cash transaction. No actual valuation, issuer eligibility, current-law,
cash-flow activity, tax or complete company/sector claim follows.

## Assumptions, pre-mortem and delivery

| Choice/provenance | Why used | Failure mode and early check | Status |
|---|---|---|---|
| Different strikes, synthetic contracts | Exposes actual versus hedged risk | Actual intrinsic substituted for hypothetical; independently compute both payoffs | Example |
| Supplied component marks | Isolates accounting from option pricing | Total value counted twice or aligned option booked; require decomposition and gross cash identities | Conditional input |
| Common-loss time-value changes,33(b) | Has inspected support and existing baseline | Unjustified signed selector; refuse opposed/increasing cumulative changes | Explicit finite scope |
| Inception equality only for fully matched terms | Avoids inventing an equality extension for mismatched contracts | Equal initial numbers conceal differing terms; refuse without matched critical terms | Conservative scope |
| Transaction-related inventory,6.5.15(b) | Provides complete cost/reserve/cash consequence | Time-period amortisation wrongly joined; type and classification finding | Source-grounded choice |
| Exact fractions and CPU Python | No stochastic or root-solving uncertainty | Decimal or sign mistakes; exact journals and independent arithmetic | Engineering choice |

The pre-mortem is a balanced book with the wrong inventory/profit split, caused
by copying actual strike/valuation into the hypothetical item. The explicit
104-versus114 counterexample is the earliest discriminating check. The source
audit passes for this scope; no general signed-value branch is admitted.

Freeze the plan, source notes and independent expectations before implementing.
Run `CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/aligned-option-components-20261016/verify.py`.
Preserve numbered attempts and manifests. Integrate Version3.32 with131
protected3.31 sources; inspect new and neighboring pages. Retain all53
obligations/six interactions and provisional human acceptance. Refresh F2's
exact residuals, then audit B1 dated credit/debt schedules. No continuation veto.
