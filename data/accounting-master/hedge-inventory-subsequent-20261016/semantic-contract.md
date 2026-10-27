# HedgeInventorySubsequent/1

Closed top-level fields: wire, operation, hedge, context, opening_cash,
purchase, settlement, findings, cost_formula, events. Wire is
HedgeInventorySubsequent/1, operation report, cost_formula weighted_average.
All numbers are canonical reduced rational strings. Context equals the
internally reconstructed RepeatedItemRebalancing/1 context. The byte resolver
must supply every input-lock file with its exact digest; the checked hedge
module bytes are executed directly. No caller-supplied opening cost or reserve
is accepted.

Purchase(date,quantity,unit_price,supplier_cash) and settlement(date,cash) must
equal the terminal measurement date, full designated quantity, price, supplier
cost and derivative carrying value. The thirteen exact Boolean findings in
reference.FINDINGS cover the whole purchase, acquisition recognition/cost/NRV,
full permitted carrying-value settlement, no later hedge valuation, no other
cash/earnings, pre-tax scope, an interchangeable uniform batch, no other
inventory/purchases and consistent nature/use. These are supplied conditions.
Opening funding is nonnegative and must support purchase before settlement.

Events are ordered by nondecreasing date after acquisition. Same-date order is
the list order; IDs must be unique and cannot reuse purchase, settlement or
basis. Empty events is a valid unsold report. Sale fields are id,kind,date,
quantity,cash,recognition_satisfied; quantity must be positive and no greater
than remaining units. Cash is nonnegative. NRV fields are id,kind,date,per_unit,
valuation_satisfied,uniform_unit_nrv,recovery_conditions_met. The NRV must be
nonnegative; valuation and uniformity findings must be true. A negative change
in allowance requires true recovery_conditions_met; null is permitted only
when no recovery occurs. Every event requires positive remaining inventory.

Acquisition transfers the entire signed reserve directly into gross inventory
cost. Subsequent unit cost is fixed at adjusted cost divided by initial units.
Sales remove gross cost and allowance in the same unit fraction; carrying
amount is expensed. NRV sets allowance to remaining units times the positive
difference between original unit cost and current supported per-unit NRV.
Reversals reduce inventory expense and cannot exceed the allowance for units
still held. Each stage reports quantity, gross cost, allowance, inventory,
cash, cumulative pre-tax profit/equity, cost of sales, net NRV expense, reserve,
derivative and all signed debit-positive books. Journals, stage books, equity
and gross cash reconcile exactly. No rounding rule is inferred.

The response contains wire,status,reason,hedge,report,stages,journals,flows,
mutations. Positive status is conditional_complete. Malformed or contradictory
requests and changed bytes reject; missing findings/bytes are unresolved;
false findings, other methods and funding shortfalls are unsupported. Refusals
return null hedge/report and empty arrays, even if an earlier event was valid.
No report mutates books. Annual presentation, revenue recognition derivation,
tax/NCI, general NRV estimation, other cost formulas, new purchases, partial
forecast realization and persistent idempotency are separate methods.
