# Progress-aware worker supervision

The user authorized replacing fixed worker timeouts with monitored progress and
bounded intervention. MC25, MC33–MC35 govern recovery, honest acceptance and
continued proposal work. Product implementation stays disabled. The campaign's
original monotonic deadline and 7,200-second invocation ceiling are unchanged.

The active campaign stopped cleanly at the read-only P16 review on 6 October
Hong Kong time. Its pending review is preserved. Three recent workers saved
substantive files and ran checks, then reached response with 14–37 seconds left.
Fixed termination discarded the response and forced fresh planning. That is
evidence of poor finishing/recovery behavior, not evidence of absent progress.

## Design and evidence contract

Keep a hard budget ceiling but replace the ordinary fixed worker cutoff with a
supervisor state machine. It reads incremental structured worker events and
verified milestone reports. A worker uses the existing clock command to report
a concrete finding or saved section/check, evidence paths and its next action.
The helper hashes those files. The supervisor verifies the hashes and filters
operational logs, clocks and progress-only notes. Repeated milestones, clock
polls, log volume and file counts do not renew progress. Read-only planning and
review may report findings with source locators; absence of edits is not failure.
These are scheduling signals, never scientific or phase acceptance evidence.

The same helper reads a supervisor-owned control record and acknowledges its
sequence in structured output. Before substantial batches the worker must read
it. On suspected stagnation, ask for a checkpoint and concrete progress first;
allow a bounded response period before stopping. A verified new milestone can
clear that suspicion. Near the normal work limit, request finishing and then
return. Recent evidence-backed progress can earn a limited finishing extension;
the invocation reserve and original campaign deadline always take precedence.
The channel is cooperative: an agent stuck in a model request cannot acknowledge
until it returns. Noncooperation terminates after the grace period or hard limit.

An editable worker may emit a complete PARTIAL response through this channel
when a subsection is saved, before its final chat response. The supervisor pins
the permitted work files at that moment. After a progress stop or time ceiling,
reuse only a schema-valid PARTIAL whose snapshot and evidence still match.
Run fresh checks and normal bounded result review. Preserve the actual failed
process outcome; never synthesize AGREE or phase completion from a checkpoint.
Changed checkpoint files require recovery work, not cached acceptance. Keep the
existing editable retry cap, single writer, stop requests and integrity checks.

## Defaults, audit and validation

Initial scheduling hypotheses: inspect events every second; suspect stagnation
after five minutes without a verified milestone; allow three minutes to report
or return; reserve the final three minutes of the nominal window for response;
allow at most five extra minutes, in two-minute grants, when recent verified
progress justifies it. Short injected tests scale these intervals. These values
are engineering choices motivated by observed late responses, not established
optima. Record intervention, acknowledgement, reason, progress and actual limits
so the first live run can expose false stalls or unproductive extensions.

The comparator is the current fixed timer. Pass requires: productive workers
survive their soft cutoff within the recorded cap; silent/repetitive workers
receive checkpoint guidance before termination; read-only findings count without
edits; ignored commands stop; provider failures stay distinct; operator stops
override extensions; and preserved partial work reaches review without repeated
editing/planning. No test-count or elapsed-time claim establishes proposal quality.

Skeptical audit: activity is not progress; reports are trusted claims backed by
concrete files, not semantic proofs. Require novelty and valid evidence, keep
independent acceptance, and record weak/invalid signals. Never extend merely for
CPU/log activity. Late responses at the absolute ceiling remain unsuccessful.
Missing acknowledgement cannot yield infinite grace. Control records must be
bound to the current worker and protected against accidental writes. Checkpoint
reuse must include unreported edits and new/deleted scoped files. The new module
must not change accepted phase contracts, frozen sources or historical reports.
These risks have explicit deterministic tests; the plan can proceed.

Save baseline, focused/full tests, supervisor review and first-live evidence in
`data/accounting-master/progress-supervision-20261006/`. Use finding-based
supervisor adjudication for this controller change, with no new review ceremony.
Resume the same approved campaign command after checking preservation and
archiving only this supervisor's stop request. Never renew the 48-hour allowance.

## Implementation audit and run procedure

The implementation uses `accounting_worker_supervision.py`, the existing clock
helper and the original process loop; there is no second model supervisor.
Completed successful command output is the only progress channel. Incremental
JSONL parsing has a one-megabyte record/read bound and keeps 128 diagnostic
events. Read-only findings require a concrete conclusion and source locator;
editable reports need a newly observed substantive content hash in the phase
write scope. A paraphrased report of identical saved bytes does not renew time.
Source-backed findings are still worker claims, not an automatic semantic audit.

The helper prints checkpoint JSON, a digest of the scoped inventory and response-evidence hashes;
it does not write files. The supervisor rechecks these before saving. This
avoids a writable exception for worker-authored supervisor records. A later
checkpoint can replace this worker's candidate, but repeated bytes never count
as new progress. Recovery checks all current scoped paths before and after the
fresh checker, including additions absent from the checkpoint. The result and
its failed process record remain separate.

Final code audit identified and corrected two implementation hazards: accepting
an acknowledgement emitted after its deadline, and recursively interpreting
JSON found in arbitrary message/prompt text as a progress report. Tests now
require timely bound helper output from completed successful commands. Fixed
startup/configuration bounds remain; they cannot spend verification reserves or
turn unused extension time into a launch after the ordinary admission window.
No retired seven-scope review ceremony is required for this local repair.

Defaults actually used: real phase workers share a five-minute progress window,
three-minute acknowledgement grace and finishing interval, one-minute final
response interval, two-minute grants and five-minute maximum extension. Short
fault-injection windows below three minutes scale those intervals. The old v1
clock remains readable for historical records and fixed packet-only probes.

Validation compares the preserved pre-repair controller with deterministic
failure injections and real short subprocesses. Pass requires preserved cleanup,
operator-stop priority, immutable control records, progress-dependent extension,
rejection of late/replayed/operational reports, and checkpoint recovery reaching
fresh verification and independent bounded review. The result note records actual
suite outcomes and the first live worker. Preservation verification binds the
932 protected files, pending P16 review, phase catalog, existing authorization,
and original campaign deadline before restart. The same approved campaign argv
is used; no allowlist broadening or global configuration edit is needed.

The full P16 inventory currently has 218 files (about 32 KB as JSON). Emitting
that inventory would risk truncation in a worker tool response, so the helper
prints its digest and the supervisor recomputes/stores the complete inventory.
This preserves detection of unreported edits without placing the inventory in
the model context. A real child-process regression also checks successful exit
after the ordinary window under an earned extension, plus active operator stop.
