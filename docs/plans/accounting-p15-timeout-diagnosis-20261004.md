# P15 timeout and no-progress diagnosis

4 October 2026, Hong Kong. Read-only investigation of run
`20261004T054134-68471e41`; the run is finished. The question is why repeated
proposal repairs time out and why the last attempt was reported as no progress.
MC24, MC25 and MC34 apply to execution and truthful recovery reporting. This
note changes no controller, phase state, proposal acceptance or retry allowance.

## Confirmed immediate causes

The last editable worker's saved budget is 98.8 seconds: 398.8 seconds remained
on the controller clock, minus its 300-second supervisor verification reserve.
Its approved plan reserves 120 seconds just for checks and the final response.
The controller starts a worker whenever its available time is positive; it does
not require enough time for the approved task or even that finishing reserve.
This attempt ran for 98.069 recorded seconds, completed three read-only commands
and changed no project files before the controller terminated it.

`_worker_result` computes the cutoff at scripts/run_accounting_master.py:885.
`execute_phase` at line 1551 defines progress as any added/changed/deleted file
in this attempt's preservation window. When there are none, it immediately
returns needs_plan_repair. The count of two controls deferral across invocations;
it does not allow a second no-change attempt inside this invocation. A short
budget therefore becomes a plan/no-progress outcome rather than an explicit
budget-exhausted checkpoint. This does not establish that the remaining task
itself is infeasible.

| Execution | Recorded worker seconds | Observed outcome | File changes |
| --- | ---: | --- | --- |
| Initial | 899.172 | Timeout after provenance work | 10 added, 1 changed |
| Retry 1 | 758.669 | PARTIAL; bounded review AGREE | 14 added, 2 changed |
| Retry 2 | 899.178 | Timeout after MC07/G12 reconciliation | 8 added, 3 changed |
| Retry 3 | 899.208 | Timeout after v7 provenance checks | 12 added, 2 changed |
| Retry 4 | 98.069 | Timeout; no file changes | None |

These durations come from each execution-N/*-N.process.json; budgets come from
the matching recovery.json and changes from changes.json. The sequence contains
four retries, with retry 5 unused. The persistent residual saying 'Repair
allowance exhausted for this invocation' predates this run and is stale. It is
retained in state and copied into last_outcome even though this run exited via
the no-progress return, before its exhaustion branch.

## Where the time and work went

Saved process durations total 23.5 minutes of planning, 22.4 minutes of plan
review, 7.0 minutes of result review, 59.2 minutes of editable workers and
0.5 minutes of checks. These are recorded monotonic process durations, not a
reconstruction of elapsed civil time. Every narrow continuation receives fresh
planning and plan review, including completion/reporting-only tasks.

The first worker prompt is 141,439 bytes; the final one is 421,334 bytes. The
compact next-plan field is only about 2.2 KB. The remaining full current_checks
field is about 82.7 KB, and the final repair_findings field is about 247.1 KB,
including a 230.9 KB continuation. These JSON component sizes are independently
serialized and need not sum to the indented full prompt. The previous prompt
refresh removed historical next-plan prose but left these larger reports inline.
The first worker returned 325,748 characters of command output across 35
commands. Oversized context and repeated reading are observed; the fraction of
model latency they cause has not been isolated.

The saved tasks also show recurring validation maintenance. Execution 0 repaired
MC34's reference after the master plan legitimately changed. Execution 2 saved
MC07/G12 analysis but its local v6 integrity check compared an old report's
coverage hash with the newer active coverage file. The exact historical bytes
were already in evidence-v6/before-coverage.json. Execution 3 resolved that
historical tuple and produced a passing v7 integrity report, then timed out
before creating p15-mapping-completion-v7.json. Execution 4 was planned solely
to finish reporting and the completion record. This demonstrates repeated
provenance/reporting work consuming attempts; it is not a failure of the
underlying accounting analysis. Source-based assessment and full P15 review
nevertheless remain unfinished.

## Repair priorities

1. Put compact current findings and exact saved-record paths in worker prompts.
   Keep full checks and continuation inventories on disk; do not inline their
   duplicate nested hashes. Verify all required findings remain discoverable.
2. Check remaining execution plus finishing budget before launching a worker.
   Save a budget-exhausted continuation when insufficient; do not classify that
   condition as failed planning or evidence of task-level no progress.
3. Preserve approved substantive scope across localized reporting completion;
   avoid a fresh large plan/review sequence merely to finish an already-checked
   task. Keep review for substantive findings and final proposal acceptance.
4. Resolve historical report inputs against the exact retained versions once,
   separately from current deliverable validation. Reuse a stable validator and
   let deterministic supervision write mechanical completion records, instead
   of asking each model worker to create another validator/report version.
5. Record current stop reasons and consumed retries explicitly; do not carry an
   obsolete exhaustion explanation into the next outcome. Distinguish successful
   partial tasks, actual repairs and budget stops while retaining the user's
   five-retry ceiling and the run budget.

The smallest checks for a future repair are a tiny-remaining-budget case that
launches no editable worker, a prompt retaining all findings without embedded
full inventories, a historical hash resolving to its original snapshot after a
current-file edit, and an outcome that reports four retries plus budget/no-change
stop without claiming all five were exhausted. Tests establish controller
behavior; they cannot establish proposal completeness or human acceptance.

No program repair or new master invocation was executed for this diagnosis.
