# P15 execution repair and remaining proposal audit

4 October 2026, Hong Kong. Authorised by the user's request to retrace P15,
review a root-cause repair, refresh the master and execute. This plan governs
controller repairs and proposal preparation. Product implementation stays held.
MC24–MC25 and MC32–MC35 apply to orchestration; P15 still addresses every
MC01–MC35 requirement and G1–G18 gap. No requirement or acceptance criterion is
reduced. Five retries means at most six editable attempts in one phase execution;
successful partial work, failures and unlaunched budget stops are reported
separately within that ceiling and the existing two-hour invocation.

## Baseline and traced causes

The baseline is completed run `20261004T054134-68471e41`, its five execution
directories, current P15 coverage/result, retained v6 mapping analysis and v7
historical resolution. The master is stopped. P15 is incomplete; P16–P19 are
pending. The older human checkpoint predates this run and needs correction.
The repository has extensive unrelated changes, which must be preserved.
During refresh, preserve the original state and correct the last stop's known
misclassification from the saved recovery budget/process records. Its single
no-progress strike came from the underfunded attempt and must not count toward
two future fully funded no-progress attempts. Historical run files stay intact;
the correction records five launched attempts, four retries and four timeouts.

| Observed defect | Call path and cause | Required repair and discriminating check |
| --- | --- | --- |
| Last worker had 98.8 seconds although its plan reserved 120 seconds for finishing | `execute_phase → worker → _worker_result`: launch admission checks only positive time after the 300-second supervisor reserve. Planning also starts without reserving a useful ensuing execution. | Require a full declared worker window plus supervisor reserve before editable work; require planning/review/work budget before a new planning cycle. A typed budget stop launches nothing, preserves the next task and never increments no-progress or retries. Test the actual 398.8/300/900-second case and refusal after startup consumes its finishing interval. |
| Prompt grew from 141 KB to 421 KB | `_worker_result → prompt` compacts recovery changes but embeds full `current_checks`, `repair_findings.continuation.checks` and hash inventories again. | Save the complete packet beside the prompt; send failure IDs, criteria, actions, status, counts and exact record paths. Remove repeated passing checks/hash maps from inline context. Test with the actual final packet shape and synthetic failures; original records remain discoverable and unchanged. |
| About 53 recorded process minutes spent planning/reviewing | `execute_phase` replans every partial task and reviews every returned partial result, including mechanical reporting. | P15 alone uses one reviewed substantive scope per invocation, then continues its unfinished tasks when structural checks pass and files progressed. Refresh next-plan/checks between attempts. Failed checks, substantive review findings, changed scope, real no-progress or an external block retain their repair/stop paths. Full phase acceptance still requires a completed independent result review. |
| Repeated historical-hash repairs | Ad hoc reference validators traverse old reports' `input_hashes` as if they describe today's mutable coverage. A v4 report's exact coverage bytes already exist in `evidence-v6/before-coverage.json`. | Distinguish checking a historical report's own immutable bytes from replaying its historical inputs. Resolve an explicitly replayed tuple `(report, original path, expected hash)` to the exact retained snapshot. Never rebase an old report or exempt a current input. Verify the saved v7 resolution and counterexamples. Retire worker-created validator/completion chains as execution prerequisites. |
| Missing `p15-mapping-completion-v7.json` became the next task | That file is absent from P15's declared deliverables (`coverage.json`, `result.md`) and criteria. The supervisor already captures checks and continuation. | Let the supervisor retain its existing deterministic check/continuation records. Do not require another model to create redundant completion JSON or another validator version. Preserve earlier reports as history and describe their limitations; substantive mapping review remains due. |
| Stale “allowance exhausted” and misleading no-progress | First no-change attempt immediately returns `needs_plan_repair`; old residual is copied into `last_outcome`. Only retries 1–4 actually ran. | Record current stop category and actual attempt/retry/partial/timeout counts. Archive the previous outcome and clear only the known obsolete operational residual at new execution. Report exhaustion only after all six editable slots were used; budget stops cannot defer an otherwise viable task. |

Prompt size and repeated reading are observed; their exact contribution to model
latency is not measured. Earlier 900-second attempts did save useful work.
These failures do not establish that the accounting analysis is infeasible.

## Implementation sequence

