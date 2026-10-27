# First following-period assessment audit

24 October2026. MC05/11/13/16/24/26/28/35;G2/G4. The old cumulative formula
paid=current expense minus payable is wrong after carry: expense starts at zero
while payable can be positive. The new method must first reconcile carried
opening payable minus actual new-period payments to remaining payable,then add
the independently calculated new tax. Cash must not change at assessment.

The only supported incoming caller has no new-period tax assessment. Its payment
kernel cannot exceed the carried liability,so every completed tax payment belongs
to that original vintage. This permits exact automatic attribution from the
recorded trace without guessing payment allocation. The first new assessment
creates a second vintage; later payments will need a new explicit allocation
interface. Refuse a stopped incoming execution rather than silently assess its
unfinished request. Preserve its full result for inspection.

Reuse the checked information catalog/reconciliation on a population formed from
the new opening and completed states. Reuse the exact close-day loss transition
on the carried loss opening,with no provisional supersession. The computation
wrapper must label that scope accurately. Loss availability comes from the
validated opening cursor; all generated losses become available only at the
new exclusive endpoint. Prior recognition capacity is irrelevant to current use.

Assumptions: the explicitly selected same entity/regime,no credits/refunds/
prepayments,first assessment only,zero prior new-period current expense and
directly traceable carried payments. These are supported-subset choices,not tax
defaults. Missing/false declarations refuse the asserted method. Exact opening,
payment-vintage,loss,journal and statement checks are primary. Counts and dates
are explanatory. Annual/source admission remains false;new deferred assessment
and broad multiyear execution remain open.
