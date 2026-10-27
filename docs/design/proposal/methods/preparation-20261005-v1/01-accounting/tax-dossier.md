# Current and deferred tax from an explicit temporary difference

Tax expense, cash tax and deferred tax answer different questions. Current tax
measures the amount payable for taxable profit. Deferred tax records specified
future consequences of recovering assets or settling liabilities. This method
keeps those quantities separate and traces both back to an entity, tax authority,
law/rate version, tax base and recovery assumption. It prepares P17 under
MC13/MC15/MC16/MC19/MC20/MC28/MC29/MC35. All tax-law facts and rates below are
synthetic assumptions, not assertions about Australian or any other tax law.

## Authority and application

T112 is official AASB 112 compilation 7 dated 29 September 2023, registered
F2023C00930 on 24 October 2023, incorporating amendments through 14 September 2023.
The cover applies to annual periods beginning on/after 1 January 2023 and ending
on/after 30 September 2023. The comparison on physical page 5 identifies IAS 12
incorporation for for-profit Tier 1 reporting. We assume the same established
Australian for-profit Tier 1 FY 2024 reporter as the lease dossier, with no later
early adoption and no first-adoption transition. No full current IFRS claim is
made. Later schedule years hold this rule version fixed for consequences;
actual reporting after 2024 requires version/applicability revalidation.

T112.98J–98L applies the single-transaction amendment from 2023, including the
equal taxable/deductible temporary differences discussed below. T112.4A creates
the Pillar Two deferred-tax exception; the illustrative entity is assumed outside
Pillar Two and has no tax consolidation, overseas establishments, combinations,
goodwill, uncertain tax positions, tax credits, revaluation or OCI/equity tax
items. Those are exclusions from these examples, not exclusions from the mission.
[source-register.json](source-register.json) pins exact text/PDF/version/pages;
[source-inspection.md](source-inspection.md) distinguishes read rules from local
derivations. No jurisdiction tax statute was acquired or purportedly applied.

## T01 facts and recognition

On 1 January 2024 the entity buys and makes available equipment costing 1000, with
probable future economic benefits and reliably measured cost (P116.7/15).
It uses a cost model, five-year life, nil residual value and even consumption;
annual book depreciation is 200 (P116.48/50/55/60–62). No impairment, component
change, sale, foreign currency or capitalized output arises. Assumed tax law
allows depreciation 400 in 2024, 300 in 2025 and 100 in each of 2026–2028. Remaining
tax deductions are available against taxable recovery of the asset, and full
cost is deductible in total. Initial tax base and carrying amount both equal 1000,
so no temporary difference arises on purchase. The initial-recognition exemption
does not erase differences that originate later from depreciation.

Assume pretax book profit 500 per year **after** book depreciation and no other
book/tax difference, taxable profit restrictions or losses. Current tax rate is
enacted 25% throughout T01, and the same rate is expected on all reversal dates.
Tax is payable on 31 March following each year-end; no advance payments exist.
The tax method consumes the evidenced book profit 500 and asset history; it does
not manufacture the rest of the company's operating journals. The wider company
must provide the cash needed for settlements. The purchase and tax journals
below give every event in this method's declared boundary.

T112.7 defines the tax base from future deductions, not the closing book balance.
For year index t, carrying amount C_t=1000−200 t and tax base
B_t=1000−cumulative tax depreciation. T112.15/16/17(b) supports the taxable
temporary difference C_t−B_t where positive, and the deferred tax liability
DTL_t=(C_t−B_t)×25%. It is **not** multiplied by another probability or discounted
(T112.53). Under the stated absence of losses/permanent differences,

\[
\text{taxable profit}_t=500+200-\text{tax depreciation}_t,\qquad
\text{current tax}_t=25\%\times\text{taxable profit}_t.
\]

The current-tax formula is a local deduction for these facts, not a substitute
for tax-law computation. T112.12/46 governs recognition and measurement of the
unpaid obligation. Deferred expense is the period change in recognized DTL here;
general allocation must preserve its originating profit/OCI/equity treatment
(T112.58/60/61A), and cannot always post the change to profit.

## Full fixed-rate schedule and dated journals

| FY-end | Book carrying amount | Tax base | Taxable difference | Closing DTL | Taxable profit | Current tax | Deferred expense/(benefit) | Total tax expense |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-12-31 | 800 | 600 | 200 | 50 | 300 | 75 | 50 | 125 |
| 2025-12-31 | 600 | 300 | 300 | 75 | 400 | 100 | 25 | 125 |
| 2026-12-31 | 400 | 200 | 200 | 50 | 600 | 150 | −25 | 125 |
| 2027-12-31 | 200 | 100 | 100 | 25 | 600 | 150 | −25 | 125 |
| 2028-12-31 | 0 | 0 | 0 | 0 | 600 | 150 | −25 | 125 |

