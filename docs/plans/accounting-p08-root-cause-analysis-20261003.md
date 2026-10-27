# P08 root-cause investigation and proposed repair

Date: 3 October 2026. User request: trace P08 carefully, establish root causes or
testable hypotheses, and propose repairs. This work addresses MC15, MC17, MC19,
MC25, MC30 and MC33–MC35; it does not change any phase acceptance or close G4/G7/G8.

## Investigation contract and skeptical audit

The baseline is the stopped run `20261003T075910-81c6e8bb`, its reviewed P08 plan,
three timed-out work attempts, the current uncommitted P08 code and retained
authority dossiers. Distinguish (1) missing applicable authority, (2) missing
implementation, (3) orchestration/recovery defects, and (4) unverified claims.

Trace the actual worker/check/review paths and build a bounded timeline from
structured process records and selected log fields. Run the existing focused
tests and checker, and disposable mutation/control-flow probes where they can
distinguish hypotheses. No fresh model worker, accounting-source campaign or
master invocation is needed for this diagnosis. Do not repair product/controller
code during this investigation; retain evidence for a concrete repair plan.

Pass criterion: each asserted cause has an inspected code path, preserved run
evidence or a reproducible probe; distinguish causes observed in this run from
latent defects and untested hypotheses. Missing evidence vetoes the corresponding
causal claim. Lost protected bytes or an active writer stops diagnostics. Test
counts, source counts and elapsed time are explanatory only. A passing engineering
suite does not establish a complete second accounting regime or phase acceptance.

Defaults: use the recorded Python interpreter and CPU-only standard-library
diagnostics; compare with the last checked AASB slice and unchanged original phase
criteria. Existing 900-second worker limits and all source-applicability decisions
are hypotheses to examine, not defaults to enlarge or inherit automatically.
Use 120-second process caps for local checks and save complete output below
`data/accounting-master/p08-diagnosis-20261003/`. Disposable probes must not change
source records, controller state, next-plan files or accepted evidence.

Skeptical audit passed: the checks address the actual failure paths rather than
accounting superiority or source-volume proxies. Preserve the stopped invocation
as historical evidence; do not treat an exit code of zero with reason `timeout`
as success, or conflate a source-preparation record with an admitted lifecycle.
The investigation ends with findings, their limits and a sequenced repair plan.

## What the fresh diagnostics establish

The current P08 engineering bundle fails verification. The checker ran in
27.586 seconds: 33 tests, one failure, zero errors and zero skips. The failing
positive replay test is `RecoveryValidationTests.test_actual_deliverable_replays`.
Its validator reports 62 findings: two missing/mismatched recovery fields,
58 missing input pins and two stale code pins. The AASB authority checks and
three independent arithmetic cases pass. The matched-comparison check accepts
the honesty of the incomplete result; it does not establish criterion 3.

The latest invocation spent 900.126, 900.092 and 900.035 seconds on its three
editable P08 attempts. They completed 34, 40 and 34 shell commands respectively.
None produced a structured work response; none reached the supervisor's phase
checks or result review. The first attempt did run local checks: its preserved
v3 report has 33 passing tests and explicitly incomplete criterion 3. Subsequent
edits changed the checker without regenerating the result. That historical pass
does not describe today's code/results.

All 150 observed input hashes and 857 unique protected release/accepted-evidence
hashes were preserved during the diagnostics. No master worker, source retrieval,
production/controller repair or acceptance update was executed for this diagnosis.

Evidence: [diagnostic manifest](../../data/accounting-master/p08-diagnosis-20261003/manifest.json),
[current check](../../data/accounting-master/p08-diagnosis-20261003/checker-summary.json),
[attempt trace](../../data/accounting-master/p08-diagnosis-20261003/attempt-trace.json).

## Confirmed causes and their consequences

### 1. The code, authority research and saved result are at different versions

