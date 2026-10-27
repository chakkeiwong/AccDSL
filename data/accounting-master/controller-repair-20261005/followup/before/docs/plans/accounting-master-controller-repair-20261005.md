# Controller repair before resuming P16

Authorization: the user's direction to continue the proposal campaign, within
the original 48-hour deadline. MC25/MC27/MC33/MC34 govern durable execution and
evidence; MC01–MC35/G1–G18 remain the mission. No product implementation is
enabled. Baseline run `20261005T005619-5a850819` stopped on nine controller
findings. P16 contains four proposed contracts; its remaining five contracts,
profile, fourteen decisions and independent acceptance are unfinished.

## Question and evidence contract

Can the controller resume useful proposal work without launching after a known
stop/deadline, losing invocation accounting, accepting incomplete final evidence,
or damaging saved evidence? Compare with the exact retained controller review,
current source and prior controller tests. Passing requires targeted fault
injection for every finding, preservation of accepted/frozen inputs and a fresh
independent startup controller review. A test count, a partial design or an
author assessment cannot accept the full phase or establish accounting truth.

Continuation vetoes: changed protected evidence, unresolved process ownership,
unreadable preservation, inconsistent invocation state or failed controller
review. Candidate review findings trigger bounded repair. Budget/known-stop
refusal before launch consumes no editable retry. Existing no-progress rules
and original campaign deadline remain; no allowance is renewed.

## Repairs

1. Recheck stop and absolute cutoff immediately before Popen, after preparation.
   Persist an explicit not-launched result and propagate it as a budget/stop
   deferral, retaining post-launch checks. Do not call on_spawn or count a retry.
2. Enforce the ordinary 7,200-second ceiling at CLI and Master.run; clamp campaign
   dispatch to it. The separate campaign deadline remains capped at 172,800.
3. Clean atomic_json's own temporary file on serialization/fsync/publication
   failures and handled interruption; preserve the original exception and prior
   destination on pre-replacement failure. Do not ignore arbitrary temp files.
4. Persist a campaign pending invocation with a reserved run identity before
   dispatch. Capture accepted-phase baseline after reload under runner.lock;
   bind it to the start manifest before work. Publish progress, terminal outcome
   and next-plan decision together in the final run manifest under the lock.
   Reconcile that immutable result exactly once on resume before another run.
   Missing terminal evidence after an interrupted run is a supervisor stop,
   not permission to reset progress counters. Never read a later mutable plan
   or stale self.state as this invocation's outcome.
5. Bounded partial reviews require actual work/check/approved-plan records;
   snapshot existing declared evidence and an explicit absent-file set. Resume
   rechecks both. Full acceptance retains complete-file requirements.
6. Fail preservation traversal on enumeration errors before authoring; propagate
   them as continuation vetoes. No incomplete inventory can authorize work.
7. P19 must explicitly resolve or supersede every upstream blocking decision
   with pinned evidence; a final empty list cannot drop a blocker.
8. P18 requires a render record binding PDF input and output page hashes, and a
   review record binding that exact render record. A rebuilt PDF with old pages
   or old review must fail until evidence is refreshed.

## Skeptical audit and preservation

The latest state is authoritative; the generic stored campaign reason is stale.
The repair must cover interruption between run completion and campaign update,
and a serialized ordinary run occurring before campaign lock acquisition.
Tests need fault injection at those boundaries, not only successful loops.
Partial-review absence is permitted only for the declared incomplete work, not
missing work/check/plan evidence. Renderer provenance is evidence binding, not
automatic proof of visual inspection or resistance to deliberately forged files.
Independent review must still read substance.

P15 pins the old proposal test file and artifact-format note. Preserve both
unchanged. Add a successor proposal test suite retaining all 17 original test
cases, with positive fixtures satisfying the strengthened P18/P19 requirements
and new failure cases. Use that current suite for startup checks; the frozen
earlier fixtures document their historical checker contract. Add an artifact
format supplement and point worker instructions to it. Do not rewrite accepted
hashes to hide changed inputs. Controller tests may be updated because they are
not accepted phase evidence. Preserve original controller files, state, pending
review and candidate-packet import receipt before edits.

Default audit: 7,200/172,800 seconds and five retries are user-authorized limits,
not tuned throughput assumptions. Fail-closed ownership and final evidence are
reviewed correctness requirements. The reserved-ID/manifest design is a local
engineering choice, tested by replay, interruption and interleaving injections.
No numerical, accounting, model-selection or empirical ranking claim is made.

Audit decision: proceed with targeted repairs, current suite and independent
startup review, then resume the existing exact approved campaign command. Stop
on integrity/ownership/deadline failures; repair actionable review findings
within the remaining allowance. Record actual commands, checks, preservation,
result, and next action in the repair evidence directory and checkpoint.

## Pre-resume review, 5 October 2026

The nine original findings have implemented repairs and targeted fault tests.
The retained runs passed 190 controller tests and 20 current proposal tests.
Final source inspection checked the pending identity before dispatch, the
baseline captured after state reload under the runner lock, terminal publication
under that lock, and one atomic campaign update for append/count/clear. A missing
terminal record cannot authorize another invocation. The review packet now
includes the actual `MAX_RUN_SECONDS` value used by all three call paths.

The current checker still rejects full P16 completion: five contracts, the
initial profile and fourteen decisions remain unfinished. Preserved partial
uncertainty work is eligible for its saved independent review. No candidate
packet, test count or proposed contract is being promoted to phase acceptance.
The remaining uncertainty is the independent review of the changed controller;
startup must pass the current suites and modular reviews before authoring. The
original monotonic deadline and no-progress count remain unchanged.