| Date / event | Debit | Credit |
| --- | --- | --- |
| 2024-01-01 purchase | Equipment 1000 | Cash 1000 |
| Each 31 December 2024–2028 depreciation | Depreciation expense 200 | Accumulated equipment depreciation 200 |
| 2024-12-31 current tax | Current tax expense 75 | Current tax payable 75 |
| 2024-12-31 deferred tax | Deferred tax expense 50 | DTL 50 |
| 2025-03-31 settlement | Current tax payable 75 | Cash 75 |
| 2025-12-31 current tax | Current tax expense 100 | Current tax payable 100 |
| 2025-12-31 deferred tax | Deferred tax expense 25 | DTL 25 |
| 2026-03-31 settlement | Current tax payable 100 | Cash 100 |
| 2026-12-31 current tax | Current tax expense 150 | Current tax payable 150 |
| 2026-12-31 reversal | DTL 25 | Deferred tax expense 25 |
| 2027-03-31 settlement | Current tax payable 150 | Cash 150 |
| 2027-12-31 current tax | Current tax expense 150 | Current tax payable 150 |
| 2027-12-31 reversal | DTL 25 | Deferred tax expense 25 |
| 2028-03-31 settlement | Current tax payable 150 | Cash 150 |
| 2028-12-31 current tax | Current tax expense 150 | Current tax payable 150 |
| 2028-12-31 reversal | DTL 25 | Deferred tax expense 25 |
| 2029-03-31 final settlement | Current tax payable 150 | Cash 150 |

The fixture expands every annual depreciation date separately. Each tax payment
clears a previously recognized liability and creates no new tax expense.
Current tax at each year-end remains unpaid until its next-March settlement;
no payment of DTL itself occurs. Across all five years, total current tax 625
equals total tax expense 625 and net deferred expense is zero. Annual after-tax
profit is 375; this is a consequence of the given pretax profit, not a whole-company
statement. A balance-only deferred-tax test misses incorrect current-tax timing.

T112.79–81 requires separate major tax-expense components and a tax-rate
reconciliation. Here 125=500×25% each year. Current and deferred balances cannot
be offset against one another. Deferred assets/liabilities require the conditions
in 74, and current assets/liabilities those in 71. Under CF107.35–36, assume taxes
relate to operating profit and cannot be specifically identified with investing
or financing transactions: actual next-year payments are operating cash outflows.
Deferred charges are noncash. The illustrative note retains tax base, expected
reversal, rate source/effective date, current/deferred movement and payment date.

## T02: an enacted rate change is a separate measurement event

Branch from T01, keeping 2024 unchanged. On 31 December 2025 assume a new 30% rate
is enacted for taxable profit from 1 January 2026 onward. The 2025 current rate
remains 25%, so 2025 current tax remains 100. All 300 of the closing taxable temporary
difference reverses after the new rate begins; T112.47/51 therefore yields
DTL=300×30%=90. Before remeasurement the ordinary 25% timing movement raises
DTL 50 to 75; the rate event adds 15. Post Dr deferred tax expense 15 / Cr DTL 15
dated 31 December 2025 after the ordinary 25 expense. Total 2025 deferred expense 40
and total tax expense 140 follow; applying 30% to 2025 taxable profit would be wrong.

| FY-end | Closing DTL | Current tax | Deferred expense/(benefit) | Total tax expense |
| --- | ---: | ---: | ---: | ---: |
| 2024 | 50 | 75 | 50 | 125 |
| 2025 | 90 | 100 | 40 | 140 |
| 2026 | 60 | 180 | −30 | 150 |
| 2027 | 30 | 180 | −30 | 150 |
| 2028 | 0 | 180 | −30 | 150 |

For 2026–2028 the yearly current entry is Dr current expense 180 / Cr payable 180;
the reversal is Dr DTL 30 / Cr deferred expense 30; the following 31 March pays 180.
The 2025 rate-change 15 is separately disclosed from timing origination 25 under
T112.80(c)/(d). It stays in profit because this case's originating transactions
are in profit; an OCI/equity origin would change allocation. If a government
merely proposes 30% without substantive enactment, T112.47–48 does not permit
this remeasurement. Whether an announcement is substantive enactment is a
jurisdiction-specific fact, not a synonym for “announced”.

## T03–T05: failure and alternative cases

