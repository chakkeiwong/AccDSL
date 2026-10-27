# Accounting master program — reviewed execution plan

## Controller recovery and final evidence (5 October 2026)

The [controller repair](accounting-master-controller-repair-20261005.md) addresses
the latest independent findings before P16 resumes. Both CLI and direct ordinary
invocations enforce 7,200 seconds. A final pre-launch stop/deadline check records
`launched: false` without spending an editable retry. Atomic JSON publication
cleans its own failed temporary files, and preservation traversal errors veto
authoring rather than silently omitting subdirectories.

Campaigns persist a pending invocation identity before dispatch. Under the
runner lock, each run reloads state, captures its baseline and saves a start
manifest before work. Its final manifest binds terminal outcome, file/acceptance
progress and next eligibility from that run. The campaign accounts for it once,
including after interruption between run completion and campaign update. Missing
terminal evidence remains a supervisor stop. Concurrent serialized ordinary
work cannot supply a stale baseline or overwrite the consumed run decision.

Bounded partial reviews pin present evidence and explicitly record absent final
files. Resume invalidates when either set changes; complete phase acceptance
still requires all evidence. P18/P19 now also require bound render/review records
and explicit dispositions of upstream blocking decisions, as specified in the
[evidence supplement](accounting-proposal-evidence-supplement-20261005.md).
The current startup suites are `test_accounting_master.py` and
`test_accounting_proposal_current.py`; the latter retains all original proposal
test cases with updated positive fixtures and new regressions. The accepted old
proposal tests and artifact-format note remain unchanged as historical evidence.

The follow-up startup review also requires prepared worker packet/schema/prompt
and recovery bytes to remain unchanged through success and interruption. Local
configuration queries use the same registered bounded process lifecycle, with
separate stdout/stderr and the original absolute cutoff. Event/process records
are checked against exact supervisor writes. New valid operator stop requests
are allowed external input and always prevent response acceptance; an existing
request cannot change unnoticed. This does not identify a hostile same-user
actor. Test overrides require explicit isolated test mode and are rejected in
the live worktree. Built-in validation reads and binds the saved primary JSON.
Consuming historical campaign success rechecks current protection and proposal
readiness under the runner lock before publishing current readiness.

The final follow-up also verifies metadata-independent cleanup of a new,
unreaped direct child, retaining an unresolved stop when quiescence cannot be
verified. Handled shutdown is deferred across each runtime publication and its
expected-hash update. Unknown editable phases are rejected before any launch.
Malformed startup records are retained alongside a durable non-executable stop;
campaign errors never recreate an allowance. Startup requires separate successful
non-skipped execution in both required suites. P18 checks complete page coverage
against the actual PDF using the existing PyMuPDF dependency. The reviewed
finding-adjudication mechanism below governs the final supervisor disposition;
it is distinct from independent per-phase plan/result acceptance.

## Active scope: governing proposal first (4 October 2026)

The user's correction supersedes the historical implementation order below.
`run` now performs only proposal preparation. P15 audits requirements and prior
evidence; P16 specifies architecture and the proposed initial profile; P17
specifies accounting, sector, research and forecasting methods; P18 integrates,
builds and inspects the manuscript; P19 assembles and independently reviews
readiness. All old P00–P14 contracts and evidence are retained, with their queue
held. Accepted prototypes do not approve the product architecture.

The user's 5 October direction grants a 48-hour full proposal campaign. The
`campaign` action repeats normal bounded `run` invocations under one durable
monotonic deadline, continuing saved work through P16–P19 as dependencies clear.
It retains the existing five-retry phase limit, startup tests, plan/result
reviews and evidence protection. Resume never resets its deadline. Automatic
invocations preserve stop requests, and integrity, interrupted ownership,
repeated no-progress, unavailable eligible work or the campaign deadline stop
the loop for supervisor attention. This is explicit user-authorized campaign
execution; the ordinary `run` action retains its existing resume semantics.
See `docs/plans/accounting-master-campaign-20261005.md`.

The user's 4 October continuation sets the allowance to one initial attempt plus
up to five retries for each phase execution, within the existing two-hour run
limit. Planning corrections use the same configured cap. Earlier integrity,
dependency and no-progress stops still apply. The executable catalog is the
source of this limit; the reviewer packet reads it directly. See
`docs/plans/accounting-master-five-retries-20261004.md`.

