# Supervisor review of progress supervision

Reviewed 6 October 2026 Hong Kong time. MC25 and MC33–MC35: preserve work,
maintain honest evidence, and continue internal proposal preparation. This is
supervisor finding adjudication, not a new independent model AGREE. The previous
controller receipt and its 23 findings remain preserved in `before/`.

The comparator is the stopped controller's fixed worker cutoff. The revised
controller keeps its process ownership/cleanup, independent result acceptance,
phase repair cap, proposal-only scope, invocation limit and original campaign
deadline. It adds one cooperative channel and a bounded scheduling state machine.
No model/provider configuration or permission rule changes are needed.

| Finding | Disposition and evidence |
| --- | --- |
| Saved work could reach timeout without a final response and be replanned | Complete PARTIAL checkpoints are validated and bound to the worker, approved plan, phase, dependencies, scoped files and evidence. Timeout recovery reaches fresh checks and bounded result review without another editable attempt. The failed process stays failed. Fault-injection integration test passes. |
| Activity could be mistaken for progress | Only completed successful command output with the current worker identity and timely monotonic timestamp is consumed. Editable milestones require new substantive content; operational records and progress notes do not count. Read-only conclusions need located evidence. These are scheduling signals, not semantic acceptance. Repeated/invalid/role-mismatch tests pass. |
| A silent worker could consume the full ordinary window | A checkpoint request follows five minutes without verified progress; three minutes of grace permits acknowledgement and new evidence or a response. Clock acknowledgement alone cannot renew work. Real silent-child cleanup test passes. |
| Productive finishing could still hit the old cutoff | Verified recent progress plus acknowledgement can earn two-minute grants capped at five extra minutes. Each further grant needs new progress. Real child successfully finishes beyond the ordinary window; hard-ceiling and ignored-instruction tests pass. |
| Delayed acknowledgement could resurrect an expired worker | Reports issued after their effective deadline are rejected, and request acknowledgements must be issued within the request interval. Late-grace test passes. |
| Unused extension could admit a worker after its ordinary launch window | Final pre-launch check uses the ordinary window; configuration/startup remain within it. Extension is earned only after launch. Pre-launch boundary and verification-reserve tests pass. |
| A stale checkpoint could hide edits, additions or deletions | Helper prints a digest of the full scoped inventory; supervisor recomputes and retains it. Recovery compares every scoped path before and after fresh checks. New/changed/deleted/unreported-file and different-plan tests pass. |
| Worker-written control or recovery records could weaken integrity | Helper writes no files. Supervisor publishes control, supervision and checkpoint records through existing exact-write runtime guards. Tampering vetoes reuse on success/failure. |
| Full inventories could be truncated in the tool channel | P16 inventory is roughly 32 KB; the helper emits its digest while the supervisor saves the full map. Response evidence stays explicit. CLI read-only and snapshot tests pass. |
| Additional code could be absent from future controller reviews | New supervision module and plan are in CONTROLS; fallback review packets include the module and checkpoint methods. Recovery navigation includes recovered responses. |

Remaining limits are explicit: the channel is cooperative and cannot interrupt
a provider call until it returns. A novel located finding can still be wrong;
independent review remains responsible for substance. The first live worker must
be observed for protocol recognition, real progress and correct result dispatch.
Timing values are engineering hypotheses, not demonstrated optimal thresholds.
Absolute budget and operator/integrity stops remain authoritative.

Test logs, preservation results and the restart receipt in this directory provide
the execution evidence. Test counts establish controller behavior only. No P16
acceptance, full proposal readiness, accounting validity or forecast validity is
concluded from this repair.
