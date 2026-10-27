# Standards mapping and corrected transaction examples v1

An accounting method must say which financial facts permit its use, what state
it changes and which source supports those changes. This proposed specification
adopts Claude's mapping structure and replaces the defective acquisition,
interest and revenue examples. It addresses MC08/MC10, MC16–MC17, MC20–MC23,
MC25/MC28–MC30 and MC35. The examples are synthetic design calculations; they
are not executed product rules or professional accounting acceptance.

## A method record and its evidence

Each `AccountingMethodSpec` has these eight groups. The portable JSON/IR encoding
and full accounting interface remain P16 obligations; missing fields cannot be
silently filled from an unrelated method or prototype.

| Group | Required meaning |
| --- | --- |
| Authority and version | Standard issuer/framework, jurisdiction, source bytes/hash, exact paragraphs and inspected parts, annual-period/application dates, amendments/transition/elections and limits of incorporation. |
| Applicability and facts | Entity/instrument/transaction scope, recognition facts, contract terms, judgments and their source or selected-assumption evidence; explicit exclusions and unresolved alternatives. |
| Recognition and timing | Economic event, accounting recognition time, service/payment distinction, opening state, period/calendar and preconditions for applying the method. |
| Measurement | Formula, rate/day-count/compounding convention, currency/unit, estimation inputs, rounding, valuation uncertainty and supported mathematical capability. |
| State and journals | Economic/contract state, account roles and balances, events, repeat identity, atomic journal lines, cumulative-to-period deltas and reversals/corrections. |
| Presentation and disclosure | Statement classifications, movement reconciliations, narrative/estimate obligations, links from balances to source/elections and unsupported disclosures. |
| Examples and alternatives | Matched inputs, independently derived journals/closing balances, boundary/failure/replay cases and competing treatments with the conditions that distinguish them. |
| Evidence and remaining work | Separate source-inspection, derivation/arithmetic, semantic-model review, runtime-conformance, professional-domain review and human-comprehension statuses, with exact receipts and limits. |

“Reviewed” without a named evidence class is insufficient. Internal source and
arithmetic review can be complete while professional review is pending. Pending
professional review cannot transfer feasible internal work to a paid reviewer.
No external engagement is authorized by a method record. An incorporating AASB
text supplies evidence within its checked version/entity scope; a universal IFRS
claim requires the applicable framework and amendments to be established.

## Sources inspected for these examples

`standards-source-register-v1.json` pins the retained PDF/text and inspected
paragraphs. S9 is AASB 9 compilation 5, dated 31 December 2022, registered as
F2023C00399 on 2 May 2023. S15 is AASB 15 compilation 8, the same compilation
date, registered as F2023C00402 on 3 May 2023. Their covers state application to
annual periods beginning on or after 1 January 2023 and before 1 July 2026.
Their comparison sections identify IFRS incorporation and Australian-specific
paragraphs. We inspect the named for-profit provisions; we do not infer rules
for not-for-profit entities or later amendments.

The worked cases use an illustrative for-profit entity with an annual period
beginning 1 January 2024, the stated compilations and no later early adoption.
Those are explicit scenario facts. Actual applicable law, elections and current
2026 reporting must be checked for the target entity/period. The source register
has no full-standard or full-current-applicability acceptance status.

## Financial-asset acquisition

S9 paragraph 5.1.1 specifies fair value plus or minus directly attributable
transaction costs for instruments outside FVTPL. B5.4.8 describes which costs
are transaction costs; it does not independently decide their recognition.
For the following purchase, assume a correctly established FVTPL classification,
price equal to fair value, an incremental broker fee consumed on acquisition,
settlement at once, no other separately recognizable asset, and no tax or foreign
currency effects. Expensing the fee is the local journal consequence of those
facts and the fair-value measurement basis; the source does not prescribe the
account names used here.

Case A01 has price/fair value 100 and broker fee 2:

| Account | Debit | Credit |
| --- | ---: | ---: |
| Financial asset—FVTPL | 100 | 0 |
| Transaction-cost expense | 2 | 0 |
| Cash | 0 | 102 |

Both sides total 102; the asset is 100 and expense is 2. For the otherwise matched
amortised-cost asset A02, assuming that category is separately justified, debit
the asset 102 and credit cash 102. Include the qualifying cost in its effective
interest calculation. Neither example classifies an instrument from its label.

