# PiecewiseMethodFamily/1 exact reference

This family adds conditional unknown input domains to an unchanged
MethodMonetaryEffects/1 definition. It does not invoke native state transitions,
authorize journals, supply source facts or add a nonlinear solver.

Definition fields are exactly profile, method, selected_method_digest, domains,
measurements, obligations and branch_limit. method is the complete original typed
definition, with original types, dependencies, accounts, calculations, postings
and flows. Its canonical digest must equal selected_method_digest. domains maps
every declared input exactly once to interval, premise and source_ref. Intervals
have canonical rational lower/upper and Boolean inclusion flags, with nonempty
finite support. Premises have the existing id/status=proposed/meaning form or null.
Conflicting shared premise IDs reject. Null prevents solving.

Measurement rows have id, category, target, type and domain. category is
calculation, journal or flow; target is a calculation ID, aggregate account name
or flow ID. The complete type equals the original selected output type. Measurements
use the same interval/premise/source_ref form. No measurement is an authority or
balancing equation. obligations uses id, meaning and nonempty affects; unresolved
membership conditions keep target existence unknown. Collection identities are
unique. At most 256 inputs/measurements/obligations and 64 complete branches.

Closed singleton input domains substitute an exact constant in the compiler,
while their original constraints and source domains remain in the formula. Other
inputs remain shared variables. ref, const, add and sub are affine; mul requires
at most one syntactically symbolic operand. min produces ordered disjoint arms:
left <= right selects left, and right < left selects right. Ties belong to left.
Fixed operands simplify arithmetically. A multiplication of two symbolic operands
is unsupported even if additional constraints might later fix one. Algebraic
cancellation is not used to invent a known-value premise. All input dimensions
and declared dependencies are checked by the existing typed compiler first.

Each complete branch records its ordered decision paths, exact affine output
formulas, original input bounds, branch conditions and output measurement bounds.
The union is the complete supplied family; contradictory combinations may remain
as checked infeasible arms. No solver-selected parent assignment is substituted.
The branch cap prevents expansion beyond the caller's bound; exhaustion returns
unknown with the full original definition and no completed-partition claim.

Before solving any branch, symbolic simplification must establish zero aggregate
journal and exact equality of total cash flows with the cash-account journal.
An unproved identity is unsupported. No balancing constraint is added to filter
bad assignments into apparently valid journals. Independent point replay still
uses the unchanged original method evaluator and checks its returned journal,
flows, calculations, every input/measurement interval and each branch condition.

The existing budget fields remain explicit. max_slots is zero; max_cells is one
global branch-attempt cap (0..64); max_integer_assignments is 0 or 1. Each branch
is one linear conjunction and gets at most one cell. elapsed_ms is one global
deadline starting before compilation, with each branch receiving the remaining
time. This accounts for compilation and replay before scheduling the next solve;
bounded Python compilation/replay is not preempted at an exact wall-clock instant.
Solver timeout/resource limits apply per solver call, as in the original
solver; they are not represented as a global operation count. Formula-node limits
apply to each branch and a bounded total emitted-formula cap. A zero budget is
unknown. Status distinguishes witness found from full declared-search completion.

Results retain definition, digest, budget, premise/obligation inventory, complete
branch manifest when compiled, and per-arm feasible/infeasible/unknown/unvisited
dispositions. Any checked witness establishes conditional candidate existence;
all arms must be rechecked infeasible before conditional emptiness. Unresolved
target obligations prevent either from becoming unconditional target admission.
Semantic replay accepts alternate exact witnesses and rechecked conflict subsets;
generated status and manifests must match recomputation. Runtime and chosen
witness/core are diagnostic, not identity. Timing-sensitive unknown outcomes are
rechecked as unresolved, never silently promoted.

Constants and returned amounts stay reduced rational strings. Exact arithmetic
and input/output expression sizes reuse existing bounds. Finite rational inputs
are authored hypotheses; no integer lot interpretation is inferred. Existing
native preconditions, memory, legal facts and source/treatment decisions remain
separate dependencies for later composition.
