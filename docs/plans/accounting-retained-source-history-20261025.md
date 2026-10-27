# Bind retained disclosure measurements to conditional typed histories

25 October 2026. MC01, MC04, MC05, MC09, MC10, MC24, MC28, MC34.
S2-S4 bounded design/conformance work. S7/E3 remains deferred.

## Question and skeptical audit

Can an explicitly supplied typed history be constrained by the retained real
annual/interim cash observations without erasing source context, converting
net movement to identified transactions, or admitting the history as actual?
The comparator is the unchanged RetainedTemporalSourceRelations/1 plus
TypedHistoryMeasurementAttachment/1. Neither alone binds a complete retained
source report to supplied history definitions and replayed mapping results.

The plan passes only as a source-bound conditional interface and adversarial
case. It does not generate transactions from disclosures. The earlier idea of
automatically decomposing net movement into arbitrary bounded receipts and
payments is rejected: those bounds have no source justification. Callers
must supply complete histories, premises, bounds and exact mappings.
Constructed histories in tests demonstrate underidentification relative to
the selected cash observations, not compatibility with the whole filing.

## Evidence contract and assumptions

Baseline: preserved 256-observation/143-relation statement report; six selected
cash observations and two source-bound temporal bridges; unchanged typed
history solver, exact rational replay and dimensional/context checks.
Pass: recompute and retain the full source report, preserve distinct annual
and interim basis contexts, bind every selected observation exactly once,
check both full parent constraint systems, and replay alternate witnesses.
Reject tampered sources, bindings, units, contexts, missing observations,
unknown fields and forged admission. Missing mapping premises must remain
unresolved; infeasible and exhausted-budget results remain distinct.

Promotion vetoes: changed frozen evidence, incomplete parent verification,
implicit context conversion, dropped source dispositions, or admitted actual
history from numerical feasibility. These invalidate this interface and
trigger repair. A conflicting supplied history rejects that candidate only.
Explanatory diagnostics: witness values, chosen solver witnesses and timings.
No ranking, probability, full-source consistency, legal-book identity, actual
transaction population, cash classification or accounting compliance follows.

| Choice | Provenance and purpose | Failure mode / early check | Status |
|---|---|---|---|
| Annual and interim separately | Retained source basis contexts differ | Same-date silent merge; reject context mismatch | Reviewed source constraint |
| Proposed nearest-million intervals | Existing optional source hypothesis | False issuer rounding assertion; no hypothesis means unresolved | Explicit hypothesis only |
| Supplied event dates/bounds/chart | Authored counterexample, never extracted facts | Arbitrary completion; preserve premises and unresolved source obligations | Constructed test assumptions |
| Existing bounded exact rational solver | Current attachment comparator | Budget exhaustion mistaken for infeasibility; zero-budget test | Engineering baseline |
| Full report plus selected constraints | Existing source interface | Selected feasibility mistaken for whole report; explicit unselected dispositions | Bounded interface |

Research intent: preserve the question above separately from implementation.
Expected failure: independently feasible parents can be inconsistent together.
Repair trigger: any mismatch between independent rational replay and compiled
constraints. Continuation veto: corrupted sources or inability to verify either
parent; candidate rejection alone does not stop design work.

## Work and validation

1. Add an optional source-to-history adapter with closed input/output schemas.
   It accepts a retained source request, one supplied typed history per selected
   bridge and explicit field bindings; it does not infer a legal entity/book.
2. Build annual and interim counterexamples, including different gross event
   amounts for the same observed endpoints, partial mappings, missing premises,
   incompatible contexts, joint infeasibility and limited budgets.
3. Run focused unittest cases and unchanged source/history regressions with
   the existing Python 3.11.15 / Z3 4.16.0 environment; no installation or GPU use. Record exact commands,
   versions, input hashes, complete exchanges and semantic replay results.
4. Record decision and remaining source-admission dependencies, refresh master
   controls, then prepare a separate manuscript integration only after checks.

Artifacts: data/accounting-master/retained-source-history-20261025/.
No whole requirement closes. Preserve Version4.32 until a verified successor.

Recovery environment correction before tests: .venv/bin/python is absent.
python3 resolves to /home/chakwong/miniconda3/envs/tfgpu/bin/python3 and imports
Z3 4.16.0 successfully. Only standard Python and Z3 are used; hide GPUs before
the test process and do not import TensorFlow. The source parent receives an
explicit zero-slot measurement budget; history parents retain their event budget.

The constructed examples supply hypothetical cash, debt and capital openings,
borrowing and repayment events, dates and finite amount bounds. These are
counterexamples for selected cash observations, not disclosed debt/equity facts
or histories consistent with every filing observation. Full reports remain
retained so this distinction can be inspected.
