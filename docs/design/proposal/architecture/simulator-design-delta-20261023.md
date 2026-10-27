# Simulator design delta: state, decisions and settlement timing

23 October 2026. Proposed extension to the initial corporate profile, addressing
MC13–18/23–26/28. Source comparison:
`docs/design/research/financial-statement-simulator-survey-20261023.md`.
The current frozen portable package is preserved. This note specifies the next
design increment; it does not claim a new registered schema or product endpoint.

## What is already designed

`interfaces-contract-v1.md` I2–I4 already distinguishes scenario projection,
accounting assessment, journal proposals, commits and reporting. It also names
receivable/payable terms, inventory lots, asset memory and sector state.
`core-contract.md` defines contract scheduling and behaviour/measurement
interfaces. Chapter 7 specifies event dependencies, information restrictions,
funding limits, simultaneity and partial failures. Reuse these distinctions.

The narrower `CorporateJointHistory/1` closed schema actually contains a
`CompanyState` with account balances, inventory units and source/view references.
`Facts` separately supplies the asset and debt examples. `Scenario` contains
aggregate annual drivers. `EconomicEvent` has a date and sequence, but its
parameter payload is limited to amount, units and consideration. `Projection`
retains ordered proposed journals and annual statement lines. The existing
Northstar chain is therefore a substantive linked-statement design. It is not
yet a general per-claim settlement scheduler or behavioural-policy schema.

## Architecture recommendation and alternatives

Keep one typed model and deterministic accounting/reporting meaning, accessible
through typed constructors and the textual DSL. Use a dated event scheduler as
the initial execution backbone. A financial-planning equation system, a
system-dynamics model or an agent-based policy may generate decisions/events
through an explicit adapter. None may write committed account balances directly.

This choice follows from three requirements: recognition and payment can occur
on different dates; contracts with identical carrying totals can have different
remaining obligations; and insufficient funds can be a model outcome. Pierson's
stock/flow and reporting distinctions, Caiani's event order and heterogeneous
claims, and Gentry's explicit financing decisions support those separations.
They do not select a general behavioural law.

| Alternative | Where it remains useful | Why it is not selected as the whole initial simulator |
|---|---|---|
| Aggregate financial-planning equations | High-level scenario authoring, simultaneous funding relations and investment targets | Annual amounts alone do not determine payment feasibility; include dated obligations and a declared equation solver where needed. |
| Continuous stock/flow engine | Operating policies with meaningful flow rates and delays | Reporting boundaries, invoice obligations, contract events and default still need explicit treatment; arbitrary integration steps must not silently choose accounting dates. |
| Full agent-based economy/JMAB | Endogenous customer/credit responses in a separately justified research model | The inspected benchmark is an artificial economy with its own behavioural laws and calibration; it is not an issuer opening-state or financial-statement accounting package. |
| ACTUS/valuation library | A candidate contract schedule/payoff or valuation adapter | Keep recognition, policy decisions and reporting in AccDSL; runtime/version/license and exact correspondence work remains before library selection. |
| Typed library without textual syntax | Required authoring comparator and possible usable first interface | It can express the same semantics; the relative benefit of text remains a separate question. Neither route may hide opaque host-language decisions in portable IR. |

This is a provisional recommendation for the initial profile. The unresolved
Francis/Rowell comparison and Gentry derivation prevent a claim of completed
comparative survey or superiority. They do not prevent specifying the dated
obligations already required by the mission.

## Proposed state and operation changes

Extend records under a new profile version; do not mutate the frozen v1 record
bodies or reuse their hashes for changed meanings. Names below are proposed
design names, not already registered APIs.