The catalog contains an explicit class, schedule and write scope for every
phase. Eligibility and worker launch both enforce proposal mode. Design workers
may write only their designated document/research directories and declared
deliverables. Read-only reviewers must leave all project bytes unchanged even
on errors. Product code and controller-owned checks are outside these scopes.
Any future exploratory probe needs a stated design question, decision consequence
and stop condition; it cannot be promoted into a product module by passing tests.

The supervisor derives `proposal-ready.json` from accepted proposal phases,
current source/coverage/contracts/profile/fixtures, built/rendered PDF evidence
and a completed independent review of the same candidate. A worker-written
boolean, structural checker or legacy phase acceptance cannot open the gate.
Missing or stale evidence closes it. Internal readiness leaves human acceptance
pending and ends this proposal campaign; it does not auto-start implementation.
The first implementation slice must be chosen from the completed proposal.

Phase check outputs are fresh, supervisor-owned JSON with source/output hashes.
Declared evidence artifacts are checked for nonempty content, valid structure
and expected results. Review calls use role-specific response schemas and one
bounded retry in a fresh directory after timeout, provider error or invalid role.
Prior responses remain intact. Proposal workers use the registered structural
checker, not manufactured unit tests of prose; result review checks substance.

Worker prompts summarise passing checks and hash inventories; the full packet,
checks and continuation remain linked on disk. Failures, criteria and next
actions remain explicit. Editable workers require their full declared window
plus the supervisor verification reserve. A new planning cycle reserves time
for planning, review and useful execution. Insufficient time is a resumable
budget stop, without a launched retry or no-progress penalty.

Worker supervision follows
[the progress-supervision repair](accounting-progress-supervision-20261006.md),
which supersedes the fixed worker cutoff described in the historical timing
notes below. A protected v2 budget records the ordinary window and hard ceiling
on the host monotonic clock. The clock helper reads a supervisor-owned control
record and prints acknowledgements, file-backed milestones or located read-only
findings. The process loop consumes completed successful command events once,
ignores log activity and repeated evidence, and records its decisions beside the
worker. These scheduling signals cannot accept a phase.

After five minutes without verified progress, the supervisor requests a
checkpoint and allows up to three minutes for a concrete response. A clock poll
alone does not cure stagnation. It requests saving/checking three minutes before
the ordinary cutoff and a structured response one minute before. Recent new
verified progress plus acknowledged instructions can earn two-minute finishing
grants, up to five minutes total. Each additional grant needs new progress.
Editable admission still requires 900 seconds plus the 300-second verification
reserve; review and planning use their catalog windows. Every extension is
clamped by that reserve, the invocation ceiling and original campaign deadline.
Health probes and packet-only reviews retain their short fixed bounds.

During a checkpoint request the clock displays the actual response grace as
remaining time and directs each role to its own response schema. At campaign
boundaries, a completed bounded result review also counts as progress, provided
its response hash, role verdict, current invocation path and successful process
record match. Older reviews, failed processes and planning alone do not renew
the campaign. This scheduling progress cannot accept the full phase.

An editable worker can print a complete PARTIAL response and scoped hashes with
`--kind checkpoint --checkpoint-json` through the clock helper. The supervisor
validates and saves it, bound to the worker budget, phase, approved plan and
prerequisite evidence. After a progress stop or timeout, unchanged scoped files
and evidence permit fresh checks and normal bounded independent review without
another edit/plan cycle. Added, changed or deleted scoped files invalidate reuse;
checks revalidate the snapshot as well. Operator stops and integrity failures
veto reuse. The original failed process remains failed, and a recovered PARTIAL
cannot accept the whole phase. The helper never writes supervisor records.

This channel is cooperative: a worker blocked in a provider request cannot read
instructions until that request returns. Unacknowledged instructions end at the
recorded grace limit. No model/provider, approval policy or retry allowance is
changed. Scheduling defaults are engineering hypotheses; live observations must
check for false stalls and unproductive extensions.

P15 follows `docs/plans/accounting-p15-execution-repair-20261004.md`: one
independently reviewed substantive scope per invocation, then bounded saved
assessment groups. Passing file progress can continue inside that scope after
PARTIAL or a timeout, with current checks and refreshed next-plan data. Routine
partial work is reviewed at the terminal phase review rather than after every
group. Failed checks, substantive rejection and actual no-progress require the
repair path. Other phases retain their existing planning/review policy. A
progress.md-only change is not file progress. Full independent result review
and every original criterion remain necessary for phase acceptance.

