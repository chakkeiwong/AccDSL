# Return components in the company statement language

This specification extends the design of company operations with return
rights and recovered-stock lots. It is conditional on supplied facts and a
selected historical accounting profile. The retained P/S CompanyComposition
case supplies the matched legal-book trace. Its owner, dates and accounting
premises remain unchanged. A later Northstar instantiation must supply its own
opening facts; neither renaming P nor importing P's resulting journals is an
admitted migration.

## Compatibility and state

CompanyOperationPathDraft/1 remains the legacy mode. With no extension chosen,
the existing parser, schema, exact arithmetic, account set, reports, failure
behavior and hashes remain authoritative. The richer profile requires a new
profile/version and explicitly selected methods. It cannot add fields to an
old closed record or redefine the meaning of its inventory_units field.

The company book owns cash, balances, dated journals and gross cash origins.
A module owns component memory and a documented allocation of those same
balances. Component cash/capital is never an extra asset or financing source.
Every state carries entity/book/branch, currency, period, information/source
references and a conditional-or-historical status. An event binds that state
and a caller-trusted method identity. All required inputs are validated before
publishing a proposed transition; the failing event leaves the preceding
state unchanged.

The return component records contract identity, original sold units and unit
cost, unit refund, estimated returned units/handling/deterioration, outstanding
refund liability and recovery asset, the rights-closure finding and source
references. Later changes of expectations or incomplete returns require their
own methods. The finite settlement below supports a completely closed return
window and explicitly classified selling handling costs.

Recovered inventory is a separate lot with id, owner, originating contract,
units, carrying amount, tax base, acquisition/settlement date and information
references. Existing homogeneous inventory retains its own units and unit
cost. The new book invariant is inventory = homogeneous_units × unit_cost +
sum(recovered_lot_carrying_amount). It is wrong to increase homogeneous units
by the returned quantity while keeping a different old unit cost. Selection
of a recovered lot is explicit; no FIFO, weighted average or tax allocation
is silently selected. The initial native subset sells a whole recovered lot.

Additional balance-sheet accounts are refund_liability, recovery_asset,
deferred_tax_asset and deferred_tax_liability. Additional temporary accounts
are selling_expense and deferred_tax_expense; the existing tax expense becomes
explicit current_tax_expense in the richer profile. Account-map aliases are
versioned and lossless, not inferred by name. Debit-positive sign convention
is retained. The account registry assigns every account to exactly one book
and financial-statement class, and every temporary account participates in
profit and the closing transfer to retained earnings.

## Settlement and sale

Let n be actual units returned, c their former unit cost, d deterioration per
unit, h handling per unit and u refund per unit. Let F and R be the opening
refund liability and recovery asset. For the retained, fully closed case,
cash refund is n u, handling cash is n h, and recovered lot carrying amount
V = min(n(c−d), supplied inventory NRV). The selling-cost treatment of h is a
required premise; capitalizable recovery work needs a different method.

The debit-positive journal is:

| Account | Change |
|---|---:|
| Cash | −n u−n h |
| Refund liability | +F |
| Recovery asset | −R |
| Recovered inventory | +V |
| Revenue | n u−F |
| Cost of sales | R−V |
| Selling expense | n h |

The sum is zero. Record separate gross operating payments n u and n h, both
referencing this event. Mark the return rights settled, preserve their history,
and create the recovered lot. A later whole-lot sale with proceeds P records
cash +P, revenue −P, inventory −V and cost of sales +V; its tax base is consumed
according to the supplied tax method. Unknown values or findings halt before
the affected event. Overselling, duplicate lot ids and a second settlement
are rejected. Inadequate cash is an economic funding failure, not permission
to create a financing entry.

For the retained return: n=2, c=12, d=2, h=4, u=20, F=40, R=16 and NRV=20.
Thus V=20, cash payment=48 and settlement book loss=4. Selling the recovered
lot later for 40 produces book profit 20. The exact journal and the retained
source after-state provide separate comparators for these deductions.

## Tax conditions and reconciliation

