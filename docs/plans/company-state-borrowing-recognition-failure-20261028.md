# SIM-F035: borrowing must not become revenue

28 October2026. Ready C04; MC12/13/14/19/24/28/33. This continues the original
balanced-but-wrong journal case after the accrued-coupon discriminator.

Skeptical audit: a balance check or replay alone answers the wrong question.
Use unchanged declared debt_issue/debt_redeem with an independently specified
liability, cash, profit and financing-flow oracle. Source admission, debt
valuation and reporting compliance remain outside this synthetic test.
Borrow and partial redemption occur in order on the same day as the accrual
cursor; moving redemption to another day without accrual would test a separate
clock failure. Explicitly test that refusal without inventing an accrual rule.

Question: does borrowing100 produce cash100 and debt100, profit0, and financing
receipt100, while repayment40 reduces both cash and debt and creates no expense?
Baseline/comparator: independent full signed balances, all memory leaves,
journals and report bridges for two account maps. Candidate: unchanged declared
financing methods. Opening cash20/capital20, zero debt and other balances are
synthetic conveniences;100/40 expose gross versus net classification. Original
SIM-F035 supplies the event-type failure, not these amounts. No seeds/GPU.

Primary pass criterion: all independent economic and state expectations agree.
Veto: missing states, stale source identities, mismatched journals or unexpected
refusal invalidate the affected comparison. Protected-hash corruption is a
continuation veto. Repair trigger: a malformed mutation must be repaired and
its failed attempt preserved before interpreting economic behavior.

Negative controls: over-redemption, duplicate issue, missing approval, wrong
event date and tracked-debt mismatch. Deliberately credit revenue and suppress
the corresponding debt-memory write in an authored bad method; maintain valid
role typing and balanced journals. Compare variants with supplied financing
and operating cash labels. If generic execution accepts these variants, reject
them using event-specific oracle; do not describe them as behavior of the
unchanged builder or prove arbitrary economic-method correctness.

Check counts/replay are explanatory/engineering diagnostics, not proof of
admission. No method ranking, actual company or universal recognition claim.
Preserve full requests/results, independent expectations, original row, source
hashes, exact command/environment/commit and decision table under
company-state-borrowing-recognition-failure-20261028. Update supplemental
count only after evidence passes; preserve original criteria/statuses. Verify
protected releases and relevant tests, then continue ready work.

