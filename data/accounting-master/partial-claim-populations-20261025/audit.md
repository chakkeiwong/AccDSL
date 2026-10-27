# Audit: reuse partial collections and partial company state

25 October 2026. MethodCollections/1 already represents a complete collection
as status=complete/rows and a partial collection as status=partial/rows/reason.
Its uniqueness diagnostic remains unresolved for a partial empty collection and
satisfied for a complete empty one. CompanyMemoryTypes/1 instead types actual
map members and gives an empty map its ordinary empty meaning. Do not change
either frozen implementation or introduce a second membership-status system.

Attach an existing MethodCollections value to each relevant constraint in
SourceConstrainedCompanyStateDraft/1. Retained source adapters always emit a
partial population with no identified rows and an explicit reason. They accept
no caller population override. Query results preserve their derivation: observed
displays and any explicit rounding interval come from the original partial
state; count, gross remaining amount and settlement schedules are unresolved.
An empty list of observed rows is not a claim that there are no actual rows.

Use separate constructed MethodCollections examples to show complete empty and
complete identified populations. Their counts are conditional on caller-supplied
completeness and unique known IDs; amounts require known nonnegative exact
rationals. A due date describes a contractual term, not a predicted payment.
Return no simulated receipts, journal or CompanyBook. Partial memberships
cannot yield a total merely because all observed amounts are known. No net
source caption is equated to this gross outstanding amount.

Comparator: exact original partial-state output, native collection assessment
and independent finite counts/sums in constructed examples. Pass criteria:
preserved 54 constraints and all dependencies on combined view, unknown versus
empty discrimination, duplicate identity refusal, tagged missing amount/date
handling, explicit rounding-premise preservation and replay mismatch refusal.
Source corruption or invented completeness veto the adapter. Missing source
facts veto dependent queries while allowing display and independent work.
This is a deterministic engineering design; no new research or numerical
default, actual-company feasibility claim or accounting admission is made.
