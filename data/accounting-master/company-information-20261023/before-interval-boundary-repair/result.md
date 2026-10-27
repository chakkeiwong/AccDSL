# Assumption-information selection — result

23 October 2026. S3/S4; MC05/10/13–16/18/24/25/28. The 98-check synthetic
selector passes for the baseline, four named alternatives and the two information
views. Each declaration covers the header and each annual input by canonical
digest. Changing a year requires new clocks for that year. Source timing and
assumption timing are conjunctive. Public information requires publication;
system views require ingestion and acceptance. Overlapping calendar-day clocks
leave chronology unresolved. The exchange itself must pass trusted local replay.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain this bounded information-selection draft | Exact component coverage and cutoff behavior pass the 98 deterministic cases | Missing, late, self-asserted, private, mistyped, incoherent or path-mismatched evidence is unresolved or refused | All clocks are authored synthetic test fixtures; no observed historical vintage is present | Specify explicit policy authoring and its independent clocks | Historical look-ahead control, real identity, prospective forecast, forecast accuracy, or production authentication |

The initial recorded run had 87 checks and passed. A later timing audit found
that overlapping calendar days could leave authorship and publication order
unknown even when both dates preceded the cutoff. The selector now treats that
chronology as unresolved, and the original evidence is retained in
checks-before-chronology-repair.json. The repaired 98-check suite passes.

Post-run red team: a fabricated observation set can satisfy internal timing
logic if falsely granted trusted status. Trust is supplied only by the local
caller and the fixture's explicit test scope; the packet cannot grant itself
real-world authentication. Real source or authoring records and a reviewed trust
mechanism are still necessary before any historical backtest. The weakest
evidence is the absence of independent date observations.

Read-only reproduction: CUDA_VISIBLE_DEVICES=-1 python3
data/accounting-master/company-information-20261023/verify.py.
