# The returned multi-table upper bound has fixed-assignment scope

20 October 2026. P15/P16/P17/P19; MC23, MC25–26, MC29–35.

The selected multi-table function maximizes the matrix of pairwise heuristic
lower scores, then sums the pair upper bounds on that same assignment. In
exact arithmetic, this bounds the exact score for the chosen assignment.
Interpreting it as an upper bound on the globally optimal exact table
assignment is wrong in general. The accompanying derivation gives the precise
inequalities and a realizable binary-table example. This does not invalidate
the pairwise GriTS relaxation bounds or claim the source explicitly proves a
global theorem.

For pair score matrices L <= O <= U and feasible assignments M, let M_L
maximize L(M). Then L(M_L) <= O(M_L) <= U(M_L), while the global optimum O*
satisfies L(M_L) <= O* <= max_M U(M). There is no general inequality
O* <= U(M_L). A proposed global-bound repair optimizes the upper matrix in a
separate assignment problem; a fixed-assignment interpretation needs only an
explicit label. Both require numerical qualifications before deployment.

The first predeclared search inspected all 18,496 canonical pairs of
two-table multisets drawn from sixteen binary 2x2 grids. There were 10,636
unique lower-score assignments, with no insufficient upper bound among them.
In 668 cases, at least one tied lower maximizer had an insufficient upper sum;
none failed for every maximizing assignment. This negative result was retained,
and the follow-up plan sought a witness independent of a specific tie rule.
These are finite-domain counts, not estimated frequencies in documents.

The refinement found such a two-order witness after 2,539 collection pairs:

    True T0: [[a,a],[a,b]]       True T1: [[a,a],[b,b]]
    Pred P0: [[a,b],[b,a]]       Pred P1: [[b,b],[b,b]]

The current-shortcut source model and exhaustive exact substructures yield

    L = [[1,1],[2,2]],   O = U = [[2,1],[2,2]].

Both assignments have lower sum 3. Their upper/exact sums are 4 and 3. Swapping
the two predicted tables leaves L unchanged and swaps the two upper/exact
sums. Any deterministic selection based only on L therefore makes the same
choice in both orders and returns an insufficient global upper sum in one
of them. No SciPy execution or tie-rule assumption is needed. In the failing
order, the returned upper sum is 3 while the global exact optimum is 4;
normalized by the eight slots per side, these are 3/8 and 1/2.

The local oracle includes both current early-exit shortcuts and the inspected
diagonal-first inner/outer DP tie order. A separate exhaustive substructure
enumerator verifies the four exact pair optima. The witness uses one-character
scalar-valid strings, so the normalized LCS reward is exactly 0 or 1. All
pair entries and sums are small integers exactly representable in the source's
float32 matrices. Thus rounding does not explain this witness. No acquired
module, NumPy, SciPy or pylcs executed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Restrict returned upper to fixed assignment | Exact source indexing plus derivation | Global interpretation fails on the two-order witness | Installed solver choice for either individual order | Preserve precise bound labels | Pairwise GriTS bounds are wrong |
| Retain a separate global-bound proposal | Monotonicity of assignment maximization on L/O/U | Mathematical derivation passes | Floating conversion, summation and solver certification | Inspect float32 numerical enclosure next | Production implementation repaired |
| Preserve the negative first search | Exact 18,496-case record | No unique-assignment violation found in that domain | Larger/other domains | Do not claim a unique binary2x2 witness | Universal validity from the negative subset |

Ten source anchors, 63 assertions and nine rejected altered claims bind the
finding. No new network acquisitions, historical experiments or model ranking
occurred. The result adds evidence without changing candidate 3.44, its 396
pages or not_ready status. All 53 obligations, six interactions and 46
operations remain; zero whole rows close. Independent/domain/human acceptance
and historical benchmark identity remain open.

The next source-only question is numerical: the caller converts lower and
upper matrices to float32 before selection and summation. Outside the exact
integer witness, nearest rounding does not by itself preserve a lower/upper
direction. A separate plan will test that issue with exact rational examples
and standard-library binary32 conversion, without running the dependency.

Execution: tfgpu Python3, -B, CUDA_VISIBLE_DEVICES=-1, standard library only.
One-time commands: verify.py --prepare, search.py, refine.py under its recorded
refinement plan, build_records.py, verify.py --check and --record. No-argument
verify.py is read-only replay. Completed construction stages must not repeat.

