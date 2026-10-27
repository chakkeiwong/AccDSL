Read-only bounded reviewer. No tools, edits, commands or agents.
The full assessment packet was legible but the review timed out before verdict.
Review only the precise question and original excerpts supplied here. Return
at most 350 words: material findings, needed repairs, and one final line
VERDICT: AGREE or VERDICT: REVISE. Do not restate the packet or make tables.
AGREE is bounded agreement with this negative assessment/scoped question answer,
not whole-proposal readiness, compliance, implementation or human acceptance.
Every scoped contract answer retains broader source/method/validation obligations.

Question: Is E12 concretely answered for query-scoped state retention and grouping without claiming a universal equivalence algorithm or full domain authority?
[
  {
    "id": "P15-E12",
    "question": "What entity and economic memory must survive aggregation and extension?",
    "proposed_answer": "P16 query-scoped memory and P17 group/perimeter, bank and insurance transitions supply concrete structural examples; source gaps remain E07/domain obligations.",
    "alternative": "Store aggregate account totals and assume omitted rights, timing and dependencies can be recovered later.",
    "next_step": "Retain actual control/cohort/lot facts and prove any new grouping within its query scope.",
    "blocks_proposal": false
  }
]

docs/design/proposal/architecture/history-families-contract-v1.md
SHA256 87140fbbbbd9137d792f22ed92e92d274a0a1cf9b2c332f2e743df2d92bcc3bd
## H4. Economic memory, grouping and refinement

A historical accounting balance does not describe all future contractual cash
flows. A principal of 100 with a fixed rate of 5% and a principal of 100 whose
floating rate was 5% can produce the same stipulated historical interest of 5.
If the next full-year rate is 7%, future interest is respectively 5 and 7. A
principal due next year and one due a year later can likewise have identical
current balances but different principal repayments within a one-year query.
The histories must retain rate/reset terms and maturity even when their
historical postings happen to agree. The example establishes arithmetic under
specified simple-interest assumptions, not a recognition or valuation method.

Required state is determined by requested scenarios, horizon and outputs plus
the applicable domain methods. It includes legal entity/perimeter, ownership and
rights, contract/lot/cohort identities, currency, principal/units, recognition
and measurement basis where applicable, rates/resets, schedules/maturities,
options/guarantees/collateral and linked dependencies whenever those affect the
query. “Unknown” is a value status requiring preservation; absence of a field
cannot silently mean no guarantee or no option. Later banks, insurance, groups,
FX, securities and cross-standard methods must extend these state requirements;
a scalar balance schema is not a whole-product substitute.

A grouping request names constituents, transformation/version, retained detail,
scenario domain, horizon, outputs, rules and exact/approximate claim. An exact
certificate must show that aggregation G commutes with every admitted transition
T for that domain, G(T(s,u))=T_group(G(s),u), and that requested outputs satisfy
O(s)=O_group(G(s)). These are proof obligations, not general facts about
financial balances. Missing proof/evaluation returns `GROUPING_UNSUPPORTED`;
it leaves detailed histories available and cannot delete them. A certificate is
part of query/resolution identity, with constituent and rule versions.

For the deliberately narrow simple-interest fixture, two principals 40 and 60
share entity, currency, a fixed 1/20 annual rate, a common day-count convention,
no intermediate principal change, and maturities after the half-year horizon.
Only total principal and interest are requested. Individual interest is
40*(1/20)*(1/2)+60*(1/20)*(1/2)=1+3/2=5/2. Grouping gives
(40+60)*(1/20)*(1/2)=5/2 by distributivity. Principal remains 100 under both
representations; any stipulated interest-payment cash transition subtracts the
same 5/2. This proves the named aggregate outputs/transitions for those
assumptions, not contract-level cash flows or other accounting measurements.
Constituent records remain linked so a later query can refine the group.

A changed output (individual contract exposure), rate/reset/maturity/guarantee
assumption, rule or horizon requires a new sufficiency decision. Reusing the old
certificate returns `RESOLUTION_REVALIDATION_REQUIRED`. Refinement produces a
new resolution version linked to its parent and constituent detail; if the
required detail was never preserved, return `DETAIL_UNAVAILABLE`, not fabricated
lots or contracts. Refinement can restore represented detail, not recover facts
that were never known.

