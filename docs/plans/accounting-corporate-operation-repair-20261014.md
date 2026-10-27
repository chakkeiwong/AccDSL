# P17-04: corporate operation audit and customer-contract repair

14 October 2026. MC02/04/07/13–16/19/20/28/30/32–35;
G2/G4/G7/G12/G15; E07. Baseline: Version 2.74, its preserved source tree,
`methods/corporate-methods-v1.md`, `corporate-extensions-v1.md`,
`standards-mapping-v1.md`, the common method boundary, and the retained
lease/tax dossiers. Output is a proposed method and documentary case, not a
runtime engine. Product implementation and the historical controller remain held.

## Skeptical audit and question

The existing methods already separate delivery, invoice/right and collection,
and include inventory, payroll, component depreciation, lease modification,
gross deferred tax, pensions, impairment, provisions and equity compensation.
Repeating their presence as a new completion would use the wrong baseline.
The concrete missing transitions selected first are an advance before an
unconditional invoice and a sale with a refund right. The current simple
revenue recurrence explicitly excludes them. An additive advance entry alone
can double-count a receivable when the later gross invoice arrives, and a
balanced gross sale can overstate revenue despite a known refund obligation.

Question: can those events be represented with their own state and source
conditions, through later billing, reporting-date remeasurement and settlement,
without duplicate receivables, premature revenue or netting away distinct
refund/recovery balances? Use the original scoped positive-increment method as
the comparator for what it supports, not as a universal accounting rule.

The retained AASB 15 compilation no. 8 is dated 31 December 2022, incorporates
amendments through 15 December 2022, and applies to annual periods beginning
on/after 1 January 2023 and before 1 July 2026. Use an explicitly synthetic
Australian for-profit 2024/2025 case. Inspect scope/contract eligibility,
control, price and reversal constraints, paragraphs 105–109, B20–B27 and the
compilation details. This is historical selected-rule support, not a current
ASC/ASBE comparison, a tax ruling or proof about Apple's contracts.

The audit passes for the bounded repair after these limits are recorded.
Before executing arithmetic, inspect the exact paragraphs and record the
complete residual operation matrix. Missing source applicability blocks its
method admission; it does not block independently supported methods.

## Evidence contract and intent ledger

Primary pass criterion: a reviewer can reconstruct the state, conditions,
event order, each proposed journal and resulting profit, balance sheet, cash
and equity effects. The advance allocation must be consumed once. Refund
liability and recovery asset must remain separately measured and presented.
Show a balanced but wrong gross-sale/advance candidate and reject it using the
recognition/scope condition, not the balance check.

Wrong source edition or transaction scope, premature recognition, duplicate
rights, unmatched journal/economic changes, wrong signs, omitted estimate
inputs or broken conservation veto the affected example and trigger repair.
Corrupted source/candidate or conflicting writer is a continuation veto for
dependent work. Missing private facts veto issuer admission, not the synthetic
method specification. Arithmetic, hashes and compilation are engineering
checks; they are not evidence of current global compliance or full MC15
completion. No stochastic comparison or ranking is involved.

The main mechanism is distinguishing paid consideration from created rights,
then retaining refund and recovery states after performance. Expected failure
is balancing the books while computing the wrong economic quantity. A failed
example triggers correction of event/state logic, not abandonment of the
company-history approach. Do not infer probabilities, an optimal estimator,
actual return rates, legal tax treatment or runtime conformance.

## Material choices and early checks

| Choice | Provenance / status | Risk and early diagnostic |
|---|---|---|
| Single fixed-price contract for advances | Simplest author hypothesis extending the existing case | Offsetting unrelated contracts or creating rights twice; check both orderings and applied-credit identity |
| Gross bill and applied advance separately recorded | Derived engineering choice | Treating already-paid consideration as a new receivable; check cash + AR + CA − CL equals earned revenue |
| Synthetic 100-price service, advance 30 | Teaching inputs, not empirical defaults | Numbers hide repeated credit use; include over-application rejection and final cash/rights check |
| 100 goods at price 10, cost 6; estimated returns 10 then 12 | Teaching measurements; B23 estimation/constraint conditions explicitly assumed | Expected-return count mistaken for source fact or calibrated probability; missing evidence makes measurement unresolved |
| No recovery costs or deterioration in base case | Explicit synthetic assumption, not zero default | Recovery asset overstated in real cases; include a separate cost/deterioration sensitivity and gross-presentation rejection |
| Pretax accounting slice | Scope choice | Implied zero actual tax; expose tax as an unresolved downstream input and do not call the slice a complete company statement |
| Fraction arithmetic, CPU Python | Deterministic convenience | Floating rounding or test mirroring; compare independent identities and intentionally wrong balanced alternatives |

## Work sequence and preserved evidence

1. Save the operation matrix under `data/accounting-master/p17-completion-20261014/P17-04/`:
   revenue/advances/returns, inventory/payables, payroll, PPE/modifications,
   impairment/provisions, leases, tax, closing and presentation. Link existing
   methods; give each remaining operation a concrete next action or blocker.
2. Record selected source paragraphs, hashes, application dates and amendment
   information; inspect their PDF pages where layout affects interpretation.
3. Specify advance/bill allocation and return recognition/remeasurement/
   settlement. Verify exact deterministic journals and independent balance,
   cash and income identities; include the adverse controls above.
4. Preserve 2.74, integrate a connected reader-facing subsection in a new
   candidate, and update the companion method record. Explain why the simple
   recurrence's scope had to widen before introducing extra state.
5. Verify preserved displays/citations, build and inspect changed/adjacent
   pages. Record result, actual command/environment/time, P18 disposition and
   remaining authority/fact/method limits. Then refresh the next ready
   operation or P17-05 rather than stopping at this unit boundary.

Ordinary finance/software readers should be able to explain why cash need not
be revenue, why a prepaid bill creates only a net new right, and why a sale
with returns has both a refund liability and a separate recovery asset. Apply
the already-read linear scholarly narrative skill and teaching contract.
Human comprehension remains pending during authorized provisional drafting.

All source/build/check files live in the P17-04 dossier. No new dependencies,
GPU work, external workers, paid review, publication or outreach are required.
