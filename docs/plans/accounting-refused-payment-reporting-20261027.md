# Keep refused coupon obligations in complete reports

27 October 2026. MC04/05/08/10/11/12/13/15/16/17/18/24/25/26/28/33/34;
W05/11/12/13/16/17. Follows exact financing viability evidence.

Question: does the unchanged typed company runtime preserve the exact accepted
prefix and unpaid coupon when the certified receipt-6 payment fails, and can that
retained state produce a complete internally consistent financial report?
Use guarded-memory-runtime bridge.build with the exact witness and every action
sequence, on both account charts, and compare current state to the independent
expected_path state at the first refused event. Run receipt-7 draw/pay as the
positive continuation control. Native financial fallback must be disabled.

Skeptical audit: earlier settlement/carry evidence concerns a distinct zero-coupon
principal promise and cannot be relabelled as coupon arrears. This increment
reuses the existing accrued interest payable and due-minus-paid memory only.
Unpaid interest is retained, but legal default, arrears assessment, partial
settlement and late recovery need explicit future events. Do not fabricate those
events or infer a payment from available cash. A stopped program can report its
accepted prefix; it cannot call the intended remaining commands executed.

Primary criterion: exact account, memory, journal-flow and stopped-prefix equality
with the protected recurrence, plus independently derived balance-sheet/income/
cash-flow totals and explicit unexecuted commands. Runtime report balancing alone
is insufficient. For draw/pay at the witness: cash=85/16, payable=43/8, facility
debt=0, used=true, paid1=95/16 and paid2=0. Recognized receipt remains 6. Check the
report's cash-flow detail against each actual accepted flow and keep missing
future events/source completeness unresolved. Refused actions never enter seen.

Controls erase payable/history, invent payment/receipt, alter cash-flow origins,
discard remaining commands or claim completion; a saved-result checker must
reject them. Positive and negative cases should preserve existing hashes. No
automatic partial payment or zero-coupon-contract reuse. Evidence counts are
explanatory; success is scoped to this exact bridge/reporting comparison.

At most three fresh 120-second CPU attempts, GPU hidden, no new dependencies.
Store locked inputs, full current states/reports, controls and manifest under
data/accounting-master/refused-payment-reporting-20261027/. Next specify an
explicit coupon-obligation continuation with compatibility to this accepted
prefix; review its timing/classification assumptions before implementing it.
No legal/accounting admission, company distress claim, fees, agents or E3.
