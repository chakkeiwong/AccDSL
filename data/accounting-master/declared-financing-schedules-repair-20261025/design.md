# Verified financing schedules and finite interest coverage

MC02/06/11/13–18/23–28/32/34/35. DeclaredFinancingSchedules/1 accepts full v2
program/result,selected successful report ID,exact financing role map,memory
pointers,synthetic policy and finite interval table. Recompute full execution;
select report or preclose carry report;derive current-period opening from the last
successful carry. Stopped programs may expose earlier successful reports.

Rebuild the supported financing definitions from the program's original opening
and exact supplied policy/intervals,not from registry nicknames. Match method hashes.
Within the selected period,retain every supported gross account movement,typed
inputs,operation/event identity,date,request/result hash and cash activity.
Schedules:debt,interest payable,capital,retained direct equity,dividend payable.
Credit-positive amounts use negative ledger signs;retained direct movements may
legitimately decrease and are distinct from current-period profit. Reconcile each
opening plus increases less decreases to the selected closing. Derive interest
expense,paid interest,dividend declarations/payments and contribution separately.

Unknown methods with any nonzero gross posting to scoped accounts or interest
expense must refuse classification even if the event nets to zero. Unknown methods
that change cursor or tracked debt also refuse. Other operating events are
retained as out-of-scope with exact hashes;their financing effect must be zero.
Compare tracked debt with ledger throughout. Supported methods retain the explicit
interest cash activity;sum financing-related cash by actual activity and origin.

Interest coverage is a separate result:retain the opening cursor and every executed
[start,end_exclusive) interval. Verify successive endpoints and actual event dates,
then expose the cursor at the selected report against cutoff+1. A missing suffix,
opening carry debt/cursor mismatch or coverage before current-period opening must
not be labelled complete merely because all schedules reconcile. Return explicit
coverage gap and needs;do not invent interest for unexecuted dates or fail unrelated
reconciled monetary schedules. Generic report/carry stays provisional. Unknown
cursor movement refuses rather than being relabelled a gap.

Next-period examples may pay carried interest or repay debt at the opening boundary
without an additional declared interval. Those movements remain reconciled while
the missing current-period interest interval stays visible. No future interval or
expected future-state hash is invented. General multi-year calendar authoring is
still open. Financial note completeness/source admission stay false for all cases.

Also supply DeclaredWorkingCapital/2 as the same schedule algorithm bound to the
verified v2 program. Compare its complete schedules,period selection and cash
diagnostic with v1 on a compatible operating program;changed protocol/provenance
identities are expected. On the combined book,its four-account bridge leaves2.2
of unexplained operating cash,which agrees with the independently derived unpaid
interest increase under the selected operating-interest policy. This explains the
example only;no general indirect cash-flow rule follows.

Preserve maturity,covenants,fees,valuation,shares outstanding,distribution law,tax,
source population and note completeness as unresolved. Exact movement schedules
cannot answer those missing contract/source questions.
