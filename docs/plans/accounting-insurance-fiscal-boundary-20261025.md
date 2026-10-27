# Preserve exact insurer journals across explicit fiscal boundaries

25 October 2026. S2-S5; MC02/06-13/16/19-22/24-28/30/32-35.
Baseline: accepted InsuranceLossBook/1 and frozen CompanyBookCarry/1 plus
DeclaredCompanyProgram/2. The first adapter intentionally uses one cumulative
interval. This work must not reinterpret its January 1 postings as December 31
postings or claim that the source establishes the host fiscal convention.

## Skeptical audit and research intent

Question: can an explicit calendar-year host program preserve the same six
journals and loss origins while resetting temporary balances and preserving
loss/progress memory across two year ends? A naive insertion of a carry fails:
the second-date methods expect cumulative income/expense balances. This is a
real precondition mismatch, not evidence against the native schedule. A new
wrapper must transform only the temporary-balance conditions and host period
observations, retaining native dates, monetary definitions and memory effects.

Candidate: InsuranceFiscalBook/1, a closed wrapper around the exact retained
request plus explicit period policy, retained account and per-leaf carry
policies. Compile calendar-year observations at 2025-12-31, 2026-12-31 and
2027-12-31; native events stay on 2026-01-01 and 2027-01-01. Begin with a
zero-profit 2025 carry, then carry the -5 profit in 2026 and the 10 profit in
2027. Reopen 2028 with cash105, liability0, loss component0 and cumulative
equity105 (plus any independently supplied equipment/equity complement).

These year-end observations are explicit hypothetical observations with event
completeness unknown. They do not assert that no omitted business occurred.
Calendar years are a tested fixture policy, not a default for real insurers.
The retained equity account must already be an equity account and must not be
an insurer role. Preserve every memory leaf; resetting loss component, step or
case identity would destroy continuation. Closing resets only income/expense
balances and records their signed sum in the selected retained account.

Primary criterion: all six gross journals, native dates, loss origins and
memory transitions equal the cumulative baseline; period profit is 0,-5,10,
operating payments 0,50,45, and final cash/liability/equity reconcile exactly.
Closing journals have no cash effect, temporary accounts reopen at zero,
unrelated state survives, and complete traces replay. Use two native cases,
two charts and complements present/absent. Compare full reports and archive
links, not merely final cash. Test an unsplit control to expose cumulative5.

Promotion and dependent-run vetoes: source/dependency/hash mismatch, native
date movement, dropped origins, policy not bound to the request, resets of
required memory, wrong or aliased retained account, stale conditions, missing
carry/report, forged result, duplicate command or invalid state. Implementation
failure triggers a bounded repair. A counterexample to the explicit fiscal
policy does not reject sector simulation; unsupported broader inputs stay out.
Runtime/test counts are explanatory only. No ranking or forecasting claim.

Assumption audit: calendar years and preserving all memory are explicit local
hypotheses; test date membership, zero-profit opening carry and year-two state.
The existing carry algebra and exact rational signs are reviewed baseline
mechanics, not new accounting authority. No rounding, midpoint selection,
inferred legal facts or new native measurements are introduced.

1. Lock dependencies and run the smallest naive-carry discriminator. Record
   precisely which stale temporary-balance condition stops continuation.
2. Implement a separate bounded compiler; change neither frozen engine nor
   accepted cumulative adapter. Recompute and verify the baseline first.
3. Rebase second-year temporary-balance pre/postconditions by the prior closing
   vector, hash each revised method, and record exact transformation deltas.
4. Run focused refusal/correspondence cases and existing carry/program/insurer
   regressions. Preserve complete records, source lock, actual manifest and
   exact read-only replay in insurance-fiscal-book-20261025.
5. Integrate only the accepted scope in a later bounded manuscript successor;
   refresh the master and reassess broader sector/reporting dependencies.

No whole requirement closes: retain53/6/46, S1-S5 partial, S6 held, S7/E3
deferred. No source applicability, complete fiscal accounts, durable posting or
general insurer admission is established. No workers, commits, installations,
GPU use, publication or outreach. An invalid harness or a genuinely unresolved
human choice blocks dependent work only; continue independent ready work.
