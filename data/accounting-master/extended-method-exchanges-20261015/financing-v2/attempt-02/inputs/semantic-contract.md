# FinancingComponents/2 documentary contract

16 October 2026. P3a2 under the financing residual subplan. MC02/04–07/11/
13–28/30/33–35; G2–G4/G7/G12–G18. This defines finite interoperable examples,
not a deployed accounting service. The 66 method variants are closed: 32 retained
variants and 34 residual variants across ten new component tags. Product
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
profiles, the original corporate/group/insurance profiles and FinancingComponents/1 require explicit
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

## Residual financial methods

Debt issue keeps legal principal and interest distinct from amortised carrying
value. An exact effective rate satisfies the whole-term cash identity. A fee
can be admitted once at issue; its narrow bracket has opposite monotone-PV
signs and is an enclosure only. Exact accrual from that bracket is refused.
Whole-year and half-year factors must satisfy the compounding identity and
explicit contractual anniversaries; invalid calendar shifts need another
method. At maturity a short payment preserves the unpaid legal claim and
default state. No waiver is inferred.

The modification method has one contractual year remaining. Discount new cash
at the original rate; include lender fees and exclude third-party fees from
the inclusive ten-percent test. Qualitative findings remain required.
Substantial modification removes old debt and records supplied replacement
fair value; fees are expense. Otherwise recognise the present-value change in
profit and deduct fees from carrying value before recomputing the exact rate.
The retained debt cash basis controls principal/interest cash allocation.

Ordinary-share issues, treasury repurchases and cost-based reissues change
equity without creating profit. Issued, treasury and outstanding share counts
remain separate. Compound issue splits supplied debt value and original equity.
Accrual never remeasures that equity. Original fixed-share conversion is noncash;
redemption retains original equity and splits cash between original debt basis
and accumulated interest. The finite early repurchase values the remaining
coupon/principal schedule at the supplied comparable debt rate and allocates
residual consideration to equity without capping it at original equity. All
coupons remain future; there is no unpaid accrued coupon. The extinguishment
loss is not interest paid. Exact PV and separately labelled source-rounded PV
are different admitted variants, never silently equal quantities.

Equity awards revise service/non-market estimates cumulatively; a market hurdle
enters grant fair value and cannot by itself reverse cost. Cancellation
accelerates unrecognised service cost. A cancellation payment deducts equity
up to settlement fair value and expenses the excess. Cash awards remeasure
cumulative liability and expense, including settlement-date value. Choice
awards require completed services in this profile. Counterparty choice splits
liability and equity; same-date liability remeasurement precedes settlement,
and share settlement transfers liability to equity. Entity choice uses supplied
present-obligation findings. For an equity-classified grant, either elected
alternative expenses its excess over the other alternative's settlement fair
value; a missing cash alternative is unresolved. A cash-classified share
settlement above the liability remains unsupported. Employee-service cash
expense is operating; separately identified equity repurchase is financing.
This cash split is a stated IAS7/IFRS2 deduction for these facts.

EPS posts no journal. Exact ordinary-share day intervals partition the complete
reporting period. Plain rights, one option series with strike plus future
service, one settlement-choice series with known after-tax adjustment, and
uncapped full-period weighted participation each have separate methods. The
continuing-operation numerator controls antidilution. Participation allocates
declared dividends and undistributed earnings by supplied rights. An EPS Report
must use that complete period and carry the independently calculated earnings,
weighted shares and per-share amounts; other reports require null EPS.
Multiple ordered series, changing participation and losses with participation
require additional methods.

Fair-value hedges post both derivative change and attributable debt-risk change
to profit, with no cash-flow-hedge reserve. Discontinuation fixes the final basis
and an exact one-year revised rate; amortisation removes basis before payment.
Derivative settlement remains separate from debt principal and coupon. Reform
relief requires direct-cause, economic-equivalence, additional-change and
derecognition findings, followed by timely designation documentation. Equal
illustrative coupons alone do not establish eligibility; no historical-source
finding establishes actual facts or current law.

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
plus OCI plus issue/award/basis-transfer/repurchase/reissue movements. Cash change equals net
category cash and separately gross receipts minus payments. Actual interest
paid is independently recovered from the receipt events. Gross income-statement
lines, OCI components and direct equity movements remain available separately.
These are pretax component reports, never complete-company after-tax statements.
