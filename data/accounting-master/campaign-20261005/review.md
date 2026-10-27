# Supervisor review of the 48-hour campaign extension

Proceed with the authorized proposal campaign. This is supervisor finding
adjudication of the changed controller, not a new independent-model controller
review. Original independent phase plan/result reviews remain unchanged.

The campaign repeats the existing `Master.run`, without modifying catalog
criteria, workflow, worker sandboxes, declared budgets or five-retry ceiling.
Its absolute deadline survives resume and is passed into each invocation, so
startup delay cannot extend the overall allowance. A host-boot change vetoes
automatic resume; civil clocks do not replace an incomparable monotonic clock.
The prepared record starts the allowance at the user's current request, and
preparation time consumes it. The existing narrow entrypoint prefix matches
the exact new campaign command with 172800 seconds.

The outer campaign lock prevents competing campaign supervisors. The normal
runner lock still guards every actual invocation and its helpers. Campaign
metadata is written only between invocations, and worker inventories include
that metadata among protected supervisor files. A normal competing run cannot
share the runner lock; there is no second editable worker. The trusted local
single-workspace assumptions and process-group containment limitations remain.

Automatic calls set `resume_stop=False`, so they never archive a stop request
as if it were fresh user consent. A stop observed before startup review prevents
the review from launching; the normal process stop callback covers a stop that
arrives after launch. The campaign checks again between invocations. Integrity
veto and interruption stop immediately. Repeated invocation no-progress stops
after two attempts, in addition to existing phase deferrals. No eligible next
phase stops for supervisor investigation. Checked file progress can continue
after a run budget or retry limit; it does not accept the phase.

New phase acceptance is observed separately from file changes, permitting
read-only result review to advance the campaign. Proposal readiness comes only
from the existing run outcome and derived readiness checks. A later resume of
a completed campaign rechecks current evidence before retaining readiness.
Product implementation remains disabled on every outcome.

Final verification: 175 controller and 17 proposal tests pass. Eleven added
regressions cover progress continuation, fixed deadline and resume, insufficient
total budget, stop between invocations, stop at the actual run boundary, two
unchanged invocations, integrity veto, stale boot/invalid deadline, unavailable
eligibility, stale cached readiness and startup at an absolute campaign cutoff.
The existing real internal-helper integration and all worker timing, five-retry,
acceptance, preservation and proposal tests continue to pass.

The final audit added explicit absolute-deadline propagation and stale-readiness
validation after the first passing test run. The full controller suite was then
rerun; the earlier log is retained. `git diff --check` passes. All 912 original
protected files, every accepted phase's evidence, and all prior controller
review evidence match. `validation.json` records these checks and the rule match.

No material unresolved code finding remains in this extension. The substantive
uncertainty is campaign sufficiency: 48 hours may still leave proposal decisions
or source gaps open. File progress may include reporting, and one successful
worker cannot establish stable throughput. The plan preserves these limits;
supervisor inspection and full substantive phase review must distinguish useful
content from reporting churn. A stopped campaign does not silently restart or
grant itself more time. Any local repair before explicit resume must preserve
the fixed deadline and existing evidence.
