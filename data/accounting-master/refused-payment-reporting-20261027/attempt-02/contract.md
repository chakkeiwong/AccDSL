# Refused coupon reporting contract

27 October 2026. Implements accounting-refused-payment-reporting-20261027.md.
The audited plan reuses the unchanged guarded-memory runtime and complete report
oracle. It compares both account charts, four receipt-6 action paths at the same
certified point, and receipt-7 draw/pay as a positive control. Native financial
fallback is disabled. Actual execution must stop at its first refused payment.

Primary criteria: every accepted transition, signed journal, dated flow, current
state, remaining command and full report must equal the independent oracle.
Additionally compare current accounts/memory/flow amounts against the independent
symbolic recurrence at the accepted-prefix length. Return the same unpaid coupon
in report lines and due-minus-paid memory. Expected draw/pay R6 figures are cash
85/16, other assets 189/2, debt 100, unpaid interest 43/8, expenses 185/16, income
6 and equity -89/16. Operating net cash is -3/16; financing net is zero, while
draw and repayment gross flows are each 1. These are synthetic signed-account
conventions, not an accounting-policy recommendation.

The report remains recorded-period-only and retains source/completeness issues.
No automatic partial payment, legal-default assessment, zero-coupon reclassification
or later recovery is inferred. A reporting result is neither an executed remaining
command nor a new program opening. Wrong payable, history, cash/flow attribution,
remaining commands, seen events, completion status or report is rejected by a
saved-result checker. Counts/time explain workload only. At most three fresh
120-second CPU attempts; GPU hidden; locks and full traces preserved.
