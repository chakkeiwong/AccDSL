# Tie-aware refinement after the first finite search

The predeclared search examined 18,496 collection pairs. It found 10,636 with
a unique maximizing lower assignment and no insufficient selected upper bound
among those unique cases. There are 668 collection pairs where at least one
maximizing assignment has an insufficient upper sum, but zero where all lower
maximizers do. Preserve this negative/conditional result; do not claim a
tie-independent single-instance counterexample from it.

Next bounded diagnostic: in the same binary2x2 domain, seek a tied example whose
lower-score matrix is unchanged by swapping the two predicted tables, while
the exact/upper-optimal pairing changes. If found, two input orders produce
the same solver input but need different matchings to avoid an insufficient
upper sum. Any deterministic solver that receives only that lower-score matrix
must select the same matching for both inputs, so at least one order fails the
global-bound interpretation. This avoids choosing or running SciPy's tie rule.

Use a separate one-time refinement artifact. Cache at most 256 local pair
scores and stop at the first witness satisfying exact matrix equality under
column swap and strict upper/global-exact disagreement. If none is found in
18,496 cases, retain the generic interval-matrix proof and classify the
realizable-grid result as tie-dependent; do not invent a stronger conclusion.
No alphabet/shape/network/runtime budget expansion is authorised by this note.