Approximation is a distinct, optional future claim. Its record must name each
output, unit, scenario/horizon domain, absolute/relative tolerance, justification,
error argument or evaluation evidence, and exact-detail fallback. No tolerance,
empirical error bound or approximate grouping is approved by this contract.
Changing the query invalidates the approximation's applicability. Counts of
similar contracts and similarity of old postings are insufficient evidence.



docs/design/proposal/methods/bank-methods-v1.md
SHA256 e8e15aa7cb2214b0050fa65ac12d243b5b518f386b21a28800a5d8e13a8b495f
## B1. State and event order

BankState contains cash/reserves by settlement venue and currency; deposits by
customer, access rights and maturity; assets by contract, gross carrying amount,
allowance, original EIR, accrued cash flows, collateral and credit state; undrawn
commitments; funding lines and covenants; accounting equity; regulatory mappings;
and evidence/information views. LoanState separately retains origination credit
risk and current risk, SICR finding, credit-impaired/POCI status, forbearance,
modification, write-off and recovery history. Aggregating by today's loan balance
alone loses both staging evidence and later response to shocks.

Each time step first admits information known then, forms permitted credit and
liquidity forecasts, chooses behavior under that information, and schedules due
events. Accrual, actual settlement, impairment measurement and regulatory queries
have separate business identities. A deposit received from outside debits
cash/reserves and credits deposit liability. A loan credited to the borrower's
deposit debits loans and credits deposits without initially transferring reserves;
a transfer to another bank then debits deposits and credits reserves. A loan paid
directly outside instead debits loan/credits reserves. These two funding paths
cannot be treated as identical cash events. Deposit interest debits interest
expense/credits deposit or accrued payable; withdrawal requires settlement funds.

## B2. Expected credit loss

For each admitted scenario j and date t, calculate contractual due flows minus
the cash expected to be received, including supported collateral/enforcement
cash and timing; discount the shortfall under the applicable original EIR or
specified exception. With mutually exclusive exhaustive scenario weights w_j,
ECL is the sum of w_j times those present-value shortfalls. Default-time hazards
must be converted to disjoint default-time probabilities; summing cumulative PDs
over dates counts the same default repeatedly. Collateral recoveries cannot be
credited both in LGD and as a second recovery cash flow. A shorthand PD×LGD×EAD
is admissible only if its definitions and discounting reproduce the specified
cash-shortfall calculation; it is not a universal replacement.

For the general approach, twelve-month ECL considers lifetime shortfalls arising
from possible defaults during the next twelve months; it is not just unpaid
cash in those twelve months. SICR uses the change in lifetime default risk since
initial recognition, reasonable forward-looking information and the applicable
rebuttable presumptions. Do not install a two-times-PD or30-day rule as an
unconditional universal trigger. Lifetime ECL follows a supported SICR finding;
cure needs a supported reversal of that finding. Subsequently credit-impaired
assets use original EIR on amortised cost for interest in subsequent periods;
POCI has a separate credit-adjusted-rate and cumulative-change method.

The general measurement interface requires scenario_cashflows, law_ref,
information_view, horizon_admission, credit_assessment and discount_rule. An
unweighted history set can produce conditional losses or loss bounds, but cannot
produce an unbiased probability-weighted ECL by silently using equal weights.
Return measurement_unresolved for the ECL claim. Trade receivables and certain
other assets use the separately applicable simplified approach; the general
loan staging rule must not overwrite AASB9.5.5.15–16.



docs/design/proposal/methods/insurance-methods-v1.md
SHA256 a3629ed2946b4fc48cedcf68d8c3569750a374eab27d125c008a9c814d952b8d
## I1. Group state and general measurement

Contract records retain insured risks, premiums/benefits, service and settlement
dates, options/guarantees, cancellation/repricing rights and acquisition costs.
Group admission evaluates portfolio/similar-risk management, onerous status and
required issuance cohorts under AASB17.14–24, recognition under25–28 and boundary
under34. Cash outside the boundary belongs to future contracts, not this group's
profit. GroupState retains expected dated cash flows, current discount curves,
inception rates, explicit risk adjustment, CSM, loss component, LRC/LIC,
coverage units, service experience and assumption vintages. Same premium totals
are not sufficient state for merging different guarantees or claim tails.

