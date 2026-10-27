# Keep credit schedule components distinct after financial write-off

27 October 2026. MC03/05/08/11/13/15/16/17/19/24/25/26/28/33/34;
W07/09/11/12/16/17. This begins the next independently ready bank design unit.
Baseline: the nine retained dated-credit schedules, CreditLinkedSchedule/1,
CreditLinkedBook/1 and the completed conditional cash-classification evidence.
No new legal, standards or recovery policy is inferred.

Question: can a complete dated nominal-component record preserve the distinction
between actual collections, uncollected scheduled cash, financially written-off
portions and remaining modeled receipts when the book becomes derecognized?
The existing native outputs already retain uncollected_contract,
writeoff_contract and legal_forgiveness=not_assessed. Do not claim these are
missing. The gap is an explicit complete rollforward and its limits for later
recovery instructions, not another copy of ending balances.

Skeptical audit: written-off contractual cash is a schedule amount, not the
carrying value of the write-off, and not an assessed enforceable right. A
financially closed flag cannot answer whether a claim was forgiven. The
performing-prepayment example changes the modeled receipt schedule under its
supplied unchanged-terms finding; do not label that a legal amendment. Explicitly
retain the schedule replacement and dated signed delta before reconciling it.

Candidate: a separate read-only record bound to the exact retained request and
result. For every event keep the current modeled schedule, cumulative actual
collection allocations, uncollected amounts, removed write-off portions and
explicit noncredit estimate-schedule changes. At each due date check original
scheduled cash plus cumulative modeled revisions equals collections plus
uncollected plus write-off portions plus remaining schedule. Preserve event
order, zero entries, source IDs and the unknown legal status. Keep all native
financial journals/reports unchanged and retain their identities.

Comparator: an independently authored endpoint table and an independent
per-due-date allocation calculation. Inspect every source event and its current
native interpretation first. The partial-write-off case starts from 66 and
363/5, collects 44 and 55, retains write-off portions 66/5 and 363/25 and
uncollected 44/5 and 77/25. Total 693/5 equals 99 + 693/25 + 297/25.
The full-write-off case retains all 693/5 as removed scheduled cash although
financial gross and allowance close to zero. The prepayment case must show its
signed dated schedule revision rather than forcing the original total to fit.

Promotion/pass: exact complete component records and native archived rows
agree on all nine cases; every dated conservation relation holds; no mutation
of native financial output; adverse controls reject lost/duplicated portions,
wrong dates, stale source/result, hidden schedule replacement, erased zero rows,
false legal forgiveness/admission and treating write-off schedule as cash.
Counts and an overall total alone are explanatory, not sufficient.

Default audit: nominal rational amounts follow supplied schedules; no discount
rate or probability is invented. Native ACT/365F carrying-value mechanics stay
in their existing layer. Legal status remains not_assessed, not a Boolean
survival/waiver assumption. No journal or new receipt after close is introduced.
If a later recovery cannot be represented by the existing engine, identify that
specific supported/unsupported boundary and write a separate source-qualified
plan before implementing a new event. Do not invent a favorable recovery.

At most three fresh 120-second CPU attempts, GPU hidden, no dependencies or
external engagement. Preserve source locks, independent expectations, all cases,
controls and run manifest in data/accounting-master/credit-claim-continuity-20261027/.
Source drift or inability to reconcile dated components vetoes integration and
triggers local repair; an exhausted bounded unit leaves other packages ready.
After the result refresh the bank continuation gap and integrate separately.
