# W05 financing history and opening invariants

26 October 2026. MC13/15/16/17/18/20/24/25/28/33/34/35.
Continuation after the selected term-execution integration. S1–S5 partial;
S6 held; E3 forecasting deferred. This is bounded specification/conformance
work, not production implementation or actual-issuer accounting admission.

## Question and evidence contract

Can the existing typed state/condition machinery express reusable opening and
continuation checks for E01's financing claim, issued shares and missed-payment
history, so that late settlement preserves past failure and invalid imported
states cannot enter the selected synthetic program?

Comparator: the frozen E01 independent complete-state oracle and its four
programs in data/accounting-master/gap-program-20261026/settlement_cases.py.
Inspect its exact fields, schedules, policies and invariants before coding.
Do not infer legal default from missed payment or invent event history from an
ending balance. Inspect existing common opening/invariant profiles before
introducing a successor; prefer declared checks over new financial callbacks.

Pass criterion: exact retained valid-state agreement, rejected targeted
corruptions, preserved source/evidence hashes and complete-state continuation
comparisons on the selected fixtures. Valid imported opening facts and known
history must be distinguished from independently verified historical truth.
Counts, runtime and PDF builds are explanatory only. Missing selected premises
must remain unknown/unsupported as the existing contracts require.

Vetoes: inconsistent oracle, changed frozen input, malformed type/context,
missing required history, unsupported selected policy, partial state silently
accepted or a command returning an accepted after-state after failed validation.
An invalid harness blocks inference and triggers repair; failure of a current
declaration triggers the next smallest repair, not research-direction rejection.
No stochastic ranking, legal conclusion, default policy change or whole-language
readiness follows from finite synthetic checks.

## Skeptical audit and assumptions

Initial audit passes for inspection and scoped design. E01 supplies only local
method pre/postconditions: these cannot be silently promoted into a complete
opening invariant. The selected zero-coupon, one-accretion-interval, no-fee,
no-tax, no-penalty and no-acceleration assumptions are fixture hypotheses,
not general financing defaults. Equal ending balances are insufficient for
historical equality. First check retained intermediate states and the independent
oracle, then document the precise invariant and temporal dependencies before
executing the conformance probe.

Default audit: exact rationals and supplied dates follow the frozen typed
fixtures (baseline); account roles come from their explicit maps (reviewed
within that scope); supplied population/history completeness is a premise to
check, not source truth; any newly imposed bound is an implementation hypothesis
requiring empty/boundary/overflow controls. CPU execution is a convenience
choice and all tests are deterministic. No financial or scientific defaults
are changed. Record newly discovered scope mismatches in audit.md before runs.

## Execution and durable artifacts

1. Inspect E01, its independent oracle, relevant common opening/state profiles
   and selected E03 dependencies. Record reuse and any missing representational
   capability in data/accounting-master/financing-opening-invariants-20261026/audit.md.
2. Write the smallest selected contract/declarations and targeted controls.
   Preserve original E01 evidence. Separate snapshot consistency from temporal
   history preservation and actual-source admission.
3. Run a bounded deterministic CPU probe, using
   env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 with an explicit
   script path, bounded output and saved evidence. First run focused diagnostics;
   do not repeat a successful evidence writer. Capture exact commands, environment,
   source hashes, elapsed time, checks, result and unresolved cases.
4. Refresh master/recovery pointers and decide the next E03 composition from
   the actual result. Preserve the broad W05/W06 and full gap-program queues.

No agents, commits, installs, GPU, outreach, fees or publication. Human review
is an acceptance dependency and does not stop feasible internal preparation.