Historical report inputs resolve to exact retained snapshots, separately from
current deliverable references. The supervisor saves mechanical verification
and continuation records; workers must not manufacture extra completion files
or versioned validators as new acceptance prerequisites. Current outcomes record
actual editable attempts, retries, completed partial tasks, timeouts and stop
category. The five-retry ceiling and two-hour invocation remain unchanged.

The independent review also identified recovery and evidence defects, now
repaired: process ownership includes the Linux boot ID; losing an observed
checkpoint stops execution; worker inventories include persistent configuration
and prior run records; integrity-check failures veto continuation; unresolved
deletions stop the scheduler; preflight is read-only with prior-byte backups and
durable restoration obligations; partial snapshots bind declared checker inputs;
and the manuscript binds actual TeX recorder inputs, including figures and data.
Git internals retain the worker sandbox's protection; disposable language caches
and exact supervisor-generated runtime files are excluded from write inventories.

The explicit migration adds P15–P19 and binds the workflow without changing old
phase contracts or laundering their acceptance. Keep the existing lock, cleanup,
time/repair limits, narrow command prefix, standing sequential-worker grant and
frozen corpus protections. Details, audit and test contract:
`docs/plans/accounting-proposal-first-repair-20261004.md`.

The rest of this file retains the original control-plane design and historical
execution details. Its descriptions of the former P00–P14 implementation queue
do not authorise that queue under the active proposal-only mode.

Date: 2 October 2026. User authority: create, review and execute a master program for the consolidated gaps, with actual repair, refreshed plans between phases, and reusable upfront approvals. Scope: MC01–MC35 and G1–G18; the existing mission remains authoritative.

## Objective and execution contract

Build a real sequential orchestration program, then execute it. A phase follows:
refresh plan from current evidence -> skeptical review -> implementation ->
deterministic verification -> read-only result review -> repair and reverify
when required -> record scoped result -> refresh next plan. A failed phase
does not mark its gap closed. Independent eligible phases continue when one
has a genuine external block.

Source collection is already accepted. Baseline checks, derived source
inventories, compiler/runtime conformance, accounting support, empirical
forecasting and independent human acceptance remain different evidence classes.
A phase accepted internally advances only its declared slice. All gaps remain
open until their original requirements have appropriate closure evidence.

## Skeptical audit before implementation

| Risk | Required design response |
| --- | --- |
| Wrong baseline or repeated acquisition | Verify the accepted 192-report panel and current hashes; never restart its collector by default. |
| Proxy success | Exit zero, a reviewer token, populated JSON, passing tests or an acquired file cannot alone establish accounting validity or gap closure. Require predeclared scoped evidence, actual checks and explicit residuals. |
| Static/stale phase checklist | Refresh a plan after every accepted, failed or blocked phase from actual outcomes, hashes, unresolved issues and dependencies. Review it before implementation. |
| Repair as advice only | Execute repair workers against captured failures; rerun verification and result review. Store each attempt separately. |
| Infinite retries or hidden cost | Bound per-command time, total run time and repair attempts. Exhaustion is visible and resumable, never completion. Limits are operational convenience choices, not scientific stopping criteria. |
| Test-tampering or evidence loss | Freeze controller/catalog/schema identities during worker execution. Protect accepted source bytes and historical release files; preserve existing material before substantive updates. |
| Approval storms | One stable absolute Python entrypoint; one dedicated prefix rule; argument-list subprocess calls without shell wrappers. Noninteractive workers keep workspace-write/read-only sandboxes and never ask for nested approvals. A denied capability is reported once, not repeatedly escalated. |
| Unsafe global permission changes | Add only the reviewed project entrypoint rule in a separate file; preserve existing rules/settings. Test exact command matches and negative examples with execpolicy. Do not disable the sandbox or use broad interpreter/shell rules. |
| Unreviewed autonomous delegation | Sequential implementation/read-only-review workers are opt-in in the upfront grant. Do not start them until that approval is received. No parallel or recursive workers. |
| Environment mismatch | Record interpreter/tool paths and versions. Claude's native executable is missing in both ordinary help and a trusted health probe; do not silently claim Claude review. Use the existing Codex CLI after explicit worker grant, with no model override. |
| Invalid promotion / unfair comparisons | Forecast and stochastic phases need separate evidence contracts and matched baselines before execution. Source-QA exposure and issuer dependence remain visible. |