| Record or operation | Required contents and behaviour | Existing owner to extend |
|---|---|---|
| Opening economic state | A reference to the accounting opening plus receivable/payable claims, contractual principal/schedules, inventory lots, in-service asset cohorts and committed facilities. Every amount has entity/book, currency, date, provenance and known/unknown status. | `CompanyState`, `Facts`, I4 state requirements |
| Settlement claim | Stable claim identity; source event/contract; counterparty or explicit unknown; gross amount, paid amount and outstanding amount; currency; due date/calendar; collection/payment policy and its information dependencies. Distinguish contractual due date, expected collection date and realised payment. | `EconomicEvent` and corporate state |
| Decision result | Policy/version and parameter references; decision instant and permitted information; proposed actions with quantities, constraints and reasons; unresolved inputs. It proposes no financing without a specified facility/capital action. | `decide` and `scenario.project@1` |
| Event generation | Opening economic state, decision result, scenario driver view, horizon/calendar and method lock produce dated candidate events plus remaining obligations. Decisions observe only permitted information; the event generator can consume later innovations only as they are realised. | `scenario.project@1` |
| Scheduled event | Economic occurrence, recognition/accrual interval where relevant, settlement instant, claim/contract references, dependencies and event type. Ordering must resolve noncommuting events; unresolved order is not decided by lexical ID. | `EconomicEvent`, Chapter 7 scheduler |
| Funding decision | Amount due, available cash, eligible facilities/collateral/covenants, draw settlement time and permitted capital actions. Return explicit funding actions, unpaid obligations or unknown feasibility. | Chapter 7 funding waterfall |
| Accounting transition | Retain the economic event, applicable measurement/treatment and independent quantity/money changes with the journal. A failed validation does not partly mutate state. | Existing accounting operations and receipts |
| Joint report | Same branch/history/scenario and period throughout; opening, classified movements, closing, income, cash flow and equity. Show line-level unresolved dependencies and preserve non-cash movements. | `report.build@1`, `Projection`, `ReportMap` |

Claim-level settlement obeys `outstanding = recognised claim + adjustments -
settlements`; each adjustment has its own event and basis. A payment cannot
exceed the identified payable unless an explicit advance/refund event explains
the excess. Receipt of cash is not a second revenue event. Acquiring an asset
does not start depreciation until its in-service date under the chosen method.
All of these rules require operation-level inputs; an annual ratio is not a
substitute for an unavailable contract or fact.

At a settlement event, check available eligible cash and any permitted facility
whose draw can settle before the payment. If those resources are known and
insufficient, preserve the unpaid obligation and return economic funding
failure. Do not post a full payment or invent debt. If resources or due dates
are unknown, report unresolved feasibility rather than default. Partial
settlement, refinancing and bankruptcy require their own declared methods;
the initial diagnostic assumes full payment or no payment.

Cash-flow concepts must declare their formulas and classification. In the
Northstar reporting package principal repayment is financing. Caiani's internal
OCF subtracts principal and must have a separate identifier. Under a restricted
bridge where all other components agree, `cash_after_principal =
statement_operating_cash - principal_paid`. Outside that shared scope, retain
the component reconciliation instead of asserting the identity.

## Diagnostic before adopting the extension

Question: can annual statement reconciliation alone establish that the supplied
payments can occur? Comparator: the unchanged Northstar portable stress7/stress9
journals and their checked opening. Candidate check: dated prefix liquidity,
with no committed facility and atomic full-payment semantics.

Primary pass criterion: replay of the original order reproduces all retained
closing balances and cash-flow categories, while a deliberately reordered
supplier payment before collections is rejected for insufficient cash despite
the same unconstrained year-end algebra. At floating shares 0, 1/2 and 1,
original statement balances and equity must agree with retained expectations.

Vetoes: changed baseline bytes, unbalanced journal, mismatched closing account,
wrong cash-flow classification, partial application of a refused payment, or
using unknown collection timing as a known date. Failure repairs the diagnostic
before any design conclusion. Event/check counts are explanatory only.

The baseline opening cash is 74.6; the supplier payment is 160. Putting that
payment before the 280 collections creates a cash deficit of 85.4. This is an
authored timing counterexample, not a claim about Northstar's original chronology
or any real company. No unobserved financing capacity, invoice or probability
is inferred. Exact rational arithmetic is used because the retained fixture is
rational; no continuous-law inference or benchmark ranking follows.