General measurement follows32–38: fulfilment cash flows are probability-weighted
future net outflows, adjusted for timing/financial risk without double counting,
plus explicit non-financial risk adjustment. CSM removes initial unearned gain
under its conditions; an initial net loss is recognized under47, not negative
CSM. Paragraphs40–44 separate remaining coverage and incurred claims. For a
nonparticipating group, accrete CSM at the specified locked-in rate, apply future
service changes at their required rate to CSM up to its available amount, record
any excess loss and allocate current service over current plus future coverage
units under B119. B96–B97 distinguish future service from incurred-claim changes,
financial changes and current experience; not every revision is a CSM adjustment.

A MeasurementInput must resolve cash-flow/law, discount, risk-adjustment method,
service grouping and coverage-unit evidence. Missing probabilities or RA support
permit conditional sensitivity cases but block a source-supported measurement.
Risk adjustment is the compensation the entity requires under37; a standard
deviation, confidence quantile or arbitrary percentage is only a candidate method
until justified for that entity. Disclosures and the confidence-level equivalent,
where applicable, are separate obligations. Market-consistent financial inputs
and entity risk compensation must not be conflated.



docs/design/proposal/methods/groups-fx-methods-v1.md
SHA256 44c8db1d3a474d95dfc96099bc98211902aab30c5ea197d6016d6f1520291008
# Group boundaries, eliminations and currencies

The group is a dated relationship among legal entities, not an attribute added
to otherwise context-free amounts. This method specifies control assessment,
acquisition accounting, consolidation adjustments, ownership changes and currency
translation for MC02, MC05–MC07, MC11, MC16, MC19–MC20 and MC25–MC29. Sources are
the retained official EU 2023/1803 text, IFRS3, IFRS10 and IAS21 paragraphs cited
below. They support the inspected historical mechanisms; later amendments and
actual reporting applicability require a dated jurisdiction-specific review.

## G1. Perimeter and consolidation state

ControlAssessment records investor/investee, relevant activities, rights and
their substantive/protective character, variable returns, ability to use power,
principal/agent analysis, effective interval and evidence. IFRS10.5–9 requires
power, returns and their connection, with reassessment on changed facts. An 80%
share count is evidence to analyze, not an automatic substitute for control.
Unknown control yields separate conditional perimeters and unresolved group
results; no entity disappears merely to make reconciliation easy.

PerimeterVersion binds control intervals, ownership classes, report cutoffs,
functional/presentation currency, policy-alignment adjustments and the exact
source entity books. ConsolidationAdjustment is a distinct group book with
matched counterparty/event references; legal-entity journals remain intact.
The procedure is: select time-compatible entity books; apply supported policy
alignment; translate them; add like balances/movements; eliminate investment
against acquisition equity; eliminate intragroup balances, income/cost and
unrealised gains; allocate profit/OCI to owner/NCI; reconcile all statements and
movement notes. IFRS10.19–23/B86–B96 support these steps. Reporting-date differences
need B92–B93's conditions and intervening adjustments; a generic nearest-date
join is invalid.

## G2. Acquisition and ownership case

Assume a business combination, no common-control transaction, parent obtaining
control and80% of ordinary residual interests for cash96. Acquiree identifiable
assets fair value160 and liabilities60 give net100. There is no prior interest,
contingent consideration, tax difference, separately unrecognized intangible,
transaction cost or impairment; those absences are synthetic facts. Select
proportionate-share NCI under IFRS3.19: NCI20 and goodwill96+20−100=16 under .32.
In parent books debit investment96/credit cash96. In the consolidation overlay,
debit acquiree acquisition equity100 and goodwill16, credit investment96 and
NCI20. Only post-acquisition income enters group performance. Asset measurement
exceptions, deferred tax and a bargain gain reassessment under .36 would change
the calculation; goodwill cannot absorb an unexplained missing balance.

If post-acquisition net profit is20, all accrued in retained earnings with no
dividend/OCI, NCI increases4 to24 and parent's attributable profit is16. Parent
buys another10% for15 while retaining control: transfer12 from NCI (10% of
current net120), credit cash15 and debit parent equity3. Remaining NCI12;
goodwill16 unchanged; no new profit. IFRS10.23/B96 makes this an equity transaction.
This example has equal ordinary rights; preference rights need their actual
allocation and cannot use a simple ownership fraction.

