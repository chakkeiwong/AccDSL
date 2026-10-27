# Conditional history-to-group scope: inspected-interface audit

27 October2026. This unit implements the plan at
docs/plans/accounting-control-group-boundary-20261027.md.

Inspected baseline: history.py returns exact rational instants, complete or
partial interval atoms and conditional gain/loss events. It never admits sources,
control or postings. GroupPeriodReport/1 compares opening/closing context,
control edges and book population. CompatibleBookComposition/1 requires one
control edge and ownership_fraction=1; it checks control at each snapshot but
does not consume an evidenced interval history. Its ownership/control premise
is supplied text. Existing GroupPeriodReport tests already refuse changed
control edges and some incompatible policies. The fixture is a2025 two-book,
USD, full-ownership conditional report with200 opening and220 closing cash.

The audit passes for a narrow scope adapter, with two adjustments. First, a
reporting basis is not identical to the existing free-text measurement-basis
field: an explicit supplied basis bridge must name both. Second, calendar dates
have no timezone: require an explicit fixed-offset calendar embedding and
compare exact midnight boundaries. Do not round a partial-day history to dates.
These are declared engineering premises, not inferred financial facts.

Input ConditionalControlGroupScope/1 contains the original history request and
group report request, expected digests for both, a fixed offset, and a basis
bridge with history_basis, group_measurement_basis and premise. Expected hashes
bind content but do not authenticate the person supplying them. The adapter
evaluates the history anew; it does not trust a transported result. It checks
two distinct group entities, a single selected edge, identical opening/closing
periods and edges, aligned history subject/basis, and exact embedded query
boundaries. The original objects are never mutated.

Output retains the complete history result, exact request/implementation hashes,
calendar/basis premises, route, outstanding financial-method dependencies and
source/accounting/posting/report authorization flags all false. Routes:

| History | Ownership premise | Route | Reason |
| --- | --- | --- | --- |
| Any unresolved atom | Any | unresolved_history | No stable interval is established even conditionally |
| All no-control | Any | outside_controlled_group | This parent-child consolidation route is unsupported |
| At least one gain or loss | Any | changing_perimeter_methods_required | Acquisition/loss and dated reporting methods are missing |
| All control | Less than100% | nci_methods_required | Current group composition supports full ownership only |
| All control |100% | stable_scope_candidate | Only the current report's control/ownership scope matches; remaining report checks still apply |

Mixed control/no-control without an explicit transition is invalid evaluator
output, not permission to report. Adjacent same-status atoms may differ in source
identity without changing the route. A loss followed by regain must remain a
changing-perimeter case despite matching endpoints. Unknown actor availability,
conflicts and missing coverage remain in the complete result.

Primary criterion: independent expected routes/dependency sets and the complete
underlying history result agree for all declared cases; supplied request hashes,
calendar/basis/subject binding and no-mutation checks pass. Stable scope alone
does not establish accounting validity. Separately verify the original report's
complete unchanged fixture and its explicit changed-edge/partial-ownership
refusals. Those baseline diagnostics are validity checks, not promotion to an
acquisition-report implementation.

Promotion vetoes: lost unresolved history, wrong route, wrong source/time/subject
binding, any authorization flag true, or a report emitted by this scope adapter.
Continuation veto: corrupted pinned baseline or missing evidence makes affected
comparisons invalid. Expected route refusals trigger the next financial-method
specification; they are not rejection of the simulator direction. Diagnostic
counts and runtime are explanatory. Statistical ranking is N/A.

Default audit: fixed offset and whole-interval premises are convenience scope;
equivalent offsets and sub-day mismatches test their boundary. Closed schema
and finite bounds follow existing interfaces and refuse unsupported inputs.
The source registry can be incomplete or false; no coverage result establishes
external completeness. The no-source-admission convention is preserved.

Pre-mortem: the adapter could pass while testing only summaries derived from its
own logic. Prevent that with a hand-authored route matrix, full-history equality,
baseline report equality and specific malformed-input reasons. It could also
mislead by accepting a100% share fraction as control; histories of no-control
and control gaps with100% ownership explicitly veto that interpretation.

Post-success next work: the separately planned dated authority and conditional
acquisition/NCI method specification. No goodwill/fair values are manufactured.