T03 has unused tax loss 100, 25% rate, no carryback, no usable taxable temporary
differences, no convincing taxable-profit evidence and no available tax-planning
opportunity before expiry. T112.34–36 then supports **no recognized DTA**; retain
the 100 loss and unrecognized potential 25 with expiry/source facts. Do not call
25 an asset simply because multiplication succeeds. If the evidence is missing
rather than negatively established, return `RECOVERABILITY_UNRESOLVED` with no
automatic recognition and an internal investigation task. T112.37/56 requires
reassessment; this is not a permanent conclusion about future recoverability.

T04 proposes changing the closing DTL to 30% on an unsubstantiated rate announcement.
The rule does not qualify: preserve the proposal and enactment question, retain
the last supported measurement or mark the new view unresolved, and post no
automatic tax-rate journal. T05 omits tax law assigning the future deductions.
The accounting asset balance cannot identify its tax base. No deferred-tax
amount is admitted until the tax-base hypothesis is explicit and supported.

An initial asset purchase with zero tax deductions and no initial accounting or
tax profit effect can fall within T112.15(b)/22(c)'s exception; that is materially
different from T01's initial equal 1000 tax/book bases. A positive difference is
not sufficient by itself to recognize DTL. Business combinations, goodwill,
investments, uncertain tax positions and Pillar Two require their own methods.

## T06: the lease interaction after the single-transaction amendment

Use L01's ROU/liability 210 at 1 January 2024. Assume tax law permits deduction of
cash lease payments and assigns the relevant deductions to repayment of the
lease liability, not recovery of the ROU; taxable economic benefits arise from
using the right. Under this stated attribution, both initial tax bases are zero.
The 210 taxable ROU difference and 210 deductible liability difference are equal.
T112.22A says the initial-recognition exemption does not apply. Assume probable
sufficient future taxable profit from separately evidenced operations, with the
same entity/authority and compatible loss-use periods under 24/27A–29. Recognize
DTA 52.5 and DTL 52.5, not “no deferred tax”:

| Date / event | Debit | Credit |
| --- | --- | --- |
| 2024-01-01 recognition | Deferred tax asset 105/2 | Deferred tax liability 105/2 |
| 2024-12-31 reduce DTA 52.5 to 27.5 | Deferred tax expense 25 | Deferred tax asset 25 |
| 2024-12-31 reduce DTL 52.5 to 26.25 | Deferred tax liability 105/4 | Deferred tax expense 105/4 |
| 2025-12-31 reverse remaining DTA | Deferred tax expense 55/2 | Deferred tax asset 55/2 |
| 2025-12-31 reverse remaining DTL | Deferred tax liability 105/4 | Deferred tax expense 105/4 |

At 2024-end lease liability 110 gives DTA 27.5 and ROU 105 gives DTL 26.25. Net deferred
tax benefit 1.25 accompanies a book lease expense 126 versus tax deduction 121;
year 2 reverses that benefit. If the company has taxable profit before the lease
effect, the marginal current-tax reduction is 30.25 each year, giving total
marginal tax reductions 31.5 in 2024 and 29 in 2025, equal 25% of lease expense 126/116.
These are marginal tax consequences, not negative standalone tax payables.
Gross records remain even if presentation offset is permitted; same currency
or equal values alone cannot establish the right of setoff in T112.74.

The authoritative compilation's accompanying Example 8 (physical pages 50–51,
not itself a normative paragraph) explains this deduction-attribution pattern.
Its footnote 2 explicitly gives a competing tax-law attribution to the lease
asset, under which initial temporary differences do not arise. Therefore neither
“all leases create equal gross deferred tax” nor “equal balances need no deferred
tax” is a valid universal rule. Actual tax attribution and DTA recoverability
must be established. T06 does not carry the L02 modification into tax; that
interaction is a specific next case rather than an implicit extension.

## Evidence, decisions and remaining work

The arithmetic oracle uses exact fractions to reconstruct tax bases from
deductions, liabilities from their future reversals, and journals from dated
events. It checks T01/T02 current versus deferred timing and T06 gross balances;
negative controls expose a wrong sign, discounting and obsolete no-recognition
shortcut. Source inspection and arithmetic are bounded internal evidence;
semantic cross-review, final interface encoding, runtime conformance, actual
tax-law applicability, professional review and human comprehension retain their
separate status. No professional engagement is requested by this packet.

The next useful work is an actual entity/tax-authority case with law-derived
deductibility and enactment evidence, then loss expiry/recoverability, OCI/equity
allocation, revaluation/recovery-by-sale, modification, uncertain-tax treatment,
Pillar Two scope and multi-entity setoff. Packet 2 compares frameworks on matched
facts and reports authority gaps. Missing current ASC or official ASBE tax
amendments must not be filled by assuming equivalence.