1. Preserve affected controller/doc/state bytes, the current Git identity and
   release/accepted-evidence hashes under
   `data/accounting-master/p15-execution-repair-20261004/` with the writer idle.
2. Add structured budget deferral and current execution accounting to the
   controller. Preserve real timeout classification, process cleanup, exclusive
   writer locking, stop requests, preserved deletions and final review recovery.
3. Add packet summarisation at prompt construction, with full original packets
   stored on disk. Do not compact the authoritative checker, acceptance or
   pending-review records. Keep all actual failures and proposed next actions.
4. Opt P15 into continuation within its reviewed scope. Other phases retain
   their existing repair policy. Do not reuse a plan after failed checks or a
   substantive rejection. Terminal independent review can require repair even
   when every structural check passes.
5. Install the following bounded task sequence in P15's catalog. Refresh its
   authoring instructions to distinguish current sources and historical
   reports, and to forbid inventing additional validation/completion gates.
6. Run focused adversarial regressions and the controller/proposal suites.
   Review the actual diff and record finding dispositions. Use proportionate
   supervisor review for these operational repairs, honestly distinguished
   from the required independent P15 plan and terminal result reviews.
7. Refresh the checkpoint/next plan, verify protection and the existing exact
   command rule, then execute the normal master command. Observe its actual
   first prompts, budgets and continuation decisions before relying on them.

## P15 bounded substantive work

The initial planner must inspect current coverage and the listed substantive
notes, then cover this remaining sequence in one executable plan. Every worker
finishes one coherent group, saves it immediately, and returns PARTIAL before
its finishing reserve. A later worker selects the first still-incomplete group
from actual saved sections and current findings; do not redo completed research.
Groups may be split when source inspection requires it. A timeout with saved
work resumes that group's remaining obligations, rather than starting a new
reporting-only task. Final review, rather than group counts, decides adequacy.

1. **Reconcile saved findings.** Retain the P00–P14 prior-work register, earlier
   source/narrative/chronology assessments, reviewed MC25/G18 work and the v6
   MC07/G12 mapping analysis. Correct stale review-status descriptions using
   the completed retry-1 review from the baseline run. Record that MC07/G12
   substantive acceptance is pending. Verify the v7 historical resolution;
   no v8 completion file is required. Inspect existing bounded reviews for
   substantive findings before updating coverage.
2. **Histories and uncertainty.** Reconcile MC06, MC08–MC12, MC14 and MC18 with
   manuscript, normative definitions, fixtures and actual P03–P06 evidence.
   Distinguish a witness from a complete family, exact from approximate
   aggregation, admissible weights from unsupported probabilities, and
   scenario information from future information. Give each related gap its
   concrete missing specification and evidence obligation.
3. **Accounting and sectors.** Reconcile MC13, MC15–MC17 and MC19–MC22 with
   corporate, consolidation/FX, instrument, bank and insurance cases and P08's
   incomplete authority preparation. Name what is specified, what was actually
   checked, which source limits remain and what P17 must supply. Do not
   implement held product modules or invent authority.
4. **Language, research and integration.** Complete MC23–MC24, MC26–MC33 and
   the remaining G1–G18 obligations against actual manuscript/specification,
   literature/software investigation and P11/P12 records. Assess MC34–MC35
   against actual work order and open internal preparation. Existing counts
   or a passing schema do not establish methods, reuse or research quality.
5. **Compare initial profiles and assemble the audit.** Compare the proposed
   corporate/shared-IR profile, typed-library-first authoring and
   instrument-first scope on the same source-to-record/history/journal/
   statement, uncertainty, chronology, recovery and extension obligations.
   Explain the broad sector-first alternative and its dependencies. State
   tradeoffs and open decisions without selecting architecture because code
   exists. P16 makes the documented proposed selection.
6. **Integrate and review.** Update coverage and its substantive audit/result
   so every row has specific evidence, a design consequence and remaining
   obligation; account for every historical phase honestly. Use the registered
   checker, return a completed structured response, and obtain full P15 result
   review. On REVISE, repair actual findings and recheck. Only then may the
   master advance to P16–P19.

Do not copy a generic residual into all gap rows. Read the relevant source
passage before changing a substantive assessment. Reuse existing immutable
sources. A claim of current conformance requires current checks; an old report
is evidence only about the exact input version it recorded. Avoid citing live
supervisor plans/state as stable accounting evidence. Work in P15's declared
document scope and leave wider unknowns explicit.

