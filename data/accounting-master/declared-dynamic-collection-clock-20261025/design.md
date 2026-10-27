# Declared receivable collection and assessment

The implementation uses CompanyBook/1, CompanyMethodRegistry/2 and
DeclaredCompanyProgram/2 unchanged. Claims have explicit stable IDs, due dates
and separately typed memory leaves for remaining principal, last assessed
principal and last assessed overdue amount. Opening claims must exactly sum to
the selected receivable account. Unassessed stored zero placeholders are exposed
as null observations, with status unassessed, never as measured zero delinquency.

Every payment selects a claim, requires a known nonnegative amount within that
claim's remaining balance, posts debit cash / credit receivables and updates only
its remaining principal. It preserves assessment memory. Every assessment has an
explicit contiguous half-open window and occurs on its last included date. Its
cursor must equal the window start. It copies remaining principal into dated
assessment memory; overdue principal is that amount only when the assessment
date is strictly later than the due date under the selected synthetic policy.
The journal and cash-flow lists are zero/empty. No impairment is calculated.

An assessment seals its date for later payments. Equal-day order before that
assessment remains caller order. Reports move the book date but do not move the
assessment cursor, refresh a dated observation or infer event completeness.
Carry preserves all protected claim and clock leaves, including stale or absent
assessment. A following-period assessment can continue an explicitly declared
window across the boundary; year-end itself does not invent an assessment.

The guarded runner regenerates the selected method definitions from the opening
book and exact policy. It classifies by definition hash, not registry key. A
foreign method cannot post to the receivable account or write protected leaves,
including offsetting gross postings and equal-value replacements. Carry resets
of protected leaves refuse. The existing pure engine is evaluated provisionally;
if a guard refuses a command, only the earlier verified prefix is returned. No
external writes occur. Whole-result canonical replay rejects altered state,
flags, observations and provenance, even if a caller recomputes its own hashes.

The bound is eight opening claims and sixteen windows, subject also to inherited
registry, command, byte and trace limits. These are engineering limits, not
financial facts. Arbitrary claim insertion, due-date revision, partial source
population, allowance measurement and tax remain separate dependencies.
The text path uses the existing command language and hashed imports; it does not
claim that this text authors the imported algorithms.

## Checks and execution

Focused command: python3 -B -m unittest discover -s tests -p test_declared_collection_clock_v1.py
Working directory: /home/chakwong/python/AccDSL. Deterministic Python, no GPU,
training or stochastic ranking. The evidence runner sets CUDA_VISIBLE_DEVICES=-1.

Two synthetic account charts begin with cash 100 and receivables 100 (claims 60
and 40), funded by capital 200. Collections 20 and 10 leave cash 130, receivables
70 and unchanged equity 200. January assessment: overdue 0/0. February:
40/0. December: 40/30. Carry and a further collection 40 leave cash 170,
receivables 30 and assessed overdue 0/30 on 31 January 2028. Exact full monetary
balances also match the retained native collect method under these premises.

Negative tests cover duplicate IDs, wrong dates, window overlap/gap/reversal,
unknown versus false inputs, overpayment, same-day sealing, stale observations,
carry resets, foreign gross postings and protected writes, registry aliases,
tampering and dependency changes. Passed test counts alone cannot promote the
candidate; named comparisons and exact refusal/state checks supply the evidence.
