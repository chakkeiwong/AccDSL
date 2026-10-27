# OriginMatchedCessation/1

A read-only conditional report for an exactly matched, documented multi-origin
purchase history with one named partial stop. It proposes balanced journals;
`posts=false`, `mutations=[]`. No product/controller runtime is implemented.
Canonical reduced rational strings and canonical ISO dates are required.
Unknown fields reject. Missing/null required admission is `unresolved`; false
scope admission is `unsupported`; malformed or contradictory data is `rejected`.
Any refusal returns no report, stages, journals, cash flows or stopped trace.

Top-level fields are exactly `wire`, `operation`, `context`, `opening_cash`,
`findings`, `origins`, `history`, `stop`, `after`, `closing`. Wire is
`OriginMatchedCessation/1`, operation `report`. Context has entity, legal book,
currency, quantity unit, underlying, historical rule, maturity and information
date. Every origin has distinct `id`, `item_id`, `instrument_id`, designation
`date`, positive `quantity`, positive `price`, `initial_value`, `initial_cash`
and `facts_available_on`. Both initial amounts are explicitly zero. Each origin
date appears in history and its entry price equals that date's measurement.
All origins precede stopping. The origin-to-item/instrument map is documented
from designation and cannot be reconstructed from an aggregate reserve later.

Findings separately admit external eligible instruments and individual items,
group management/proportional variability, documented exact matching,
qualification through history, remaining qualification, the stopped portion's
loss of qualification, a proportion of the entire instrument, zero-value/cost
origins, the finite linear measurement model, no historical ineffectiveness,
complete values/events, continuing loss recoverability, complete stopped-loss
facts, inventory/NRV and pretax/no-other-activity scope. Supplied findings do not
certify that these facts hold for an actual company or under current law.

History and later `measure` records have unique id, operation, date, price,
one signed `instrument_values` entry per active instrument, one signed
`item_changes` entry per active item, and facts_available_on. Active origin j
must have actual value q_j*(price-f_j) and opposite item change. After stopping,
item change uses its continuing quantity. The entire actual instrument stays
owned. At each admitted measurement active continuing origin gains have the
same weak sign; unsupported opposed histories refuse. Measurements run from
the first origin to maturity with nondecreasing dates and no future facts.
The relationship-level signed lower-of must agree with the full effective-gain
trace; summing independent lower-of reserves is not an alternative algorithm.

Stop has id, date, origin_id, quantity, highly_probable, expected,
unrecoverable_loss and facts_available_on. It follows the last history measure
on that date. Quantity is positive and strictly below the named origin quantity.
Highly_probable must be false. The directly matched gross frozen amount is
z*(stop_price-f_k). Continuing dates/prices remain unchanged. Expected cash
flows retain their reserve except a supplied unrecoverable loss; no-longer-
expected cash flows release the full signed reserve immediately, with no
simultaneous additional loss claim.

After contains `measure` records or `assess_stopped` records with id, operation,
date, expected, unrecoverable_loss and facts_available_on. Assessment follows a
same-date measurement (the stopping measurement also qualifies). A nonnegative
loss may release only a remaining negative stopped reserve. Cancellation is
irreversible here. Future changes on the retained stopped instrument portion
enter profit independently of that frozen reserve. No optional re-designation,
second stop or continuing-reserve impairment calculation is supplied.

Closing has date, quantity, unit_price, supplier_cash, settlements and
facts_available_on. It follows a maturity-date measurement. Quantity equals
continuing units plus stopped units only if still expected. Supplier cash is
the full purchase price; settlements map every actual instrument ID to its
full latest signed value. Supplier payment occurs first, then each gross
instrument flow in origin order. Every intermediate cash balance must be
nonnegative. Transfer the attached signed reserves to inventory basis; close
all actual derivative balances and reserves. Tax, cash-flow activity, netting
permission, other inventory costs and later sales are not calculated.

Success preserves context, origin identities and original measurement terms,
the stopped gross/remaining/released trace, chronological balance snapshots,
per-instrument assets/liabilities, proposed debit-positive journals and gross
cash origins. Opening cash is also capital. Before closing, the checked identity
is full derivatives = continuing reserve + stopped reserve + profit. After
closing, cash+inventory=capital+profit. Input/source changes refuse atomically.
Parser bounds (1–8 origins,1–32 history rows,0–32 later events) are convenience
limits, not accounting or scientific defaults.
