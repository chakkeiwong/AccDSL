# Fixed-payment lessee method and a subsequent modification

This proposed method recognizes the right to use equipment and the obligation
to make payments, then tracks depreciation, interest, cash settlement and changes
in the agreement separately. It prepares P17 under MC13/MC15–MC17/MC19/MC20,
with source and comparison evidence for MC23/MC29 and internal preparation under
MC35. It is a specification with synthetic calculations; no product transaction
engine, general accounting compliance or professional acceptance is established.

## Authority and version

Source L16 is the official AASB 16 compilation 8, compilation date 31 December
2023, prepared 18 December 2023 and registered as F2024C00049 on 16 January 2024.
The upstream filename and portal label say November 2022 because amendments
incorporated extend to 10 November 2022; they are not the compilation date. The
cover applies the compilation to annual periods beginning on or after 1 January
2024. Paragraph C1D covers the 2024 sale-and-leaseback amendment, which this case
does not use. The comparison on physical page 5 identifies IFRS 16 incorporation
for for-profit Tier 1 reporting. This is an Australian source supporting selected
incorporated provisions, not a finding of full current IFRS or AASB compliance.

We assume an established Australian for-profit Tier 1 reporter for FY beginning
1 January 2024, with no later early adoption. The future schedule holds the
inspected rules fixed to illustrate consequences; reporting applicability in
2025–2026 must be rechecked before actual use. Source P116 supports the selected
depreciation assumptions and CF107 supports cash-flow classification. Exact
sources, hashes, physical pages, paragraph/text anchors and inspected scope are
in [source-register.json](source-register.json) and
[source-inspection.md](source-inspection.md). A source paragraph supports its
stated condition, while the journal names and exact numbers below are local
deductions under the declared facts.

## Applicability and contract facts

L01 is a single identified, non-specialised item of equipment available to the
lessee from 1 January 2024 through 31 December 2025. The lessee has exclusive
economic benefits and decides how, when and for what purpose to use it within
the contract. The lessor has no substantive substitution right. These are
assumed contract facts satisfying L16.9 and B9/B13/B21/B24; a production record
needs the actual contractual evidence and interpretation. The lessee is not a
joint arrangement and there are no connected contracts, service components or
embedded derivatives.

The lease is noncancellable for two years, with no extension, termination or
purchase option, residual-value guarantee or ownership transfer. Equipment has
a remaining economic life of ten years, a ten-year usable capacity before lease
restrictions, fair value 1000 and alternative uses for the lessor after return.
These additional matched facts support packet 2's classification comparison;
neither fair value nor useful life replaces the L16 control test. Amounts are in
one synthetic currency unit (CU); fair value 1000 is not itself a low-value
classification. The lessee elects no low-value exemption, and a two-year term is
not short-term. No sublease or sale-and-leaseback exists.

Payments of 121 are due and paid at each year-end. There are no advance payments,
incentives, initial direct costs, restoration obligations, indexation, variable
payments or tax/foreign-currency effects in L01. The implicit rate cannot readily
be determined; assume a supported annual effective incremental borrowing rate
of 10% for comparable term, security, ROU value and economic environment
(L16.26 and Appendix A). This is a selected example input, not an observed market
rate. Payment dates are exact annual anniversaries; partial periods and day-count
conventions require another case. The right is consumed evenly, no impairment is
indicated, cost measurement is selected and no cost is absorbed into another asset.
Thus straight-line depreciation over the two-year right is appropriate under
L16.29–33 and P116.48/50/55/60–62. No threshold or model is selected by this example.

## Recognition and measurement

Recognize at commencement, when equipment is made available, rather than merely
when the contract is signed (L16.22 and Appendix A). At 1 January 2024 the unpaid
payments have present value

\[
L_0=\frac{121}{1.1}+\frac{121}{1.1^2}=110+100=210.
\]

L16.24 adds prepayments less incentives, initial direct costs and qualifying
restoration cost to the ROU asset. All are zero here, so ROU cost is also 210.
The liability recurrence is \(L_t=L_{t-1}(1+r)-P_t\), with interest on the
opening remaining liability, as L16.36–38 require. ROU depreciation is
\(210/2=105\) each year. ROU and liability are distinct records: matching initial
values do not justify forcing them to remain equal.

## Dated journals, balances and statement consequences

Each row below is a separate balanced event. Accrual and payment are ordered at
the same year-end; depreciation is a third event. Cash is an effect on the wider
company's balance, not an invented negative opening bank account. The wider
company supplies available cash at each settlement. If the lease is isolated
with no other cash flows, opening cash 242 suffices; that is a display assumption,
not a condition for recognizing a lease. Financing is outside this lease method.

| Date / event | Debit | Credit |
| --- | --- | --- |
| 2024-01-01 commencement | ROU equipment 210 | Lease liability 210 |
| 2024-12-31 interest | Interest expense 21 | Lease liability 21 |
| 2024-12-31 payment | Lease liability 121 | Cash 121 |
| 2024-12-31 depreciation | Depreciation expense 105 | Accumulated ROU depreciation 105 |
| 2025-12-31 interest | Interest expense 11 | Lease liability 11 |
| 2025-12-31 payment | Lease liability 121 | Cash 121 |
| 2025-12-31 depreciation | Depreciation expense 105 | Accumulated ROU depreciation 105 |
| 2025-12-31 return, after depreciation | Accumulated ROU depreciation 210 | ROU equipment cost 210 |

The final derecognition is the local cost/contra-account clearing for an expired
right with zero carrying amount; it does not add expense or extinguish an unpaid
obligation. The source does not prescribe these account labels.

