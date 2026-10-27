## Operating events

Every event uses the common method boundary the event-basis, authorization and commit contracts. The following schema fields
are required in addition to event identity/date. Each object identifier resolves
to its contract, context and admitted source or assumption. A purported cash
collection does not establish a sale; a purchase order does not establish receipt.

| Event and required fields | Recognition and state transition | Journal and adverse outcome |
| --- | --- | --- |
| deliver(contract, obligation, quantity, price_allocation, control_evidence) | Recognize only when the specified point-in-time or over-time rule is met; update fulfilled quantity and cumulative revenue | Release any related contract liability first; debit contract asset for earned consideration not yet unconditional; credit revenue. An unconditional receivable is created by the separate invoice/right event. Missing control/price constraints means unresolved, no guessed sale |
| invoice(contract, bill_id, unconditional_amount) | Create unconditional receivable; release related contract asset or create contract liability | Debit AR; credit CA then CL as appropriate. Missing unconditional-right evidence is unresolved |
| collect(receivable, settlement_id, amount) | Reduce open bill amount and increase actual cash; extra advances require their own rule | Debit cash, credit AR. Excess collection is outside the positive-bill method, not extra revenue |
| receive_goods(lot, quantity, unit_cost, ownership_evidence) | Add quantity/cost to admitted owned inventory and payable | Debit inventory, credit AP; consignment or unreceived order does not establish owned stock |
| consume_or_sell(lot_allocation, quantity, cost_formula) | Remove the specified available lot quantity and cost | Debit COGS or admitted production asset, credit inventory; overselling cannot silently create stock |
| pay_supplier(payable, settlement, amount) | Reduce payable and cash; financing, discounts and FX are separate events | Debit AP, credit cash. Insufficient available cash blocks this settlement and may trigger a separately modeled default |
| place_in_service(component, cost, residual, useful_life, method) | Admit PPE recognition/cost and available-use date; start depreciation then | Debit PPE, credit cash/AP; depreciation debit expense/eligible asset, credit accumulated depreciation |
| employee_service(employee_group, period, earned_pay, deductions) | Recognize earned compensation and withholding/employer obligations separately | Debit expense/eligible asset; credit pay and authority payables; settlement debits those payables. Unknown labor/tax law cannot default to zero |
| close(period, statement_maps, reconciliation) | Aggregate this path's revenue/expense, OCI and equity movements after all required accruals | No balancing plug. Unreconciled tax, cash, inventory or financing movement remains an explicit failure |

AASB 15 paragraphs 9, 22, 31, 35–43, 47–59, 73–86 and 105–108 provide the
selected revenue conditions; the retained compilation applies to the stated
for-profit FY2024 example. Variable consideration is estimated under a selected
method and admitted only subject to the significant-reversal constraint, not
recognized solely because its unconstrained expectation is positive. Principal
versus agent, returns, warranties, contract modifications and distinct bundles
require their own scoped decision records. If their facts are unresolved, retain
alternative eligible methods; do not borrow the simple delivery rule by label.

The following schedules make the distinction between performance and billing explicit. For one performance obligation with price 100, cumulative revenue 60,
unconditional bills 50 and collection 30, AR=20, CA=10, CL=0 and cash=30. Revenue
60 is represented by those three assets. Billing before performance changes
intermediate balances but not the final result. For bills 80 instead, AR=50,
CA=0, CL=20; net assets remain 60. Cumulative performed-service cost 40 then 70
posts 40 then 30, not 110. A downward revision follows the correction method and
keeps the old result tied to its original view.

For this simple contract, retain cumulative recognized revenue R, unconditional
billings B and collections C, with 0 ≤ C ≤ B. After each event, AR=B−C,
CA=max(R−B,0), CL=max(B−R,0), and cash received=C. This recurrence applies per
contract, with no impairment, variable consideration or unbilled prepayment;
it is not permission to offset unrelated contracts. For billing 80 before
delivery, debit AR 80/credit CL 80. Recognizing service 60 later debits CL 60 and
credits revenue60. Collecting30 debits cash 30/credits AR 30, leaving AR 50 and
CL 20, without a second receivable or an artificial contract asset. If service
comes first, recognize CA 60/revenue60, then bill AR 80 against CA 60 and CL 20.
Both orders end at the same state. Cash received before an unconditional bill
needs an explicit advance event that debits cash and credits CL and records
the advance applied to later billing; it cannot pass through collect(AR).

Inventory uses identified cost for non-interchangeable items or the admitted
cost formula for interchangeable items. AASB 102.9, 23, 25 and 28–34 support
lower of cost/net realizable value, relevant cost formulas and write-down/reversal
conditions. A method never chooses LIFO merely to fit a reported balance. FIFO
lots 10 units at 2 and 10 at 3, sale of 12 units: cost 26 and stock 8 units/cost
24. Weighted average gives cost 30 and stock 20. Under the same given selling
price 48, margin differs 22 versus 18. Both alternatives require their own
permitted policy, consistent application and evidence; matching total cash does
not remove the difference. NRV 16 for the remaining FIFO lot records expense 8,
inventory allowance 8; recovery to NRV 22 reverses 6, leaving allowance 2. Recovery
to 30 is capped at original cost 24. US LIFO remains a separately sourced question.

