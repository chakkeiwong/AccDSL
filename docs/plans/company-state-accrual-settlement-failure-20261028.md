# SIM-F036: accrued coupon settled in the following period

28 October 2026. Ready C04 continuation; MC12/13/14/19/24/28/33.

Skeptical audit: the original failure is coupon5 recognized but unpaid in year1,
then paid in year2. A coupon paid immediately would test the wrong target. Use
the existing declared financing builder's separate interest_accrue and
interest_pay methods, native reporting and annual carry. No new accounting
engine or hand-entered replacement amount. Full-year2027 principal100 at5%
under the supplied actual-days/365 policy produces5. Payment on the first day
of2028 isolates settlement of that liability; it does not assert completion of
all2028 interest or events. Generic balanced journals cannot prove the debit
settles the correct obligation; deliberately re-expensing must be checked.

Question: does accrual followed by carry and settlement preserve expense5 in
the first period, payable5 at its close, then cash outflow5 with no second
expense? Exact comparator: independently assembled signed journals, all book
balances, finance cursor/debt memory, annual carry and both reports. Candidate:
unchanged declared builder/runtime. Primary criterion is equality of those
states/reports, not number of checks or balanced-book status alone.

Expected failures: treating accrual as cash, dropping payable at carry, repeating
the expense on payment, paying beyond liability/cash or replaying a payment.
Incorrect comparisons or missing guard outcomes veto the affected result and
trigger repair. Source/protected hash corruption is a continuation veto until
resolved. A deliberate bad-method control is expected to reveal the limits of
generic execution, not reject the broader project. No inferred source facts,
accounting compliance, complete2028 statements or actual-company assertion.

Material choices and provenance: coupon5/year1-to-year2 timing come from the
original SIM-F036 row. Principal100/rate5% and opening cash20/inventory100/debt100/
equity20 are explicit synthetic choices; exact interval and complete balance
checks expose wrong amount or funding. Operating classification is a supplied
policy, with financing classification as a separate control; neither is a
universal accounting default. Two account maps test role/name independence.
No random seeds or GPUs: deterministic native/exact arithmetic only.

Execute fresh attempts under company-state-accrual-settlement-failure-20261028.
Preserve original row, source hashes, command/commit/environment, complete inputs
and outputs, independent expectations and negative cases. Run relevant existing
tests and fresh protected checks, record decision/inference tables and update
C04 without changing original statuses. Continue ready work after the result.
