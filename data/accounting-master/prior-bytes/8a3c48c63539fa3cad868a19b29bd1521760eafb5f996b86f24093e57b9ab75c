# Accounting master — controller review and repairs

Date: 2 October 2026. Plan: ../../plans/accounting-master-program.md.
This record concerns orchestration correctness and permissions, not accounting
validity, benchmark accuracy or completion of G1–G18.

## Author's skeptical review

The controller is an executable sequential program with a P00–P14 dependency
catalog. Plans are generated from current state and previous findings, reviewed
before implementation, and frozen by hash. Implementation is followed by actual
tests and a read-only result review. Failures enter an executed repair attempt;
checks and review run again. Exhausted repair attempts retain the partial work.
An unchanged external block is not retried on ordinary resume; independent
eligible phases continue. The operator may explicitly retry a repaired external
dependency with the same command prefix and --retry-blocked.

The initial review found and repaired these issues before requesting the
upfront execution grant:

1. The unittest singleton retained an earlier discovery root. Replaced it with
   a fresh TestLoader per suite. The failing zero-test fixture now reports an
   honest failed check rather than a discovery exception.
2. The real corpus regression module imports scripts as a package. The first
   baseline preflight lacked the repository root in sys.path. Added that root
   to baseline/phase test setup and reran the failed baseline into a separate
   attempt directory; the original failure log is preserved.
3. A subprocess that did not consume stdin could block a large prompt before
   the timeout loop. Changed worker input to a file-backed stream and tested
   a nonreading process with a one-megabyte prompt.
4. An implementation could accidentally rewrite its approved plan or
   supervisor state. Added before/after guards and rejection tests.
5. Previous next-action recommendations were not present in the next plan.
   Added them and verified propagation into the following phase's packet.
6. Accepted artifacts could become stale. Resume now checks their recorded
   hashes and transitively invalidates dependent accepted phases.
7. Existing editable files needed preservation without usable Git. Preserve
   their prior bytes before each implementation/repair and record actual file
   changes for result review. Frozen source/release files have separate hash
   protection; a detected change vetoes continuation.
8. A generic interpreter allow rule would be too broad. The dedicated rule
   matches only the fixed absolute master entrypoint. Both the proposed rule
   alone and the effective existing-plus-proposed rule set return allow for
   the exact documented command. Unrelated Python and shell commands do not
   match the dedicated rule.

Author review verdict: proceed to the explicitly authorised noninteractive
health probe and independent read-only controller review. Substantive worker
execution remains gated by that review; a timeout or unavailable reviewer is
not a pass. Claude is unavailable: its native executable is missing in both
the ordinary help check and a trusted minimal health probe. No Claude verdict
is claimed and no installation was attempted.

## Executed evidence before the upfront grant

- 27 controller tests passed, including deliberate bad output repaired to the
  expected value before acceptance, failed-plan repair, zero-test rejection,
  stale evidence, interruption/resume, exclusive locking, unchanged external
  blocks, shell-literal handling and process timeouts.
- The repaired real baseline preflight passed independent corpus verification,
  all five existing bounded reference suites and the 20 corpus regression tests.
- P01's real deterministic preflight produced 192 source-work records, no gold
  labels, 56 sourced filing-date records and 136 unverified publication dates.
- Original source/release files and historical checker reports were retained.
  New legacy-check results were redirected to the new run directory.

Evidence paths:

- data/accounting-master/runs/preflight-20261002/P00/corpus-regressions.log
  preserves the initial import failure.
- data/accounting-master/runs/preflight-repair-20261002/P00/baseline.json
  and neighbouring reports preserve the repaired baseline.
- data/accounting-master/runs/preflight-20261002/P01/source-work-register.json
  preserves the derived source inventory.
- data/accounting-master/accdsl-master.rules is the reviewed candidate rule.

The actual worker review, approval-rule installation, phase attempts and future
repairs are recorded separately under data/accounting-master/runs. A successful
phase is accepted_internal for its bounded slice; mission_complete is always
false until the original mission receives separate justified acceptance.

## Recovery from the first controller-review timeout

