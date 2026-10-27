# CorporateComponents/4 documentary exchange contract

15 October 2026. R03-P2b. This version specifies the named finite transitions
below under supplied historical-source and valuation premises. It is a new
profile, not an enlargement or replacement of CorporateJointHistory/1.
Every accepted record has a closed JSON Schema body. The common I1 envelope,
L1 portable identity and accounting-owner/replay rules retain their meanings.
No accounting service, persistent runtime or production implementation runs.

## Inputs and identity

The schema lock binds this text and all schema bytes. Each method binds a
specific event variant, component variant, source edition/paragraphs and exact
method text. SourceSupport retains the source PDF, method and source-reading
bytes. Source text supplies conditional rules; synthetic admissions supply
the case facts. Neither represents a real-company conclusion. Context binds
entity, legal book, branch, monetary unit, accounting family and relative
calendar. T0/T1/etc. are synthetic ordered instants, not publication dates.
Authority has a synthetic applicability interval and exact primary and
supporting source references. Australian cases also carry actual synthetic
event dates and annual-period start/end dates: AASB15/137 scope uses the
beginning of the annual period, not the event date. The retained compilations
require starts from 2023-01-01 inclusive to 2026-07-01 exclusive. Retained
AASB107 starts at 2024-01-01; only authored 2024/2025 cases are supported.
Assurance needs AASB15 classification, AASB137 measurement and AASB107 cash
classification. Context identifies an Australian for-profit reporter; USD is
an illustrative measurement currency, not evidence of US jurisdiction.
Outside these source/issuer/period bindings an event is refused. A current-law or investor-information request
is outside this profile. No historical source is silently treated as current.

CompanyState has signed debit-positive account balances and one typed
component state for the finite slice. ComponentState is a closed tagged union;
EconomicEvent is a separate closed tagged union of method-specific inputs.
Neither admits an arbitrary payload or general journal-as-event. All rationals
are reduced pairs of decimal integer strings with positive denominator. All
IDs and object keys in this finite protocol are ASCII, so sorted-key compact
UTF-8 JSON agrees with the inherited canonical convention. No floats, duplicate
keys or non-finite numbers are allowed. Record hashes use
`SHA256(UTF8('accdsl.portable.v1/'+schema_id) || 0x00 || canonical_record_bytes)`.
Dependencies equal exactly the distinct embedded immutable record references,
ordered by canonical reference bytes. Blob bytes are independently SHA256-bound.

The input component must reconcile to its related account balances. A new
state must retain untouched components and accounts and have the expected
sequence increment. Case reports identify `uncomputed` tax except for the
explicitly supplied origin-only tax calculation. Pretax equity contributions
cannot be represented as the company's final after-tax equity. Separate
component cases are not automatically a joint company or tax jurisdiction.

## Named transition rules

- **production.accumulate:** add supplied current material/conversion costs to
  WIP and recognize the supplied payable. Increment physical starts and current
  cost pools; do not pretend completion or payment occurred. Closing quantities
  and progress remain null until the completion observation; unknown is not zero.
- **production.complete:** all material enters at start, homogeneous units,
  no loss, FIFO opening units completed first. Reconcile opening+started to
  completed+closing. FIFO current conversion effort is opening units times
  remaining fraction plus new completed plus closing conversion effort;
  weighted average pools opening costs and uses all completed equivalent units.
  Transfer only completed cost to finished goods; no expense or cash. Exact
  rational costs are the primary profile; cent posting needs its separate
  rounding/allocation profile and is refused here.
- **production.loss:** separate full-effort, no-salvage/no-fixed-overhead batch.
  Established normal output determines cost per good equivalent unit. Abnormal
  loss is actual loss less admitted normal loss, floored at zero; charge its
  cost to expense. Refuse actual output above the admitted normal output in
  this branch rather than invent an abnormal gain rule.
- **inspection.replace:** the old component is already depreciated to the
  event instant. Derecognize its remaining cost as expense, capitalize the
  eligible new inspection cost and pay cash. Preserve the physical part.
  **inspection.consume** separately depreciates physical and inspection
  components over their remaining supplied lives, with zero residuals.
- **lease.reduce:** supplied homogeneous surrendered fraction q removes qA
  and qL; gain is q(L−A). Discount the single remaining payment at its newly
  admitted one-period rate; its difference from (1−q)L adjusts surviving ROU.
  Heterogeneous rights and termination fees are outside this finite method.
  **lease.usage** expenses non-index/non-fixed usage separately into a payable.
  **lease.mature** charges the remaining single-period interest and ROU
  depreciation and pays the contractual amount; usage payable is untouched.