In a separate alternative starting before that additional purchase, sell all
80% for130 when net assets120, goodwill16, NCI24 and OCI zero. On loss of
control, group gain=130+24−(120+16)=18. Derecognize individual assets/liabilities
and goodwill, remove NCI, recognize consideration and gain. The separate parent
book's investment gain is not added again. If20% is retained and60% sold for100
with retained fair value35, group gain=100+35+24−136=23; recognize the retained
investment35. Its subsequent associate/financial-asset method needs separately
established significant-influence/classification facts. IFRS10.B98–B99 also
requires the appropriate prior-OCI treatment; this case assumes none.

## G3. Intercompany inventory and tax

Assume parent's external inventory cost60 is sold to its controlled subsidiary
for100 on credit, all still held at report date, tax ignored in the base case.
Parent records AR100/revenue100 and COGS60/inventory60; subsidiary inventory100/
AP100. Consolidation debits AP100/credits AR100 and debits revenue100/credits
COGS60 and inventory40. Group inventory60, revenue and COGS zero, and no group
profit arises. When subsidiary later sells externally for120, group COGS is60
and profit60, not20; release the previously eliminated40 in the continuing
adjustment roll-forward. Reversing a closing overlay and recreating a new one
must not recognize the profit twice.

If the purchaser's independently supported tax base is100, group carrying
amount60 creates deductible difference40. At assumed applicable25% and with
all IAS12 DTA conditions satisfied, recognize group DTA10/deferred-tax benefit10;
reverse on outside sale. The original tax expense and cash obligations in the
seller's tax jurisdiction remain. Different rates, recoverability or tax-law
transfer rules change the answer; tax is not simply eliminated with group profit.
For an upstream subsidiary sale, attribute elimination and related tax effects
to the appropriate subsidiary/NCI performance; downstream parent's profit
elimination does not mechanically reduce NCI by the same fraction.

## G4. Functional currency versus group presentation

EntityCurrencyState names the functional currency and its evidenced rationale,
foreign-currency nominal balances, monetary/nonmonetary classification, historical
or fair-value measurement dates, rates and sources. IAS21.21–23 and .28 require
transaction-date translation and closing-rate remeasurement of monetary items;
historical-cost nonmonetary assets retain transaction-date rates. A functional
currency change is prospective under .35–37. Hyperinflation, lack of exchangeability
and hedge accounting require separate applicable methods; do not import the
historical .26 text into a later amended period without checking it.

Example: buy goods for foreign100 at functional1.2 per foreign unit; debit
inventory120/credit payable120. Closing rate1.3 gives payable130 and FX expense10,
while inventory remains120 before any NRV test. Pay at1.25: debit payable130/
credit cash125/credit FX gain5. Cumulative expense5 matches125 cash less120 asset
cost. Translating the inventory again to130 would be wrong for this declared basis.

Group presentation is a different operation under IAS21.39–41. A subsidiary has
opening net assets100, equity100, no debt or distributions, annual profit20
entirely earned at rate1.25, and closing assets120. Opening historical rate1.2
and closing1.3 give translated assets156, contributed/opening equity120 and
profit25; translation OCI11 reconciles the difference. It is explained as
100×(1.3−1.2)+20×(1.3−1.25)=11, not a free balancing plug. If ownership is80%,
parent/NCI shares of profit are20/5 and OCI8.8/2.2 under the stated equal rights.
Use transaction rates; an average is acceptable only as a justified approximation,
not when significant fluctuation invalidates it. Goodwill and fair-value
adjustments follow IAS21.47's foreign-operation treatment, rather than freezing
them automatically in the parent's currency.

Group reports retain the translation reserve by entity, ownership and event.
Loss of control requires the appropriate reserve reclassification under IAS21.48
and IFRS10.B99; a no-control-loss change transfers the relevant attribution in
equity under applicable conditions. Cash translation effects reconcile cash
separately from operating/investing/financing movements. An intercompany monetary
balance's exchange result cannot simply be eliminated as if no currency exposure
existed; IAS21.45 and net-investment .32 require the substantive classification.
