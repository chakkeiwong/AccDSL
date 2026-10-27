# Exact piecewise-affine families for typed monetary method expressions

24 October 2026. S2–S4; MC08/09/10/11/13/16/24/26/28/35.

Question: can an existing MethodMonetaryEffects/1 definition be evaluated as the
complete conditional family of its declared unknown inputs, including minimum
branches, without changing its typed formulas or treating one witness as the
family? Comparator: unchanged method_monetary_effects_v1.derive on exact known
assignments. Starting methods: existing selected settlement and sale definitions.

Skeptical audit passes for a restricted compiler. Current rational_solver_v1
supports conjunctions of linear rational constraints. Generic Boolean minimum
encoding expands sign partitions; explicit disjoint arms preserve the same
minimum with fewer declared branches. Products of two symbolic operands remain
unsupported. Do not replace unknown inputs by bound endpoints or solver-selected
values; only explicitly singleton closed domains may be substituted as constants.
Retain full domains and named proposed premises. No nonlinear solver migration.

Define PiecewiseMethodFamily/1 with complete method definition, all input domains,
explicit output measurement constraints, unresolved target obligations and explicit
branch cap, plus the existing budget. Output categories are calculations, aggregate
account postings and identified flows. Typed output domains must match exactly.
Missing premises remain unresolved. Every method input is bound exactly once,
including unmeasured ones. Preserve source references and type/context/scale.

Compilation supports ref, const, add, sub, fixed-factor mul and min only. At a
minimum, create left <= right and right < left branches; ties belong to left.
Nested minima preserve all complete combinations within the explicit cap. A cap
stop is unknown with the complete original definition and no completeness claim.
Report a deterministic branch manifest and per-branch budget disposition. Enforce
one global cell cap and elapsed-time budget across branch solves, not a fresh full
budget per arm. Existing formula/solver limits apply to every executed branch;
zero budgets mean unknown. Preserve unvisited branch descriptions.

Before solving, require symbolic identities for zero aggregate journal and cash
flow/journal agreement within every compiled arm. Do not add balancing equations
that silently exclude invalid input assignments. If the identities cannot be
established by the scoped exact simplifier, return unsupported rather than
inventing authority. This is deliberately conservative; broaden only under a
separate evidence contract. Native preconditions and memory effects remain
unresolved target dependencies, not implied by monetary balance.

Primary pass: fully fixed inputs match exact existing derived calculations,
journals and flows; variable-domain witnesses independently replay through the
unchanged evaluator and satisfy all domains/measurement/branch conditions; ties
and disjoint arms are checked; alternate valid witnesses are permitted. Expected
adverse cases: nonlinear unknown products, missing premise, unmatched dimensions,
unbalanced formula, wrong cash-flow identity, infeasible measured output, resource
stop, forged witness/core and altered method digest. No floating approximations.

Default/assumption audit: affine restriction and fixed domains are explicit model
choices, not facts about issuers. Min tie assignment is a representation convention
with identical numerical value. Existing exact solver is a comparator/reuse choice;
no speed superiority, statistical ranking or new default is claimed. All synthetic
values and domain assumptions have provenance. CPU-only deterministic tests.

Promotion veto: any lost family arm, fixed unknown, type erasure, unsupported
identity or replay mismatch. Repair triggers before recording. Nonlinear refusal
rejects that candidate fragment, not the research direction. Continuation veto is
missing/corrupt required comparator or unavailable exact solver. Keep evidence
separate from accounting/source/native admission.

Implement scripts/piecewise_method_family_v1.py with design, cases, tests and
recorded exact replay under data/accounting-master/piecewise-method-family-20261024/.
Write manifests, result and a next dependency plan; update active controls after
checked progress. No forecast experiment, production promotion or paid review.
