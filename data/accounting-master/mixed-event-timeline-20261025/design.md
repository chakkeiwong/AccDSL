# Mixed native-event and decision timeline

MixedEventTimeline/1 accepts a complete PeriodBook/1 and root fields
profile,id,expected_state_sha256,context,scenario,schedules,operations. The first
six non-profile fields have the checked decision scheduler meanings. Schedules
use StateDecisionSchedule/1 unchanged. Each supplied operation entry has
id,priority,date,operation. Its date must equal the native event's own date.

Initial operation adapters: allocated_tax_payment and partial_inventory_sale.
Both have direct calendar dates and are already supported by the unchanged
AnnualInventoryProgram/1 transition. Their complete field shapes, canonical
amounts, findings/authorization records and allocation identities are checked
statically. Actual remaining stock, payable,vintage availability,funding and
performance conclusions are checked by the native transition on the book at
that action. Unknown/false findings remain unresolved/unsupported there.

Other operation shapes remain unsupported by this timeline. In particular,
current assessment uses an interval/activity-through date, deferred assessment
binds measurement to a state hash, carry changes period boundaries, and nested
return/lease events have their own envelope. No arbitrary date or changed
measurement hash is supplied to make them fit the first adapter.

Validate all operation structures and decision templates before executing. Merge
calendar occurrences and supplied native entries by date and explicit priority.
Same-day priority ties remain unresolved, including a native/decision tie. Event
identities must be unique across both populations. Caller operation IDs and
schedule names are distinct namespaces; native event IDs remain explicit.
The root permits64 total actions, including at most32 native entries and the
existing scheduler limits. Input array order is not economic order.

At a decision, materialize the existing typed request against the current book.
At a supplied operation, call the existing native transition unchanged. The
timeline's authored_closed_path premise covers both populations. A false guard
advances the timeline cursor without changing the book. On refusal retain exact
prior state,all successful/no-action traces,the failed entry and request/result,
and the remaining timeline. Full financial statements are generated from that
prefix. Fiscal completion,source/accounting admission,commit and durability stay
false. No restart or production execution guarantee is added.

Discriminating case: carried tax payment4 changes cash452 to448 and payable
41/4 to25/4. The policy enables a1-unit sale only when cash is below the authored
threshold450. Payment before decision sells1 unit at15, ending cash463,total
inventory70 and selected-lot carrying10. Decision before payment takes no action,
ending cash448,total inventory80 and lot20. The threshold is a synthetic rule,
not an estimate,financial recommendation or universal cash reserve.
