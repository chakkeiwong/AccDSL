# Review timeout recovery repair

3 October 2026, Hong Kong. Scope: MC25/MC34/MC35, master execution only.

P05's implementation and two concrete repairs produced passing deterministic
checks, but both result reviewers exhausted the 240-second convenience limit.
The controller treated each missing review as a request for editable repair.
That wastes attempts and changes checked code without a returned defect.
The running invocation was stopped through its approved entrypoint before
changing the controller; its clean stop and partial results are preserved.

The engineering question is whether unavailable review can be retried and
resumed without reimplementing unchanged, already checked work. Preserve the
existing source baseline, phase criteria, sandboxes, standing authorization,
bounded total run time and requirement for a completed result review.

Use a 600-second phase-review allowance, with one fresh read-only retry after
a timeout. This is an operational hypothesis based on repeated 240-second
timeouts and P04's 238.855-second completed review, not a scientific default.
Controller packet review retains its existing budget. Retry paths have unique
files; timed-out responses are never read as verdicts. Exhaustion records
`needs_review`, keeping a checked-work checkpoint for normal resume. A
substantive REVISE still triggers implementation repair. Failed checks,
changed phase evidence or prerequisites require revalidation and repair;
they must not reuse the pending review as a path to acceptance.

Skeptical audit: the failure is review availability, not proof of a correct
runtime. Tests and authored PASS remain insufficient for phase acceptance.
Fresh review must inspect the same evidence and original criteria. The pending
checkpoint must detect changed/missing contributed files, tests, deliverables,
plan and check reports; dependency/phase changes invalidate reuse. A stop,
integrity failure or exhausted invocation must not launch another reviewer.
Keep the repair focused; do not weaken accounting claims or restart corpus work.

Primary criterion: fault-injected review timeout/retry/resume invokes no editable
worker when checked evidence is unchanged, and only a clean review plus passing
nonzero checks accepts a phase. Vetoes: reuse of changed evidence, acceptance
from timeout, ignored REVISE, lost partial work or failed controller regressions.
Test counts and elapsed times are explanatory only. No accounting, forecasting
or human acceptance follows. The suite and a supervised real continuation will
preserve results under `data/accounting-master/review-retry-repair/`.

Audit decision: proceed with the focused implementation and controller tests.
Record the changed-code review before resuming the same approved entrypoint.
Use the remaining approximately one hour of this invocation's two-hour work
window for continuation; no new service, paid review or broader permission.

## Implementation review and verification

The supervisor reviewed the changed call chain from process timeout classification
through phase review, saved checked work, normal resume and final acceptance.
One fresh retry uses a separate directory. A timed-out response is preserved but
cannot return from `phase_review`. Both exhausted retry and insufficient review
budget preserve `needs_review`; neither promotes acceptance. Only the typed
process-timeout exception follows this route. Other failures retain their
existing handling, and integrity failures remain continuation vetoes.

Resume validates the saved checkpoint hash, phase criteria, prerequisite evidence
and phase-file hashes before skipping implementation. It reruns deterministic
checks and obtains a new read-only result review. Changed inputs return to normal
planning/implementation. A completed REVISE clears the pending checkpoint and
executes repair; a completed AGREE is accepted only with passing nonzero checks
and unchanged checked evidence. The accepted evidence now includes the clean
review response itself. Recovery navigation includes nested review retries.

All 92 controller tests passed (16.420 seconds, Python 3.11.15, CPU-only Python
tests, deterministic; no accelerator framework imported). Eleven new tests
exercise timeout classification, ignoring timed-out AGREE, review-only retry and
resume, altered tests/criteria/prerequisites, substantive REVISE, explicit stop,
insufficient budget, failed checks and reviewer mutation. Full output is in
`data/accounting-master/review-retry-repair/controller-tests.log`.

The strongest remaining operational uncertainty is whether 600 seconds suffices
for a real phase review. The real continuation will test that hypothesis; another
timeout must retain review work rather than manufacture a verdict. This is
supervisor code review and fault-injection evidence, not a new independent-model
controller verdict or an accounting-validity assessment.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Proceed with bounded continuation | Review retry/resume avoids editable work; REVISE repairs; 92 tests pass | No failed test or acceptance bypass found in changed call chain | Real review completion within 600 seconds | Preserve P05 checked evidence, obtain fresh checks/review, continue eligible phases | Accounting/forecast validity, full mission completion or guaranteed review latency |

The original permission grant and installed rule are unchanged. Preserve the
old controller/state before files and import only P05's completed implementation
and passing-check evidence into `needs_review`. Its previous timeouts remain
failed review attempts. Wider G1–G18 requirements remain open.