If price differs from fair value, S9 5.1.1A directs attention to B5.1.2A. The
observable-valuation condition and any deferred difference must be evaluated;
do not automatically post the difference as a day-one gain. Case A03, with
price 100/fair value 105 but missing evidence about that condition, returns
`TREATMENT_UNRESOLVED` for the recognition method and no committed journal.
The known acquisition facts remain available for investigation. A classification
or judgment failure cannot be repaired by merely balancing a guessed entry.

## Effective interest and impaired assets

For an annual effective rate r, an interval of d years with no intervening cash
flows has accumulation factor g=(1+r)^d, interest I=A(g−1), and closing carrying
amount A+I. With an end-of-interval cash flow C, closing amount is A+I−C.
Cash flows inside the interval require separate timed subintervals. Rate units,
year-fraction convention, payment timing and monetary rounding are method inputs.
A simple quoted rate would use its own stated convention; it cannot be silently
substituted for this effective-rate relation.

In A04, A=100, r=21/100 and d=1/2. Since (11/10)^2=121/100, g=11/10 and I=10
exactly. Debit the asset 10 and credit interest revenue 10. A subsequent cash
receipt of 6 debits cash and credits the asset by 6, leaving 104. Claude's linear
formula would give 10.5 and is wrong for this declared convention.

The exponential relation is an analytic specification, not a claim that every
rational input has a rational result. A rational-only profile needs a verified
exact factor or must return unsupported/approximate status with an error bound
under a separately specified numerical method. No rounding can turn a numerical
approximation into exact evidence. Zero or negative valid rates must not fail a
generic positive-rate assertion: A05 uses r=−19/100 and d=1/2, g=9/10, I=−10.
It debits interest revenue 10 and credits the asset 10. This generic
fractional-period operation uses the positive-base convention r>−1; handling a
zero or negative base requires a separately defined operation and eligibility
check. This is not a claim that every individual power at r=−1 is undefined.
Display rounding uses an explicitly selected quantum and tie
rule, applied consistently to the journal and balance update.

S9 5.4.1 distinguishes three relevant cases. A performing asset uses EIR on its
gross carrying amount. A purchased/originated credit-impaired (POCI) asset uses
the credit-adjusted EIR on amortised cost from initial recognition, 5.4.1(a).
An asset that becomes credit-impaired later uses its applicable EIR on amortised
cost, 5.4.1(b); it does not acquire a new credit-adjusted rate merely from that
change. In a fixed-rate example this is the unchanged original EIR. Recovery
to a non-impaired basis also needs the conditions in 5.4.2. B5.4.7 cautions that
high credit risk alone does not imply a credit-adjusted EIR.

A06 has gross amount 100, allowance 20 and applicable fixed EIR 10%; a one-year
subsequently impaired interest calculation is (100−20)×10%=8. A07 separately
has POCI amortised cost 60 and credit-adjusted EIR 20%, giving 12. These cases
verify rate/base selection only. Full gross-asset/allowance roll-forwards, ECL
measurement, modifications, write-offs and recovery methods remain P17 work.
The fair-value option anchor is 4.1.5 and the write-off anchor is 5.4.4; source
applicability still precedes either operation.

## Revenue, billing and collection

S15 paragraph 35 specifies when control transfers over time, with further
conditions in 36–37. Paragraphs 39–43 govern progress measurement and updates.
Paragraphs 105–108 distinguish contract asset/liability presentation from an
unconditional receivable. They do not make every billing unconditional, nor
equate every project cost with progress.

The R cases assume one qualifying performance obligation with separately
established over-time eligibility, a fixed transaction price 100, a supported
progress measure, unconditional bills due at their stated issue time, no prepayments
outside those bills, no financing/taxes/credit losses, zero opening balances and
no other contract assets. Costs in the C cases concern service already performed,
do not create future resources and fall within the stated S15 98(c) treatment;
they are not a generic prescription for capitalizing or expensing contract costs.
S15 95–96 require checking another standard's scope and future-resource criteria.
Invoices, revenue and costs have their own economic events and recognition times.

For this restricted fact pattern let R be cumulative revenue, B cumulative
unconditional billings and P cumulative collections. The derived controls are
AR=B−P, CA=max(R−B,0) and CL=max(B−R,0), where AR is receivable, CA contract asset
and CL contract liability. These relations are valid here because the billing
and payment assumptions are explicit; they are not universal IFRS formulas.
Within this example, 0≤R≤100, 0≤B≤100 and 0≤P≤B. A collection that exceeds
unpaid billings returns `OUTSIDE_EXAMPLE_SCOPE` without posting; advances and
refunds need their own method. Missing recognition or billing evidence leaves
the treatment unresolved rather than manufacturing those facts from the totals.

