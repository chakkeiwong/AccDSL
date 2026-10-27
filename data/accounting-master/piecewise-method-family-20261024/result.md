# Exact conditional piecewise method families checked

24 October 2026. PiecewiseMethodFamily/1 retains the existing complete typed
monetary definition and all explicitly assumed input domains. It compiles fixed
factor arithmetic and disjoint minimum arms, checks journal/cash identities and
replays each feasible assignment through the unchanged exact method evaluator.
350 conformance checks, 56 targeted methods, 12 cases and 295 protected inputs
pass. Nineteen unit methods concern the new family; regression counts overlap.

The settlement example retains both branches of min(20,nrv) when nrv ranges from
5 to25. A tie belongs only to the left arm. Nested minima retain all four declared
combinations, including contradictory arms that the solver proves infeasible.
Fully fixed inputs reproduce the prior journal and cash flows. A variable sale
case reproduces proceeds7/3 and carrying cost2/3 exactly. Unknown quantities are
also supported when unit coefficients are explicitly fixed. A product of two
symbolic inputs remains unsupported; no domain endpoint is silently selected.

One global cell cap and elapsed budget schedule all branch solves. With one cell,
a discovered witness can establish conditional candidate existence while the
second arm remains unvisited; a first-arm contradiction cannot establish family
emptiness. Compilation cap or zero budgets remain unknown with the full original
definition retained. The wall-clock policy schedules bounded operations rather
than preempting Python compilation/replay at an exact instant. Per-solver timeout
and resource limits retain the original solver meaning.

Symbolic journal and cash-flow identities must simplify exactly before solving.
An unproved identity is unsupported; balancing equations are never introduced to
hide invalid arithmetic. Independent Fraction evaluation agrees with compiled
outputs. Altered methods, branch choices, measurements, outputs, completeness and
conflict labels reject. Alternate valid witnesses are accepted.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain exact restricted method-family reference | Known comparator, independent original-method replay and branch completeness checks pass | No tested type, lost-arm, identity, resource-status or replay veto | Native preconditions, state/memory and source authority remain separate | Audit exact prerequisite binding and admission obligations before composition | General nonlinear solver, executable native method, accounting eligibility or real-company history |

The strongest alternative explanation is that a balanced monetary family may
include quantities or interpretations prohibited by native prerequisites. That
limitation is explicit and motivates the next audit; it does not invalidate the
arithmetic family. Later composition must apply checked conditions, preserve
unknown evidence and avoid converting caller findings into truth. No statistical
ranking, default solver change or forecasting experiment occurred.

Version3.66 remains 451 pages, not_ready; this increment is not yet integrated.
S1–S5 partial; S6 held; S7 deferred. No whole MC requirement closes.
