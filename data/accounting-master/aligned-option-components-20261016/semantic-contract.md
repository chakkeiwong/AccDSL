# AlignedOptionComponents/1

Read-only complete transaction-related option/inventory report. Source support
is the historical EU2023/1803 original IFRS9.6.2.4(a),6.5.11/15,B6.5.5/32–33.
This profile does not change the older AASB-profile component examples.

The exact request contains wire,operation,context,opening_cash,opening_price,
premium_cash,findings,item,actual,aligned,quotes,closing. All amounts are
canonical reduced rational strings. The purchased call and hypothetical call
have separate identities and positive initial total time values. Both quantities
equal the purchase quantity; expiry matches the fixed reporting context. The
aligned strike equals the item's hedged price level. Initial spot is no higher
than either strike, so initial intrinsic values are zero. Premium cash equals
only the actual initial time value. Explicit findings admit terms, component
values, qualification, recoverability and transaction-related inventory.

Each dated quote binds both contract IDs and supplies spot, both total time
values and both total option values. Intrinsic values are independently computed
as quantity*max(spot−strike,0). Total values must equal intrinsic plus time.
Quotes are strictly dated and end at expiry with both time values zero. No
quote may exceed its inception time value: only the common cumulative-loss
profile is admitted, even though individual period changes may reverse.

The intrinsic reserve is the smaller actual/aligned intrinsic gain; the excess
actual intrinsic gain is profit. When initial actual time value is higher,
the cost reserve equals the cumulative aligned change. When initially lower,
it equals the negative of the smaller cumulative actual/aligned loss. Actual
cumulative time-value change less that reserve is mismatch profit. Equal
initial values require matched strikes and matching time values at every quote.
Equal initial values with unmatched terms, signed collars and opposed
cumulative changes require another method.

Measurement entries change only the actual option asset, two distinct reserves
and earnings. No hypothetical option asset or cash flow is posted. At expiry,
the purchase quantity/price and gross supplier payment must agree with the
last quote; actual settlement must equal the actual option value. Supplier
funding is required before option settlement. Transfer both reserves separately
into inventory basis, retaining their signs. Gross cash is exactly actual
premium, supplier payment and actual option settlement.

Success returns conditional_complete, the inception comparison branch, all
measurements, balanced proposed journals, cash origins and the closing
inventory/cash/equity bridge. posts=false and mutations=[] throughout. Unknown
findings/source bytes are unresolved; false admission or outside-profile inputs
unsupported; malformed or contradictory identities rejected. Refusal yields
no partial measurements, journals, flows or closing result.

No pricing algorithm, actual legal qualification, current-law admission,
tax, cash-flow activity classification or independent domain acceptance follows.
The supplied hypothetical terms identify the risk being measured; a balanced
book does not establish that those terms are correct.
