# Repeated operations along a conditional company path

CompanyOperationPathDraft/1 joins the repeated-operation interpreter to the
consecutive-year design. Northstar's2025–2027 path now executes21 identified
operations per year. It retains14 claim identities by the third year, including
settled claims whose IDs cannot be reused, and carries each asset's cost,
accumulated depreciation and service date. All29 report lines in each year agree
with the checked annual path;164 conformance checks cover the joined semantics.

The first year supplies the pinned historical opening and its authored operation
list. Later years supply new operation lists and annual terms. They cannot
override carried claims, asset memory or facility drawings. Settlement payloads
must refer to the actual carried claim IDs: an aggregate receivable total cannot
substitute for a missing reference to one of the split invoices.

Annual result identities include authored inputs, the preceding closing memory,
every journal and report, and the current economic state. A report request names
the branch and period. Revised assumptions create another branch and replay from
the original opening. With fixed collection allocations, increasing2026 selling
price from11 to12 raises profit25.6 and tax6.4, reduces cash6.4, and leaves32 of
additional receivables. Those claims persist through2027 unless an explicit
later settlement is also changed. The2025 result remains unchanged. A revision
of2025 re-executes all three years; an old later result cannot be spliced into
the changed predecessor chain.

If an operation in2026 lacks a required amount, execution stops at that operation
and preserves its earlier journals. The2027 opening remains unavailable. A
payroll unknown after bridge repayment retains11 applied split operations;
annual profit remains unresolved. Moving supplier payments before collections
in2026 produces a cash failure and likewise blocks2027. Earlier complete years
remain available under the same path identity.

This draft reuses an explicitly internal adapter to pass a conditional closing
to the annual opening interface. That adapter is not a complete portable
CompanyState/Facts/View exchange. The path labels the opening conditional and
binds it to its predecessor, but full source and method admission remains the
next task. Each journal currently names a documentary method and input paths;
it does not yet reference a registered production method or a source-available
decision information set.

Typed schemas and reference semantics are available under
data/accounting-master/company-operation-path-20261023/. A separate textual
frontend, generic package admission, durable state/revision storage, arbitrary
facilities and broader group/bank/insurance methods remain open. The joined design
is not yet integrated into the Version3.51 manuscript, which remains not_ready.