Run only the new read-only-input checker under
`data/accounting-master/simulator-timing-20261023/verify.py`, with Python's
standard library and `CUDA_VISIBLE_DEVICES=-1`. It writes results only to its
own directory; never invoke the historical builder or verifier main functions,
which rewrite frozen evidence. Preserve source hashes, the actual command and
measured diagnostic duration beside the result.

Next integration work: specify the closed successor schemas and matched
authoring examples for these records, then extend the complete Northstar case
only where timing, claims or policy inputs are missing. Preserve broader
corporate, group, bank and insurance design obligations separately.

Executed successor: settlement-decision-draft-20261023.md now specifies one
identified payable, facility headroom/eligibility, an explicitly authorised
draw and separate conditional settlement events. Its 28 documentary cases
pass 74 checks. This closes the narrow payment-record ambiguity, not general
claim generation or the borrowing's later interest and repayment schedule.
The current document increment remains Version 3.49; these newer records are
a separate provisional design pending integration.

The next executed example is now complete at
data/accounting-master/funded-year-20261023/result.md. It explicitly allocates
purchase/sales claims and the additional loan's two-day interest/repayment,
then reconciles the full year in 18 conditional paths. General claim generation
and portable/textual authoring remain open; the example does not close them.

## Bounded schedule annotation for the existing projection

The immediate specification uses a separate `SettlementScheduleDraft/1` record
that references the preserved projection. It annotates its complete ordered
set of proposed journal events with settlement instants and explicit funding
knowledge. This is a proposed documentary subprofile, not registration of the
full general economic-state extension above. Neither full claim generation nor
whole-company textual compilation is implied by accepting this annotation.

Its closed body contains `profile`, `projection_ref`, `horizon`,
`funding_knowledge` and `events`. `projection_ref` is the existing typed
Projection reference. Horizon is a half-open pair of UTC instants, equal to
midnight UTC at the retained forecast's start and exclusive end dates. Each event
has `event_kind` matching exactly one projection event, `at`, and `after`.
`at` is either a known UTC instant or an explicit unknown with reason and
named documentary obligations in `obligations`; these are not yet admitted
production evidence references. `after` contains predecessor event kinds. Every
projection event occurs once, with no invented, omitted or repeated event.
The implicit financial prerequisites remain: purchase before delivery,
delivery before collection, purchase before supplier payment, all income/tax
events before closing. An annotation may add dependencies but cannot remove
those prerequisites. This bounded annotation retains the original event
amounts and classifications; it does not manufacture invoice identities.

The initial funding variants are `known_none` with explicit scenario-assumption
text, and `unknown` with a reason and named obligations. The documentary
package names these assumptions locally; production integration must use the
existing admitted assumption/evidence references. A committed
facility requires the fuller facility contract specified above and is outside
this bounded check. `known_none` means no eligible facility for these payments
in the scenario; it is not a statement about actual issuer access to credit.

Validate shape and reference closure first, then complete event coverage,
acyclic dependencies, the half-open horizon and dependency/date compatibility.
Unknown instants or an unordered same-instant settlement pair produce
`unresolved_timing`; they are not ordered by array position or event name.
Only then evaluate the known schedule. At each payment a known cash shortfall
with `known_none` returns `funding_failure` and the last unmodified state;
the same shortfall with unknown facility access returns `unresolved_funding`.
Unknown access is irrelevant when cash alone suffices for every event. The
result must say no facility was required, not that all financing was known.

Two ordered schedules provide the principal cases. In the funded-by-cash
schedule, collections settle before suppliers. In the second, suppliers settle
before collections; all the annual numbers remain identical but the payment
fails. A third leaves collection timing unknown and preserves unresolved
feasibility. A fourth leaves funding access unknown on the early-payment
schedule and must not declare default. Negative controls cover an omitted
event, a duplicate, a cycle, a predecessor scheduled later, an out-of-horizon
event and unsupported extra fields. A same-instant cash pair with no dependency
must remain unresolved; a declared dependency can resolve it.

The body schema, schedules and independent checks live with the diagnostic at
`data/accounting-master/simulator-timing-20261023/`. Authoring examples use
typed JSON bodies; textual DSL lowering remains a separate pending obligation.
