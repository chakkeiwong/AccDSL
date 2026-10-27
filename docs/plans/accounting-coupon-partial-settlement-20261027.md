# Continue an unpaid coupon with an explicit partial instruction

27 October 2026. MC05/11/12/13/15/16/17/18/24/25/26/28/33/34;
W05/11/12/16/17. Prerequisite: checked unpaid-coupon carry, including external
refusal archive. Design/conformance evidence only.

Question: can a separately selected, source-defined late coupon method apply an
explicit affordable amount to the retained coupon without changing the original
missed decision or treating the liquidity shortfall as the whole liability?
Use the next opening from receipt-6 draw/pay and draw/draw, both charts. The
illustrative instruction pays 85/16 on 2 January 2028, using only carried cash;
it leaves payable 1/16. This date/amount is a supplied synthetic instruction,
not an inferred managerial action. No new funding is invented. A split-payment
control uses two amounts 85/32 on 2 and 3 January; the same total reduces the same
claim while preserving distinct dated flow history.

Skeptical audit: old paid2 means amount paid toward coupon2; the new method must
declare that it is cumulative and preserve the original action2='none' in this
stopped case. Historical success cannot be inferred from a later paid amount.
The immutable external refusal archive retains due-date execution and remains
bound to the carry opening. A distinct phase partial2 records later settlement;
this is an explicit new method selection, not transparent compatibility with
the old two-decision policy solver. Its output is not fed back into old policies.
No schema migration is needed because no field is added; the new registry and
phase meaning are separately identified. Full settlement is outside this funded
case unless supplied funding is separately established. Overpayment must refuse.

Implement postings and cumulative paid2 through the existing typed monetary/
memory engines with native financial fallback disabled. Retain source, clause,
right, used, due1/due2, paid1 and original actions. Preconditions: exact origin
history, current payable equals due2-paid2, positive amount <= payable and cash,
strictly after original due date, monotone event date, supported current phase,
and zero repaid facility debt. Postconditions: same accounting relation,
nonnegative cash/remaining claim, exact cumulative paid2 and preserved history.
Classify cash payment under the inherited synthetic operating convention only.

Primary criterion: independent full state, journal, gross flow, report and
history-frame comparison, on both charts and instruction schedules. Controls
cover early date, duplicate/replayed event, stale opening/archive, overpayment,
zero/negative amount, wrong cumulative write, changed action/used memory, and
wrong cash-flow classification. Do not accept balance-only checks. External
archive authenticity/source truth and durable store concurrency remain open.

At most three fresh 120-second CPU attempts, GPU hidden, no new dependencies.
Write exact schema/expected states and source locks before the run under
data/accounting-master/coupon-partial-settlement-20261027/.
After comparison integrate reporting/carry/partial settlement together and refresh
the master. All 18 packages stay open; S1–S5 partial, S6 held, E3 deferred.
