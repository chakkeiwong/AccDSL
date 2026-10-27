# Monetary derivation and state effects: inspected boundary

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31. This is an
engineering audit of the retained synthetic return example, not an accounting
authority review or a claim that the simulator covers a whole company.

## Finding and skeptical audit

The native implementation already derives journals, stages memory, checks the
result, and recomputes proposals before application. The portable
MethodDefinition already names preconditions, algorithm, account roles and
report mappings. The missing feature is a reusable, typed executable description
of those calculations and effects. A second untyped dispatcher would repeat the
native implementation without closing that language gap.

Core 0 supplies scalar expressions and symbolic alternatives, but rejects products
of dimensional quantities and has different unknown semantics. Its evaluator's
observation lower-bound and finite call behavior must not be imported as supplied
fact semantics. EventBook verifies balanced caller-provided postings; that does
not derive recognition or measurement. The company engine contains explicit
Python method branches and stages application correctly; its equal-date scheduler
sorts by event identity, unlike the retained supplied order. It is a comparator
for the staging pattern, not a substitute for the selected return semantics.

The next increment therefore derives exact rational amounts, account deltas and
gross cash flows from a closed expression program. It reuses the established
dimensional type algebra and canonical fact validator. A later adapter composes
that program with event/state structure, preconditions, identity and memory
effects, then recomputes the complete proposal. No journal or after-state supplied
by a caller will be accepted as evidence that the algorithm ran.

## Selected operations

Settlement reads the component identity, settlement flag, sold units, unit refund,
unit cost, outstanding refund and recovery; the event supplies actual units,
unit handling, unit deterioration, NRV, cash facts, new lot identity and date.
Rights-closure and handling-classification findings are explicit prerequisites.
For n units, per-unit refund p, cost c, deterioration d and handling h, calculate
refund n*p, handling n*h, and recovered carrying value min(n*(c-d), NRV).
Here each product uses compatible entity/book/measurement contexts and declared
quantity and currency dimensions. The previous refund F and recovery R are state
amounts; they are not recomputed from a current estimate.

The debit-positive journal is refund_liability F, recovery_asset -R, inventory V,
revenue refund-F, cogs R-V, selling_expense handling, and cash -refund-handling.
Keep two separate operating cash flows, refund and handling, including zero
flows as the native implementation does. Clear component refund/recovery; mark
settled; create the new live lot with units n, carrying and tax base V, acquisition
date, and component identity; append tax adjustment R-F. These tax-basis and
adjustment rules are selected native assumptions, not a general tax method.

Whole-lot sale reads the live lot's carrying amount and supplied proceeds. It
requires completed performance, fraction exactly one and nonnegative proceeds.
Post cash proceeds, revenue -proceeds, inventory -carrying, cogs carrying; retain
one external_sale operating cash flow. Set units, carrying and tax base to zero
and mark the existing lot disposed. Do not delete its identity or permit resale.

## Common transition obligations

Before either operation: validate the closed raw state and event structures,
method identity, event uniqueness, canonical date, period membership and date at
or after both state date and tax close. Keep supplied equal-date event order.
Validate the preceding book; match identities; preserve unknown prerequisite
reasons rather than replacing them with zero or false. Unknown tax findings may
remain unused for a non-tax event. Source pointers are references, not proof of
source authority or accounting admission.

After deriving effects: require a balanced journal over the exact account
registry, classified gross flows whose sum equals the cash delta, and a valid
resulting book with correct lot/component allocation. Negative resulting cash is
funding_failure. Stage balances, component, lot, adjustment, seen IDs, date and
flows together. On any failure preserve the complete preceding state, including
identity memory. Proposal replay binds the original event and before-state and
recomputes journal, flows and after-state; digests alone are insufficient.

Tax close, surrounding-company adapters, reporting and annual carry remain
separate methods. Report/carry validates source/context and bridges and preserves
lifetime identities and prior-year tax adjustments. This increment neither
reimplements nor implicitly admits those methods.

## Evidence roles and defaults

Exact agreement with independently recomputed native journals/flows for selected
settlement and sale cases is the engineering criterion. Wrong types, unresolved
amounts presented as known, altered source identity, or mutated inputs veto that
criterion. Counters and successful syntax checks are explanatory only. An
invalid comparator or missing required source prevents interpretation and triggers
repair. A candidate calculation failure triggers implementation repair; it does
not reject the simulator research direction.

Debit-positive signs, canonical rational encoding, explicit dimensional context
and conservative unknown propagation come from the retained native and v1/v2
requirement layers. Their earliest checks are exact signed fixtures, mismatched
currency/date/scale tests and unknown-times-zero tests. Finite expression and
coefficient bounds are implementation safety hypotheses, not financial defaults;
boundary tests must reject explicitly. No floating rounding or implicit scale
conversion is introduced. Dates/context rebinding is a future explicit adapter
obligation: matching declared contexts alone does not prove information timing.

## Decision

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Implement exact typed monetary derivation first | Source contract enumerated | No unresolved execution-design veto | Complete event admission and memory composition still open | Closed calculations, postings and gross-flow interpreter | Full method eligibility, production execution, accounting compliance or forecasting accuracy |

The audit passes for that bounded repair: the comparator is the retained
recomputed method, no balanced-journal proxy replaces exact semantic comparison,
and later state composition remains explicit. The strongest alternative
explanation of a future match is duplicated native formulas with wrong context
binding; independent arithmetic cases, adverse types and later exact source
binding address different parts of that risk.
