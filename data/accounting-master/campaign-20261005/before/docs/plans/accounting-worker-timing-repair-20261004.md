# Worker timing repair and P16 continuation

## Question and scope

The user has asked to continue the repair plan and next phase. This is a new
continuation after the previous five-hour allowance ended. Repair the controller,
then use one normal invocation (7,200 monotonic seconds, initial attempt plus
five retries per phase). Continue the proposal sequence from P16; implementation
of the proposed accounting product remains held. This supports MC25/MC34
reproducibility and continuation of all P16 requirements, without closing them.

The baseline is controller state at next-plan generation 208 and completed run
`20261004T112501-7614c3b1`. All six editable workers timed out, each after saving
substantive work. Their first-to-last heartbeat intervals were about 862
monotonic seconds, while civil timestamps advanced only 790–804 seconds. The
last worker derived a civil deadline later than its actual termination. This
supports a clock-mismatch hypothesis; it does not explain every timeout.

## Mechanism and skeptical audit

The supervisor already uses `time.monotonic()`. Worker packets supply an allowance
and `measured_at`, encouraging workers to calculate deadlines from UTC. The
repair gives every worker fixed monotonic deadlines and a small read-only clock
command that recomputes remaining time from the same host clock. The budget
record carries the boot identity and is protected by the existing worker file
inventory. UTC stays as provenance only. A different boot or invalid clock
record cannot yield a usable remaining-time estimate.

For a 900-second editable admission, reserve the last 60 seconds of that nominal
window as margin: enforce process termination at second 840. Begin saving and
checking by second 600, and begin the final response by second 780. These values
scale down for shorter test windows. The 600/780 boundaries are instructions to
the trusted worker, not an OS prohibition on edits. The 840 response cutoff is
enforced by the supervisor even if the worker ignores instructions. No program
can guarantee that an interrupted model has saved an unfinished paragraph.
This combination provides an authoritative clock and a testable early response
boundary without claiming a cooperative save instruction is hard enforcement.

Workers check the clock before each substantial tool batch and after checks.
They save one completed subsection before opening another; at `finish` they
save/check only, and at `respond` they return the schema immediately. A bounded
task should fit the work interval, not the full phase. Return PARTIAL with an
exact next task when full P16 is incomplete. The supervisor still requires a
clean process exit and a valid structured response. Saved files or a final JSON
observed after the enforced deadline never become successful completion.

Audit findings and disposition:

- Merely printing another deadline does not make workers consult it. Supply an
  executable clock check and explicit per-batch/finish instructions; evaluate
  actual use in the next invocation. Ignored instructions remain a live risk.
- Earlier termination could increase timeouts. Keep full 900+300-second admission,
  narrow each plan to a substantive subsection, and record the earlier cutoff
  separately from the nominal allowance. Do not enlarge limits or reset retries.
- Passing timer tests does not establish model timeliness or proposal quality.
  Real execution must report its actual process outcome; phase acceptance still
  needs all registered checks and independent substantive review.
- Preserve the existing P16 correction: optional partial review is pending while
  the full contract inventory fails. It must not block further reviewed drafting.
- Existing contracts, accepted P15 evidence and frozen corpus are the baseline;
  do not repeat saved uncertainty supplement reporting or edit accepted plans.
- No scientific method comparison, stochastic forecast claim, new model setting,
  extra worker, permission bypass or global configuration change is involved.

Audit decision: proceed with this localized timing repair. Clock values and
response margins are reviewed engineering hypotheses, not scientific defaults.
The early diagnostic is deterministic drift/jump testing plus one real bounded
P16 subsection. Inspect real use at the first worker boundary. If workers still
ignore the clock or return late, retain timeout classification and investigate
before another unchanged invocation. Integrity/ownership failures veto execution;
incomplete P16 content triggers further substantive work within the run budget.

## Verification and evidence contract

Primary engineering pass criteria: clock output is independent of civil-clock
drift/jumps; the exact monotonic cutoff survives startup and process launch;
workers cannot mutate their clock record unnoticed; a timely structured PARTIAL
preserves its subsection without accepting the phase; late exit remains timeout.
Exercise a worker that ignores the response boundary and a boot mismatch. Run
the controller and proposal suites. Verify frozen and accepted evidence and the
existing exact entrypoint rule before execution.

Save pre-edit files, focused/full test logs, changed-code diff, supervisor review
and preservation results under
`data/accounting-master/worker-timing-repair-20261004/`. Rebind the controller
receipt only after reviewing current code and tests; label it supervisor
adjudication, not fresh independent controller review. The master records the
actual next invocation, process times, plans, checks and phase outcomes normally.

Resume P16 with a freshly reviewed plan for the family-linked versus
self-contained joint-model comparison and remaining attachment failures. Then
advance to conditioning, duplicate-evidence protection, likelihood updates and
conditional outcomes. Six full contracts, the proposed initial profile and
integrated dependency order remain open. P17 follows only after P16 acceptance.

Exact execution command (existing approval):

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py run
```

The prior five-hour window and its stale next-action instruction are historical.
Preserve them in the continuation archive, update mutable current instructions,
and refresh the next plan for this authorization. No new approval is required.