`scripts/check_accounting_p08.py:277` now imports the v4 recovery validator and
requires the result to embed its record, hash and source pins. The saved
`authority-and-methods.json` still reflects the v3 preparation. Attempt 1 added
`corporate_authority_eu_recovery_v1.py` and changed two validators, then timed out
before publishing a matching result. Attempt 2 wrote v5 source findings but did
not finish any code or result integration.

The mismatch is causal, not merely correlated: a disposable in-memory result
with the current v4 recovery record, its hash and current input pins goes from
62 validation findings to zero. Its `phase_criteria_complete=false` value is
unchanged. This repairs engineering consistency only; it cannot supply the
missing EU lifecycle. See the
[regeneration probe](../../data/accounting-master/p08-diagnosis-20261003/deliverable-regeneration-probe.json).

The source archive is not corrupted. All pins in v3, v4 and v5 match; all v5
anchor quotations tested occur in their retained texts. Quote matching does not
endorse the associated applicability interpretations. The active recovery loader
is hard-coded to v4 (`corporate_authority_eu_recovery_v1.py:7`), so it still asks
for native-language corrections and eligibility work that v5 reports inspecting.
The v5 record has no live validation or admission path. Historical records are
usefully preserved, but no explicit current version joins their conclusions.

The worker built dossiers and results through temporary scripts and inline
commands. A checked, reproducible project builder and a validated publication
step are missing. Updating validation requirements before producing matching
data leaves the working bundle inconsistent if the process is interrupted.

### 2. EU execution has not been implemented; source retrieval alone cannot enable it

There are three independent barriers:

1. `corporate_authority_eu_v1.py:103` unconditionally raises after validation.
   Its current record deliberately represents preparation, not admission.
2. `corporate_financing_v1.py:126` calls that preparation guard, then continues
   into AASB-only jurisdiction/basis/tier checks at line 137. A disposable stub
   that makes the EU dependency call succeed still gets
   `authority jurisdiction/entity/tier mismatch`. This is a control-flow probe,
   not a bypass used for an accounting result.
3. `corporate_financing_v1.py:336` rejects every comparison regime except AASB.
   `compare_same_facts` emits null EU results by construction. Event and note
   dependencies still use the AASB claim set; the note description also names
   AASB 7 directly.

Consequently, finding the last source cannot finish P08 without actual dispatch,
authority, event/note and comparison changes. The current rejection is correct
for an unadmitted treatment. The defect would be treating this preparation-only
code as an almost-complete second regime or merely removing its rejection.

The 33-test suite mostly exercises AASB execution, preservation and rejection of
unsupported EU treatment. It has no admitted EU success case. Its expectations
that all non-AASB rows stay unresolved must be updated deliberately when a
supported EU profile is added, while preserving rejection tests for unadmitted
profiles and wrong/missing authority.

### 3. The source dependency list wrongly promoted citations into amendments

The archived preparation's `metadata.amendment_links` includes six documents
that the base regulation's RDF links through `cited_by`/`work_cited_by_work`, not
`amended_by`: 2025/572, 2025/768, 2025/1358, 2026/237, 2026/240 and 2026/593.
The first worker consumed that list without rechecking its predicates and
labelled the three 2025 entries as promotion vetoes. The retained primary texts
and the later v4 inspection identify these as EEA incorporation decisions.
Their Article 1 provisions amend Annex XXII to the EEA Agreement; the selected
fixture assumes an EU Member State issuer. These documents should not have been
treated as amendments to Regulation 2023/1803 for that comparison.

This is a confirmed dependency-selection error. The inspection of each source
was not useless, but the wrong classification expanded the admission queue.
The early access code also constructed regulation URLs such as
`CELEX:32025R0572` and `/eli/reg/2025/572/…` for a document whose retained text
identifies it as an EEA decision. Later metadata-derived XHTML routes retrieved
the texts that the earlier PDF requests had not obtained.

The necessary correction is semantic filtering by exact RDF subject and
relationship, followed by source-specific applicability. It is not permission
to dismiss all later amendments or non-English corrections. Genuine corrections
must still be connected to the affected claim, dates and reporting context.
See the [source-dependency trace](../../data/accounting-master/p08-diagnosis-20261003/source-dependency-trace.json).