Tax facts are company- and jurisdiction-specific inputs. The matched example
assumes the original sale revenue and cost were already taxed/deducted;
refunds and handling are deductible on settlement; recovered inventory enters
tax stock at V; selling that stock later deducts its tax base. The rate is a
supplied 1/4 with the required enactment finding, and usable taxable profit
supports the opening deferred tax asset. These are retained synthetic facts,
not statements of actual law or defaults for another company.

The opening refund liability 40 has tax base zero, giving deductible temporary
difference 40 and DTA 10. The recovery asset 16 has tax base zero, giving
taxable temporary difference 16 and DTL 4. Both reverse on settlement. The
deferred tax expense is therefore 10−4=6. No offsetting is inferred merely
because both balances belong to the same group.

Settlement taxable profit is −n u−n h+V, here −28. Book profit from the journal
is F−n u−R+V−n h, here −4. Subtracting gives taxable-minus-book adjustment
R−F=−24. That adjustment belongs to the settlement event once. The later sale
has equal book and tax cost V, so it adds no temporary-difference adjustment.
The annual close must not apply −24 separately at every interim close.
Compute cumulative current tax from cumulative taxable income and subtract
current tax already recognized; carry the tax-event identifiers and tax-close
cutoff to make that dependence explicit.

P's retained first-half pretax income 56 yields taxable income 32 and current
tax 8, then deferred expense 6 and profit 42. Annual pretax 66 yields taxable
income 42 and annual current tax 10.5; the second-half increment is 2.5.
Annual after-tax profit is 49.5. Simply applying 25% to book profit at the
first close would compute current tax 14 instead of 8 and miss the separately
required deferred expense 6. Equal total tax in a special case would not
make that classification or cash amount correct.

A complete tax close requires the temporary-difference inventory, tax bases,
deduction/recognition timing, enacted rate, origin and DTA recovery findings.
Missing support makes the tax-dependent annual report unresolved, although
earlier valid journals remain a dated prefix. Loss/refund tax, other rates,
different recovery treatments and investment tax exceptions outside the
selected profile require another method; no balancing plug closes them.

## Reports and annual carry

Report inventory as the sum of all supported lots while preserving their
detail; show recovery assets and refund liabilities separately. Profit includes
selling expense and both current and deferred tax. Direct operating cash sums
the separate gross refund, handling, customer and tax cash events. The indirect
bridge includes profit, noncash depreciation and deferred-tax expense, and
changes in inventories, receivables, payables, recovery assets, refund
liabilities and other supported operating balances using their signed effects.
Do not both add deferred-tax expense and subtract DTA/DTL changes again.

For retained P, opening cash 500 and annual operating cash 101.5, investing
cash −20 and financing cash −90 give closing cash 491.5. Opening equity 622
plus profit 49.5 gives 671.5. The two legal entities remain separate: P's
internal receipts belong in P's legal cash flow but are eliminated in the
group report by the existing consolidation method. Reusing group totals as
a legal-book comparator would be wrong.

Only a complete annual close exports next-year opening memory. It carries
component/lot identities (including settled history needed to prevent repeats),
remaining units/carrying/tax bases, cash/claim/asset/facility controls, tax-event
history and unresolved obligations. Reset period income and cash-flow totals
without deleting lifetime event identities. Reconstructed conditional memory
is not a newly observed historical fact. Partial closes export no complete
opening state and preserve unresolved later years, matching legacy behavior.

## Implementation sequence and limits

First make the new account registry, module memory and lot-controlled inventory
explicit in a closed schema. Then add typed/text return-settlement and whole-lot
sale authoring, static reference/type checks and strict finding semantics.
Integrate proposed transitions into one shared chronological journal executor;
include tax origin, gross cash and complete-year checks before adding reporting
and carry. Compare the entire retained legal-book trace and every legacy
scenario, not only a cash total. Keep richer corporate/group/bank/insurance
requirements visible; one return method does not settle their interfaces.

This is a governing extension design and finite trace check. Native engine
integration, general lot sales, estimation updates, broader tax methods,
full portable normalized IR and independent/domain/human acceptance remain.