Audit decision: proceed with controller implementation and local control-plane
tests. Substantive workers wait for the single concrete upfront grant and a
successful controller review. No program-generated review can authorise new
spending, accounts, outreach, publication or wider filesystem permissions.

## Defaults and limits

| Choice | Provenance / reason | Failure mode / early check | Status |
| --- | --- | --- | --- |
| Sequential workers | One shared workspace; preserve single-writer semantics | Child outlives timeout or a second runner starts; test process-group termination and exclusive lock | Reviewed engineering constraint |
| 900-second implementation attempts; 720-second plans; 600-second phase reviews; 240-second controller packets | P02/P03 required a distinct planning budget; P05 result reviews repeatedly exceeded 240 seconds and P04's successful review took 238.855 seconds | Bound each worker and the total invocation; reuse checked work after review timeouts and inspect actual verdicts | Operational hypotheses, not scientific stopping criteria |
| Five retries per phase execution after the initial attempt | Explicit user direction on 4 October 2026; bounded by the run wall limit | Cap may expire before completion; preserve exact findings and partial work; diagnostic verifies six attempts and no seventh | User-set operational limit |
| 7,200-second run wall limit | Bound one invocation | Mission remains unfinished; save explicit budget-limited status and next plan | Operational bound, no completion claim |
| Existing configured Codex model | Avoid changing model/account configuration | Health probe and structured response validation expose incompatibility | Inherited configuration, not a method-performance claim |
| Medium reasoning for narrow controller packets; high for phase planning/result review; implementation retains configured effort | Broad/max and some high-effort controller packets exceeded their bounds; narrow packets and fault tests supply complementary evidence | A reviewer may miss a defect; every material finding needs a documented disposition and executed verification | Operational hypothesis, no model-quality ranking; no global/model change |
| Workspace-write implementer and read-only planner/reviewer; never approvals | Eliminate nested UI prompts while retaining filesystem sandbox | Required access may be denied; record actual blocker and continue independent work | Explicit upfront grant required |
| Project-local dependencies only | Preserve the scientific environment | Missing libraries must be isolated; no global/conda install | Engineering constraint |

## Evidence contract and verification

Question: does the master execute bounded phases, actually repair failures,
refresh reviewed next-phase plans, preserve evidence and resume without
duplicate successful work or repeated approvals?

Comparator: the current manual sequence and the frozen corpus/reference
baseline. This is control-plane engineering, not a method-performance study.

Primary pass criteria: executable runner; exact allow-rule match; tested
phase state transitions; a real failed verification followed by executed
repair and successful recheck; next-plan refresh containing the observed
outcome; a real bounded run with durable logs/state and honest residuals.

Vetoes: zero-test false pass; stale plan/control hashes; invalid worker
responses; accepted results without deterministic checks/review; lost evidence;
concurrent writers; unbounded child processes; arbitrary shell command injection;
promotion of all G1–G18 from phase-level evidence.

Explanatory diagnostics: check/test counts, elapsed time, file counts and
number of repairs. They are not accounting accuracy or forecast metrics.

Artifacts: scripts/run_accounting_master.py; scripts/accounting_master_catalog.json;
tests/test_accounting_master.py; docs/plans/accounting-master-program.md;
data/accounting-master/{state.json,events.jsonl,next-plan.json,next-plan.md,runs/};
docs/design/review/accounting-master-review.md; docs/plans/accounting-master-checkpoint.md.

## Upfront permission package

The reviewed entrypoint will install only:
~/.codex/rules/accdsl-master.rules, matching
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py

The same exact prefix will be used for install-and-run, run/resume, status,
review and refresh. The installer validates positive and negative matches
before installation and preserves existing rules. User settings and existing
approvals are not overwritten. Runtime-managed policy can still reject an
action; an allow file cannot override it.

The single approval request will expressly cover sequential sandboxed Codex
implementation and read-only review workers for this master program, bounded
public-source research and project-local code/test/artifact work. No paid data,
new accounts, professional engagement, outbound messages, deployment, global
package installation, permission bypass, Git initialization or source deletion.
Network/worker startup failures are diagnosed once and recorded.
Worker invocations disable unrelated apps/plugins/hooks/MCP startup and nested
agent capability for this command only. The configured model and authentication
are retained. Workers may not start detached jobs. Child process-group identity
is persisted; SIGTERM triggers cleanup, and resume checks for an existing prior
worker before it permits another writer. Ambiguous ownership stops for a scoped
diagnostic rather than signalling an unrelated process.

