# AlignedZeroCostCollar/1

Read-only `report` for one fully aligned purchased-call/written-put combination
and one terminal inventory purchase. Historical EU2023/1803 IFRS9 profile only.
The exact request fields are wire, operation, context, opening_cash, quantity,
opening_spot, call, put, findings, quotes and closing. Context has exactly
entity, book, currency, underlying, start, expiry, information_date and rule.
Identifiers are nonempty strings; ISO dates have start < expiry <= information
date. Rule equals `EU2023/1803-original-IFRS9`. Call and put each have id,
quantity, strike, expiry, underlying and premium. IDs differ; quantity,
expiry and underlying match the purchase; 0 < put strike < call strike;
opening spot lies between them. Positive equal premiums are actual gross flows.

Canonical rational strings encode amounts. Quantity and opening cash are
positive. Quotes form a nonempty strictly increasing sequence after start and
through expiry, ending at expiry. Each quote has date, spot, call_time, put_time,
call_value, put_value, item_change, call_id, put_id and facts_available_on.
Both per-leg time values and spot are nonnegative; actual values must equal
intrinsic plus time. Complete information must be available by the context
information date. The signed hedged-item risk change must offset combined
intrinsic exactly for this fully matched profile. Both expiry time values
must be zero. No monotonic-time-value assumption is imposed.

The exact true findings are external_contracts, not_net_written,
eligible_designation, highly_probable_purchase, combined_risk_alignment,
complete_valuation, zero_discount_no_carry, credit_not_dominant,
continuing_qualification, recoverable_reserves, inventory_recognition and
pretax_no_other_flows. They are supplied admission facts, not inferred from
prices or equal premiums. Null is unresolved; false is unsupported.

Closing has date, quantity, supplier_cash, call_receipt and put_payment. It
must occur at expiry for the full quantity; gross supplier cash equals terminal
spot times quantity, call receipt equals the call's actual terminal value, and
put payment equals the put's positive liability. Funding order is call premium
payment then put premium receipt, and at expiry supplier payment then call
receipt then put payment. Any intermediate shortfall is unsupported.

The journal representation uses debit-positive signed balances: cash, call_asset,
put_liability, inventory, capital, intrinsic_reserve and time_reserve. Liability,
capital and reserve credits are negative in balances/entries; reported reserve
and liability amounts have their ordinary financial signs. Every proposed
entry sums to zero. Initial capital equals opening cash. Time reserve is signed
call time minus put time; intrinsic reserve is call intrinsic minus put
intrinsic. At settlement both actual legs clear; basis adjustment clears each
reserve separately. Profit remains zero under admitted exact matching.

Successful output is conditional_complete with stages, proposed journals,
cash flows, closing state and context. posts=false and mutations=[] always.
Malformed or inconsistent requests, source changes and future information are
rejected; missing facts are unresolved; outside-profile claims unsupported.
Every refusal returns result null and no stages, journals or flows. No actual
posting, valuation algorithm, probability model, tax or cash-flow-activity
classification is provided. General mismatched/opposed components and stopped-
item reserve attribution remain separate obligations.
