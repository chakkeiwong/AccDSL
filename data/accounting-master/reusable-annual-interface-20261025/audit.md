# Reusable annual-interface audit — 25 October 2026

MC05/11/13/16/24/26/28/35; G2/G4; S2–S5. The active question is how a finite
company book repeats periods while preserving all liability and recognition
history. The current comparator is the complete checked period-vintage result.
Forecasting remains deferred and product implementation remains held.

## Inspected dependencies and concrete defects in direct reuse

| Inspected source | Checked behavior | Reuse decision |
| --- | --- | --- |
| following_period_tax_v1.py:25–53 | Account classes follow fixed nested results; carried_payments collapses all opening payable into one vintage and looks only for aggregate tax_payment | Wrong for several carried liabilities; replace caller/population plumbing, retain reconciliation kernels |
| following_tax_reassessment_v1.py:73–106 | Destructures old_v,current_v, sums one current vintage and returns exactly two rows | Not a reusable finite-population assessment; use an explicit current assessment id and preserve every other row |
| tax_vintage_continuation_v1.py:37–66 | Requires two vintages and equates all lifetime settlements with current cash | Wrong across boundaries; do not reuse this invariant |
| period_vintage_continuation_v1.py:34–68 | Separates immutable historical records from current-period openings/settlements | Correct for the checked opening; extend meaning to assessment additions before reuse |
| following_deferred_assessment_v1.py:31–131 | Fresh population, per-item bases and single-pool capacity are explicit, but population/report lookup traverses fixed predecessors | Retain arithmetic and fresh-state requirements through a separate explicit period-book view |
| second_assessed_carry_v1.py:70–110 | Checks aligned clocks, closes actual profit, archives recognition and opens per-vintage balances | Financial operation is reusable; predecessor shape and vintage validation are not |
| shared_tax_reassessment_v1.py:44–170 | assess/reconcile/replacement_losses accept explicit population and immutable opening loss state | Reuse these pure kernels with reviewed current-population construction |
| shared_tax_continuation_v1.py:159–205 | Full-state native/payment kernels preserve account and flow footprints | Reuse for selected events and explicit-allocated payment after validating allocations |
| module_invocation_v1.py:11–13,38–50 | Finite portable-input limits: 2,000,000 bytes, 100,000 nodes, depth64 | Retain as an engineering convenience limit; no arbitrary-size or unlimited-period claim |

The current invariants establish the finite examples, not general annual
composition. Another year-specific wrapper would not fix these defects. A
single ordered program over an explicit period book removes the positional
two-vintage dependency. No frozen predecessor will be refactored.

## Assumptions and evidence contract

| Choice | Provenance and reason | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| One entity/currency, 26 accounts | Existing checked reference book | Mistaken whole-company breadth | Reject context/account changes | Scoped baseline |
| One current cumulative assessment per period | Existing selected hypothetical model | Duplicate expense or overwritten carried tax | Three-liability append then same-id replacement | Reviewed proposed contract |
| Immutable period loss opening | Cumulative loss kernel | Double use or duplicated generation | Reassessment after use/expiry | Required accounting-model invariant |
| Explicit finite operation sequence | Existing replay and prefix behavior | Hidden automation or inherited decisions | Same program replay, stop at first refused operation | Engineering choice |
| No tax credits/refunds | Earlier no-credit model | Negative payable silently clipped | Replace below paid amount must refuse | Scoped limitation |
| Fresh deferred evidence | Existing measurement binding | Old capacity renewed silently | Any event after measurement invalidates its current-state binding | Required proposed dependency |
| Existing portable limits | Existing input validator | Recursion depth mistaken for economic horizon | Root-once import and flat ordered operation list | Convenience limit, not scale evidence |

Primary criteria are independent rational controls, complete account/journal/
cash/report linkage, exact historical preservation and correct refusal/prefix
behavior. Changed source hashes, wrong arithmetic, lost identities/history or
an implicit new assessment veto evidence and trigger repair. A failed fixture
vetoes that result, not continued contract repair. Counts and runtime explain
execution only. No statistical ranking, legal claim or forecast claim is made.

## Work sequence

1. Specify the common period book, liability records and operation signatures.
2. Implement a finite reference evaluator seeded once from the checked
   continuation: native events, payments, first current assessment and replacement.
   Check at least three liabilities and preservation of all earlier rows.
3. Add fresh deferred assessment and boundary operations to the same evaluator,
   then test multiple periods, loss expiry and recognition invalidation.
4. Record/replay results, integrate the settled contract, refresh complete
   coverage and continue the remaining simulator gaps. No new numbered caller.

Premortem: a balanced journal can hide an overwritten vintage, renewed capacity
or double-used loss. Independent per-identity histories and fresh-state bindings
must pass before any numerical result is accepted. The current audit passes
for this sequence; annual completion and human/domain acceptance remain open.
