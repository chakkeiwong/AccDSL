# HedgeInventoryClose/1

The closed request contains wire, operation, hedge, context, opening_cash,
purchase, settlement, sale and findings. Wire is HedgeInventoryClose/1;
operation is report. Numeric values are canonical reduced rational strings.
The complete RepeatedItemRebalancing/1 request is replayed internally after
the source/input lock resolves; no supplied terminal state is authoritative.
The context must equal the accepted hedge context.

Purchase is date, quantity, unit_price, supplier_cash; settlement is date,
cash; sale is date, quantity, cash. Purchase and settlement occur on the
terminal measurement date, with no later hedge event. Both quantities equal
the sum of designated layers, price equals the terminal observed price,
supplier cash equals quantity*price and settlement cash equals the signed
derivative amount. Sale occurs on a later calendar date. Positive settlement
cash is a receipt, negative is a payment. Opening cash and sale proceeds
are nonnegative. Negative supplier/adjusted inventory cost is not supported.

The twelve exact required findings are declared by reference.FINDINGS. They
cover full receipt, inventory/sale recognition, complete acquisition costs,
NRV support, full permitted settlement at carrying value without fees or
intervening valuation, full sale, no other cash/earnings and pre-tax scope.
Missing findings are unresolved; false findings are unsupported. These
findings are inputs, not conclusions inferred from the calculated amounts.

The operation constructs a pre-tax opening subledger from opening cash/capital
and the replayed derivative/reserve/ineffectiveness. It then processes purchase,
settlement, direct basis transfer and sale, retaining intermediate books and
separate operating cash origins. Every journal and book must balance, and cash
must remain nonnegative under this declared sequence. Direct basis transfer
affects inventory and reserve only; no earnings/OCI-reclassification amount
arises. No tax is calculated. Report scope is cumulative through the sale
date; it is not one annual income statement if dates cross year-end.

Result contains wire,status,reason,hedge,report,stages,journals,flows,mutations.
Positive status is conditional_complete. Rejected input means wrong shape,
inconsistent amounts/context/timing or corrupt source bytes; missing bytes or
facts are unresolved; other methods/false findings/funding failure are
unsupported. Refusal returns null hedge/report and empty remaining arrays.
No accepted or refused report writes actual books. Extra fields requesting a
second transfer or injecting a terminal reserve reject; this does not claim
cross-request persistent idempotency.

Partial receipts/sales, cancellations, changed valuations, tax, NCI, full-company
consolidation, alternate funding order and runtime integration require separate
methods. Source versions are historical and application-specific findings
remain caller responsibilities.
