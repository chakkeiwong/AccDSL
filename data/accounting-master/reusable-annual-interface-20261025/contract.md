# Reusable finite-period reference contract, revision 1

25 October 2026. Proposed governing semantics under the selected hypothetical
single-entity, single-currency, full26-account model. This document specifies
the common interfaces; individual operations require their own checked evidence.
No law, actual admission, arbitrary size or complete-company claim follows.

## Program and imported root

An AnnualProgram/1 request contains exactly profile, root_request, root_sha256
and operations. The root is the complete PeriodVintageContinuation/1 request;
evaluate it once and require complete_provisional. A stopped imported root is
unresolved, not silently resumed. Preserve its complete result once in the
program result. The flat ordered operation list never embeds the previous
program result as the next request. Imported historical vintages, recognition
archive and findings remain exact; the financial opening is the root opening.

The explicit PeriodBook/1 carries opening, after, account_classes, opening_loss,
loss_state, historical_vintages, period_vintages, current_assessments,
deferred_assessments, period_archive and findings. Account classification is
validated against the complete account set; its immutable source binding comes
from the imported root, not a caller's arbitrary reclassification. The
income_tax_payable account is added exactly once by the reporting adapter.

All portable values, operation lists and root records retain the existing input
limits (2,000,000 canonical bytes, 100,000 nodes, depth64). These are finite
engineering bounds, not an economic horizon. Over-limit requests fail before
execution. Full-size results may be larger because they retain trace evidence;
report size separately rather than treating it as a model-validity criterion.

## Liability rows

Each period_vintage has stable id, origin, period, opening_payable,
new_assessment, settlements and closing_payable. Origin identifies the imported
historical record, an earlier archived closing row, or the first assessment
that created the liability. Its source digest must match that retained record.
Amounts are exact reduced rationals. All amounts except journals are
nonnegative; closing=opening+new_assessment-sum(current-period settlements).
All closing amounts sum to the credit balance of income_tax_payable.

For an imported row, opening equals the root's opening_payable and the existing
period settlements are retained. Old tax_vintages remain byte-exact. For a
newly created current liability, opening is zero and new_assessment equals the
latest cumulative conditional tax assessment. At most one row is current under
this selected single-regime model. There may be any finite number of carried
rows, including zero rows. Do not infer fiscal age from row position or the
historical words carried/current in imported ids.

Every settlement records event_id, date, amount, payment_amount, original
operation digest and financial-kernel-result digest. Per-event allocations sum
to exactly one actual dated operating tax cash outflow. Historical settlements
from archived periods never enter this identity. Origin, opening and prior
history cannot change during a period.

## Operations and financial meaning

native and allocated_tax_payment retain the checked continuation input shapes.
Native events use selected return/lease kernels and cannot write tax accounts.
Dates are chronological and in the financial interval; event ids are
lifetime-unique. Payments require known affirmative authority, unique known
liability ids, positive amounts, per-row headroom, an exact total and actual
shared cash. No FIFO, proration, borrowing, tax calculation or new credit is
inferred. Preserve successful prefixes and exact remaining operations.
Once current tax has been assessed, native financial activity must occur on or
after that assessment's exclusive endpoint, matching the existing selected
kernel. A payment may occur on the recorded assessment day because it changes
payable and cash without creating new assessed income. A later assessment must
cover all subsequently recorded activity.

current_assessment contains id, mode (first or replace), model, interval,
information, allocations and loss_policy. All fields use the existing explicit
tax-information and loss declarations. The initial model is the conditional
cumulative no-credits method already checked; selecting another model is
unsupported. Interval starts at the immutable financial/loss opening; its
exclusive endpoint cannot shorten the prior assessment or precede an already
recorded event. activity_through=end_exclusive-1 day.

The population uses explicit account classes and the union of lease identities
in opening, after and earlier period trace states. Reconciliation checks every
native adjustment exactly once. Loss calculation always restarts from
opening_loss; old provisional usage or generation is retained in assessment
history, not subtracted twice. A generated loss id cannot reuse any earlier
generated identity, including superseded generations.

first requires no current assessment and zero current-tax expense. It appends
one liability id derived from the unique first assessment id. For tax amount
T, debit current_tax T and credit income_tax_payable T. Preserve every older
row and settlement. replace requires an existing current row, preserves its
stable id, recomputes T from the same original loss opening and posts only
T-old_T. Its closing liability is T-current_period_payments; a negative result
is unsupported because no receivable/refund model is selected. Older rows are
unchanged. Neither operation creates cash.

deferred_assessment contains id, model, measurement, findings, recovery_capacity
and items. It requires a current assessment covering all recorded activity.
The measurement binds the actual current state and date; each item and aggregate
tax base reconciles. The selected single-pool profit-or-loss model retains its
existing explicit support and capacity conditions. Store the result with its
post-assessment state digest. Any later financial event or current assessment
makes that state-specific deferred assessment stale. Earlier results remain
history. No automatic capacity renewal or credit/OCI/equity/offset route.

provisional_carry contains id, selected model, next_period and findings. Require
the current assessment endpoint and loss cursor at the financial end, a current
deferred assessment binding the exact closing state, and closing date equal to
the day before the endpoint. The next interval is contiguous. Close actual
income into retained earnings; preserve every permanent balance. Archive the
complete period opening, closing, liability rows, assessment histories, losses,
findings, report and carry journal. Open a row for every archived liability,
binding its prior row digest and closing amount, with zero new assessment and
no new settlements. Reset flows and tax adjustments only in the new financial
state; preserve them in the archive. Both assessments reset to unassessed.

## Result and refusal behavior

The result preserves root_result, request/source/implementation digests,
complete final period book, ordered trace, stop reason/index, remaining
operations and statements from the actual opening. Each trace entry binds the
before state, original operation, journal, cash flows and complete proposed
after state. apply recomputes the entire result and requires exact equality.
No durable commit or runtime scheduling is implied.

Malformed request or changed sources: invalid before execution. Unknown required
finding: unresolved. Unselected model or unsupported credit/route: unsupported.
Insufficient actual cash: funding_failure. These operation-level refusals return
stopped_provisional with the unchanged successful prefix. Internal invariant
failure vetoes evidence and triggers repair; do not describe a failing method
as successful merely because the prefix is retained.

## Discriminating reference cases

Starting from the checked root after its payment and depreciation gives cash
709/2, payable23/4, profit-2, and liabilities11/4 and3. First hypothetical tax
of4 appends a third row: payable39/4, current expense4 and profit-6, with no
cash movement. A payment allocated1,1,2 gives cash701/2 and liabilities7/4,2,2;
total payable23/4. Replacing the current cumulative tax with3 keeps the same
third id, leaves its payable1, gives aggregate19/4 and profit-5. Replacing it
below its payment2 must refuse without affecting the prior successful steps.

Next validate loss expiry/replacement, fresh deferred measurement, stale
measurement refusal, a full boundary and another assessment appending a fourth
liability. Those later operations are specified here but remain unchecked
until their reference evaluator and independent cases run.
