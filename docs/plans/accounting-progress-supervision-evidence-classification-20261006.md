# Focused repair: progress-evidence classification

Date: 6 October 2026. This is a bounded controller repair inside the active
proposal campaign. Product implementation remains disabled and no phase is
accepted by this work.

## Question and observed failure

Can the progress supervisor accept a read-only finding that cites a substantive
proposal artifact together with `progress.md` or a structured checker record,
while refusing operational-only evidence? The live P16 planner supplied two
new located findings. The supervisor rejected one because `progress.md` was
classified as invalid and rejected the other because every run record under
`data/accounting-master` was classified as operational. That is a scheduler
classification defect; it does not show that the planner lacked findings.

## Plan and skeptical audit

1. Lock hashes of the controller, tests, campaign record and deadline before
   editing. The locked baseline is
   `data/accounting-master/progress-supervision-20261006/evidence-classification/baseline.json`.
   It records 56 preserved files and 932 protected hashes under both campaign
   and runner locks; the initial hash-only record remains preserved too.
2. Classify evidence into substantive, context-only (`progress.md`), approved
   structured checker support (`checks.checker.json` under a run), and
   operational. Keep logs, process records, budgets, controls, supervision
   records and arbitrary run files excluded.
3. Preserve editable admission: new substantive content in the declared write
   scope is required; no context or checker exception is added for editors.
4. For read-only findings, require at least one substantive item with a nonempty
   locator. Context and checker support may accompany it and are omitted from
   novelty fingerprints, so changing supporting material alone cannot renew
   time. A checker alone cannot establish a new proposal finding.
5. Add deterministic regressions for mixed context/substantive evidence,
   checker support, context/checker-only rejection, changed support rejection,
   support-independent novelty and operational-only rejection. Replay the two
   captured live reports in an isolated monitor with their original timestamps.
6. Run the focused supervision tests and the complete controller/proposal
   suites. Record the actual counts and hashes before resuming the campaign.

The baseline is the current controller, not a scientific comparator. A passing
suite only establishes deterministic scheduling behavior; it cannot establish
proposal quality or phase acceptance. The stop condition is any changed
protected file, failed suite, malformed evidence admission, or a deadline/reset
mutation. The original campaign deadline and retry allowance remain fixed.

Skeptical audit passed after tightening step 4: accepting a checker by itself
would promote a scheduling report into substantive progress. Require a located
deliverable/source in every finding, validate every cited hash, and accept only
the registered proposal-check schema at exact phase-check paths. A failed check
can explain a finding; `passed=true` is not required and never accepts a phase.
Historical run records stay unchanged. Only the scheduler's accumulated
no-progress boundary may be reset after verification, with an explicit repair
receipt; original time and retry limits remain authoritative. MC25, MC33, MC34
and MC35 are addressed; broader proposal requirements retain their status.
