# Unpaid coupon survives the reporting boundary

27 October 2026. Attempt 01 passes ten retained cases: six final-day carries and
four non-final-day refusals, with 406 assertions, sixteen controls and 181
protected files. Runtime 1.670 seconds. The independent checker compares the
complete closing journal, closing and opening books, history archive and report.

At the failed receipt-6 second payment, carry preserves cash 85/16, coupon
payable 43/8, due2 43/8, paid2 zero and used borrowing rights. Closing transfers
the recorded loss 89/16 to the signed equity account and clears temporary
income/expense accounts. The opening contains no new-period flows, while the
closed book retains all old gross flows. The original refusal and unexecuted
commands remain bound in a separate archive. No payment, waiver or fresh right
is created by crossing the reporting boundary.

The generic carry engine accepts a type-correct reset of used=false. The selected
coupon wrapper rejects it, along with missing policies and resets of due memory.
This demonstrates why typed validity alone does not establish the required
financing-history semantics. June 30 refused states remain unassessed for fiscal
carry; their dates are not relabelled to manufacture year-end states.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept selected coupon carry | Full independent book/journal/archive/report equality passes | Sixteen stale, reset, wrong-boundary or invented-admission controls rejected | Optional later payment and its historical timing | Specify a dated partial-coupon instruction using existing cash and preserved refusal evidence | Payment executed, restored borrowing right, actual arrears/default, fiscal/source admission or durable restart |

No stochastic ranking applies. Counts/runtime are descriptive. The strongest
alternative explanation, a coherent opening hiding erased memory, is addressed
by all-leaf preservation and external refusal binding. Actual historical truth
and event completeness remain unresolved. The manifest records command, Git,
Python, CPU, source locks and outputs; GPU hidden. Version 5.45 governs. This
companion and refused-payment reporting await integration; all 18 packages stay
open, S1–S5 partial, S6 held, E3 deferred.