The lifecycle guarantee is limited to the initial process group and ordinary
supervisor interruption/restart. Workers are trusted not to escape that group
with detached jobs; this is an explicit, unenforced operating assumption, not
cgroup containment or protection against a malicious worker. A cgroup-based
runner would be a separate future hardening task if that threat model is needed.
The current scope does not require new host privileges for cgroup management.
Handled signals are deferred across launch, identity capture and registration;
the dedicated supervisor is single-threaded. Uncatchable termination between
fork and durable registration is outside this containment guarantee and is not
represented as safe resumable completion.

Internal helper calls require a one-use capability and the inherited supervisor
lock. They cannot be started directly or overwrite a previous attempt's result.
The helper closes its descriptor after validating the grant; the parent retains
the lock, and restart cleans a positively identified abandoned worker before
another phase runs. Stable pidfds protect recovery signalling from PID reuse.
Rule publication is serialized and atomic, with an idempotent installation
receipt for recovery between publication and the authorization record.

## Phase coverage and continuation

### Checked partial work and criterion veto

The 3 October P08 repair adds a registered standalone checker, invoked once with
literal arguments inside the bounded supervisor check process. It includes P08's
unit suite and explicit completion criteria. Engineering success and reviewer
AGREE cannot override a missing/incomplete declared criterion. P08 requires all
four criterion fields and complete admitted same-fact comparisons before phase
acceptance. Passing incomplete engineering results remain useful repair evidence.

Editable failures (including timeout or missing final response) are checked only
after child cleanup and integrity verification. The supervisor records current
checks, missing files, hashes and next actions in a continuation, without inventing
an implementation response. A worker may return PARTIAL for a bounded task; a
review of that task does not accept the phase. Further partial-work attempts need
a fresh reviewed plan. The catalog supplies finite P08 tasks; completed checked
work is skipped. Two unchanged failures defer that phase until declared inputs
change or an explicit --retry-blocked invocation. External block signatures also
include phase-specific source inputs. Independent eligible phases can continue.

The existing 900-second editable cap and two-repair allowance remain. Editable
workers additionally reserve 300 seconds of invocation time for the supervisor's
bounded checks and durable recording. An absolute cutoff covers startup queries,
prompt preparation and execution; query timeouts and the final launch allowance
are recomputed against it. No worker starts when that reserve cannot be retained.
Progress/check records are hash-validated navigation; they cannot
confer acceptance. P12's unchanged pending full-phase review remains reusable.
See [the audited repair](accounting-p08-execution-repair-20261003.md).

Every editable repair, including failed checks and result-review findings, now
requires refreshed planning and a separate plan review. Partial-review BLOCKED
is persisted as a block and cannot fall through into implementation. Accepted
phases carry the exact phase-contract hash and prerequisite evidence identity;
changes invalidate reuse. Legacy acceptance requires an explicit evidence-backed
migration rather than automatic rebinding. The nine existing accepted phases
were compared with their retained reviewed contracts before migration.

Preservation covers all file types and root configurations in editable scope.
Explicit exclusions are Git/service configuration, dependency/cache directories,
frozen corpus/snapshots and supervisor records; only declared phase deliverables
are editable beneath data/accounting-master. Editable symlinks require explicit
preservation before work. Invalid structured recovery records remain linked with
a bounded recheck diagnostic. Initial refresh is within the guarded run lifecycle;
final refresh failures produce consistent veto outcomes in the manifest, event,
return value and non-executable next plan.

Every execution attempt persists running/repairing before launching work or its
internal verification helper, including after a partial-work replan. The actual
locked helper path is covered by an integration regression. Stop requests defer
verification without starting another child; preserved work is rechecked on resume.

### Controller review after repair

The previous seven-scope unanimity rule caused repeated whole-controller review
without reaching the substantive work. Replace that operational choice with
finding-based review: the supervising agent inspects the current code, records
every material finding as repaired with verification or refuted with concrete
evidence, and binds its verdict to the current controller/plan/test hashes and
the durable review note. This is explicitly **supervisor adjudication**, not a
claim that independent reviewers returned seven new AGREE verdicts. Unresolved
material defects still veto execution. The controller suite runs freshly before
reuse of either kind of review. Per-phase planning and result reviews remain
separate read-only worker calls.

