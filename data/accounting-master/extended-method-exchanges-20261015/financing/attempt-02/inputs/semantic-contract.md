# FinancingComponents/1 documentary contract

15 October 2026. P3a under the financing successor subplan. MC02/04–07/11/
13–28/30/33–35; G2–G4/G7/G12–G18. This defines finite interoperable examples,
not a deployed accounting service. The 32 method variants are closed. Product
execution, current-law admission, valuation calibration and tax computation are
outside this evidence. `tax_status=uncomputed` never means tax is zero.

## Identity, bytes and references

Records have exactly kind, schema, key, revision, body and dependencies. The
revision is zero in this packet. JSON is UTF-8, sorted keys, compact separators,
no floats, duplicate keys or nonfinite numbers. Unicode is not normalized.
Rationals have reduced signed integer numerator and strictly positive
denominator; zero is 0/1. JSON-schema format dates must be real calendar dates.
Record digest is SHA256 of `accdsl.portable.v1/` followed by the schema ID,
a zero byte and canonical record bytes. Dependency lists contain every distinct
record reference occurring in the body, sorted by its canonical reference bytes.
Every referenced record and blob must exist with the declared bytes and length.
References to another profile are not a migration. All five corporate component
profiles and the original corporate/group/insurance profiles require explicit
adapters; no such adapter is inferred here.

## Bound economic events and admission

Each event basis binds exact opening state, component, method, authority, source,
view and context. Entity, legal book, branch and functional currency must agree.
Net foreign-currency cases use EUR functional and USD exposure currency; other
examples use USD. Business-event identity is the entity/book/branch/event tuple.
Method and component tag must agree with the closed event variant. The method's
primary and supporting source references must equal the authority's references
and occur in the view. Method contract and profile must be the locked versions.

Only archival synthetic admission is supported. A historical-investor view
cannot claim availability from these records. EU source support has no invented
legal validity interval. AASB9 annual-start scope is [2023-01-01,2026-07-01);
the separately retained AASB107 compilation starts 2024-01-01 and states no
upper boundary. Cash support is EU IAS7 for EU contexts, AASB107 for AU contexts.
Each event declares a calendar annual reporting period containing its date.
Its reporting-period start must satisfy every bound source's own scope. An
authority's logical instant interval is separate from those calendar scopes.

An event instant strictly follows its opening instant. Its date cannot precede
the opening as-of date. Closing sequence increases exactly once; closing
instant/date equal the event instant/date, and context/view remain bound.
Admission findings explicitly bind the source, context and event; eligibility
is conditional on the supplied facts. Unknown values produce partial results
and named obligations. Unsupported methods or valuation domains do not become
zero. Ineligible or wrongly bound inputs are rejected without changes.

## Financial transitions

Debit journal amounts are positive and credits negative. Proposals have one
nonzero line per account in lexical order. The journal must equal the independently
derived financial change, including a correct empty journal for state-only
events. A balanced but differently measured journal is rejected. State balances,
component values, cash, OCI and direct-equity movement counters must all agree.
Cash receipts and payments accumulate separately as the positive and negative
parts of each category's movement. Each event here has at most one net cash
movement per category; these examples do not infer gross subflows from a
compound event. Reserves are credit-positive in component state; signed ledger
balances are debit-positive. The derivative can be an asset or liability.

Amendment-date additional consideration is measured once when binding terms,
discharge and equity classification are admitted. Announcement is state-only.
Delivery transfers pending equity to capital without measuring inducement again.
Cash bonus discharge is financing cash, once, after binding. Awards preserve
original and incremental service clocks; added instruments do not shorten the
original vesting period. Cash-to-equity modification removes the remeasured
liability and credits equity for performed services at replacement-date value;
the difference is expense or income. Future service is not accrued early.

Cash-flow hedge effectiveness is cumulative, limited by the offsetting hedged
item change. Ineffectiveness goes to profit. Settlement is a separate cash and
derivative event. Inventory basis transfer removes the reserve directly from
equity and the asset's carrying value; it is not an OCI reclassification.
Interest cash paid remains separate from derivative settlement and reserve
release. Discontinued forecast transactions retain the reserve while expected;
release requires that they are no longer expected. Measurement after an asset
basis transfer or interest payment needs another method and is refused here.

Option purchase precedes measurement, amortization, settlement or
discontinuation. Intrinsic and excluded time-value reserves remain separate.
Transaction-related costs adjust asset basis; time-period costs are allocated
over the explicit protection calendar under the admitted even-allocation rule.
The actual/aligned component rules retain intervening OCI, including a zero-cost
collar. Negative time-value components and more general mixed-sign alignment
paths need additional methods and are unsupported in this finite profile.

Rebalancing first measures cumulative ineffectiveness on the old ratio. A
documented unchanged objective permits the prospective ratio change. Added
layers retain their own designation dates and reference prices. One subsequent
measurement has an explicit since-rebalance item change; further observations
need a cumulative anchor absent from this version and are refused. The layer
quantity/price illustration assumes admitted zero discounting and is a state
diagnostic, not an additional derivative posting.

Net foreign-currency hedges preserve gross sales/services at the admitted spot
rate. A separate hedge line and reserve bridge earning periods; gross revenue
or expense is never replaced by the hedged net amount. Nil-net designation
requires all four IFRS9.6.6.6 findings, not just a zero exposure. The finite
illustrations exclude discount, forward-point and credit effects, require sales
before service, and supply external counterparties and eligibility.

## Commit, replay and visibility

Authorize, propose and report are read-only. Only commit can publish a change.
A committed business-event identity is looked up before freshness or financial
rederivation. Exact canonical request retry returns the existing receipt and
publishes nothing, even after a newer head/view. Another request with that
identity conflicts. An uncommitted request must bind the current dependency
view and exact expected owner/state/generation. Authorization must be eligible,
source-bound, basis-bound and posting-permitted.

One atomic publication changes owner head, identity/receipt index, journal,
economic delta, receipt and transitive published record closure together.
Other owners remain byte-for-byte unchanged. Rejected, partial, unsupported
and exhausted-budget requests publish nothing. Lost acknowledgement has two
explicit documentary worlds: no commit, which permits the exact request once;
or committed, which permits only receipt replay. A transport observation cannot
decide which world occurred. No database durability is established by these
authored worlds. Numbered validation attempts retain failed checks.

## Annual and lifetime reports

Report requests specify inclusive start, exclusive end and an exact contiguous
receipt chain from opening to closing state. Every receipt must be in that
owner's committed world with the exact indexed request, journal, delta and
dependency closure. All economic event dates lie in the period, no committed
in-period continuation is omitted, and opening date is no later than the period
start. Annual periods are calendar years. A lifetime period starts with the
opening year and ends after the final event year. All reports retain currency,
book and view. Frozen old-view reports may be read with require_current=false;
require_current=true refuses a superseded view.

Profit, OCI, direct-equity and cash movements are differences of closing and
opening cumulative balances/counters. Opening historical expense is excluded
from current-period profit. Assets include positive derivatives; liabilities
include negative derivatives. Equity includes cumulative profit and reserves.
Assets minus liabilities equals equity. Change in equity equals period profit
plus OCI plus issue/award/basis-transfer movements. Cash change equals net
category cash and separately gross receipts minus payments. Actual interest
paid is independently recovered from the receipt events. Gross income-statement
lines, OCI components and direct equity movements remain available separately.
These are pretax component reports, never complete-company after-tax statements.