### 4. Timeout recovery preserves bytes but does not preserve a checked work boundary

The approved nine-step plan combines open-ended authority closure, regime
implementation, exact examples, mutations, result regeneration and reporting in
one 900-second editable attempt. The plan review approved it without a measured
case that all of those tasks fit the allotted time. The source set expanded
during execution, but the controller kept the same approved plan for all retries.

In `run_accounting_master.py`, an implementation `ProcessTimeout` exits the
worker call at line 1134. The `finally` block records changed files, but execution
skips `check_phase` at line 1146 and reaches the generic exception handler at
line 1195. That handler supplies an execution-error string and starts another
repair under the unchanged approved plan. The per-invocation retry limit resets
on the next `run`. The isolated probe reproduces both invocations: plan, plan
review, implementation, repair, repair; zero checker calls; `needs_repair`.

This is not total loss of continuity: `phase_recovery` supplies changed-file
inventories and prior records. Its limitations matter here. It chooses the
latest available supervisor check, which remains the previous invocation's
27-test report, even though local v3 work had a newer 33-test report and later
edits invalidated that report too. The controller has no current checked bundle
or structured subtask boundary to select the next small task. `progress.md` was
also stale across the second attempt, and the final version describes intended
checks rather than a completed handoff.

The 120-second final reserve in `_worker_result` is prompt data. It does not
enforce a transition from editing to validation/reporting at that boundary.
The outer timeout works; completing a final model response is not guaranteed.
The response schema permits only `IMPLEMENTED` or `BLOCKED` for an editable
worker, with no explicit resumable partial-work result. Together these choices
encourage another broad attempt instead of a small, verifiable completion.

### 5. A service interruption contributed to the final attempt, but is not the common cause

`execution-2/repair-2.log:79` records a model stream timeout, followed by two
connection failures. This happened near the attempt's end, after a temporary
dossier script's syntax error had been corrected. It helps explain why that
attempt returned no structured response. Equivalent connection errors are not
recorded for the first two attempts, so an API/network outage cannot explain
all three timeouts.

Retained source-access records account for about 107 seconds across this run's
P08 research batches, versus roughly 2,700 seconds across its editable workers.
That sum is not a full profiler. It supports separating source retrieval from
model/service latency, repeated inspection and artifact work; it does not
identify the dominant unmeasured component. Simply increasing all timeouts has
not been justified by the available evidence.

## Additional acceptance weakness found by a probe

The current controller's acceptance predicate requires `checks.passed`, a
positive test count and reviewer `AGREE` (`run_accounting_master.py:1179`). It
does not require the phase's explicit criterion-completion result. Its regular
`_checks` path runs unit tests, not the P08 standalone checker's completion field.

An isolated synthetic checker response with `passed=true`, one test and
`phase_criteria_complete=false`, paired with a deliberately mistaken `AGREE`,
was accepted. This is a latent defence weakness, not a claim that P08 was
incorrectly accepted: P08 remains incomplete and its previous real reviewer
correctly rejected criterion 3. Engineering consistency must remain a separate
output; a machine-checkable incomplete criterion should also veto phase
acceptance before a reviewer token can promote it.

## Remaining hypotheses and smallest discriminating checks

| Hypothesis | Present evidence | Next check and decision |
| --- | --- | --- |
| The Portuguese 2003 corrigendum can be retrieved through another legitimate representation | Two failed routes are recorded; work metadata and the containing OJ issue link are retained. The affected provision was not read. | Inspect the exact work/expression/manifestation links and containing Portuguese OJ page 23; make one bounded retrieval batch using those links. Record whether the text affects Article 4. Do not infer that it is irrelevant from its language or age. |
| That corrigendum materially blocks the selected eligibility claim | v5 labels it a blocker, but has no inspected corrected provision | Compare the retrieved correction with the Article 4 proposition used by the fixture. Keep an unknown material dependency unresolved if the text remains inaccessible; do not present all source research as blocked. |
| v5 has enough eligibility/transition analysis for the remaining inspected provisions | Its pins and quotation presence pass, but its decisions have not received an independent applicability review | Produce and review a claim-by-claim disposition for original 2024/2025 reports, no early adoption and the existing synthetic terms. Quote integrity alone cannot close this hypothesis. |
| Smaller work slices fit the current worker budget reliably | Focused deterministic checks take under 30 seconds; broad workers time out | Record edit/check/handoff timing for the first two new slices. Increase a specific slice's budget only if measurements show useful bounded work cannot fit; retain finite limits. |