The retained AASB 116.7/15, 29–30 and 48–62 support cost and depreciation. Asset
100, residual 10, three-year even use gives 30 per full year. A year-two estimate
change after first-year depreciation to residual 10 and three remaining years
gives (70−10)/3=20 prospectively; an error in original cost is a correction, not
an estimate change. Component replacements derecognize the replaced component's
remaining amount before recognizing its replacement; no perpetual double asset.
Borrowing-cost capitalization, impairment, provisions, employee benefits and
share-based payment are specified as additional scoped methods below, not silently
assigned zero in real-company cases.

## Lease and tax integration

A lease connects asset use, a financing obligation and income tax. The following schedule extends the operating-company example by separating these three measurements. The retained lease and tax dossiers supply the dated provisions, modification case and assumptions. The official lease compilation is
dated December 2023 despite the older filename. Lease liability, ROU cost,
accumulated depreciation, remaining payments, rate version and option judgments
are separate state fields. Tax retains carrying amounts, legal tax bases,
reversal dates, enacted/substantively-enacted rate evidence, recovery support,
and original profit/OCI/equity allocation. Gross DTA/DTL are retained before any
permitted offset presentation. A liability schedule is not a tax-base schedule.

For the two annual 121 payments at 10%, initial liability and ROU are 210.
Year-one interest is 21, liability after payment 110, depreciation 105 and ROU
105. Year two interest is 11, and both balances finish at zero. A same-asset
modification just after year one creates two future payments 144 at revised
20%, PV 220, so liability increases 110 and ROU increases 110 to 215. A payment
index reset has different rate rules; it cannot reuse that modification blindly.

To demonstrate connection to company statements, assume a synthetic entity with
opening cash/equity 500, no other opening balances, and annual cash service
revenue 400 less cash operating costs 100, all recognized in their years. There
are no dividends, other assets, debt, losses or permanent differences. Add the
base lease above. Assumed tax law deducts cash lease payments against taxable
income, attributes those deductions to the lease liability, gives zero tax bases
to ROU/liability, and taxes profits at enacted 25%. Sufficient usable profits and
all recognition conditions for DTA are assumed. Tax is paid the following year.
No current-period tax payment is invented from tax expense.

At commencement debit DTA 52.5 and credit DTL 52.5 in addition to the lease
recognition. At year-one close DTA is 27.5 and DTL 26.25. The DTA reduction 25
is deferred expense; DTL reduction 26.25 is deferred benefit, net benefit 1.25.
Taxable profit is 300−121=179; current tax/payable 44.75. Pretax book profit is
300−105−21=174, total tax 43.5 and profit 130.5. At year two, deferred expense
1.25 combines with current tax 44.75 to give total tax 46 on pretax profit 184.

| Closing year | Cash | ROU | DTA | Lease liability | DTL | Tax payable | Equity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 679 | 105 | 27.5 | 110 | 26.25 | 44.75 | 630.5 |
| 2025 | 813.25 | 0 | 0 | 0 | 0 | 44.75 | 768.5 |

2024 assets 811.5 equal liabilities 181 plus equity 630.5; 2025 assets 813.25
equal liabilities 44.75 plus equity 768.5. Select financing classification for
lease interest under the retained AASB 107 regime. Direct operating cash is 300
then 255.25 after the first tax payment; financing lease cash is −121 each year;
no investing cash arises. Indirect operating cash in year one is profit 130.5
plus depreciation 105 plus interest 21 minus deferred benefit 1.25 plus unpaid
current tax 44.75 = 300. Year two gives profit 138 +105 +11 +1.25 =255.25.
The second tax payable settles next year. Zero OCI and no owner transactions
mean the equity change equals cumulative profit. This case tests gross tax,
cash timing and financial-statement coherence, not a real entity's tax law.

## Returning to the company forecast

The Northstar case remains the broader ordinary-company teaching
baseline: collections, purchases/payments, inventory, payroll, PPE, financing,
tax, statements, annual/interim and revision views are already specified. Its
2024 collection/purchase/payment solution is 245/155/145. The 2025 forecast in
the Northstar reference fixture opens with cash 74.6 and equity 90.6, spends20
on capital expenditure at period end, pays dividend8 and uses a base floating
rate 7%. Its simplified tax is settled in the year earned. The old manuscript's
alpha is the fixed-rate share; here x is the floating-rate share, so x=1−alpha.
For 2025 the same unknown floating fraction x in [0,1] appears in interest 5+2x, pretax profit
82−2x, tax 16.4−0.4x, profit 65.6−1.6x, OCF 48.6−1.6x, cash 95.2−1.6x,
equity 148.2−1.6x and assets 288.2−1.6x. AR 55, inventory 40, PPE98, AP40 and
debt 100 complete the balance sheet. All rows use the same x; there is no default
distribution on x. A 9% floating rate gives all-floating interest 9, profit 62.4,
cash 92, equity 145 and assets 285. Quarterly or annual cash bounds do not establish
daily payment solvency without event-date cash flows.

The lease/tax example extends the interaction evidence without changing the
original Northstar fixture or pretending that its teaching 20% tax formula is
an IAS 12 method. In a real-company package, each required method is admitted
separately and unsupported operations remain visible. The extended obligations
for pensions, impairment, provisions, valuation and share-based payment are in
the additional corporate methods that follow; omission from a finite company case never proves
the actual company has none.
