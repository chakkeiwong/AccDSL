# ACTUS contract events need explicit adapter conventions

23 October 2026. S1/S2; MC17/23/25/29–31. This is a targeted reading of the
retained ACTUS technical specification, not a claim about the latest standard
or an executed implementation. It follows the simulator comparison and funded
year. No external code was run or adopted.

## Inspected source

Source: docs/design/research/standards/actus-techspecs.tex. Inspected ranges:
315–430 (events, transitions, payoffs, time, sequence and schedule), 474–565
(business-day rules, calendar, year fraction and role sign), 668–705 (risk
observer), 773–945 (PAM schedule, states and early payoff/transition functions),
and 955–1005 (interest, capitalisation and resets). The retained service README
was read as historical packaging evidence. Its 2023 release and token-based
core build instructions establish neither current runtime access nor tested
dependency versions. No software adoption rests on that README.

The specification separates contract payoffs from state transitions. PAM
describes initial exchange, maturity, interest and optional fee, prepayment and
reset events. This is a candidate boundary for proposed loan cash flows. Its
risk observer leaves actual future dynamics to user-defined implementations;
it does not supply an empirically justified company policy.

| Issue | Retained source meaning | Required AccDSL boundary |
|---|---|---|
| Timezone | The date/time section says timezone information is unsupported | Do not strip the UTC suffix and claim lossless conversion. Specify timezone/calendar mapping and reject ambiguity. |
| Midnight | The implementation note interprets 23:59:59 as midnight | AccDSL distinguishes that second from next-day midnight. Require explicit conversion and round-trip tests at reporting boundaries. |
| Simultaneous events | A dictionary sequence indicator orders events | Reconcile contract ordering with company dependencies; do not override funding/payment prerequisites. |
| Day count | The year-fraction section defines an interface, leaving implementation open | Inspect the selected runtime's convention before claiming equivalence to the local Actual/365 calendar-date rule. |
| Calendar shifting | Shift/calculate order and example calendars are described | Select rules explicitly. The retained prose repeatedly says non-working day in its shift definitions; resolve against dictionary/code before implementation. |
| Position sign | RPL maps to -1; positive flows enter the creating party | Declare borrower perspective and distinguish economic principal from signed liability state. |
| Currency/scaling | Payoffs contain currency and notional/interest scaling factors | Explicit unit factors suffice for the local example; general FX/scaling needs separate inputs and accounting. |
| Risk observations | The observer supplies risk values or unscheduled events | Preserve cutoffs, scenario provenance and unknowns; access to future values is not permission for policy foresight. |
| Accounting | Inspected functions produce contract cash and state | AccDSL retains recognition, carrying measurement, journals, classification, tax, consolidation and reporting. |

## Conditional algebraic correspondence

For a borrower choose RPL, principal N=85.4, unit conversion/scaling, no premium,
fee, prior accrued interest, reset or prepayment, and year fraction y=2/365.
PAM's initial-exchange payoff is -R*N=+85.4. Signed notional then equals -85.4.
Its interest payoff under these conditions is y*r*(-85.4); at r=0.05 this is
-427/18250, the local interest cash outflow. If interest settles before maturity
and accrued interest is then zero, maturity payoff reduces to -85.4.

This substitution supports a conditional payoff bridge. It does not establish
runtime schedule correspondence, intraday-time equivalence, dictionary ordering
or accounting journals. Fees, accrued-state initialization, maturity-interest
order and calendar shifting can change the result. The specification's wording
and formula are the source; this simple substitution is the local deduction.

## Decision

Retain ACTUS as a candidate contract-event component. Before adoption, pin an
accessible implementation and inspect PAM initialization/payoff/transition,
day count, calendar and event-order code. Compare the exact borrower example
and midnight/same-date edge cases, preserving dictionary/spec/code edition
correspondence and dependency terms. No runtime dependency is adopted here.

The inspected interface leaves material timing and risk assumptions open at
the adapter boundary. This resolves that immediate design question, not the
full simulator comparison or implementation selection. An unresolved component
does not stop independent whole-company language work.

## Follow-on inspection of pinned service code

The public service tree was retrieved on 23 October with tree object
7293157a7f272925dbce68b5a037d2e23c585c9e (a tree identity, not a commit ID).
Four exact blobs were retained and their Git blob SHA1 identities independently
recomputed. Local files and the raw API responses are under
docs/design/research/software/actus-interface-20261023/. Only source text was
inspected; no library was installed, built, executed or accepted.

The build file requests Java 17 and org.actus:actus-core:1.1.0, using both
mavenCentral and mavenLocal. That request does not pin the resolved core binary
or prove its availability. It differs from the historical README's stated
Java/core release. The dependency lock, underlying implementation, dictionary
edition and normative correspondence remain unverified.

EventController's computeEvents first selects termination, maturity,
amortization or settlement date, then falls back to LocalDateTime.now plus
five years if all are absent. It invokes ContractType.schedule and apply and
converts the resulting events to a short output model. This wall-clock fallback
cannot define a reproducible AccDSL horizon. An adapter must require the
explicit requested horizon or return an unresolved/unsupported result.

The controller parses observations with LocalDateTime and divides values by
their supplied base. Its MarketModel calls TimeSeries.getValueFor(time,1).
The inspected implementation chooses the latest observation at or before the
requested time. That is an explicit carry-forward rule, not interpolation or
an inferred risk forecast. The shown path contains no missing-series/base-zero
admission check and does not turn empty/before-first lookup into a typed
unknown. These observations are about the inspected path; no complete-service
security or robustness conclusion follows. AccDSL must validate the observer
input and preserve unsupported/missing observations before calling it.

Event.java exports event type/time, currency, payoff, notional, rate and accrued
interest. Numeric fields are doubles and the output does not contain AccDSL's
source/assumption lineage or accounting journal. The adapter must preserve the
request/source context and an explicit numeric comparison policy; it cannot
claim the exact rational reference result merely because decimal printouts
look equal. No whole-company statement or booking decision is supplied by
these fields.

Batch handling retains a separate Success/Failure event stream per contract;
parse/evaluation exceptions become failure messages. This is useful failure
separation, but is not the same as AccDSL's known funding failure versus
unresolved information. The exact core PAM/day-count/calendar and dictionary
code still needs inspection before any executable equivalence claim.

Network note: the first sandboxed API request failed DNS resolution. The same
bounded request succeeded with the authorised elevated network path. This was
sandbox evidence, not evidence that GitHub or the library was unavailable.
