# Preserve receivable term versions and assessment basis

25 October2026. S2–S4;MC02/05/08/10–13/16/19–22/24–28/30/32–35.
Baseline: frozen ReceivableLifecycle/1 and the two-chart overwrite discriminator
under amendment-semantics-audit-20261025. Question: can a date-only prospective
term event change later assessment meaning while preserving the earlier one?

Audit passes for a new explicitly versioned reference. Overwriting current due
or resetting historical overdue fails the target. Source corrections remain
separate as-of reconstructions. Reuse typed memory map insertion and exact
book/context/event checks; do not change frozen validators or infer legal truth.

Proposed minimal state: per-claim immutable term records with ID, due, effective
date, originating event and predecessor; explicit current-term ID; assessment
records carrying date, remaining, overdue and term ID. Dates alone cannot
resolve same-day ordering: define amendments before assessment and refuse sealed
assessment-day retroactivity, following the existing clock. Effective dates
must be prospective from the current state and within the declared period.
Retain actual event chronology separately from source availability/ingestion.

Start with an explicit migration of a checked lifecycle snapshot. Preserve all
claim identities, balances, old assessment values and source/old-state hash.
The old due date supplies one initial term only under an explicit no-prior-
amendment premise; absent history stays unknown rather than inferred complete.
Return provisional state, never silently execute migration or mutate sources.

Discriminator: old dueJanuary31, assessed overdue20 atFebruary28; extend on
March10 toApril30. Earlier assessment remains20 under old terms, a later
March assessment is0 under new terms, balances/flows unchanged. Check both
charts, repeat extension, receipt after extension, carry and exact replay;
negative cases include stale state/term, duplicate event, backdating, unknown
claim, mismatched customer, missing premise, changed principal/consideration,
ambiguous predecessor and changed replay output. Do not import impairment,
interest, modification gain/loss, enforceability or real-source admission.

Promotion criterion: exact typed state/history and independently expected
assessment outputs, with immutable refusal. Balancing and schema validity are
vetoes only; no general accounting inference. Record default provenance and
remaining limits in the result. First inspect the actual typed mutation and
carry interfaces, then implement the smallest compatible module. Continue to
matched authoring only after the state contract passes. No forecasting or
external engagement. Save evidence under receivable-term-history-20261025.
