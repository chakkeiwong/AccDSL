# Check conditional joint measurement constraints

24 October 2026. S2–S4; MC04/08/09/10/13/16/24/26/28.
Audit: data/accounting-master/joint-source-constraints-audit-20261024/review.md.

Implement a closed JointMeasurementConstraints/1 assessment over exact named
observations and linear equalities. Each observation declares its dimensional
context, exact interval or unresolved value, original evidence reference and
explicit interval premise. Each equation declares coefficients, exact right
side and explicit measurement-identity premise. Missing premise/interval yields
unresolved without invoking the solver. No authority is inferred from a premise.

Use existing Problem, Budget, q, domain_formula and solve. One observation identity
maps to one real variable across every equation. Require exact types/contexts
within each equation, canonical rational coefficients and complete identifiers.
No division, optimization, disjunction, integer variable, callback or arbitrary
solver expression is accepted. No implicit rounding conversion; use supplied
open/closed endpoints unchanged. Validate all data before any solve.

Primary criterion: hand-solvable compatible and contradictory systems, strict
endpoint infeasibility, repeated shared IDs and independent exact witness
verification. Test missing assumptions, malformed contexts/types, tampered witness,
zero/limited budgets and unsupported numeric forms. Existing P04 scoped tests are
the solver-regression comparator. Do not mutate or rerun historical record writers.

Defaults and bounds: explicit Budget fields; <=256 observations/equations,
<=4096 aggregate terms, <=1 MB canonical input, <=4096-bit rational coefficients,
and existing exact rational context/type validation. These are finite reference
limits, not economic defaults. Probe limits and all unknown categories. Only
exact feasible/infeasible/unknown/unsupported conditional measurement conclusions
are permitted; actual history, executable opening and admission flags stay false.

Artifacts: data/accounting-master/joint-measurement-constraints-20261024/ with
design, exact inputs/results, source identities, environment/budget, tests,
manifest/replay and decision. Solver witnesses/unsat cores may vary: replay must
verify mathematical result and witness validity, not assume byte-identical
model choice or timing. Distinguish this from deterministic input/definition hashes.

Then audit and bind selected retained source relations and their explicit
rounding/identity premises, preserving dashes and all omitted relation dispositions.
No source assumption is silently enabled. CPU-only deterministic mathematical
checks; no statistical ranking, forecast or production promotion. Version 3.62
remains not_ready; S1–S5 partial, S6 held, S7 deferred.