- **benefit.remeasure:** update DBO and plan assets at the event date and
  record the net change in OCI, with no ceiling in this liability-only slice.
  **benefit.curtail:** reduce freshly remeasured DBO and recognize past-service
  gain in profit. **benefit.settle:** reduce the legally discharged DBO and
  actual plan-asset/cash consideration; profit is discharge minus price.
  **benefit.service:** use the post-event DBO/assets for the supplied remaining
  year fraction and simple rate, then add current service cost. A surplus or
  ceiling requirement is refused rather than silently set to zero.
- **funding.recognize:** in the distinct IFRIC14 example, the IAS19 surplus
  is wholly unavailable and a separate past-service funding obligation is
  wholly unavailable after payment. Recognize that obligation as net pension
  liability and OCI loss. **funding.pay** increases plan assets while consuming
  the liability and cash; there is no second profit or OCI movement.
- **restoration.change:** cost-model liability was included in the same
  asset's cost. A decrease consumes asset carrying amount to zero and sends
  excess to profit; an increase adds cost, followed by any separately supplied
  impairment requirement. This finite branch records that impairment directly
  against PPE, retaining it in the component. The exhausted-life branch sends
  changes to profit. **restoration.pay** requires equality with the last
  liability measurement and consumes liability/cash. The supplied operating
  classification remains a provisional fact-specific interpretation; an
  unresolved classification may not produce complete categorized cash flow.
- **impairment.allocate:** one admitted cost-model CGU, goodwill first, then
  proportional positive carrying weights with individual floors and repeated
  redistribution. The component retains asset IDs, gross carrying, allocated
  losses and valuation status. Missing values, unallocated loss, all-zero
  weight reversal, tax, corporate assets and NCI need distinct methods. They
  are not generalized by this finite exchange.
- **tax.revalue_impair:** same-asset surplus takes impairment in OCI first,
  then profit. Reverse the old related DTL in its OCI origin; recognize a
  deductible difference in profit only under the supplied recovery finding.
  This is a no-time/no-tax-base-change impairment, not a full tax close.
- **advance.allocate:** consume the identified fully prepaid right and mark
  the bill allocated with no monetary line. Any previous allocation conflicts;
  fictitious debit/credit lines are not an acceptable empty journal substitute.

The historical method texts referenced by each MethodDefinition give the
derivations, source clauses and worked values. Missing fact inputs are unresolved,
failed factual/identity invariants reject, and unsupported method/profile or
valuation scope returns unsupported. No numerical zero fills any of these states.

## Authorization, proposal, commit and reporting

`accounting.authorize@1` returns a dated Admission and PostingAuthorization
bound to the exact basis, event, method, source, context and selected view.
`accounting.propose@1` is read-only and returns the authorized journal,
economic delta and closing candidate. Authoring those candidates does not
publish them to an accounting store. `accounting.commit@1` requires all four
references (basis, authorization, journal, delta). Structural and binding
validation precedes business-event lookup; financial validation compares the
complete proposed transition with the declared component calculation.

The business identity is entity/book/branch/event, encoded as a canonical
four-item array (never ambiguous slash concatenation). Exact prior request
bytes return the original receipt before checking current-head freshness.
Changed bytes for the same event conflict, including changed budget or request
ID. A new event requires the exact opening state/generation and owner head.
Successful commit publishes the dependency closure, journal (possibly the
explicit state-only variant), delta, new state, receipt and event lookup in one
atomic change. Every other owner remains unchanged. Rejected, unsupported or
unresolved requests have no accounting-store effect. All cases include complete
before/after store worlds; fixture-registry presence is not publication.

A lost acknowledgement leaves two possible complete worlds, before or after
publication. Resubmit identical bytes: commit once in the first, replay in the
second. Partial publication is invalid. A receipt published without its closing
state/component is not a third recovery outcome. Corrected evidence creates a
new view; prior exact replay remains an audit operation, while a new current
proposal must use the corrected view. No original journal is silently edited.

`report.build@1` is read-only and pins both opening and closing states in its
arguments before mapping their common context to
assets, liabilities, pretax/origin-only equity, profit, OCI and classified cash
movements. Profit and OCI derive from signed account changes from an explicit
opening reference; an inherited revaluation reserve is not current-period OCI. Cash
movements come from event histories, not changes in closing liabilities.
Uncomputed tax and any unresolved classification remain explicit report limits.
An assigned operating restoration outflow still carries its provisional
interpretation status; allocation completeness does not certify that policy.

## Compatibility and remaining scope

CorporateComponents/1 remains byte-for-byte protected. Its methods are
re-expressed under the successor source schema; this does not prove automatic
migration of its wire records. Old references retain their IDs/hashes. A request carrying
CorporateJointHistory/1 is refused by this profile; changing its name is not a
migration. Later migration can be proved only for mapped purchase/state fields
and compatible assumptions. Finite state-only advance behavior is specified
here but does not silently accept its predecessor's wire body. P5 must reconcile
the wider restoration/impairment/tax and sector joins still
outside these named transitions. This profile alone does not close R03-P2 or R03.

