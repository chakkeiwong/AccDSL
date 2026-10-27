# Supervisor review of the P15 execution repair

4 October 2026. Reviewed against the before-images in this directory and the
actual call paths in `run_accounting_master.py`, support helpers, catalog,
tests and execution plan. This is local supervisor review, not a new independent
model review. Historical independent controller reviews remain retained.

| Finding | Resolution and evidence |
| --- | --- |
| Underfunded editable workers | Full-window admission plus supervisor reserve precedes launch. A typed BudgetDeferred propagates to a resumable budget_exhausted outcome. The original 398.8-second remaining/300-second reserve case launches nothing. Startup that consumes the finishing interval also launches nothing. |
| Planning without execution budget | New planning admission covers plan, plan review, editable work and verification. A refusal preserves tasks, no-progress state and unused retries. |
| Unbounded repeated machine context | Every worker saves its complete packet; prompt-only summaries remove passing-check lists and hash maps. Errors, failed assertions, criteria and actions survive. Acceptance and pending review use the original records. The old 421,334-byte prompt reconstructs around 52 KB. |
| Repeated partial reviews/replans | Only P15 opts into passing-progress continuation under a reviewed sequence. It still refreshes checks and plans. Failed checks, reported substantive issues and terminal REVISE require fresh planning/review. No completed review is fabricated from a timeout. |
| Historical-input mismatch | One stable supervisor helper validates explicit report/path/hash/snapshot tuples. Current coverage is independently checked. Exact snapshot corruption or a tuple absent from the report fails. The saved v7 resolution passes. |
| Extra completion-file loop | P15 catalog and instructions return to substantive assessments/profile comparison. Supervisor check/continuation records supply mechanical reporting. Old validators/reports are preserved; no ad hoc completion filename becomes an acceptance criterion. |
| Wrong retry/stop accounting | Current execution counts and stop category replace the stale exhaustion residual. Four retries followed by a budget stop reports four, while a fifth retry can succeed. Six partial attempts stop honestly at the ceiling. |
| Progress.md mistaken for progress | A progress-note-only edit is excluded. Two fully funded unchanged attempts trigger deferral; no budget refusal contributes to that count. File progress still does not establish semantic progress. |
| Pending review consumed an editable slot | Replay/review consumes no editable attempt. Its rejection leaves all six actual editable slots available, tested through success at the sixth launch. |
| Conflicting planning instructions | P15 initial planning explicitly covers the remaining reviewed sequence; the old one-task planning instruction applies only to other phases. Each worker still executes one bounded group. |
| New guide edit invalidated a coverage citation | The guide's exact original bytes were restored. New instructions live in the master prompt and execution plan. The current registered checker passes without editing coverage or rebasing historical evidence. |

The 157 controller tests and 17 proposal tests pass. The registered P15 checker
passes 1,920 structural checks. Tests include failures, unavailable reviews,
stale inputs, preservation, process cleanup and proposal-gate enforcement;
test counts alone do not certify the proposal. Before/after verification
preserves the protected corpus/research and accepted phase evidence. Rule
checks confirm the existing exact public command forms; no permissions change.

The pre-run audit finds no unresolved implementation blocker. The full worker
window is a conservative inherited operating limit, not an optimised value.
The main remaining limitation is model work duration and substantive quality:
workers can still time out at 900 seconds, and structurally valid prose can
remain incomplete or wrong. Saved sections, exact source inspection and full
terminal independent review remain necessary. Runtime monitoring must confirm
budget admission, prompt sizes and the actual continuation branch.

Decision: execute one authorised invocation under the unchanged two-hour and
five-retry limits. Primary engineering criteria pass; preservation and scope
vetoes pass. P15 semantic acceptance and proposal readiness remain pending.
No product implementation, accounting validity, empirical forecast claim,
paid review, outreach or publication is authorised or inferred.
