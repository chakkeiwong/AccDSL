# Explicit tax-vintage continuation

The request contains the complete first-assessment request, its digest and an
ordered list of operations. Recompute that assessment before continuation.
Selected native events use the existing full-state return/lease adapters and must
occur on or after the assessment's exclusive endpoint. An allocated tax payment
may occur on the recorded assessment day, subject to state chronology and the
financial period. Event ids remain unique throughout the book's lifetime.

An allocated_tax_payment event has id, date, amount, authorization and allocations.
Each allocation contains vintage_id and amount. Amounts are positive exact
rationals; vintage ids are known and unique within one payment; their sum equals
the total payment. Each amount is bounded by that vintage's outstanding balance,
and the total by shared cash. There is no implicit FIFO, proration or credit.

A payment debits income_tax_payable and credits cash. It changes no expense,
loss lot, deferred balance, component or finding. Each affected vintage receives
a dated settlement with event identity, operation digest and total payment.
Zero-balance vintages and all prior settlements remain. Across all vintages,
opening payable plus new assessment minus settlements equals closing payable.
Summed settlements match each dated current-period tax cash flow exactly; closing
vintages sum to aggregate payable. These checks run before and after every event.

Results preserve the actual financial opening, complete assessment result, full
26-account state, assessed endpoint, loss state, findings, completed trace,
remaining operations and four statement ties. Failed operations preserve the
successful prefix. Apply recomputes and compares the complete result. The result
is provisional and never establishes annual admission. Later reassessment,
new-period deferred recognition and repeated carry remain separate dependencies.
