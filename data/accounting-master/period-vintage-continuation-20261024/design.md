# Period-aware continuation of a carried tax book

Recompute the complete second assessed boundary from its request and digest.
Apply ordered native return/lease events or allocated_tax_payment events to the
actual new opening. Native chronology begins at the new financial start;all
events must be chronological,in period and lifetime-unique. Use the checked
full26-account financial kernels. Native events cannot write tax accounts.

Preserve historical tax_vintages exactly. A period_vintage binds its stable id,
prior-vintage digest,period and opening payable to the frozen historical closing.
Its closing payable equals opening minus only current-period settlements. Each
settlement has event id,date,positive amount,total payment,operation digest and
financial-result digest. One payment may split across unique existing vintages;
allocations must sum to total,not exceed per-vintage outstanding or shared cash.
Known affirmative authority is required. No automatic allocation convention.

Across current-period rows,sum closing equals aggregate payable. Sum allocations
for each payment matches its one dated operating tax cash flow. Old settlements
never enter these identities. Current/deferred expense and loss quantities stay
unchanged by payments. Failed operations preserve the complete successful prefix
and remaining request sequence. Four statements use the actual new opening.

Results include complete boundary predecessor,historical/period vintages,opening,
after,trace,remaining operations,loss state,archive,findings and unassessed current/
deferred status. Pure apply compares the complete result. Assessment and arbitrary
annual recurrence remain separate contracts;do not flatten older liabilities.
