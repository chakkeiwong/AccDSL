# Current-assessment clock in the mixed decision timeline

25 October2026. MC13,MC15,MC16,MC24,MC28,MC32,MC35.
Baseline: unchanged MixedEventTimeline/1, StateDecisionSchedule/1 and native
AnnualProgram/1 current assessment. No forecasting or accounting-rule change.

Question: can a caller order an explicit cumulative tax assessment with native
payments/sales and state-dependent decisions while retaining the native clocks,
actual-turn state, failure status and valid prefix?

Skeptical audit: the naive fix of accepting event.date would be wrong because
assessment uses interval.start/end_exclusive/activity_through. Date must equal
activity_through, which must be end_exclusive minus one day. Static shape checks
must not run the assessment against the initial state or overwrite its inputs.
Economic availability is assessed at the actual turn. No deferred/carry clock
is smuggled into this scope. Unknown and false native facts keep their statuses.

Primary evidence: exact comparison of entire materialized operations, native
transition states, journals and report fields against manual interleaving.
Independent arithmetic on sale profit, current-tax expense/payable and cash
explains the order effect. Reversing sale/assessment order must either preserve
the genuinely allowed result or stop at the native assessed-interval veto; it
must not silently reorder. Invalid date aliases, duplicate IDs/priorities,
stale state and malformed static entries refuse. No mutation of rejected input.

Assumptions: existing authored rate/loss/policy findings are synthetic inputs,
not learned behavior or actual company authority. Reuse their exact provenance.
Bounds32 native/64 total actions are existing reference limits, not production
capacity claims. No stochastic ranking. Source/accounting admission remains
false and fiscal event completeness remains false even after a timeline ends.

1. Add a versioned optional timeline successor reusing prior direct-operation
   validation and scheduler; derive the new clock from the supplied interval.
2. Compare sale then assessment and assessment then sale, plus current
   replacement if supported by the same state. Test unknown facts, malformed
   clocks, mixed priorities and prefix preservation. Record exact exchanges.
3. Integrate substantive results with preserved manuscript and inspect rendered
   pages. Audit deferred-measurement state binding and period-carry clocks next;
   retain stale measurement refusal and require a new plan before broadening.

Continuation veto: broken comparator, input mutation, lost source/state or
clock ambiguity. Native candidate refusal triggers the designed order test,
not global stopping. Artifacts:data/accounting-master/assessment-timeline-20261025/.
No commits, agents, installations, GPU, paid review or outreach.
