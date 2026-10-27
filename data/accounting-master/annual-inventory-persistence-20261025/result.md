# Restartable annual inventory execution — 25 October2026

The optional single-writer store preserves all26 accounts, inventory memory,
tax vintages, archives, whole reports and refused prefixes. Chunked execution
and reopened results match uninterrupted AnnualInventoryProgram/1 execution.
242 deterministic checks over11 cases pass;17 focused tests and41 regression
methods cover annual runtime and prior P07 behavior.

Process-exit tests cover initial and operation transactions before/after commit.
A pre-operation-commit exit leaves the prior result; a post-commit exit retains
one attempted operation. An explicit retry cursor prevents repeating that sale.
A refused attempt is recorded once and remains terminal for its immutable
request. Interrupted initialization recovers an empty version0 target only when
the complete request is resupplied. Incompatible nonempty databases are preserved.
Reopening recomputes committed prefixes and rejects even rehashed financial
mutations. A new step uses the loaded native state without reexecuting the root.

The initial15-test candidate passed, but pre-freeze review found an uncovered
initialization boundary. The prior logs and rationale are preserved under
review-revision-01; two new subprocess tests and the recovery behavior address
that gap. This is a repaired coverage weakness, not a rejection of persistence.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain optional local store | Exact complete resumed/direct results and transaction/reopen checks pass | No remaining observed veto | Replay cost, hardware failure, concurrency, migrations and broader profiles | Integrate checked restart behavior, refresh full coverage, return to unresolved simulator-survey sources | Production durability, multiwriter correctness, speedup, hostile-file authenticity or accounting admission |

Engineering and exact financial continuity are supported only for tested finite
profiles. No stochastic comparison or statistical ranking occurs. The strongest
remaining alternative is a failure mode outside the process-exit tests; a valid
resume/direct discrepancy would overturn this conclusion. Power-loss and
concurrent writers were not tested. No new library, real-company admission or
whole requirement is promoted. S1–S5 partial;S6 held;S7 deferred.
