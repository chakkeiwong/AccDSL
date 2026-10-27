# Pre-implementation audit — 24 October2026

MC05/11/13/16/24/26/28/35;G2/G4;S2–S5. Question: can the full following-period
current/deferred-assessed book cross its next contiguous boundary without losing
liability/payment or recognition history? Comparator:complete fresh deferred
result and original current-year statement profit. No event continuation is
claimed by this initial boundary profile.

The older carry is incompatible with this predecessor and omits distinct vintage
state. The old vintage invariant also links every lifetime settlement to current
period cash flows. Clearing settlements or replaying them as new flows would be
wrong. Resolve this by retaining the complete tax_vintages byte-for-byte as
historical records and creating explicit period_vintages. Each period row has
stable id,prior_vintage_sha256,new period,opening payable equal to prior closing,
empty current-period settlements and equal closing payable. Historical paid
amounts remain in the predecessor and unchanged vintage record,not in new flows.
New operations are excluded from this boundary request until a compatible
continuation is separately audited. This is a useful scoped first step,not a
claim that general annual simulation is complete.

| Choice | Provenance/justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| No operations on boundary profile | Active plan requires boundary first | Old invariant accepts stale history as new cash | Extra operations refused;zero new movements | Reviewed staging choice |
| Separate period ledger with stable ids | Exact preservation of past settlements | Lifetime/history loss or cash duplication | Prior vintages exact;period settlements empty | Derived engineering design |
| Actual income transfer | Existing debit-positive carry convention | Wrong sign or inferred profit | Independent negative,zero,positive controls | Reviewed default |
| Conditional carry with unknown findings | Existing provisional mission scope | Caller assertions promote annual readiness | All flags remain false across known/unknown findings | Reviewed scope |
| Prior recognition archived | Fresh-deferred contract | Capacity silently renews | Both new assessments unassessed;history exact | Reviewed requirement |

Primary criteria:independent retained-earnings arithmetic,balanced journal,
unchanged permanent balances and components,exact tax/loss/recognition history,
explicit period partition,four zero-movement opening ties,source binding and
complete apply. Missing endpoint/loss completion,noncontiguous timing,wrong
oracle or lost history veto recording and trigger repair. Unknown annual/source
findings remain promotion vetoes,not continuation vetoes. Counts/runtime are
explanatory. No current law,actual company,annual readiness or general repeated
execution claim. Preserve tests,requests/results,source lock,manifest and replay.
