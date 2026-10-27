# Conditional financial tax state, version 1

This is a pure synthetic successor of a completed native return/lease prefix.
It preserves the complete original report and conditional loss result. It is
not accepted as an unchanged native state, and it cannot execute later ordinary
return/lease events or roll a financial year forward. These remain explicit work.

## Exact inputs, state and effects

Accrual request: profile ConditionalSharedTaxAccrual/1, unique id, complete loss
request plus digest, and known/unknown recognition declaration with provenance.
Only an affirmative recognition declaration permits accrual. Recompute the loss
proposal; reject failed or unresolved calculation while preserving that result.
The native closing state must have zero current-tax expense for the interval;
its original tax_closed_until must equal the assessment start. This finite
profile has no opening current-tax payable and makes that scope explicit.

Create state ConditionalSharedTaxBook/1 with the loss request, recognition,
accrual id, original native closing digest, context, a complete 26-account
balance vector, last operation date, assessed_until and ordered settlements.
The additional account is income_tax_payable, classified separately from trade
payables. At the last included day debit current_tax and credit that payable
for the recomputed post-loss gross current tax. Zero is an explicit zero journal.
No cash moves. The loss proposal's closing state remains separate and exact.

The exclusive assessed_until cursor never overwrites the native tax_closed_until.
State date records the accrual/settlement day inside the same declared interval.
No events from a future financial year are allowed; a later extension must carry
financial state explicitly. DTA, DTL, deferred expense and all noncash nontax
balances are unchanged, including existing nonzero deferred balances.

Settlement request: profile ConditionalSharedTaxSettlement/1, complete state and
digest, unique event id, date, positive exact rational amount and explicit payment
assumption. Require an affirmative finding, date at or after state date and still
inside the native period, no identifier collision with the accrual/native/payment
history, enough outstanding payable and cash. Debit income_tax_payable and credit
cash. Preserve event identity and a separate operating cash flow labelled by the
explicit profile convention. No automatic full payment or refund.

Every validation recomputes the native/loss result and all tax effects from the
retained request. Full canonical equality checks the state and proposed result;
changed balances, history, identity, dates and Boolean/integer substitutions fail.
Apply is pure: no transaction, persistence or commitment is inferred. All source,
accounting, annual-readiness and native-financial-carry flags remain false.

## Financial reconciliation

For accrued C and explicitly paid S, current expense increases C, tax payable is
C-S, and cash decreases S. Relative to the original recorded report, profit and
equity decrease C, assets decrease S and liabilities increase C-S. Direct
operating cash decreases S. The indirect bridge changes by -C+(C-S)=-S through
current-tax expense and a separate payable movement; no trade payable is reused.
Independent rational checks enforce balance sheet, equity, direct and indirect
cash identities. Deferred balances and the original native close cursor remain
verbatim. These are recorded synthetic amounts, not admitted tax assessments.

## Audit and test contract

The plan audit passes after rejecting direct native-tax reuse: it assumes cash
settlement, removes deferred balances and uses incompatible closing dates.
The source lock preserves those implementations. Compare zero and positive
accrual, original loss generation, full/partial/fractional payment, insufficient
cash, overpayment, unknown/false recognition, duplicate ids, stale hashes,
invalid timing and tampered proposals. Exact arithmetic and preserved complete
results are criteria; check counts are descriptive. Record actual commands and
results. A failure triggers repair, not an unsupported claim of readiness.

## Pre-freeze review refinement

Replaying the same accrual request creates the same pure proposal, not another
posted liability. Duplicate identifiers inside the native/accrual/settlement
history are rejected. Global uniqueness across durable commits cannot be claimed
without a store and is not implemented here. A settlement may follow assessment
coverage only while still inside the original native financial period; its date
must never precede the last recorded tax operation. The profile does not accept
an already extended financial state as a fresh native opening.