P00/P01 are fixed deterministic operations. Their parent independently validates
the output structure, source identities, counts, report checks and limitations,
and writes checks.json and a deterministic PASS/FAIL result-review.json. These
records are not model-review verdicts. Other phases require nonzero passing tests
and a read-only result-review AGREE before acceptance.

Repair audit, 3 October 2026 local time: use the accepted 192-report baseline;
test counts measure orchestration only; original authorization remains a standing
scope grant, never rewritten as approval of later code; refresh verifies controls;
unexpected controller defects stop scheduling. The process recovery bound covers
trusted workers in their original process group. An exited/ambiguous recovery
anchor with live descendants vetoes with retained identities rather than
signalling unrelated processes. No new containment or scientific claim follows.

Audit decision: the repair approach answers the concrete review findings with
bounded regression tests and preserves the existing approval boundary. Execute
the fixed operations first, then the next eligible reviewed implementation phases.

The executable catalog contains P00–P14 and maps every G1–G18 to one or more
phases. P00 verifies the baseline. P01 creates source-context work records.
P02–P14 execute the case, core, numerical, runtime, temporal, review/recovery,
authority, bank, insurer, integration, benchmark, forecast and manuscript work.

A successful bounded slice must retain its larger unresolved obligations.
Blocked dependent phases remain queued while independent eligible phases run.
After all scheduled slices, residual work is emitted as a continuation plan;
the mission is never declared complete automatically. Work requires a renewed
reviewed slice, not a fabricated success flag.

### Review timeout recovery

A phase review timeout receives one fresh read-only retry. Each retry has a
separate destination, and a timed-out response is never accepted. A full phase
review allowance must remain in the invocation before another reviewer starts.
Stop requests and exhausted budgets preserve the pending work. The original
total invocation limit and implementation repair allowance remain unchanged.

Passing checks followed by exhausted review retries produce `needs_review`,
not an editable repair. A saved checkpoint records the work, original approved
plan, checks, phase requirements, prerequisite evidence and contributed-file
hashes. Normal resume validates these records, reruns checks and retries result
review without reimplementing unchanged work. Changed or missing inputs invalidate
reuse. A returned REVISE still invokes actual repair and new verification; failed
checks cannot use this checkpoint to become accepted. Read-only review changes to
checked phase files veto acceptance. See
[the repair and evidence contract](accounting-master-review-retry-repair.md).

For phases using the ordinary review policy, a valid returned partial task also
receives a `bounded_partial_work` result review when the whole-phase checker is
incomplete. The reviewer sees the failed checks and the precise completed task;
its verdict cannot accept the phase. These reviews use the same saved evidence
and read-only resume mechanism. Review unavailability returns `needs_review`
without spending another editable attempt. Terminal findings and next actions
replace the obsolete request to obtain that review, and a resumed review can
advance to planning without requiring an artificial file edit. Full-phase
acceptance still requires all declared criteria and its own result review.
The [handoff repair](accounting-master-partial-review-handoff-20261005.md)
records the P16 dispatch failure and regression checks. The explicitly selected
`reviewed_scope` policy retains its separate terminal-review behavior.

## Commands

Worker recovery now uses bounded structured snapshots saved beside each attempt.
Snapshots record current missing deliverables, changed files, recent process and
check outcomes, review findings and available time. Full records remain on disk;
raw logs are never embedded in recovery prompts. Each implementation worker keeps
an optional progress.md in its output directory. It is unverified working context,
not an acceptance deliverable. Original criteria, deterministic checks, review,
repair limits and process deadlines are unchanged. See
[the focused recovery repair](accounting-master-recovery-repair.md).

Acceptance carries forward the files actually changed during each phase's
implementation and verification attempts. It does not attribute edits by other
phases between invocations to the resumed phase. Actual attempt deltas are saved
even on timeouts and failed checks; explicit evidence and required deliverables
are also hashed. Missing contributed files must be restored. Existing entry
snapshots remain preserved, and legacy partial attempts require a documented
attribution migration before reuse. See
[the attribution repair](accounting-master-attribution-repair.md).

Local engineering checks:
python3 -m unittest discover -s tests -p test_accounting_master.py -v

Approval/bootstrap and execution:
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py install-and-run

Resume:
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py run

Status:
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py status

No shell wrapper, environment assignment, command concatenation or changing
relative path is needed for normal operation.
