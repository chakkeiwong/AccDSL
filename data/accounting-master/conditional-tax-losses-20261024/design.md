# Conditional loss lots: explicit close-day use, expiry and conservation

24 October2026. S2–S4;MC05/11/13/16/24/26/28/35;G2/G4.

## Audited rule selection

The scoped code search found no reusable loss-carryforward evaluator in scripts
or the inspected corporate-residual methods. Existing taxlots.remeasure concerns
deferred recognition,not loss utilization. Reuse the frozen exact reconciliation
request/result and known/unknown provenance records; implement a separate pure
ledger. No legal or actual taxpayer rule is being inferred.

The selected hypothetical model is close_day_explicit_use_v1. All supplied usages
are evaluated at activity_through,the last day of the interval. A lot with an
exclusive expiry on or before that day is unavailable. A lot expiring exactly
at end_exclusive can be used on the prior day; any unused amount then expires
before the next opening. This convention is explicit and replaceable; it cannot
represent intra-period usage or jurisdiction-specific ordering/caps by default.
No-expiry is an explicit assumption,never the consequence of an absent field.

New losses arise at the exclusive endpoint and become available in the next
interval. They cannot be used in their generation interval. Their expiry must
be later than availability. Negative taxable profit requires zero usages and
an identified generation request with affirmative eligibility and explicit expiry.
Nonnegative profit requires generation=null and explicit allocations. A caller
supplies a nonnegative interval cap; no statutory percentage or FIFO is invented.

## State, binding and result

The closed state carries profile,context,jurisdiction,regime,cursor,lots,seen,
history and an opening_inventory declaration. Scope strings and context must
equal the bound reconciliation information. The cursor equals interval start;
the next cursor equals interval end. This is loss-ledger continuity,not proof of
financial-state continuity across independently declared native books.

Each unique lot carries id,origin_reference,available_from,expiry,original,
remaining,used,expired and eligible. Exact nonnegative rational quantities obey
original=remaining+used+expired. Lots remain even at zero,preventing identifier
reuse. Expiry is either a dated exclusive endpoint with provenance or an explicit
none declaration with provenance. Eligibility and opening inventory use explicit
known Boolean/unknown reason records. Assumption/source-reference strings are
preserved but not authenticated. Unknown/false relevant findings yield unresolved/
unsupported; they do not mutate the ledger.

A step binds exact state and reconciliation request digests,step_id,model,
utilization_cap,uses and generation. All uses have unique lot identities,strictly
positive rational amounts and no implied allocation. Total usage cannot exceed
any lot's remainder,the cap or positive taxable profit. Only lots available by
interval start and eligible through the usage day can be consumed. Every active
opening lot's eligibility remains explicit even when not selected for use.

The pure proposal retains the complete original reconciliation result. It includes
the next ledger,per-lot movements,exact totals and conditional gross tax after
usage. No negative current tax is emitted. A new eligible loss creates a quantity,
not a recognized deferred-tax asset or cash refund. Apply recomputes the whole
proposal and compares canonical bytes (Boolean and integer remain distinct).
There is no durable commit or concurrency guarantee.

Required step identity: opening remaining+generated=used+expired+closing remaining.
Each lot's original=remaining+used+expired identity continues after every step.
History records step id,interval,reconciliation digest and quantities;seen and
history identities must agree exactly. Correct supplied opening records are
conditional premises,not independently verified past tax filings.

## Evidence limits and stop conditions

Exact conservation,scope/cursor/origin binding,recomputation,expiry edges and no
double use are primary criteria. Missing/duplicate IDs,overuse,stale cursors,
changed origin amounts and false/unknown eligibility veto the affected proposal.
The original -19 reconciliation should generate19 only under explicit eligibility.
Distinct future hypothetical inputs exercise full/partial usage and expiry;
their reports are replayed and are never called original native comparators.
All flags for posting,cash refund,deferred recognition,legal/source admission,
native financial carry and annual readiness remain false. Broader accounting
completion is still open after a successful loss-ledger step.