Each positive revenue increment dR first consumes min(dR,CL) of the opening
contract liability: debit that liability. Debit contract asset for the remainder
and credit revenue dR. Each positive billing increment dB debits receivable dB,
credits min(dB,CA) of the opening contract asset, and credits contract liability
for any excess. Collection dP debits cash and credits receivable dP. Zero legs
are omitted, each event balances, and state updates are committed with the journal.
Reductions, cancellations, impairment, refunds and modifications require an
explicit correction/treatment method, not a negative value smuggled through
these positive-increment operations.

R01 recognizes 60 before billing: debit CA 60 / credit revenue 60. Billing 50
then debits AR 50 / credits CA 50. Closing CA=10, AR=50, CL=0. The combined
entry is debit CA 10, debit AR 50, credit revenue 60. Merely adding a balanced
debit AR 50 / credit a separate Billings account 50 to Claude's original debit
CA 10 / credit revenue 60 still leaves debits 60 and credits 110. The response's
proposed addition therefore cannot repair the original entry.

R02 bills 80 before recognizing revenue 60. Billing debits AR 80 / credits CL
80; performance debits CL 60 / credits revenue 60. Closing AR=80, CL=20, CA=0.
Collecting 30 debits cash 30 / credits AR 30, leaving AR=50. Revenue is still 60;
the payment is not new revenue. R03 uses the same 60 revenue/50 billing as R01
but bills first; final account balances match although intermediate states differ.
Do not reorder actual recognition events merely to make an example convenient.

## Cumulative costs, request identity and atomic changes

For the stated already-performed services, committed cumulative cost C0 and
new cumulative cost C1 imply an incremental expense C1−C0. C01 records 40 by
debit cost expense 40 / credit service payable 40. A later valid C02 snapshot
of 70 records only 30. The total expense is 70, not 110. Re-observing the same
cumulative amount records no additional expense. Payment of the payable is a
separate debit payable / credit cash event. If costs instead create qualifying
future resources, use their supported recognition/amortisation method; these
examples do not substitute for it.

An event request binds book/entity, business event identity and version, contract,
method/evidence/assumption versions, economic time, payload, and expected opening
state. The proposed command protocol first checks an existing receipt for that
business identity. An identical request returns the original receipt and performs
no posting, even when the current book state has advanced; the receipt describes
its original state versions. A different payload for the same identity returns
`EVENT_ID_CONFLICT`. A new event with a stale expected state returns
`STALE_OPENING_STATE`. A newly named request cannot override the identity of the
same underlying business event. Event identity provenance and retention must be
specified by its adapter; a random call UUID is insufficient duplicate protection.

For a new eligible request, calculate cumulative deltas from committed state,
construct all lines, check units/rounding, debit-credit conservation and the
economic/account roll-forward, then atomically commit journal, state and receipt.
Any failure commits none of those three. An apparent repeated request after an
uncertain commit must resolve its receipt before retrying. These are proposed
behavioral requirements for P16 persistence, not implemented transaction guarantees.
A valid new observation with the same cumulative amount can produce an explicit
`NO_DELTA` receipt. Declining cumulative cost or revenue requires a separately
authorized correction/election, not automatic rejection of the underlying fact.

## Accounting breadth and unresolved methods

This repair supplies reusable mapping structure and a few checked examples.
P17 must give each requested domain its method/interface, scope, assumptions,
authority, worked case and limitations. Corporate coverage still needs revenue
exceptions, leases, pensions, deferred/current tax, share-based payment, business
combinations, impairment, fair value and group/FX methods. Financing, banks and
insurers retain the full mission's structural and method obligations; an empty
package name cannot satisfy them. IFRS/US GAAP/ASBE comparisons must distinguish
recognition and measurement, rather than map labels alone.

Claude's lease, pension and tax pseudocode is not adopted by this repair. For
each such area, inspect the relevant source/effective-period conditions and
construct complete transitions before copying any formula. Unsupported current
authority remains an internal research task where feasible. Numerical diagnostics
and synthetic cases do not close accounting, empirical forecast or human review.
P18 should integrate this reasoning into one manuscript, and P19 must verify
source, method and scope dispositions without a page or staffing quota.