## Customer and supplier additions

Each addition retains separate opening/event/closing records. The calculation
uses prior recognition and remaining obligations, not a desired closing profit.
The pinned methods give derivations and paragraph anchors for the finite rules.

Returns retain expected remaining and actually returned units, refund liability,
separate recovery asset and inventory. Sale records gross cash but only expected
retained consideration as revenue; cost splits between expense and recovery.
Remeasurement changes both balances under new evidence. Final settlement requires
an updated estimate equal to actual returned units and evidenced expiry with no
unresolved claims. Partial ongoing returns or nonzero processing costs require
their own measurement; no missing recovery input becomes zero.

Assurance classifies the promise before measuring the provision. A nonnegative
population law summing to one determines expected cost without assuming claim
independence. Virtual certainty admits a separate reimbursement asset. Claims
paid and reimbursement received remain separate event fields; a new estimate
updates their remaining gross balances. Netting reimbursement against the
balance-sheet liability is rejected. A service promise cannot use this branch.

Service-warranty receipt fixes allocations from admitted inception standalone
prices. Product delivery releases only its allocation and inventory cost.
Service progress releases only the increment and actual service costs. The
uniform monthly case has six completed months at2024-12-31 and twelve at
2025-06-30 from2024-07-01. Dates/cash alone do not establish faithful progress;
missing measurement returns unresolved.

Remaining-distinct-goods modification preserves delivered revenue and inventory
history, then allocates unrecognized plus added consideration over remaining
units. The example's paragraph20 separate-contract test is supplied false.
Integrated modification recomputes cumulative price-times-progress revenue and
posts its difference from previous recognition. Mixed modification recomputes
cost-to-cost construction while remaining visits stay prospective. Additional
cash is separate from the revenue catch-up. Enforceability, allocation and
faithful progress are required findings. A true separate-contract addition is
refused pending explicit record composition; that neighboring method remains a
P2/P5 obligation, alongside variable-price updates and progress fallback.

Principal/agent state binds the promise and control role. A principal acquires
inventory/payable and records gross sale/cost; an agent records commission and
remittance liability. Both retain receipt120 and remittance100 as distinct
events. Equal final profit20 does not equate revenue or control. Reports show
operating totals and retain gross legs; no agency-specific gross/net election
is asserted.

Joint production uses admitted relative split-off sales values, retains both
stocks and expenses only sold cost. The immaterial-byproduct branch allocates
its NRV and remaining main-product cost without duplication. These EU methods
do not inherit Australian authority from neighboring customer examples.

Supplier finance recognizes the normal-credit inventory/payable, accretes the
two-year liability and expenses interest for non-qualifying inventory. Sale
and settlement remain separate. The100→110→121 schedule must equal final cash
121. Original trade-supplier identity and the historical operating-interest
election are explicit; substitution requires new classification assessment.

Report inputs bind both interval endpoints. Period profit, OCI, revenue, costs
and cash use their differences; lifetime totals cannot silently stand in for
2024 or 2025 movements. The closed income statement distinguishes product,
service and commission revenue, reimbursement income, other gains, inventory
cost, service/assurance expense, other expense, finance and tax. In particular,
reimbursement100 does not inflate assurance product sales2000 to2100.

## Asset successor and direct equity transfers

The asset methods carried forward from /3 retain the existing P17/R03 cases.
The benefit and tax section below extends them under /4; remaining customer
variants are separate successor work. The old exact requests are refused under this lock;
no implicit migration follows from shared field names.

RevaluationClass retains the complete admitted membership, item-level gross
amounts, accumulated depreciation, remaining lives, surplus and prior profit
loss. A class revaluation includes even a member with no adjustment. The
for-profit rule routes each member separately; it does not net members' origins.
Disposal preserves identity and remaining surplus. This finite profile elects
transfer on disposal; transfer during use requires the separately specified
original-cost depreciation path and remains outside this profile.

CompanyState.revaluation_transfers is cumulative direct transfer from surplus
to retained earnings, with no profit or current-period OCI. Reports add its
interval change back to the negative change in the OCI account balances. This
keeps 2025 OCI15 even when the reserve closes at zero following transfer15.
The 2024/2025 values and all individual origins are independently checked.

CorporateAssetState retains leaf units and the smallest admitted group with
the headquarters asset. Leaf tests consume their own current carrying amounts;
the group test is refused until all leaves are tested and then uses adjusted
amounts. Floors remain per asset. These finite examples supply zero floors;
missing floor assessment is unresolved. A unit value is not its members' floor.