## Proposed repair sequence

### A. Restore a coherent engineering baseline

Preserve the current hashes and historical v3–v5 records. Add a reproducible
project builder for the P08 result from declared source records and actual
executions. Its initial task is the narrowly reproduced mismatch: embed the
current v4 recovery record and hash and regenerate required manifest pins.
Keep criterion 3 incomplete and EU values null. Separate the fact that a bundle
is internally consistent from the status of unreviewed newer authority findings.

Build into a new candidate directory, validate there, then publish through a
single manifest/pointer update or another tested commit boundary. Avoid claiming
that two independent file renames are an atomic multi-file transaction. The
checker must resolve one declared candidate/version consistently. Keep earlier
source/check records immutable and preserve interrupted candidates for diagnosis.

Acceptance: current checks pass; the positive replay failure is gone; a rerun
of the builder produces the same substantive records apart from declared run
metadata; simulated interruption cannot select mixed versions. P08 remains
unaccepted because criterion 3 is still incomplete.

### B. Repair bounded progress, recovery and acceptance control

Define a finite P08 subtask queue under the existing phase: source disposition,
authority-profile implementation, lifecycle comparison, verification and result
review. Each task has explicit inputs, required outputs and a small completion
check. Preserve the original four phase criteria; finishing a subtask never
marks P08 accepted. Add a structured partial outcome and durable next-task record
so a worker can finish a useful bounded slice without claiming the phase is done.

After any editable timeout, first verify child cleanup and protected hashes.
Then run bounded local checks against the preserved candidate if its files are
usable, record missing/inconsistent files otherwise, and derive the next task
from those actual results. Never turn timeout text or a partial worker message
into a successful response. Read-only review remains required for completed
work. Replan the remaining scope when it changes or repeated timeouts occur;
do not replay the same entire approved plan by default.

Reserve supervisor time for validation and durable recording independently of
the editable worker's ability to return a final message. Start with the current
900-second worker and two-hour invocation limits; choose shorter work slices,
then use measurements before changing a limit. Record worker start/end, last
completed operation, model connection failures, local-check duration and handoff
status. Treat the final attempt's service failure separately from a failed
accounting check. New inputs for a blocked task must be part of its retry
fingerprint; unchanged failed retrievals must not be retried automatically.

Add an explicit phase-completion check to the supervisor. For P08, acceptance
requires engineering checks, all four criteria complete, two admitted same-fact
lifecycles covering both outcomes, unchanged evidence and a completed independent
`AGREE`. Retain legitimate incomplete engineering results. Use a declared
argument-list checker hook, with no shell evaluation, and avoid running the
same unit suite twice when the registered checker already includes it.

Acceptance tests: timeout after a partial write; timeout after valid outputs;
missing handoff; stale handoff/input hashes; repeated no-progress timeout;
unchanged external block; new relevant input reopening only its task; lost model
connection; and `AGREE` paired with an incomplete criterion. Every test must
preserve prior acceptance, prevent a second writer and keep the next plan aligned
with actual outcomes. Re-run the controller suite and obtain a fresh review of
the changed control paths. The old review hash cannot authorise changed code.

### C. Resolve the actual authority dependencies

Create one current, versioned authority profile that references v3–v5 as evidence
without modifying their historical decisions. Derive document roles from the
exact target RDF subject/predicates. Record citations and EEA decisions as such;
derive applicability from inspected provisions, instrument terms, reporting
context, effective dates and transition assumptions.