| At year-end, before return clearing | Opening liability | Interest | Payment | Closing liability | ROU net | Year expense | Cumulative cash effect |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 210 | 21 | 121 | 110 | 105 | 126 | −121 |
| 2025 | 110 | 11 | 121 | 0 | 0 | 116 | −242 |

At 2024 year-end the lease alone changes assets by 105−121=−16, liabilities by
110, and equity through cumulative expense by −126: −16=110−126. Across both
years, total interest 32 plus depreciation 210 equals cash paid 242. These checks
do not determine whether the original control/rate facts were correct.

L16.47–49 requires ROU/liability identification and separate depreciation and
interest presentation. The 2024 payment comprises principal 100 and interest 21;
2025 comprises principal 110 and interest 11. Principal is financing (L16.50(a)).
For this nonfinancial company choose and consistently apply the financing
classification of interest paid permitted by the retained CF107.31–33. Thus all
121 per year is financing outflow, separately identifying interest. Initial 210
is noncash and excluded from cash flows under CF107.43–44. The liability
reconciliation under CF107.44A–44D records noncash addition 210, interest 21/11 and
cash 121/121. ROU net, additions, depreciation, interest, total lease cash outflow
and undiscounted future payments 121 at 2024 year-end are available for L16.53/58
note preparation; this is not the full qualitative or maturity-disclosure package.

## A genuine subsequent modification, L02

L02 branches from L01 after all 2024 events. Both parties agree on 1 January
2025 to extend use of the **same asset** by one year and replace the outstanding
121 with payments 144 on 31 December 2025 and 31 December 2026. There was no such
option in the original agreement. This is a modification, not a reassessment of
an existing option. No additional underlying asset is added, so L16.44's
separate-lease conditions are not met. At the effective agreement date a revised
implicit rate is unavailable; assume a supported revised IBR 20% (L16.45).

\[
L_{\rm revised}=144/1.2+144/1.2^2=120+100=220.
\]

The previous liability is 110, so increase liability and ROU cost by 110. The
remaining ROU carrying amount becomes 105+110=215. Under unchanged even usage and
zero residual value, depreciate 215 over the revised remaining two years, giving
107.5 each. There is no reduction in scope or termination gain; the corresponding
ROU adjustment follows L16.46(b), not the termination rule 46(a).

| Date / event | Debit | Credit |
| --- | --- | --- |
| 2025-01-01 modification | ROU equipment cost 110 | Lease liability 110 |
| 2025-12-31 interest | Interest expense 44 | Lease liability 44 |
| 2025-12-31 payment | Lease liability 144 | Cash 144 |
| 2025-12-31 depreciation | Depreciation expense 215/2 | Accumulated ROU depreciation 215/2 |
| 2026-12-31 interest | Interest expense 24 | Lease liability 24 |
| 2026-12-31 payment | Lease liability 144 | Cash 144 |
| 2026-12-31 depreciation | Depreciation expense 215/2 | Accumulated ROU depreciation 215/2 |
| 2026-12-31 return | Accumulated ROU depreciation 320 | ROU equipment cost 320 |

After modification, 2025 closing liability 120 and ROU 107.5 are different; both
reach zero in 2026. Full modified-life cash 409 equals ROU depreciation 320 plus
interest 89. The independent oracle compares the revised PV and full balances.
Using the old 10% rate would give 30240/121 instead of 220; it is wrong for this
declared modification. An index-only reset ordinarily uses the unchanged rate
under L16.42–43, except floating-interest-rate changes. A single universal
“reset discount rate” operation would therefore be wrong.

## Failures, alternatives and replay

L03 retains a specified asset but gives the supplier practical substitution
ability throughout use **and** an economic benefit from substitution. L16.B14
then defeats identified-asset status; no ROU/liability journal is proposed by
this method. A service-accounting route still needs its own facts and rules.
L04 retains the base facts but omits a determinable implicit rate and any
supported IBR. Return `MEASUREMENT_UNRESOLVED`; do not silently select 10%.
If only evidence about substantive substitution rights is hard to determine,
B19 specifically requires a presumption that the right is not substantive.
Record that source-based presumption and its evidence; do not substitute a
blanket missing-fact error for the rule, and still assess the other control facts.

Events bind book/entity, contract/version, accounting method/source versions,
effective date and expected opening balances. Identical receipt replay cannot
recognize a second asset or payment; conflicting payload for one business event
requires explicit correction. Missing funds is a liquidity/default event,
not permission to create financing. These requirements inherit the proposed
standards-mapping protocol in original repository path
`docs/design/proposal/methods/standards-mapping-v1.md`; no replay engine was tested.

The matched US operating/finance classification and ASBE source comparison is
in packet 2. It must retain the ten-year life/FV 1000/alternative-use facts. A label
translation cannot erase differences in expense pattern. This dossier has not
independently accepted the entire ASC or ASBE amendment chain.

## Evidence and remaining internal work

Selected primary paragraphs and cross-references were read. Exact fixture
arithmetic and journal consequences are checked by [arithmetic-check.py](arithmetic-check.py),
with [arithmetic-report.json](arithmetic-report.json). Source/arithmetic support,
semantic review, runtime conformance, professional judgment and reader acceptance
are separate statuses. Root cross-review and architecture integration remain
pending; professional review has not been commissioned.

Remaining P17 methods include actual contract/rate evidence, variable/indexed
payments, option reassessment, scope reductions, payment defaults, impairment,
restoration, foreign currency, sale-and-leaseback, nonlease allocation, transition,
lessor accounting, taxes and complete disclosures. [tax-dossier.md](tax-dossier.md)
adds one explicitly assumed lease-tax interaction; it cannot infer tax bases from
the lease journal. The useful next internal action is to encode the reviewed
method and failures against P16's final accounting/event contracts and match
them to a real contract/source case.
