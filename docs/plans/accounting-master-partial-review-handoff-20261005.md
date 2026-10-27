# Repair the bounded-review handoff

The user asked whether the authorized campaign had finished. It stopped at
2026-10-04 21:55 UTC (5 October 05:55 Hong Kong), with useful uncertainty work
saved but no full P16 acceptance. The existing 48-hour authorization continues;
its stored deadline remains 1940875.230219879 on the recorded boot. This repair
addresses MC25/MC27/MC33–MC35 orchestration and evidence continuity. It changes
no accounting method, product scope, retry allowance or approval boundary.

## Traced cause

In run 20261004T202513-2bc09c08, execution 0 saved the uncertainty contract and
UC01–UC19. Execution 1 repaired chaining. Execution 2 produced an assessment.
All three returned PARTIAL. The phase-wide structural checker correctly failed
`whole architecture contracts`, since five other contracts remain unfinished.
`Master.execute_phase` required `checked.passed` before dispatching a bounded
result review, so it skipped the independent review each time. Subsequent plans
requested that review, but the loop always selected implement/repair. Execution
3 correctly refused the mismatched role. The resulting blocked_external input
signature removed P16 from eligibility, although no external dependency existed.

`load_pending_review` also required full phase acceptance readiness. Therefore
simply dispatching one review would leave bounded reviews unresumable after a
timeout or insufficient budget. These are controller-routing failures, not
uncertainty rejection, mathematical failure, timeout or research-direction veto.

## Repair and evidence contract

1. Review a valid returned PARTIAL under `bounded_partial_work` even when the
   phase-wide check is incomplete. Retain current checks and their failures in
   the packet; the reviewer must assess the completed task and identify any
   relevant artifact failures. No review follows an unfinished/timed-out worker
   that did not return a valid result.
2. Save a hash-checked pending review before dispatch. Permit resume of a named
   bounded review with valid PARTIAL work, recorded checks and unchanged inputs,
   dependencies and plan, while retaining existing full-phase resume rules.
   Insufficient time or unavailable review returns needs_review without another
   editable attempt. A stale checkpoint must be invalidated and rechecked.
3. Retain the terminal independent review path/verdict. Use its next actions and
   findings in the continuation and subsequent reviewed plan so that a completed
   review is not requested again. Bounded AGREE cannot accept a phase; REVISE
   triggers repair and BLOCKED retains a specific dependency. Preserve the
   existing full-phase acceptance predicate.
4. Add focused controller tests for incomplete-phase partial review, bounded
   review resume without reimplementation, stale evidence, rejection, and the
   inability of bounded AGREE to accept a phase. Run existing controller and
   proposal suites and inspect the diff. Update the operating note.
5. Seed the already-approved uncertainty review with the saved current work,
   fresh checks and exact source hashes under the master locks. Keep the failed
   execution and old continuations unchanged. Refresh eligibility, request fresh
   controller review through the usual entrypoint, and resume the original
   campaign with its exact approved command.

Comparator: the current controller and the saved P16 dispatch failure. Pass
means the actual review role receives complete unchanged bounded evidence,
timeouts resume read-only, and full-phase acceptance still requires all declared
criteria and an independent full result review. Test counts are explanatory.
Protected-input changes, unexplained writers, invalid evidence or a changed
deadline veto continuation. A reviewer finding rejects the particular candidate
and triggers the appropriate repair; it does not reject the mission.

## Skeptical audit before implementation

Wrong baseline: compare actual PARTIAL results and the expected incomplete-phase
checker, not a fictitious completed P16. Proxy promotion: a bounded AGREE must
never become full acceptance; explicitly test that boundary. Hidden assumption:
the checker can stop before later contracts, so the reviewer receives both its
limits and the concrete bounded artifacts. No fabricated passing checker or
special whole-contract exception is introduced. Fair comparison: same files,
same criteria, same remaining budget. Environment: standard-library controller
tests, then existing trusted model-worker entrypoint; no environment/model change.
Stop conditions: stale inputs require fresh checking; unavailable reviewers keep
a pending review; integrity and the original deadline still stop execution.

Pre-mortem: the review could succeed but its actions could be lost, causing
another review-only repair loop. Save its disposition in the continuation and
test the next planning packet. A controller change invalidates its old review;
the usual startup review must approve the new code before phase work. The saved
uncertainty assessment is an inspection aid, not independent acceptance.

Audit decision: proceed with this bounded control repair and regressions. The
existing authorization covers completing the blocked review and campaign work.
