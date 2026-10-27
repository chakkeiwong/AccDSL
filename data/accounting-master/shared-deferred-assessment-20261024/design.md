# Conditional shared deferred-tax assessment

ConditionalSharedDeferredAssessment/1 binds a complete current-tax reassessment
request and its digest, unique identity and explicit selection of
single_pool_gross_profit_loss_v1. Recompute the predecessor on its actual date.
Require complete scoped population, absence of unrepresented tax-only assets
and credits, supported allocation of recorded balances, and a supported common
entity/authority/reversal grouping. Unknown findings remain unresolved.

Populate every nondeferred asset/liability account, including tax payable, with
inventory split into other inventory and every retained lot, and leases split
into each right's asset/liability. Add every remaining loss lot, including zero
remaining quantities for identity preservation. No aggregate duplicates those
items. Each record has a declared base, rate, recognized deduction, previous
recorded DTA/DTL allocation, profit-or-loss route and explicit support findings.
Account and lease-right bases must match the already-bound prior declarations;
lot bases must match recorded component memory. Loss quantity is taken from the
exact loss ledger and cannot be altered or reused by this assessment.

For positive-magnitude carrying amount C and tax base B, signed taxable difference
is C-B for an asset and B-C for a liability. For a remaining tax loss L it is -L
under the explicit supplied recognition assumptions. A positive difference
produces gross DTL at the declared nonnegative rate. A negative difference permits
only the explicitly supplied recognized deduction U, with 0 <= U <= -difference;
DTA is rate times U. Unrecognized deductions remain reported. Zero or taxable
differences require U=0. All recognized deductions together cannot exceed the
single declared recovery capacity, in tax-base currency units, and no DTL balance
automatically enlarges that capacity. Rates and capacity have provenance.

All opening recorded allocations must sum exactly to the predecessor's DTA and
positive DTL balances. They are not a new measurement of the original opening.
If gross desired balances are A1,L1 and recorded balances A0,L0, journal changes
are DTA A1-A0, signed DTL -(L1-L0), and deferred expense (L1-L0)-(A1-A0).
Everything else, including cash, current expense/payable, tax premises, assessment
cursor, losses, components and previous histories, remains exact; append only the
new unique identity. Use the existing complete statement bridge and preserve all
unresolved annual/source findings. Pure apply compares the full recomputed result.

This profile supports conditional gross measurement and profit-or-loss movement
on the reassessed book. It does not admit actual law, supply future taxable income,
support offset or OCI/equity allocation, accept an annual close, persist a journal,
or automatically integrate the new result into the frozen carry profile. Those
extensions require successor contracts and their own evidence.
