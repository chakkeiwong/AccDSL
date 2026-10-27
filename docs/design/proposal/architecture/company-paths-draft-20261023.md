# Consecutive company years and revised assumptions

CompanyPathInputsDraft/1 composes the existing annual company profile. The first
year reads the pinned 2024 historical opening. Subsequent years read the previous
complete conditional closing, including claims, inventory, assets and facility
state. Each year authors its own demand, price, purchases policy, cash decisions,
debt terms and event dates. The path is an assumption about possible operations,
not a newly observed company history.

Northstar begins 2026 with eight inventory units. Demand32 and target10 therefore
require34 purchased units costing170. Selling32 units at11 recognises352 of
revenue and160 of cost. The year collects55 of prior receivables and90% of new
sales, pays40 of prior payables and160 of current purchases, and pays payroll55.
The collection is explicitly dated before the supplier payment: reversing those
dates produces a funding failure. These dates are synthetic choices, not an
inferred payment policy.

Depreciation becomes15: the original cohorts contribute10,2,1, and the20-cost
asset acquired in2025 contributes2 after its2026 service date. New2026 capex10
enters service in2027. With legacy interest6 and the retained immediate20% tax
assumption,2026 pre-tax profit is116, profit92.8 and operating cash87.6. Investing
cash is−10 and financing cash−10, so cash increases67.6. All29 statement lines
are checked against independent arithmetic. A third authored year independently
checks further claim, inventory and asset continuity.

## Input, state and identity

The closed schema and example are in data/accounting-master/company-path-20261023/.
The initial_year is CompanyYearInputsDraft/1. Each continuation specifies its
annual choices and an opening_settlements array. That array names every prior
claim, including zero-balance claims, exactly once. Values are explicit amounts;
there is no implicit collect-all rule. Missing, duplicated or unknown claim IDs
reject. New claim and asset IDs cannot reuse retained identities.

Opening amounts, assets and facility drawings cannot be authored again in a
continuation. The interpreter carries them from the previous closing. It retains
each claim's lifetime recognised, settled and outstanding amounts; the annual
report separately measures this year's movements. A revision that increases the
first year's sales does not silently increase a fixed second-year collection.
The extra receivable remains outstanding unless that settlement is also revised.

The annual interpreter currently accepts its opening through a registry-shaped
argument. An internal adapter supplies only the fields that interpreter reads.
It is explicitly marked internal_adapter_only and is not a conforming exported
portable exchange, a new Facts record, or evidence of historical admission.
The public path result names the preceding conditional result and closing-memory
digest. Replacing this adapter with fully admitted portable inputs remains work.

Each annual result binds its authored definition, effective annual input, source,
opening and preceding result. Identity covers the complete report and economic
memory. Appending2027 preserves the2025 and2026 annual identities while changing
the overall path identity. The branch-bound report_view requires both the path
and its result, plus a requested period. It rejects changed reports, truncated
complete paths and an old suffix joined to a revised predecessor. These hashes
detect inconsistency; they are not authentication against an author who changes
and recomputes the entire record. Re-execution supplies the conformance check.

## Revision and incomplete years

revise creates a new conditional assumption branch and re-executes from the
original historical opening. Changing2026 price from11 to12 preserves2025's
result identity, increases2026 profit25.6 and cash22.4, and leaves an additional
3.2 receivable. Changing2025 price from10 to11 recomputes both years. With the
original explicit2026 settlement amounts, closing2026 cash increases21 and the
old sales claim retains3. No historical book is restated by this operation.

An incomplete year has no closing memory and cannot open another year. A failure
in2025 leaves2026 unexecuted. An unknown2026 price leaves2027 unexecuted. A
failed supplier payment preserves the last applied balances and unsettled claims;
its dated report prefix cannot stand for annual cash or profit. Prior complete
years remain queryable under the same branch identity.

The current path still inherits one operation of each kind per year, full-year
depreciation, homogeneous inventory and synthetic immediate positive-profit tax.
There is no generic repeated-invoice grammar, source/method admission, causal
information policy, persistent revision store or broader sector closure. The
new design is not yet integrated into manuscript Version3.51.
