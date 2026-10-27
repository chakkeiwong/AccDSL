# Identified operations within a company year

CompanyOperationsDraft/1 replaces the annual profile's one-purchase,
one-delivery and one-settlement restriction with an ordered list of identified
operations. Each purchase supplies units and a new payable identity; each
delivery supplies units, price, the control-transfer assumption and a new
receivable identity. Collections and payments explicitly allocate amounts to
existing claims. Payroll, plant additions and dividends may also repeat.
The company still uses the retained homogeneous inventory and annual accounting
methods; this change does not admit more complex recognition or measurement.

Lowering the old annual input derives operation payloads from its demand,
inventory policy, prices and settlement choices. It reads no projected journals.
All18 old interest/stress combinations reproduce every original journal, cash
prefix, closing account and income amount, together with all29 report lines
and gross cash flows. The schema, lowering function, reference interpreter,
examples and174-check evidence are under
data/accounting-master/company-operations-20261023/.

## Recognition and settlement

A purchase adds units and their homogeneous carrying cost, and recognises a
payable. A delivery consumes available units and recognises revenue and a
receivable only under the explicitly supplied control-transfer assumption.
Settlement changes cash and the identified claim; it does not recognise revenue
or inventory again. Every successful operation reconciles inventory units,
claim balances, plant cost and accumulated depreciation to the accounts.

An operation proposes its complete journal and economic changes before applying
either. If one allocation overpays its claim, the entire allocation list is
refused; earlier allocations within that operation do not settle. The same
atomic rule applies when cash or inventory is insufficient. Prior completed
operations remain in the result. Duplicate operation IDs, reused claim or asset
IDs, a settlement against the wrong ledger, and a settlement before recognition
are rejected.

The annual interpreter still has one bridge draw, interest settlement and
repayment, and one annual depreciation, legacy coupon, tax and close. Tax follows
the year's income-generating operations; close is last. These operations cannot
be repeated by duplicating a payload. More contracts, deferred taxes and interim
closing require separately specified methods.

## Splitting and timing

The checks split purchases, deliveries, collections, supplier payments, payroll,
capex and dividends into two identified operations at the original instants.
Four split shares, including zero-size endpoints, preserve total journals and
all statements under the selected linear methods. New asset pieces retain the
original service date and life; new claim pieces retain the allocated total.
This is an algebraic result for the declared methods, not a rule that arbitrary
aggregation, netting or date changes preserve accounting.

For equal instants, authored array order supplies precedence. With no bridge
borrowing, collection before supplier payment permits settlement; payment first
fails even if collection is listed at the same instant. Future same-instant cash
is not available before its operation executes.

Half of the baseline receipts is140. After bridge principal85.4, bridge interest
and payroll50, a small positive cash balance remains; delaying the other half
until after payroll therefore succeeds. An initial adverse expectation that this
would fail was wrong and is retained in the pre-repair evidence. Receiving40%
first yields112 instead. After repayment and the first payroll20, the remaining
payroll30 fails by23.4 plus bridge interest. The successful first payroll and
partial collections remain, while the failed payroll makes no posting.

Operation payloads also clarify revisions. Changing delivery price from10 to11
while keeping collection allocations fixed raises revenue30 and profit24,
increases receivables30, and reduces cash6 through tax. The earlier annual
authoring profile instead recomputes its90% collection rule and increases cash21.
Both computations are correct for their distinct authored instructions; a
future authoring policy must say which instruction a price revision changes.

## Missing inputs and reports

An unknown global opening or method-dependent input prevents execution. An
unknown event instant prevents a reliable schedule and supplies no dated prefix.
An unknown payload at a known instant stops at that operation, preserving earlier
completed operations. Unknown payroll after bridge repayment therefore retains
the preceding seven operations and zero outstanding bridge principal.

Complete reports derive all statements from the same operation result. Partial
reports expose the known opening and, where available, a dated applied prefix.
Annual cash and profit remain unresolved. Reports bind the input, source and
complete run digest; hashes do not authenticate a fabricated record whose author
recomputes every digest. Re-execution remains the semantic verification.

The profile is closed and typed but has no separate text frontend yet. Combining
these repeated operations with the checked multi-year path is the next task.
Portable source/method admission, policy information views, persistence and
broader sector methods remain unresolved. This increment is not yet integrated
into manuscript Version3.51.