## Evidence contract, defaults and stops

Engineering question: can the controller carry retained P15 work forward without
underfunded launches, duplicate prompt inventories, redundant reporting loops
or false stop explanations? Comparator: the baseline run and current frozen
source/prototype evidence. Pass: fault-injection regressions demonstrate the
new control flow, required suites pass, and live execution uses the new packet
and budget paths. Vetoes: changed protected bytes, scope violations, corrupt
state, unresolved deletion, surviving owned process, failed required tests or
proposal-gate bypass. Prompt bytes and recorded timings explain behavior; they
do not establish proposal completeness or faster model reasoning.

The 900-second worker window, 300-second supervisor reserve, five retries and
7,200-second run limit are inherited authorised operating limits, not measured
optimal values. Keep them. Requiring a full window is a conservative engineering
choice that may leave unused time; test admission boundaries and report that
budget outcome honestly. P15 plan reuse is limited to passing checked progress
within the same reviewed scope; adversarial tests must show failed checks and
substantive rejection still cause fresh planning/review. This repair changes
neither numerical defaults nor scientific promotion criteria.

Save complete regression output, before/after hashes, prompt measurements,
review findings and live-run identity in the repair directory. Run manifest and
phase records preserve commands/environment/process durations. Random seeds,
GPU and statistical ranking are inapplicable to these deterministic controller
checks. No accounting validity, forecast validity, proposal acceptance, human
voice or implementation readiness follows from controller success.

Stop at the invocation limit, a real continuation veto, unresolved external
dependency, the retry ceiling, repeated fully funded no-progress, or reviewed
proposal readiness. A budget stop is resumable. A failed partial candidate is
not rejection of the research direction. Do not stop feasible internal work
merely because later human/accounting acceptance remains pending.

## Skeptical pre-implementation review

Proceed with the revised plan. The baseline is actual current evidence rather
than the stale checkpoint. The proposed repair addresses each traced cause
without using structural checks as semantic promotion. It preserves all phase
criteria, the user budget, proposal-first direction and existing permissions.
The main rejected alternatives are simply lengthening timeouts/adding retries
(does not address repeated work), flattening every report into current hashes
(destroys historical meaning), and skipping final substantive review (allows
false acceptance). No environmental or numerical comparison is being made.

The strongest remaining risk is that P15's partial sections pass structural
checks while their claims remain generic or wrong. Retain explicit source
inspection instructions and terminal substantive review. Another risk is stale
approved scope after a material finding: regression tests must prove that this
cannot enter the passing-progress reuse branch. Source unavailability limits
the affected claim; it does not justify unbounded report maintenance.

## Implementation review

The root-cause repairs are implemented. Initial verification passed 155
controller tests; review then added two adversarial cases and the 157-test
controller suite plus 17 proposal tests passed. Review caught and repaired two
additional paths: worker-reported substantive issues must reach a new reviewed
plan even when structural checks pass, and resuming a pending result review must
not consume an editable attempt. P15's initial-plan instruction now explicitly
covers the remaining sequence, avoiding conflict with the older instruction to
plan only one task.

The former 421,334-byte prompt reconstructs at about 52 KB with the new view.
Actual run prompts will be measured separately. The retained v7 historical
tuple resolves correctly. The registered P15 checker currently passes 1,920
structural assertions; its substantive review is still pending. A proposed edit
to the shared artifact-format guide exposed a live hash reference from coverage;
the guide's original bytes were restored, and the new guidance lives in this
plan and the master prompt. No worker retry is needed to repair that reference.

All 912 protected hashes and 143 accepted-evidence hashes match their baselines
(the sets overlap). Twelve checks cover every public action against the existing
dedicated and effective rules. Permissions and the standing worker grant are
unchanged. The focused diff, tests, measurements, historical-resolution result
and supervisor review are in the repair directory. Startup reruns the required
suites against the final controller before model work. Controller review is
local supervisor adjudication; no new independent full-controller verdict is
claimed. P15 still receives independent plan and terminal result reviews.

Live execution results belong in the run manifest and concise checkpoint;
controller success alone does not complete P15 or the proposal.
