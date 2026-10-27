# PartialHedgeDiscontinuation/1

The exchange is a read-only report for one matched homogeneous partial
discontinuation. Requests/results are preserved in `attempt-01/exchanges.json`.
`input-lock-v2.json` binds the fixtures, source and baseline calculator.
The verified baseline source bytes are the bytes executed. Rational amounts
use canonical reduced strings; dates are canonical ISO days. Unknown fields
reject. No input can directly supply an expected reserve or earnings balance.

Top-level fields are exactly `wire`, `operation`, `baseline_hedge`, `context`,
`opening_cash`, `findings`, `discontinuation`, `events`. The wire is
`PartialHedgeDiscontinuation/1` and operation is `report`. The internally replayed
`RepeatedItemRebalancing/1` baseline must end in measurement, contain only one
item-origin layer and match the caller's entire context. It begins with the
old method's zero-cost/zero-value derivative origin. The new global findings
admit one eligible external non-option derivative, original zero cost,
homogeneous matched portions, a proportion of the entire instrument, no other
cash/earnings, pretax scope and baseline reserve recoverability.

Discontinuation has exactly `id`, `date`, `quantity`, `expected`,
`unrecoverable_loss`, `highly_probable`, `findings`. The stopped quantity is
strictly positive and smaller than the original quantity. The date is the
baseline's last measurement. `highly_probable` must be false; `expected` may
be true or false. Findings separately admit remaining qualification,
documentation, identified matched portions and continuing reserve recoverability.
There is no elective cessation of a still-qualifying portion.

The scalar removed fraction allocates the original cumulative derivative,
item, reserve and earnings amounts. Original price and date are retained for
the remainder; stopped derivative value, stopped prior earnings and the stopped
reserve at discontinuation are retained separately. The split creates no gain.
If the stopped cash flows are still expected, their reserve remains unless an
explicit nonnegative unrecoverable loss is recognized, bounded by its remaining
negative balance. If not expected, its whole remaining signed reserve moves
to profit and a simultaneous additional loss amount must be zero.

Each later event has `id`, `operation`, `date`, `context`, `findings` and the
operation fields. IDs are unique, contexts identical, dates nondecreasing and
before the supplied maturity. The supported operations are:

- `measure`: `price`, `derivative` give the current item price and whole
  derivative carrying value. Findings admit continuing qualification, complete
  valuation, zero discount, continuing loss recoverability and unchanged
  stopped expectation/loss findings. Only the continuing portion uses the
  cumulative lower-of calculation. All subsequent value changes on the stopped
  derivative portion enter profit, regardless of its frozen reserve.
- `assess_stopped`: `expected`, `unrecoverable_loss`, with a `facts_admitted`
  finding. Apply the reserve rules above to the remaining stopped balance.
  A canceled forecast cannot be reinstated through this operation.
- `purchase_and_settle`: `quantity`, `unit_price`, `supplier_cash`,
  `settlement_cash`. It occurs on the latest measurement date. Purchase
  quantity is the continuing quantity plus the stopped quantity only if still
  expected. Price/cost and whole-derivative settlement must match the inputs.
  Findings admit receipt of all expected units, inventory recognition, complete
  costs, NRV support, unchanged valuation, early settlement and no fees.
  Record supplier cash and derivative settlement separately. Transfer only the
  remaining attached reserve to inventory basis, then close the relationship.

No event is accepted after closing. Supplier payment precedes settlement in
this bounded funding check; insufficient cash requires a separately specified
funding route. No general net settlement permission is inferred.

Success returns `conditional_complete`, context and baseline-module identity,
origin/quantity records, final financial state, any closing bridge, chronological
stages, balanced proposed journals and separate cash origins. The original
opening cash is also capital; later equity is capital plus accumulated earnings
and remaining reserve. `posts` is false and `mutations` empty. Cash activity
classification and tax are explicitly not concluded/calculated.

Refusal returns no report, stages, journals, flows or mutations. Unknown
findings/missing bytes are `unresolved`; false admission, other methods,
nonoffsetting continuing gains and funding shortfalls are `unsupported`;
contradictory structure, identity, time, numeric relationships or changed bytes
are `rejected`. `attempt-01/adverse.json` records 79 concrete cases. These
examples do not certify all malformed inputs or a production engine.

General heterogeneous allocation, instrument-only ratio adjustment, repeated
stopping/new designation, acquired nonzero origins, options, FX/credit pricing,
tax, subsequent inventory sales and full company/sector composition remain
separate methods. A supplied finding is not evidence of its actual truth.
