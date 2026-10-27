# Conditional joint measurement consistency

JointMeasurementConstraints/1 accepts named rational observations with exact full
types, source references, explicit intervals and proposed interval premises.
Equations carry an exact type, terms, right side and proposed identity premise.
The same observation ID names one variable in every equation. Repeated
coefficients combine exactly. All definitions and budgets are checked before a
missing interval/premise can return unresolved; malformed data is never hidden
behind an unknown result. Display-only remains the source baseline.

The adapter reuses rational_solver_v1.Problem, Budget, q, domain_formula and solve,
with no slots, choices, disjunctions, objective or probability law. The original
interval endpoint inclusions are passed unchanged, bypassing the unrelated
half-even disclosure helper. Feasible witnesses are evaluated independently with
Fraction against every original bound and uncombined equation. Infeasible cores
are rechecked by the existing solver; this is explicit solver evidence, not a
new independently checked proof certificate. Unknown remains a distinct outcome.

Finite implementation bounds: 256 observations/equations, 4096 terms, one million
canonical bytes, 4096-bit coefficients/scales, one cell and one assignment, no
slots; caller budgets cannot exceed 60 seconds total, 10 seconds per check or
10 million solver resource units. The reference uses 5 seconds/1 second/one
million resource units for small tests. Bounds prevent accidental unbounded
work; they are convenience limits and do not select an economic default.

The baseline x in [0,1] with either x=0 or x=1 is locally feasible. Their
conjunction is infeasible; this is the discriminating case missing from separate
interval checks. Strict bounds, exact fractions, cancellation, wrong witnesses,
unavailable assumptions and zero budgets have independent expected outcomes.
Only conditional measurement conclusions are made. There is no source authority,
actual history, executable opening, method execution or production promotion.
