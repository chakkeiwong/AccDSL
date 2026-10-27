# Policy and materializer information dates

23 October 2026. S3/S4; MC05/10/13–16/18/24/25/28/34.

The policy-information query now checks when the exact settlement policy and
the exact materializer were available, separately from the parent company's
inputs. All 93 deterministic checks pass in the recorded run and read-only
replay. All 276 protected predecessor files remain unchanged. The recorded run
took 86.408 seconds; replay took 83.118 seconds. These are engineering checks
of a synthetic example, not evidence of historical forecast performance.

The query replays the parent exchange, regenerates the whole policy path, and
recomputes its accounting result. Canonical content hashes distinguish JSON
booleans from numbers where Python equality would not. A changed policy or
materializer cannot reuse the old information declarations or observations.
Synthetic timing covers exact instants, half-open days, missing observations,
late dependencies, private publication, revised bytes and archival exploration.

Eligible inputs can produce a partial accounting result. In the unknown-payroll
case, 27 annual lines remain unresolved, two opening lines remain known, no
closing memory is emitted, and the next year is blocked by predecessor
incompleteness. Availability does not convert that result into a completed year.

## Decision

| Decision | Primary criterion | Veto checks | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain this bounded design increment | Exact dependency binding, timing conjunction and complete recomputation pass | Mutation, type, day-boundary, partial-result and baseline checks pass | Dates, trust observations and behavior are synthetic | Review the whole language and then extend the highest-dependency missing authoring semantics | Real source admission, historical execution, accounting compliance or predictive accuracy |

No continuation veto fired. The two preserved earlier failures were harness
errors: the observation helper's `event` parameter collided with a requested
mutation, and a partial-result expectation confused an omitted closing-memory
field with a null value. Their source snapshots and failure records remain in
`before-observation-helper-repair/` and `before-partial-expectation-repair/`.
Neither failure rejects the simulator direction.

## Reproduction and limits

Recorded command: `CUDA_VISIBLE_DEVICES=-1 python3
data/accounting-master/company-policy-information-20261023/verify.py --record`.
Read-only replay uses the same command without `--record`. The one-time
recording must not be repeated. `manifest.json` identifies the Git commit,
environment, CPU-only execution, source hashes, fixtures and run timing.
`checks.json` retains the individual outcomes and partial-result witness.

The strongest alternative explanation is agreement between components sharing
the same implementation defect. Independent cash/receivable arithmetic and
adverse mutation checks reduce that risk but do not establish completeness.
Any accepted changed dependency, fabricated child clock, incompatible replay
or altered protected file would overturn this local result. Real observation
provenance and general language coverage remain the weakest evidence.

Version 3.53 remains 413 pages and `not_ready`; this increment awaits a later
manuscript integration. S1–S5 remain partial, S6 held and S7 deferred. No whole
requirement closes. The next plan is
`docs/plans/accounting-language-scope-review-20261023.md`.
