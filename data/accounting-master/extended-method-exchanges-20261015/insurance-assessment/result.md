# P4b insurance assessment exchange result

16 October 2026. **InsuranceAssessment/1 attempt-02 passes its finite
documentary criterion:** 2,705 independent checks, zero failures, nine methods,
46 cases, 1,570 records, 398 exchanges, 651 adverse challenges and 64
acknowledgement-loss worlds. Of the 46 cases, 22 resolve, ten publish an
explicitly unresolved assessment and fourteen refuse the method. These counts
describe the declared examples, not actuarial or accounting completeness.

Plan: `docs/plans/accounting-insurance-assessment-exchanges-20261015.md`.
Packet SHA256:
`2843f7e19eed935a9c29c83a559ca5af235b6eae3d8e91142675a4fd73da31f1`.
The focused diagnostic passed 92 schema/arithmetic checks across all 46 cases.
Attempt 01 is retained with its single invalid adverse fixture; the auditor
correctly accepted identical facts. Attempt 02 changes that fixture and adds
a wrong-transition-date recovery challenge, without relaxing the auditor.
Its build and audit took 0.2751 and 0.9009 seconds. All arithmetic is exact;
no GPU framework was imported and no stochastic experiment ran.

## Target and checked consequences

The claimed target is a reproducible assessment conditional on supplied facts
and retained historical sources. The computed quantity is the complete typed
result of the nine finite derivations in `mathematical_checks.py`, checked
against separately authored cases. The calculator imports neither the builder
nor fixture expectations. This establishes equality for the declared examples;
it does not establish valuation or calibration for an actual insurer.

Groupwise fair-value transition gives liabilities 110 and 120, aggregate 230,
and equity change −10; pooling would wrongly give 210. A recovery of 12 is
inside the measured held asset of 50. With the old held asset of 45, the combined
equity change is −5, with no cash or current profit. A prior recovery must match
context, transition date, covered loss, amount and measured asset.

The retained annual 3×3 no-tail triangle gives reserve 148 and zero dispersion;
the predictive law therefore remains unresolved. Exact finite laws distinguish
equal mean/variance from equal tails, and a shared fit across two cells gives
variance 56 rather than the independent-redraw value 38. A failed positive-mass
fit retains its mass and withholds full moments and tails. The backward-law
example gives posterior weights 3/7 and 4/7; reserve error is centered on reserve
20, giving error 10; one-year CDR is −10. Nonlinear stop-loss expectations range
from 0 to 10 across the stated joint-law family, without assigning a probability
over that family. Technical source pins and inspected sections are preserved in
`source-reading.md`, `source_policy.py` and the immutable input snapshots.

Publication preserves accounting heads, balances, journals and unrelated owners.
It publishes the complete result, receipt, identity entry and dependency closure.
Exact replay precedes freshness, changed content conflicts, and a frozen view
never bypasses head equality. Both lost-acknowledgement worlds have exact retry
outcomes. These are observable documentary worlds, not runtime durability tests.

Preservation passes for 204 original inputs/snapshots, 7,447 predecessor files,
the prior lock, HEAD and all 100 staged entries. The original requirements and
frozen manuscript are unchanged. The wider eight-row comparator is reconciled
in `../p4b-coverage-reconciliation.md`.

## Decision and uncertainty

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | What is not concluded |
|---|---|---|---|---|---|
| Accept the nine finite assessment methods | Complete independent result/source/protocol checks pass | No target, preservation or accounting-mutation veto fired | Shared source interpretation and supplied premises | Preserve both attempts; execute refreshed P3a2/P2, then P5 | Actual transition admission, calibrated reserves, current-law completeness, runtime correctness or full readiness |

| Inference status | Finding |
|---|---|
| Hard veto screen | Attempt 01 had one faulty adverse fixture; repaired in attempt 02. No remaining declared veto fires. |
| Statistically supported ranking | N/A: exact finite illustrations; no stochastic comparison. |
| Descriptive-only differences | Check counts and short wall times measure documentary execution, not method superiority. |
| Default-readiness | No method or training default is promoted. |
| Next evidence needed | Actual facts and source admission, a target-specific predictive protocol and downstream measurement evidence; runtime testing remains separate. |

Post-run red team: the strongest alternative explanation is a common error in
source interpretation despite independent arithmetic and separate expectations.
A source correction, accepted invalid exchange or finite-domain counterexample
would overturn the affected acceptance. Actual histories, calibrated process
laws, risk adjustment, broader triangle shapes/tails and empirical comparisons
remain unevaluated. These limit promotion; they do not veto the next internal
repair phase. Version 3.13 remains 340 pages and `not_ready`.
