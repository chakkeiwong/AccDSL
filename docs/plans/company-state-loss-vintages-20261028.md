# Loss carryforward identity and recurrence: SIM-F042

28 October 2026. C04; MC08/09/10/13/17/19/20/24/28/33/34.

Question: does the retained conditional tax-loss ledger preserve loss40 through
income30 then30, and distinguish a subsequent additional loss10? Comparator:
the original SIM-F042 and exact recurrence use=min(available loss,positive
income), closing=opening+max(-income,0)-use, with explicitly eligible unlimited
carryforward and cap sufficient for this test. Expected sequence40->10->0
leaves post-loss income0 then20. The negative10 branch gives50, not30 or a refund.

Skeptical audit: current-tax recognition, deferred-tax measurement and legal
loss inventory are separate. The existing conditional_tax_losses_v1 ledger
already carries loss lots and interval history. Reuse it with native current-
tax reconciliation requests; do not write a second loss implementation. The
reconciliation examples use independently supplied annual financial openings,
so only loss-ledger continuity can be claimed. Two income30 periods must have
distinct dates and IDs; replay of one period cannot create another deduction.
The audit passes for a bounded loss-ledger discriminator, not actual tax policy.

The only supplied model is close_day_explicit_use_v1. Nonexpiry, eligibility,
cap and rate1/4 are explicit synthetic premises, never inferred tax law. Rate
only converts residual income20 to conditional gross tax5; no refund, DTA,
book carry or cash payment is implied. Early diagnostic: reproduce one negative
and one positive interval before the chain. Expiry/unknown eligibility/cap and
duplicate/overuse controls test whether those assumptions are still required.

Primary pass: exact per-lot original/used/remaining/expired quantities, date
continuity, history, conditional taxable income and immutable proposal/apply
agreement. Test source and state hash tampering, duplicate step/lot use,
forgotten balances and attempted reuse of the original40 after using30. The
independent recurrence is an oracle for the supplied eligibility model only.
Lost rights, double use, invented refunds or erased unknowns veto promotion and
trigger repair. Invalid protected dependencies or unusable harness veto
continuation until repaired. Counts/runtime are explanatory. No stochastic
ranking, tax compliance, source admission, prediction or release acceptance.

Retain exact requests/results, branch histories, failed attempts, plan, source
hashes and run manifest under company-state-loss-vintages-20261028. A failed
candidate does not reject loss-ledger research; continue the specified repair.
