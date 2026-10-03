# Bounded worker recovery repair

3 October 2026 (Hong Kong). Applies to MC31–MC35 and the master execution
obligations; no accounting or scientific acceptance criterion changes.

The current master run was stopped cleanly after P03's third 900-second attempt
timed out. Its last repair repeatedly inspected raw logs containing earlier log
reads, including a response exceeding one million characters. P02 also retained
partial implementation without all required deliverables. Preserve these failures
and their evidence. Increasing the timeout would not address rediscovery and
recursive context growth.

Implement a structured recovery snapshot before each phase worker: current
deliverable/test presence, changes since phase entry, latest process outcomes,
deterministic checks, and actionable review findings. Bound excerpts and lists,
identify omissions, and link full structured records. Never read raw logs into
this snapshot. Give workers their attempt and remaining run budgets, reserve time
for checks and a final response, and require targeted reads instead of raw log
dumps. Save snapshots so timeout and resume have the same recovery information.

Skeptical audit: the baseline remains the 192-report panel and existing phase
contracts. File counts, successful tests, and a smaller prompt cannot substitute
for required accounting deliverables or result review. Summaries can omit a
material finding; preserve full record paths and pass the original criteria and
current repair findings without weakening them. Recompute file presence on each
attempt to avoid stale recovery advice. Budget disclosure is guidance; existing
controller process deadlines remain the enforced stop. Source integrity and
unexpected controller failures retain their continuation vetoes. No model,
environment, authority, spending or permission boundary changes. This focused
repair passes the audit because timeout/resume fault injection and the existing
controller suite can test the mechanism directly.

Verify timeout-to-repair and cross-invocation recovery, latest structured findings,
bounded output despite a huge raw log, unchanged criteria, and disclosed budgets.
Run the controller suite, inspect the actual changes, record supervisor review
with current hashes, then resume via the existing approved absolute entrypoint.
Real phase completion is subsequent evidence, not promised by this repair.

## Verification and supervisor review

The implemented snapshot reads only selected JSON records and a bounded optional
progress note. It recomputes current file presence and changes, saves the complete
change inventory, and marks abbreviated prompt fields with truncation flags and
full record paths. Prior state and the original current criteria/repair findings
are retained. Time budgets and the final check/response reserve appear in each
worker packet; process deadlines remain enforced by the existing runner.

`python3 -m unittest discover -s tests -p test_accounting_master.py` passed
76 tests in 9.004 seconds. New regressions inject a timeout after useful edits,
forbid raw-log reads even with a large nested log, exercise a fresh invocation,
recover the latest failed checks/review findings, and check current missing files,
unchanged criteria and the run-limited worker budget. Partial work stays
unaccepted until actual checks and result review pass.

Supervisor inspection found no acceptance or permission widening in this repair.
The installed rule matches the exact absolute run command with --max-seconds 7200
and the stop command; an unrelated Python entrypoint has no matching allow rule.
The original authorization is preserved. This review is supervisor adjudication,
not a claim of new independent-model agreement. The next invocation reruns the
controller suite before reusing the review receipt.

Remaining limitation: excerpt limits guide navigation rather than prove that a
worker uses time well. The linked full findings and enforced deadlines prevent
silent acceptance, but a real phase may still require repair. Resume the bounded
campaign to obtain that evidence.
