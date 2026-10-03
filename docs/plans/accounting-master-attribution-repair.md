# Phase evidence attribution repair

3 October 2026, Hong Kong. Scope: MC25, MC33–MC35 and the authorised
master-program execution. Run 20261002T201419-9b58ed81 stopped cleanly at
20:38:47 UTC, with no recorded child survivors. P00/P01 remain accepted;
P02's 900-second attempt made partial source-extraction repairs but did not
finish verification. Its previous evidence remains intact.

## Question and skeptical audit

Can a resumed phase retain its own earlier contributions without accepting
unrelated changes made between invocations? The current controller compares
the whole editable repository with the first phase-entry snapshot. P02 thereby
inherits P03's four files and later supervisor edits. Editing those files can
then invalidate P02 unnecessarily. Merely discarding cumulative evidence would
lose real contributions from earlier attempts and is rejected.

Record deltas for each actual implementation/check window, including timeout
and failure paths. Carry their union across retries and resumes. Acceptance
must include those files, explicit worker/reviewer evidence and required
deliverables. Missing preserved files still prevent acceptance. The original
entry snapshot and raw cumulative records remain historical evidence.

Legacy partial attempts need an explicit, recorded migration: use the first
invocation's last cumulative record, for which no intervening phase ran, and
directly observed current-invocation differences. Never infer ownership from a
later whole-repository cumulative comparison. Unmigrated legacy state must be
identified rather than silently losing evidence. No accepted worker phase yet
needs migration; P00/P01 are fixed operations.

The baseline is the existing controller and preserved state/inventory in
data/accounting-master/attribution-repair-baseline.json. Pass criteria are
focused regressions for unrelated inter-invocation edits, prior contributions,
timeouts, check-side mutations and deletion restoration, followed by the full
controller suite and source-level review. Test counts are engineering evidence
only. A missing ownership record or lost prior contribution vetoes acceptance;
the repair does not alter accounting criteria, data, worker budgets or fees.

Audit decision: proceed. The failure is attributable to the comparison window,
the proposed checks distinguish the fix from simply dropping old evidence,
and original histories and acceptance requirements remain preserved. No new
permission is needed. Resume uses the already approved absolute entrypoint and
the remaining time from the run's 22:14:19 UTC deadline.

## Executed repair and review

The controller now saves attempt deltas in both worker and check `finally`
paths and persists their union as `contributed_files`. Acceptance hashes that
union and retains explicit evidence, required deliverables and tests. Recovery
snapshots use the same attributed set. Deletion obligations survive failures and
resumes and clear only when the files exist again.

All 81 controller tests passed (including five new focused regressions), and
both controller modules compiled. The supervisor reviewed the 255-line patch
against the preserved pre-repair files. No independent model review is claimed.
The detailed log and patch are in data/accounting-master/attribution-repair-*.

The recorded legacy migration retains 13 P02 contributions and four P03
contributions. Its inspected first-invocation records and stopped P02 delta
exclude intervening supervisor and P03 edits from P02. Original state and all
attempt files remain saved. Neither phase was accepted by this migration;
P02's missing result report is still required. P00/P01 acceptance is unchanged.

| Decision | Primary check | Veto checks | Remaining uncertainty | Next action |
| --- | --- | --- | --- | --- |
| Resume the reviewed controller | Attribution/resume regressions pass | Prior contributions, failed-check changes and deletion obligations retained | The real worker may still exceed its budget or fail substantive checks | Resume within the remaining wall budget and inspect actual phase results |

This establishes the bounded controller repair, not accounting validity or a
completed mission. The strongest alternative explanation is another interaction
missed by fault injection; an actual lost contribution or unrelated accepted
hash would overturn this acceptance. Such a finding requires repair, not a
lowered substantive acceptance threshold.
