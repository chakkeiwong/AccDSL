# Pre-implementation audit — 24 October2026

MC05/11/13/16/24/26/28/35;G2/G4;S2–S5. Question:can ordinary events and explicit
tax payments continue from the second opening without treating old settlements
as current cash flow? Comparator:full checked boundary result and its explicit
period-vintage openings. The previous lifetime-vintage invariant is wrong for
this question because it requires all old settlements to fall in the new period.

Use a new period-aware invariant and the existing full-state native/payment
financial kernels. Historical tax_vintages stay exact. Every period row binds
the corresponding historical digest,opening payable and period;only its current
settlements and closing balance change. Aggregate current settlements must match
one actual dated current-period tax cash flow per payment. No inferred FIFO or
renewed assessment. Complete prefix and apply retain all state/history/findings.

| Choice | Provenance/justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Historical vintages immutable | Boundary contract | Lost previous payments or double counted cash | Prior rows byte-exact across all operations | Reviewed design |
| Period opening minus new settlements | Explicit boundary ledger | Old expense/current payment confusion | New expense0 with carried payable settlement | Reviewed scoped identity |
| Existing native financial kernels | Full26-account checked adapters | Hidden tax write or state projection | Tax footprint and exact journal/state checks | Baseline reuse |
| Explicit allocations/shared cash | Prior caller's checked event contract | Correct aggregate but wrong vintage or overspend | Equal-total different-id and shortage cases | Reviewed scoped design |
| Both assessments remain unassessed | New financial period contract | Ordinary events mistaken for assessment | Status and loss ledger exact | Required scope |

Primary criteria:independent arithmetic,complete state,journal and cash linkage,
per-period/aggregate conservation,exact historical records,successful prefix,
actual-opening four statements and complete apply. Invalid hashes,wrong oracle,
broken conservation or missing required diagnostics veto recording and trigger
repair. Invalid/unknown/funding events stop only that operation;the completed
prefix remains. Counts/runtime are explanatory. No legal/annual/forecast or
whole-company inference. Preserve cases,checks,test observation,manifest/replay.

Architecture risk:another year-specific assessment/carry chain would duplicate
the same recurrence while leaving arbitrary-period composition unspecified. After
this period-aware adapter,review a reusable multi-vintage contract before adding
another numbered yearly caller. This does not alter frozen predecessors or reduce
the mission;it records an implementation-design gap for the next audit.