PartialGoodwillState belongs to the consolidated book. Each part preserves
reported versus test goodwill, the NCI election, supported proportional
gross-up and profit allocation. Goodwill and identifiable-asset losses use
their respective part weights. Notional NCI goodwill and its loss never enter
journals. Reports distinguish parent and NCI recognized loss from unrecognized
notional loss. Actual goodwill valuation, premiums and profit rights are inputs.

ReversalState retains original gross amount, accumulated depreciation and loss
allowance as well as the independently depreciated no-impairment ceiling.
Changed-estimate evidence is required. Capped current-carrying weights exclude
goodwill; zero weights with remaining capacity remain unresolved. The existing
70→56→80 case preserves unit value90 and residual allowances1/5.

Revaluation-model restoration retains its hypothetical cost-model carrying
amount, same-asset surplus and prior deficit. A class review must first support
the unchanged PPE used by these examples. The liability change splits into
profit and separately reported restoration OCI. An unknown hypothetical cost
amount remains null where an increase does not need it; a later decrease
requiring that amount returns unresolved. The exhausted-asset case charges
profit even when a historic surplus survives. No actual valuation is inferred.

## Benefit availability, classification and tax origins

BenefitCeiling retains the gross obligation/assets, supported economic benefit
and ceiling adjustment. The amendment calculates past-service gain before the
ceiling: gain20, OCI loss15 and recognized-asset increase5 remain distinct.
BenefitAvailability retains refund rights/costs and the future employer-service
and funding schedule over the shorter admitted horizon. These finite examples
explicitly use zero discount and mutually exclusive routes. The contribution
benefit is7+max(0,8−5)=10; compare it with the available refund25 rather than
summing routes. The state-only assessments independently corroborate supplied
opening assets25/10. They do not invent a new right or the original cash history.

MultiEmployer preserves economic defined-benefit terms even when the paragraph34
finding selects defined-contribution accounting. The fallback retains paragraph148
disclosures; the separate deficit contract recognizes100, accretes10/11 and pays121.
Common-control arrangements are refused into their IAS19.41 method. The typed
classification vocabulary is broader than the one complete fallback/deficit
path; allocation and contribution interactions remain P5 work.

UncertainTax preserves treatment grouping, full-information examination,
probable-acceptance finding and an admitted predictive measure. Deductions100,
20 and42 produce current/deferred splits0/20,20/0,14.5/5.5. Resolution to40
changes the final split to15/5 without changing total tax20. Current tax and
deferred tax share the selected deduction. Probability vectors are supplied
illustrations, not estimates of enforcement or legal outcomes. The origin
slices retain the preceding book depreciation/revenue in their supplied opening.

AcquisitionTax is a full acquisition with no acquired cash or bargain purchase:
fair-valued assets150, tax base100 and supplied25% produce DTL12.5 and goodwill12.5.
No recursive DTL is recognized on initial goodwill. InvestmentTax is an isolated
outside-basis tax slice, not a complete investment book. Taxable difference60 at
20% is exempt only when both control and probable nonreversal hold. Its mirrored
deductible test requires probable reversal and taxable profits, independently.
Unknown required findings remain unresolved. Cases changing each condition
separately distinguish these asymmetric tests.

TaxRevaluation preserves prior profit loss, gross surplus and separate cumulative
profit/OCI tax effects. The no-time/base-change reversal restores prior profit
loss10 before OCI30, with tax2.5/7.5 in the corresponding origins. A25%→30%
rate change on the original40 surplus adds DTL2 and OCI tax2, without profit.
Mixed origins and changed recovery paths require a further allocation; they
cannot inherit that single-origin rule by default.

PillarTwo binds the separately retained EU2023/2468 amendment as primary source,
with the original EU tax/cash rules as support. Its finite dated cases follow
entry into force on10November2023 and the annual-start application rule.
Current tax7 is a supplied in-scope calculation, separately recognized/reported
and paid. The hypothetical temporary difference40 creates no deferred tax.
Reports carry the exception/current disclosures and, before legislation is
effective, the supplied exposure information or its explicit unavailability and
assessment-progress statement. A null current-tax amount cannot become zero.
No general GloBE calculation, jurisdictional enactment or current-law claim follows.

Report.tax_movements separates ordinary current profit tax, deferred profit tax,
deferred OCI tax, acquisition deferred tax and Pillar Two current profit tax.
Income taxes paid are separately shown. Each tax payment binds the admitted
activity classification; the examples supply operating treatment under IAS7.35–36.
Missing classification is unresolved. No uncomputed tax is silently promoted
to a complete after-tax company result.

No illustration supplies real eligibility, return probabilities, actuarial
calibration, standalone values, progress, tax or current authority. The inherited
atomic, replay, report-period and provisional-cash boundaries remain in force.
