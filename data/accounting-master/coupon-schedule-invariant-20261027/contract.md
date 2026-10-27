# Schedule invariant: evidence and assumption audit

27 October 2026. Plan accounting-coupon-schedule-invariant-20261027.md passes the
skeptical audit. This is exact local method analysis with finite runtime checks.
Neither examples nor runtime limits become a theorem about unlimited execution.

The claimed recurrence for positive partial amounts q_i is C_i=C0−S_i,
U_i=U0−S_i and P_i=S_i, where S_i sums the accepted amounts. Initial constants
are C0=85/16, U0=86/16 and P0=0, from the identified carry cases. By induction,
U_i−C_i=1/16 and U_i+P_i=U0. Since U_i>C_i, every positive q_i<=C_i is strictly
less than U_i. Conversely an affordable schedule must have each prefix sum
<=C0. Positive amounts imply that this equals total sum <=C0. At cash exhaustion
the liability remains 1/16; one cannot remove it by further cash-only payment.

Compare the candidate's actual expression trees with independent affine
coefficients, bindings, exact guards, journals, cumulative write and unchanged
memory frame. Check concrete full states/reports with the retained independent
oracle for nonuniform, same-day, unequal rational, tiny and near-exhausting
schedules. These selected comparisons nominate no general accounting default.

The baseline is the already checked selected partial method; no source changes.
Exact coefficients and actual expression correspondence are the mathematical
criterion. Complete state/history/report agreement is the finite conformance
criterion. Source drift, changed phase/frame, wrong classification, false
admission and conflating resource refusal with infeasibility veto conclusions.
Repair triggers are local method/checker defects; upstream invalidity or the
three-attempt ceiling stops this unit. Counts and timings are explanatory only.

Runtime limits inspected before running: 64 commands, 8 MiB cumulative trace,
1,000,000 bytes for core bounded records, 4096 rational bits, 4096 scalar
characters, 4096 expression nodes and depth 48. Static compilation and per-step
validation may impose additional limits. No guarantee follows merely from a
schedule satisfying one limit. Dates must be nondecreasing, within the period,
strictly after the original close, and IDs fresh. Check the 65-command and
out-of-period refusals separately from the economic recurrence.

Assumptions: exact rational arithmetic is intentional; synthetic dates and
operating classification retain the preceding provenance; equal-date sequential
events are allowed by the actual nondecreasing date guard. New funding,
legal/default consequences and compatibility with the old policy solver are
excluded. Original refusal and later flow dates stay in the evidence.

At most three fresh 120-second CPU attempts. GPU intentionally hidden; no new
dependency. Preserve inputs, method inspection, source locks, comparison cases,
controls and run manifest. Successful predecessor writers are not rerun.
