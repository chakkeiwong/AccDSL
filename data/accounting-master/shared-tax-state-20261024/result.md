# Conditional financial tax state — 24 October 2026

190 checks over 29 cases pass, preserving 21 files. All 13 focused and 17
regression test methods pass. The source/native incompatibility probe accepts
the baseline and rejects both an extra tax-payable account and the exclusive
close cursor under the original profile. That profile remains unchanged.

The successor explicitly represents a separate income-tax payable. With a
recomputed conditional amount of 1/2, accrual debits current tax and credits the
payable by 1/2 while cash stays 500. Paying 1/4 leaves cash 1999/4 and payable
1/4; a second payment clears the liability and leaves cash 999/2. Profit changes
at accrual, not again at payment. Four statement identities tie exactly.
Existing DTA10, DTL4 and deferred expense0 remain unchanged in that example.
The original mixed loss19 generates a separate loss lot with a zero tax journal.

Recognition and payment are explicit assumptions. Unknowns remain unresolved,
false findings unsupported; overpayment, invalid dates, duplicate history ids,
forged states and changed complete proposals are rejected. Insufficient cash
blocks settlement but does not invalidate an otherwise valid accrual. Every
result preserves the full conditional loss calculation and native report.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain bounded synthetic tax successor | Exact journals and four statement ties pass | No source, balance, identity or timing failure | Later native events, financial-year carry and actual tax recognition absent | Integrate exposition, refresh coverage, then design successor interoperability | Statutory assessment, refund, deferred recognition, durable posting or annual readiness |

The target is an explicit conditional financial tax state; the computed state
matches that target under the declared assumptions. It is deliberately a new
profile, not a state accepted by unchanged native return/lease operations.
Replaying an accrual request recomputes the same pure result; there is no global
commit uniqueness claim without persistence. S1–S5 partial, S6 held, S7 deferred.

Post-run red team: the strongest limitation is that consistent tax entries do
not establish financial-period carry or allow later native events. Those are
next engineering dependencies, not evidence against the finite accrual method.
A loss/native result mismatch or independently incorrect statement identity
would overturn this result. Actual accounting admission remains unevaluated.
