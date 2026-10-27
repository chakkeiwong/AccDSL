# GroupComponents/1 semantic contract

15 October 2026. A finite documentary specification, not a running accounting
service or a complete consolidated book. Addresses the P3c MC mapping in the
dedicated plan. Original requirements and frozen GroupForeignOperation/1 remain.

Canonical UTF-8 JSON has sorted keys, no duplicate keys, floats or nonfinite
values. Record digests are SHA256 of `accdsl.portable.v1/` plus the schema ID,
a NUL byte and canonical record bytes. Dependencies are exactly the sorted,
deduplicated typed references in the body. Rationals are reduced with positive
denominator. Schema locks bind all closed method input/result variants and
this contract. Opaque bytes, wrong digests and unresolved references refuse.

Every basis binds one context, historical information view, historical rules,
one supported method, admitted facts, frozen legal books and supplied control.
Evidence bytes contain those exact facts and legal balances. Evidence must be
available and ingested by its view, and measured by the decision date. Legal
books share the context, reporting date and branch, have distinct owners, and
never change. SourceSupport must bind the retained bytes and exact anchors.
MethodDefinition must carry the method's specific source set and this contract.

Reciprocal sides must be opposite roles on distinct legal books, each naming
the other, and agree on event/invoice/lot/currency/cutoff/transaction date.
Allocated invoice IDs must match, IDs are unique, and allocations cannot exceed
either side. Reporting-date control permits balance elimination; performance
eligibility uses the half-open transaction control interval. Residuals and FX
differences are preserved. The join result is an analysis with no posting.

Inventory elimination binds legal inventories, internal receivable/payable,
investment/capital and external-sale evidence. A release must reference the
prior resolved lot, its prior external sale, group state and later period;
the remaining group cost and opening elimination are carried forward once.
Inflation binds dated positive general indices, income events, reporting date,
hyperinflation admission and LC-to-USD presentation rate. Restatement precedes
translation. All monetary calculations use dated intervals. IFRIC7 binds the
acquisition/opening/closing dates and fixed tax base. Missing notional goodwill
admission leaves every dependent valuation null. Corporate impairment uses
unit tests before group tests and respects each floor. Tax differences must
equal carrying minus tax base (taxable) or its converse (deductible); the
required conjunctions use three-valued findings. These are supplied examples,
not actual valuation or law admission.

Exchangeability binds measurement/rate date, LC-to-USD direction and purpose.
The significance finding and rate objective are supplied. Other-purpose and
later rates are explanatory only. The later rate is excluded from admitted
measurement-date evidence and cannot determine the result. Initial transition
uses its annual opening date (not earlier than2025-01-01), exact direction and
destination: USD-to-LC payable/opening retained, or LC-to-USD foreign-operation/
accumulated translation. No comparative restatement or period profit/OCI.

`group.component.commit@1` admits only an authorized proposal belonging to the
isolated group component owner. A resolved result advances its state sequence
by one, including a resolved analysis with no journal. An unresolved result
has no journal and no state change. Debit-positive adjustment lines sum to
zero; these are group worksheet adjustments only. Publication atomically adds
the result, receipt, response, full dependency closure and immutable request
decision to that owner's ledger. Only a nonempty resolved journal appends a
posting. All legal and unrelated owners remain byte-identical. The state is
the most recent component result, not a consolidated trial balance.

`group.component.report@1` requires a resolved result in the selected state
and reproduces its period/cumulative values with component-only scope and
explicit uncomputed tax or supplied conditional-tax status. It changes no head
or journal. No report is synthesized for an unresolved initial state.

Request identity is workspace plus request ID. After structural decoding,
exact stored requests replay their original result/payload/receipt and closure
before checking current view/head. Reused identity with different bytes
conflicts. New identities require the requested current view and exact head.
Refusals publish no candidate and change no world. Both acknowledgement-loss
worlds are explicit: no durable commit, or full durable commit before timeout.
The transport observation says unknown in both. Exact retry either commits
once or replays; a timeout never proves non-commit. Partial closure, changed
legal books, missing identity decisions or journal-only publication are invalid.

All examples preserve engineering, conditional accounting arithmetic and
scientific evidence statuses separately. No current-law compliance, full
company representation, runtime durability, empirical validation, migration
compatibility or human acceptance follows from these documentary checks.