For every required claim, record its source paragraph, affected operation/note,
period, dependencies, inspection decision and unresolved material issue. A failed
download is an access result; it does not by itself identify which accounting
claim is unsupported. Resolve the Portuguese correction through the bounded test
above, then independently review the claim-specific applicability matrix. Include
the remaining eligibility and transition work even if that one source is found.

Acceptance: missing hashes, wrong editions, omitted relevant amendments and
unresolved material claims reject admission. Irrelevant citation links cannot
create amendment blockers. If a necessary provision remains unavailable, retain
a precise external block and continue independent engineering preparation.

### D. Implement the second regime through the full lifecycle

Dispatch by an explicit admitted reporting profile. Keep the AASB profile and
its checked cases; add EU admission as a genuine success path only after C.
Use distinct EU claim identifiers for issuance, measurement, each accrual and
coupon, redemption, conversion and notes. Update comparison dispatch and note
descriptions. Shared rational arithmetic is appropriate only where independently
inspected authority supports the same treatment; do not relabel AASB evidence.

Use unchanged economics: principal/proceeds/fair value 100, coupon 5, yield 1/10,
two 2024–2025 annual periods, ten shares, opening cash 20 and AUD functional
currency. The hypothetical reporting context may differ; the contract facts may
not. If the provisions imply agreement, report anchored agreement rather than
manufacturing a difference. This bounded agreement cannot close MC19's wider
requirement for genuinely different treatments.

Acceptance: both EU maturity outcomes replay and pass independent present-value,
annual-interest, journal/state and note checks. Mutations of reporting context,
dates, a relevant source/decision/claim, cash flows, shares, event order or note
dependencies must reject before state mutation. A EU label backed by AASB-only
claims must fail. Unsupported US GAAP/ASBE rows remain honestly unresolved.

### E. Verify and review a complete P08 candidate, then resume the master

Build the final candidate with both regimes and every changed source/code/test
pin. Require a completed standalone checker with all phase criteria complete
and an independent result review of that exact candidate. Fix concrete findings
in the corresponding small task and recheck only affected evidence. Refresh the
next-phase plan from the actual decision and preserve the frozen report corpus.

The existing approved command remains:

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py run
```

The planned repairs use project-local code and the existing sequential worker
grant. No broader allow rule or new worker-permission mode is needed. Test the
exact command against the installed rule after controller changes; never weaken
the sandbox or request another approval for unchanged authorised scope.

## Decision and limits

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Repair engineering consistency first | Causal mismatch reproduced; in-memory correction clears all 62 findings | Current result replay fails | Publication under interruption is not implemented | A | The corrected partial bundle would not complete P08 |
| Replace broad timeout retries with checked subtask progress | Same-plan/no-check retry path reproduced | Latest run has no completed editable response | Unmeasured model-service/reasoning share of elapsed time | B | A longer timeout alone would solve the problem |
| Correct and review authority dependencies | Six citation/amendment errors confirmed; preserved source bytes match | EU admission remains unsupported | Portuguese correction's content and final applicability review | C | Foreign-language corrections can be ignored |
| Implement and admit a real EU lifecycle | Three AASB-only/rejection barriers traced | Both EU outcomes remain absent | Applicability must pass first | D, then E | AASB arithmetic or quotation presence establishes EU accounting validity |

Post-investigation red team: the strongest alternative explanation for the last
missing response is the observed model-service outage; it cannot explain the
first two timeouts or the deterministic integration failures. A genuinely
material unavailable correction could keep EU admission blocked even after all
engineering repairs. The weakest causal evidence concerns how worker time was
divided among reasoning, repeated inspection and service delay; the logs do not
provide a full profiler. The diagnosis therefore recommends instrumentation and
bounded slices, not a claim that one latency setting is the root cause.

The result rejects the current P08 candidate's completeness and consistency,
not the accounting-engine research direction. No stochastic ranking or forecast
claim is made. Repairs above are proposed; production/controller code, current
state, next-plan files and accepted evidence remain unchanged by this work unit.
