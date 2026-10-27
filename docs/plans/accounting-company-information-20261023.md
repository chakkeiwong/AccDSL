# Assumption information for conditional company paths

23 October 2026. S3/S4; MC05/10/13–16/18/24/25/28. This work follows the
partial-path exchange. Version 3.52 remains the current not-ready manuscript.

## Skeptical audit and research intent

Question: can an information query distinguish an available source opening from
an unavailable, unverified or later-authored simulation assumption? The baseline
is the complete-path admission, which correctly leaves all non-archival path
queries unresolved, and the 119-check partial/revision exchange. A future year
in an input is an economic period, never evidence of when that input was known.
No retrospective declaration may turn the synthetic example into historical
forecast evidence. E3 remains deferred.

The mechanism under test is an explicit, content-bound information declaration
for the path header and each authored annual definition. Whole-year snapshots
are deliberately coarse: all authored fields are covered, and revising any one
field requires the exact changed definition's own declaration. The unchanged
definitions can reuse their declarations. Source timing is checked separately.
This design tests information selection, not identity authentication.

Primary criterion: all required components must bind exact canonical bytes and
have eligible evidence at the requested cutoff; a late component makes the
query ineligible, missing or unverified timing makes it unresolved. Source
eligibility alone never promotes a path. Investor views use publication timing;
system views require ingestion and acceptance. Neither infers timing from an
economic date. Missing authoring timing remains unresolved in both views.

Promotion vetoes: incomplete or duplicate coverage, wrong component identity,
retrospective dates treated as verified observations, ambiguous date precision
treated as an instant, wrong view/audience, or changed protected evidence.
Unavailable immutable baseline bytes are a continuation veto for dependent
checks; a failed candidate triggers repair. Counts and duration are explanatory.
Passing establishes only synthetic temporal-selection consistency. It does not
establish historical source vintages, real author identity, a feasible forecast
protocol, or accuracy. No model comparison or default policy is selected.

## Defaults and early diagnostics

| Choice | Provenance and justification | Failure mode | Early diagnostic | Status |
|---|---|---|---|---|
| Header plus annual snapshots | Current closed path schema; exhaustive without a new leaf ontology | One recent field unnecessarily excludes an otherwise earlier field | Whole-year granularity stated; changed and unchanged years queried separately | Bounded design hypothesis |
| Exact UTC instants or calendar-day precision | Existing source-time boundary | Invented intraday certainty | Before, within and after publication day | Reviewed local convention |
| Authored, public, ingested, accepted times remain separate | Mission economic/report/public/system timing requirement | Acceptance mistaken for publication | Public and private/system fixtures differ | Required distinction |
| Synthetic declarations only | All current path inputs are authored examples | Fixture dates mistaken for historical observations | Synthetic marker and real-world-admission false everywhere | Test convenience |
| Fixed settlement allocations | Existing operation input semantics | Price change silently regenerates collections | Revised identity cannot reuse old component declaration | Protected baseline |

Implement under data/accounting-master/company-information-20261023. Save
schemas, fixtures, adverse evidence, code hashes, run manifest and result note.
CPU-only deterministic verification, explicit --record and read-only replay.
Audit verdict: proceed. The next independent work is explicit policy authoring;
the full text frontend and broader accounting/sector methods remain open.

Chronology audit: events may share an exact timestamp, so the relation is
authored <= published and authored <= ingested <= accepted. A day represents
[midnight, next midnight), while an instant is a singleton. If the earliest
possible earlier event is at or after the later event's exclusive day end,
the order is impossible. If the earlier event's latest bound exceeds the later
event's earliest bound, order remains unresolved. Equality of exact instants
is permitted. The earlier 98-check implementation mishandled these two equality
cases; preserve it and verify the repair before accepting the successor.


## Implementation outcome

The implementation passes 103 deterministic checks in data/accounting-master/company-information-20261023/checks.json. Exact path-component coverage binds the header and each annual definition; investor and system cutoffs apply publication and ingestion/acceptance clocks separately. Calendar-day overlap leaves chronology unresolved. The fixtures are authored synthetic clocks, not source evidence. The result stays below historical admission and forecast claims.
