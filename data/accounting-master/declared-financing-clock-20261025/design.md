# Declared financing methods and a finite interest clock

MC02/06/11/13–18/23–28/32/34/35. DeclaredFinancingMethods/1 builds data-only
CompanyMethodRegistry/1 entries over the same book used by operating methods.
No frozen interpreter,program or frontend changes. Inputs: book,schemas,injective
role map,cursor/principal memory pointers,explicit fixed-rate policy and finite
contiguous intervals. Roles:cash,debt,interest,interest_payable,capital,retained,
dividend_payable. Cursor is a date;tracked debt is signed money and must equal
current debt. Initial cursor equals book date;initial debt is nonpositive.

Policy contains profile,convention,annual_rate,interest_cash_activity,provenance.
The convention is explicitly synthetic actual calendar days/365 simple interest,
not an instrument valuation or standards default. Annual rate is nonnegative and
fixed in hashed method definitions;rate has inverse-year dimension and the exact
calendar fraction has year dimension. Leap days count;denominator remains365.
Each interval is [start,end_exclusive),positive and contiguous,within the declared
book period. Accrual is dated end_exclusive minus one day (end-of-day convention).
The builder calculates the fraction from calendar dates;callers supply no years,
rate or interest amount. Runtime checks actual metadata date and current cursor,
then posts -debt*annual_rate*days/365 to interest expense/payable and sets cursor
to end_exclusive. Different valid calendars/policies have different definitions.

Debt issue/redemption occurs at beginning of its event date and requires cursor
==event date,so all preceding days have been accrued at the prior principal.
Both ledger debt and tracked debt change atomically. Several explicitly ordered
principal changes at the same boundary are supported. Accrual then uses the final
principal. Skipping,repeating,overlapping or backdating intervals fails cursor,
exact-date or chronology checks. Foreign principal movements fail tracked-debt
agreement. A report alone does not execute interest:generic reports remain
provisional;full interval coverage is checked separately from balanced statements.
A report cannot be described as interest-complete unless cursor==cutoff+1.

Other methods:interest payment,equity contribution using shares*price,dividend
declaration and dividend payment. All retain applicability known/false/unknown.
Amounts/shares/prices nonnegative;settlement cannot exceed the recorded obligation
or available cash. Dividend declaration has no invented legal/distributable-profit
rule:approved is only the supplied synthetic finding. All financial methods
require tracked debt agreement. Unrelated account balances and memory survive.
Principal and equity receipts,principal repayments and dividend payments are
financing cash. Interest payment uses the required explicit operating/financing
policy. Cash shortage retains primitive invalid result and separate funding
explanation;it cannot hide another failed condition. Equity reports need explicit
contribution/dividend explanations;neither retained earnings nor capital is profit.

Finite intervals are a bounded authoring choice,not a general calendar interpreter.
At most16 intervals and the existing registry/program/trace bounds apply. Full
fiscal closing remains provisional;carry must preserve debt/cursor or supply exact
explicit reset policy. Maturity,fees,compounding,valuation,contract/source authority,
tax,shares outstanding,complete notes and actual-company admission remain open.

Example:opening cash100,inventory20,equity120. Issue100 on2027-01-01 at7.3%.
Accrue90 days to2027-04-01:1.8. Redeem40 and issue20 at that boundary;principal80.
Accrue91 days to2027-07-01:1.456;184 days to2028-01-01:2.944. Total interest6.2.
Equity contribution10 shares*3=30;dividend declared12,paid5;interest paid4.
With the retained six-event operating cycle,closing cash208,AR15,inventory25,
debt80,interest payable2.2,supplier/payroll payables12,dividend payable7,
profit8.8 and equity146.8. Assets248=liabilities101.2+equity146.8.
Operating cash3,financing cash105 under the explicit operating-interest policy.

The initial no-successor assumption failed the aggregate structure diagnostic.
composition-repair.md specifies the required per-component bounded successor.
