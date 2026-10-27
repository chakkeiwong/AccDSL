# A company year authored as operations

23 October 2026. CompanyYearInputsDraft/1 is a closed documentary profile for
Northstar. It addresses the imported-journal gap in FundedYearInputsDraft/1.
It imports a pinned historical opening and context, not a forecast projection.
It retains synthetic economic/accounting assumptions and does not define all
corporate or sector methods.

Opening cash is 74.6, receivables 35, inventory 4 units at 5, plant cost 122,
accumulated depreciation 31, payables 30 and legacy debt 100. Authored demand
30, price 10 and target stock 8 imply a purchase of 30+8-4=34 units costing
170. Delivery recognises revenue 300 and cost of sales 150 under the explicit
control-transfer assumption. It creates a customer claim 300. Collecting 90%
of that claim and 10 from opening receivables produces cash 280, leaving
receivables 55. Paying 160 against the new supplier claim leaves that claim
at 10 and opening payables at 30. Controls reconcile after each event.

The annual projection no longer supplies these postings. Each operation
derives quantities and accounts from the body and current conditional state.
A check removes all Projection records and obtains identical journals and
closing accounts. Expected results remain in a separate comparator.

## Input and authoring contract

The schema, typed/text examples, parser and reference semantics are under
data/accounting-master/company-inputs-20261023/. Objects are closed; all fields
are required. Text has one semicolon-terminated declaration per nonblank line.
Tokens use shlex POSIX quoting without comments, expansion or execution. Field
order is defined in authoring.py FIELDS. Scalar declarations are profile, name,
assumption, opening_digest, information and depreciation_method. Source,
context, period, inventory, trade, cash, debt, facility, loan and tax occur
once. Opening_claim, asset and event repeat with unique identities. Duplicate
singletons, extra tokens and missing declarations reject. Amounts are reduced
numerator/denominator strings; floats, unreduced fractions, negative inputs and
zero denominators reject. Explicit unknown amounts, control/eligibility facts
or event instants produce unresolved obligations.

Source SHA256 covers supplied bytes. Opening and context records also recompute
the existing schema-prefixed portable hash. A changed outer digest cannot hide
a corrupted opening. The period is the full calendar year immediately after
the historical opening period. Entity/book/currency agree. Source path is a
traceability label, not permission to read an arbitrary file: the evaluator
receives bytes explicitly. Archival exogenous stress does not imply a forecast
made before the sources became available.

The claimed closure starts at the checked historical opening plus authored
conditional inputs. Historical reconstruction and general source/method
admission remain separate. The synthetic method identifiers name these
documentary rules; they are not registered production methods.

## Operation rules

| Operation | Derived effect and restriction |
|---|---|
| Purchase | Demand plus target less opening units determines one purchase. Negative purchase is unsupported, not an automatic disposal. Homogeneous cost determines inventory/payable. |
| Delivery | Quantity reduces units and cost; consideration creates revenue and a claim. Unknown control is unresolved; false control refuses this method without posting the sale. |
| Settlement | Explicit allocations settle opening/new claims. No over-settlement or second revenue on collection. |
| Funding | Eligible capacity net of drawn/reserved capacity bounds the explicit draw. Unknown eligibility remains unresolved; known insufficient capacity produces failure with prior events retained. |
| Bridge interest/principal | Separate events preserve gross flows. Calendar-date interest runs from draw to repayment; interest settles on that repayment date. Fees and opening-facility accrual are unsupported. |
| Payroll/capex/dividend | Authored amounts drive named postings after cash checks. Dividend is an assumed distribution, not a legal distributability determination. |
| Depreciation | Cohorts 100/10, 10/5, 12/12 produce annual expense 13. Opening accumulated amounts 30,1,0 reconcile 31. New capex20 starts 2026-01-01 and contributes no2025 depreciation. Explicit zero residual; charge capped at remaining cost. |
| Legacy coupon | Principal times ((1-share) times fixed rate + share times imposed floating rate) times full-year coupon fraction. Share is not a probability. |
| Tax | Positive pre-tax profit times synthetic rate produces immediate expense/payment. Loss tax is unsupported; no deferred-tax/current-law admission follows. |
| Close | Zero temporary accounts against retained earnings; profit, equity, cash, claims, assets, inventory and indirect CFO reconcile. |

Depreciation admits full-year service or none. Midyear service is unsupported
until a fraction convention is specified. Annual depreciation, legacy coupon,
tax and close occur on the fiscal last date. Acquisition cannot follow the
declared in-service date. Exact UTC seconds are preserved. Array order supplies
explicit same-instant precedence and satisfies dependencies; lexical names do
not supply priority. All 14 kinds occur once: this is an annual single-cycle
example, not a repeated-invoice scheduler. Each event retains method, input
paths, journal, cash class, cash prefix and facility state. Runs bind source,
opening and the complete input body.

## Results and incomplete paths

Complete conditional results retain every journal, closing accounts, claim
rollforwards, units, asset memory, income, cash flows and equity. Results are
noncommitting: no durable store or recovery API is implemented. A refused cash
event mutates neither accounts nor economic state; earlier draw/payment events
remain. Unknown required input returns unresolved, not default or zero. An
unsupported method retains its reason and any already computed prefix.

Reporting must use the same body, opening, scenario meaning and period across
statements. A stopped path may expose its applied prefix as a dated snapshot,
but annual outputs remain unresolved. Known opening cash/equity remain
available. Prefix balances cannot be presented as the requested year end.

## Checked consequences and remaining design

All 18 inherited paths agree with independent traces. Price11 increases
revenue30, profit24, cash21 and ending receivables3: collections rise27 and
tax6. Demand31 increases purchases5, sales10, cost of sales5, profit4 and cash8
while target stock stays8. Delaying the unused12-cost cohort to2026 lowers
depreciation1, increases profit0.8 and increases cash tax0.2. These are exact
conditional consequences, not forecast performance.

Whole-company grammar, arbitrary operation multiplicity, partial/multiple
periods, revisions, information views, broad method admission, group/bank/
insurance semantics and persistence remain open. Version3.50 has not yet
integrated this successor.
