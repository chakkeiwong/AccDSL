# AddedInstrumentLayers/1

The closed request has wire,operation,baseline_hedge,context,opening_cash,
findings,events. Wire is AddedInstrumentLayers/1; operation report. Numbers
are canonical reduced rational strings. Opening findings are exactly
legacy_single_whole_instrument,no_other_cash_or_earnings,pretax_scope, all true.
The source/input lock resolves before the pinned RepeatedItemRebalancing/1
module replays baseline_hedge; the baseline must end with measurement and its
context must equal request.context. Its zero-origin derivative is the one
original instrument. Opening cash/capital is additional synthetic funding;
baseline derivative/reserve/earnings keep their replayed amounts.

Every event has id,operation,date,context,findings. Context must match; event IDs
are unique across the baseline and extension. Dates are nondecreasing and
strictly before maturity. add_instrument additionally contains instrument with
id,nominal,acquisition_value; nominal is positive, value nonnegative, and the
instrument ID is new. It follows a same-date measurement. All eight ADD
findings in reference.py are true, including unchanged objective, changed
relationship, updated documentation, eligible whole external non-option,
simultaneous acquisition/designation at equal fair value and no fees.

The addition records its own designation date, initial value and nominal and
posts debit derivative/credit cash for initial value. It changes no cumulative
hedge gain, item value, reserve or profit. The explicit cash order must remain
funded; later receipts cannot repair an unfunded earlier purchase.

A measure event adds price and values. The values map supplies exactly every
current instrument ID, including original, with signed current fair values.
Its six MEASURE findings match the existing single-price/zero-discount profile.
Nominal quantities are descriptive supplied data; the endpoint is not a pricing
model. It sums each value less its individual origin to derive cumulative gain,
retains all original item-layer origins, and applies the cumulative signed
lower-of test for offsetting values. Zero values give zero reserve; nonzero
same-sign cumulative instrument/item changes are unsupported. Difference
journals preserve reversals of earlier ineffectiveness.

State/trace retains current marks/origins and nominals, fixed item layers,
cash, net derivatives, gross derivative assets/liabilities, cumulative gain,
item change, reserve, profit, acquisition basis, pre-tax equity and per-leg
debit-positive books. Net value equals acquisition basis plus hedge gain;
cash equals opening funding minus acquisition basis; gross assets equal
liabilities plus equity after including cash. Cash movements carry acquisition
origin; financial cash-flow presentation is not assessed in this measurement
profile, and no statement offsetting authorization is inferred.

Response fields are wire,status,reason,baseline,state,trace,journals,flows,
mutations. conditional_complete reports no actual posting. Refusals return null
baseline/state and empty arrays even when earlier steps were valid. Malformed
or contradictory fields reject; missing facts/bytes are unresolved; other
methods, false findings and funding shortages are unsupported. Existing owned
derivatives, negative acquisition values, fees, removed instruments/items,
settlement, excluded components, tax and company presentation require separate
methods. An empty extension is a valid replay-only report.