The initial model health probe passed and the dedicated rule was installed.
The first whole-controller review exhausted its 240-second limit while reading
the broader historical mission/audits. It produced no final verdict; the master
stopped before phase execution and retained the log. This was a review-packet
scope problem, not an accounting or implementation acceptance result.

The review is now split into four self-contained packet-only passes: process
and permissions; state/refresh/recovery; phase planning and repair; evidence and
tests. Exact function bodies, interfaces, current tests and the reviewed plan
are supplied. Reviewers are instructed to use the packet without tools or a
new historical-project audit. All four must agree on the current controller
before execution can proceed. The same saved entrypoint approval is reused.

The recovery also creates the initial next-plan before review and extends
protected hashes to historical pre-repair/pre-expert snapshots and existing
research/filing PDFs, while allowing the current manuscript to be revised.

## Focused review findings and repair — 3 October 2026

The first focused reviewer returned seven concrete process/permission findings.
The next scope exceeded its time bound, so it supplied no verdict. The findings
were treated as repair requirements, not approval:

- SIGTERM handling now encloses standalone review and every public child-launching
  action, not only run.
- Internal helpers require a one-use supervisor grant, inherited locked descriptor,
  matching parent identity, active phase and fresh output destination.
- Integrity checks run in finally paths for failed processes and malformed worker
  responses, preserving the original error in a separate integrity report.
- Process-group cleanup retains an unreaped leader until signalling is finished
  and is idempotent. Abandoned-worker recovery uses stable pidfds.
- Rule installation is serialized; complete bytes are published atomically without
  replacing a conflicting file. Installation receipts support idempotent recovery.
- Worker startup queries the CLI's effective integration configuration rather
  than assuming one home config file, then verifies all those integrations are
  disabled for that invocation.
- The initial-process-group guarantee and the trusted no-detachment assumption
  are stated explicitly. No cgroup or malicious-worker containment is claimed.

The dependency catalog now allows shared compiler work and primary-authority
work to proceed independently of an unresolved Apple case. Original gap IDs
and wider acceptance requirements are unchanged.

Review packets are now split across seven narrower scopes. A successful scope
review is cached only against the exact packet, current controller hashes and
test evidence; changed code invalidates it. This avoids repeating an unchanged
passed review when a later request times out. No timeout is converted to AGREE.

The recovery test exposed that this Python build lacks os.pidfd_open even
though the Linux kernel interface is present. A reviewed x86-64 syscall binding
now supplies that missing wrapper; unsupported ABIs still stop explicitly.
Controller tests are an executable preflight before any model review: stale,
missing or failed current evidence triggers a fresh bounded test run, and a
failure blocks the expensive review/phase calls.

## Completed repair batch and review adjudication

The controller now passes 55 focused tests. Additional repairs preserve a
phase-entry deletion obligation across repairs/resume, handle BLOCKED from
review roles explicitly, reject stale response destinations, publish preserved
bytes atomically, reject conflicting protection hashes, retain legacy failure
logs, and commit a canonical state generation before rebuilding atomic plan
views. Cleanup defers repeated handled signals and closes recovery handles on
identity-read failure. Missing source-release protection is a production veto.

Three findings needed interface clarification rather than changing correct
behaviour:

- Rule match/not_match entries are load-time examples, not runtime command
  filters. The runtime pattern is the fixed executable argument prefix. The
  actual checker allows all six public actions; private helper execution is
  independently rejected without its supervisor grant. Source and actual checks
  are in data/accounting-master/rule-grounding.json.
- Each worker phase already creates a fresh plan and obtains review_plan
  acceptance before implementation, then verifies its frozen hash. P00/P01 are
  fixed reviewed operations; they now also save an explicit fresh contract and
  input-view record. Controller review is not used as a substitute for phase
  plan review.
- run is the explicit operator resume action, so it archives a prior stop
  request. A stop during execution prevents further work. Unknown external
  access changes are retried explicitly with --retry-blocked; they are not
  repeatedly polled. Tests cover these declared semantics.

Structured negative review findings are preserved as raw JSON and may be
losslessly represented as strings for the strict response exchange. This never
converts a malformed positive response into acceptance. An unchanged modular
scope review may be reused only after the full current controller test suite
passes; changed scope code, interfaces or evidence contracts invalidate it.
