# Accounting master: repair adjudication and execution decision

3 October 2026, Hong Kong. This is the supervising agent's code and finding
review after repair. It is not seven new independent-model verdicts. The prior
REVISE responses and raw negative responses remain in the original run folders.

The user asked for an executable program, actual repair, refreshed phase plans
and minimal approval clicks. The original standing approval covers scoped
repairs and sequential workers. The original authorization file and installed
command prefix are preserved. Changed code receives this fresh internal review;
it is not relabelled as the originally approved code.

## Evidence and finding dispositions

| Finding | Executed repair and verification | Disposition |
| --- | --- | --- |
| Recovery misses children created after its first process scan | Freeze the live, identity-checked leader and discovered members using pidfds; rescan until all live members have acknowledged STOP; only then kill the fixed stopped set. Poll boundedly for exit. Retain survivor identities on failure. Regression injects a late child and delayed termination; real-process recovery also runs. | Repaired, verified |
| Repeated installation replaces the standing grant | Preserve authorization bytes. New installation receipts bind candidate, prepared controls and original grant; interrupted recovery verifies those bindings. Tests cover repeated installation after a controller change and recovery after the grant already exists. | Repaired, verified |
| Installation mutates files before abandoned-worker recovery | Both explicit installation and interrupted-install recovery now hold the writer lock, recover prior workers, reload validated state, and only then call the installer. Reviewed the actual main branches. | Repaired, inspected |
| Nonterminal installation receipt is ignored when grant exists | Run checks every pending receipt independently of grant existence. Completion verifies the existing grant instead of recreating it. | Repaired, verified |
| Initially absent controls evade protection | Record hashes and a separate required-absence set for state, authorization and next-plan files; enforce both in worker and process finally paths. No None value is inserted into frozen hash maps. | Repaired, verified |
| Malformed state becomes runnable | Validate schema, required fields, phase IDs/statuses, lists, evidence hashes, gaps and run metadata on initialization/reload/refresh/save. Unknown status and missing-field tests fail closed. | Repaired, verified |
| Refresh can publish from changed controls | Refresh directly checks protection and state. Failure finalization saves the stop and a non-runnable veto view rather than publishing a runnable next phase. | Repaired, verified |
| Reused PID hides surviving old-group members | Check membership before marking recovery finished; veto without signalling the unrelated PID. Separate tests cover empty and populated groups. | Repaired, verified |
| Builtins accept a status string without result validation | Parent validates report identities/counts, reference reports, execution log, source hashes/context and explicit scope limits. Saves checks and deterministic PASS/FAIL result review. Applied to retained real P00/P01 outputs: 17 and 580 checks passed. | Repaired, verified |
| Unexpected controller errors become ordinary phase repairs | Only explicit MasterError failures enter the outer phase repair classification. Unexpected errors become a continuation veto with durable run diagnostics. A KeyError test stops before another phase. | Repaired, verified |
| Final acceptance omits earlier attempt/resume changes | Acceptance hashes cumulative added/changed files relative to preserved phase entry. Tests cover both an earlier repair attempt and an earlier invocation. | Repaired, verified |
| Tests can delete or change files after the last delta check | Recompute attempt and cumulative deltas after checks, persist deletion obligations, and send final deltas to review. Deleted originals veto; changed files are reviewed and hashed. | Repaired, verified |
| Mutable test cache bypasses current verification | Always execute the cheap current controller suite before reusing a controller verdict. A passed-cache regression asserts actual execution. | Repaired, verified |
| Completed check logs can be truncated | Publish legacy-check reports, corpus-regression logs and phase-test logs using the atomic byte writer. Streaming live process logs remain provisional until their process outcome is recorded. | Repaired, inspected |
| Structured negative evidence is rejected as a format problem | Preserve raw response and losslessly serialize object/list items across every negative response list field. Positive responses remain strict. | Repaired, verified |
| Packets omit top-level termination handling/imports | Include actual module imports and module entrypoint; include fixed-operation verifier context for scheduler/acceptance scopes. | Repaired, inspected |

Three prior objections were not code defects: rule match/not_match are load-time
tests rather than runtime action filters (actual policy checks are retained);
worker phases already obtain their own plan review; and a new run is the
explicit resume action, while changed external access uses --retry-blocked.
Those meanings remain unchanged and have regression coverage.

## Skeptical review of the repaired program

The baseline remains the accepted 192-report panel and original mission. Source
acquisition counts and controller tests do not establish semantic completeness,
accounting validity, forecast accuracy or human acceptance. All G1–G18 stay open.
The next plan is derived from actual statuses, dependencies, residuals and
evidence hashes; it is regenerated after every phase and at run termination.

The two-repair and wall-time limits are operating bounds, not scientific failure
criteria. Independent eligible phases continue after ordinary phase failure or
external blockage. Integrity damage, unexpected controller errors, lost process
ownership or source-baseline changes stop scheduling. This distinction is
covered by failure-injection tests.

Process containment assumes trusted workers remain in their original process
group. An exited recovery leader with surviving descendants is a conservative
veto, not a claim of fully automatic recovery. Uncatchable termination between
fork and durable registration remains outside the guarantee. These limits do
not require broader permissions for the requested bounded execution.

The strongest remaining alternative explanation is that the test suite misses an
interaction with a real worker or real corpus. Therefore the next evidence is
scheduled P00/P01 followed by reviewed implementation and result validation,
with failures preserved and repaired. A concrete failed invariant overrides this
review; a successful phase does not close its wider mission gap.

## Decision

Proceed with the existing approved command. The current code addresses every
material finding in the last review; current controller tests must pass freshly
before execution. Bind this note and the current control hashes into a supervisor
adjudication receipt. Preserve the previous REVISE receipt separately. Per-phase
read-only plan and result reviews remain required for worker-backed phases.

No professional review, paid data or other new spending has been requested.

## First scheduled run and planning-budget repair

Run 20261002T180732-83972f09 accepted P00 and P01, with 17 and 580
deterministic output checks, and refreshed the plan after each. Both P02 and
P03 then exhausted 240 seconds while performing relevant read-only inspection;
neither produced a complete plan. Their logs and failed status were retained.
The supervisor stopped the run before further repeated planning attempts.

Inspection found that the declared plan_seconds was not used: every read-only
role took review_seconds. Repaired role-specific budget selection and added an
independent-budget regression. Planning now has 720 seconds; implementation
remains 900 and review 240. The planning prompt requires targeted grouped reads,
reuse of prior inspection, and a bounded final plan rather than executing the
whole phase during planning. The original source/semantic acceptance criteria
are unchanged.

Skeptical review: this is an operational repair supported by two actual timeout
records. It does not establish an optimal budget or a scientific result. The
next real plan must return within the new bound; timeouts remain failures and
cannot become acceptance. P00/P01 evidence remains intact and is reused rather
than re-executed. The same original command approval is sufficient.
