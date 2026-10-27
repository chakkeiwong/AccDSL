# Complete-family finite outcome ranges checked

24 October 2026. The recovered verification completed successfully: 676 checks,
138 targeted regression methods, 13 retained cases and 563 protected inputs.
Nineteen focused range methods extend the existing overlapping suite. These are
deterministic engineering checks, not independent statistical replications.

SequentialOutcomeRange/1 preserves every constraint of the complete restricted
settlement-sale family. Its intermediate inventory envelope is [65,80] and its
terminal inventory is {60}. Intermediate cumulative profit is [-19,-4]; terminal
profit is {16} for proceeds40, before tax closing. Allowing proceeds in [0,100]
gives terminal profit [-24,76]. Strict input endpoints produce an unattained
intermediate inventory envelope (65,80); they do not create executable endpoint
states. The unfunded family is empty and supplies no numeric range.

Every certified finite endpoint has an exact closure-feasibility, no-better and
original-attainment check. Attained endpoints replay both original native
transitions and independently evaluate the account sum with Fraction arithmetic.
Full branch coverage is necessary for a global envelope. Partial budgets retain
local evidence without inventing global bounds. An envelope can contain holes;
it is not a claim that every interior value is feasible.

The pre-recording test correction distinguishes branches supporting a bound
from branches attaining it: both branches have inventory supremum80, but only
the high-carrying branch reaches80. The original numeric bounds and attainment
calculation were correct. The result now reports both branch sets explicitly.
Alternative valid endpoint witnesses and infeasibility cores survive JSON
round-trip checking. Altered values, states, proofs and coverage reject.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain finite range reference | Exact endpoint proofs, complete original replay and hand-derived totals pass | No lost parent constraint, false global bound or frozen-input change found | General nonlinear/unbounded families and arbitrary sequences | Integrate predicates and ranges into the governing manuscript | Whole simulator completeness, actual state or forecast accuracy |
| Preserve unknown and empty results | Global bounds require complete branch certification; empty family has none | Tight and zero budgets cannot manufacture certainty | Near-deadline scheduling can change coverage | Keep explicit resource limits and saved replay | Hard real-time preemption or an interior feasible-set description |

Recovery audit: the baseline remains the original complete native transitions,
not the preceding wrapper. Test counts are explanatory; endpoint correctness and
unchanged parent constraints are the criteria. Explicit finite affine scope,
unknown resource status and frozen-input hashes supply the relevant limits and
stop conditions. No material new scientific default or environment mismatch was
introduced by recovery. The check command was
python3 -B data/accounting-master/sequential-outcome-range-20261024/verify.py --check;
its elapsed time was 115.007 seconds. Recording and saved replay are separate
required steps, with their actual observations retained in manifest.json and
replay-observation.json.

The strongest remaining limitation is shared solver machinery: independent
Fraction replay checks witness values, while symbolic completeness relies on
the inspected exact solver and restricted affine compiler. A counterexample
passing the original constraints outside a certified endpoint would overturn
the result and trigger implementation repair. No independent implementation or
domain acceptance is established.

Version3.69 remains457 pages, not_ready. Both query operations await integration.
S1-S5 remain partial, S6 held, S7 deferred; no whole MC requirement closes.
Next: docs/plans/accounting-outcome-query-integration-20261024.md.
