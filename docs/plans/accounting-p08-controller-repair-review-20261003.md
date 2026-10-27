# P08 controller repair review and finding dispositions

The independent read-only review in run `20261003T112400-69f171c7` completed
all seven scopes. Process lifecycle and permission/install returned AGREE.
Five scopes returned eight concrete findings. The run stopped before phase
execution, with no accepted-phase evidence changed. The responses are retained
in that run and copied in the repair evidence directory.

This document records the supervising agent's adjudication of those findings
after actual repairs. It does not claim that the five reviewers returned a new
AGREE. The master program explicitly supports this finding-based review path.
The resulting receipt is bound to the current controller, tests, catalog,
schema and master plan plus this note and the test/migration evidence.

| Finding | Repair and verification | Disposition |
| --- | --- | --- |
| Startup queries consume verification reserve | One absolute cutoff includes preparation and both configuration queries. Each query and the launch recompute remaining time. Delayed-query and exhausted-cutoff tests verify the reserve survives. | repaired_verified |
| Accepted results survive a changed phase contract | Acceptance records the exact phase hash and prerequisite evidence identity; refresh invalidates either mismatch and missing legacy bindings. Mutation tests cover contract changes and prerequisites. Nine legacy acceptances were explicitly migrated only after comparing retained reviewed phase packets with current contracts and verifying existing evidence hashes. P12 pending review remains valid. | repaired_verified |
| Final refresh veto disagrees with successful terminal outcome | Resolve final refresh before final manifest/event publication. Failure records continuation_veto in the return value, manifest, event and non-executable plan. Fault injection verifies agreement. | repaired_verified |
| Initial refresh lies outside guarded run bookkeeping | Initial manifest/state registration and refresh now run within the guarded lifecycle. Initial interruption produces finished_at, interrupted status and a plan with no eligible execution. KeyboardInterrupt injection verifies this. | repaired_verified |
| Ordinary repairs bypass fresh plan review | Every next editable repair receives a refreshed packet and newly reviewed plan. Failed checks, result REVISE, missing evidence and resumed-review REVISE tests verify planning/review precede editing. | repaired_verified |
| Partial-result BLOCKED is ignored | Persist the partial review's block, issues, residuals and next actions, then return through normal block fingerprint handling. A fault test verifies no repair worker starts. | repaired_verified |
| Preservation omits source/configuration types | Inventory all files in editable scope, including root configuration and SQL/YAML, with explicit exclusions for supervisor/frozen/service/dependency/cache material. Reject editable symlinks. Tests verify original-byte retention and changed/deleted-file reporting. Exclude the preservation store itself to prevent self-inventory. | repaired_verified |
| Malformed response prevents recovery | Keep the invalid record's path and bounded diagnostic, flag recheck/replan, and continue recovery. Truncated JSON, list and null records remain unchanged and cannot become acceptance evidence. | repaired_verified |

The final controller suite executed **113 tests, all passed**, in 20.683 seconds.
The earlier repair iteration exposed a preservation-store self-inventory issue
and one outdated repair-order assertion; both were corrected before this pass.
Evidence: `data/accounting-master/p08-execution-repair-20261003/controller-tests-r3.log`.

## Final skeptical audit

The comparator remains the stopped diagnosed controller and original phase
contracts. Tests establish these engineering paths, not accounting validity.
P08's explicit incomplete criterion still vetoes acceptance; a partial response,
timeout, missing final response or reviewer token alone cannot promote it.
Replanning has finite limits, external/no-progress blocks have declared input
fingerprints, and review work remains sequential and read-only. The original
approval rule and grant are unchanged. No new packages or model settings were
installed. Existing accepted evidence and the frozen corpus remain protected.

The strongest remaining alternative explanation for slow work is model-service
latency. Process records retain actual time and error/log paths; they do not
establish a complete latency decomposition. The work queue is now bounded, and
the previously missing Portuguese correction is retained. Source applicability
and actual EU admission still require substantive review and implementation.
The reviewer scope is trusted local workers and ordinary failures, as before;
deliberate detachment and unusable storage are outside the recorded guarantees.

Decision: the eight material findings are repaired and verified. Resume the
master through its existing narrow approved command after binding this review.
Do not promote P08 or close any wider accounting/forecasting gap from this repair.

## Additional live-run finding

Run `20261003T115045-50f3dc47` preserved the timed-out source-dossier work, passed
the 35-test check, and obtained a fresh PLAN/AGREE for a smaller continuation.
Monitoring found that this partial branch left the persisted phase status as
needs_repair when starting its next worker. The real internal helper correctly
requires running/repairing. The prior injected-check tests did not exercise
that integration boundary. An orderly stop preserved all files; the stopped
second worker had made no changes and left no child survivors.

Repair: set and persist running/repairing at the start of every actual execution
attempt. Respect stop requests before attempts, and record deferred verification
without launching a helper after a stop. The new integration regression runs
the real inherited-lock/capability helper subprocess after a partial timeout,
replan and repair, and verifies both checks actually execute and pass. The stop
regression verifies no child or injected checker starts. All **115 controller
tests pass** in 22.545 seconds in controller-tests-r4.log.

Disposition: repaired_verified, identified by the runtime supervisor. This is
a ninth finding, not an additional verdict attributed to the prior reviewers.
The receipt must be rebound to the changed code/tests and this note. The existing
standing authorization and narrow rule remain unchanged.
