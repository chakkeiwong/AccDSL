# Fixed-assignment and global assignment bounds

Let i index true tables and j predicted tables. For the same cell reward and
grid domain, let L_ij be the feasible heuristic score, O_ij the exact 2D-MSS
score and U_ij its relaxation upper bound. Assume finite nonnegative values
and L_ij <= O_ij <= U_ij for every pair. Let M range over the same feasible
one-to-one assignments. With nonnegative weights, allowing unmatched entries
is equivalent to maximizing over maximum-cardinality assignments after zero
padding. Define X(M) as the sum of X_ij on M, for X in {L,O,U}.

The inspected source chooses M_L in argmax L(M). It returns L(M_L) as the
heuristic aggregate and U(M_L) in its upper-bound field. Summation preserves
the pair inequalities, so

    L(M_L) <= O(M_L) <= U(M_L).

The exact globally optimized target is O* = max_M O(M). We also have

    L(M_L) <= O* <= U* = max_M U(M),

because L(M) <= O(M) <= U(M) holds separately for every feasible M and
maximization preserves each inequality. However, U(M_L) need not equal U*,
and O* <= U(M_L) does not follow. A simple interval matrix has

    L = [[1,0],[0,1]],  O = U = [[1,2],[2,1]].

The unique lower-score maximizer is the diagonal with returned upper 2,
whereas the off-diagonal exact optimum is 4. This proves the general implication
wrong, but does not alone prove that a GriTS pair-score matrix realizes it.

A realizable binary-cell example uses these two true and two predicted grids:

    T0 = [[a,a],[a,b]]    T1 = [[a,a],[b,b]]
    P0 = [[a,b],[b,a]]    P1 = [[b,b],[b,b]].

Each one-character cell uses the selected normalized LCS reward, hence exact
equality reward 0 or 1. Independent exhaustive row/column-substructure
enumeration and the local current-shortcut calculation give

    L = [[1,1],[2,2]],   O = U = [[2,1],[2,2]].

Both table assignments have lower sum 3. The diagonal has exact/upper sum 4,
and the off-diagonal has exact/upper sum 3. Now swap P0 and P1. The entire L
matrix remains identical, while O and U become [[1,2],[2,2]]. The globally
exact score remains 4, but the assignment with upper sum 3 changes sides.

Any deterministic assignment rule whose only input is L chooses the same
index assignment for both orders. If it chooses diagonal, the swapped order
returns upper 3; if it chooses off-diagonal, the original order returns upper
3. Thus at least one of these two valid table orders fails the interpretation
of the reported field as a global exact-assignment upper bound. This argument
does not require executing SciPy or guessing its tie policy. If selection is
not deterministic, the matrix still contains a maximizing choice that fails;
there is no guarantee for all tie resolutions from the pairwise inequalities.

The T0/P0 pair is the only nontight lower in this witness. Its selected row
and column paths are both diagonal, giving one equal cell, while an exhaustive
substructure has two. Neither current shortcut fires for that pair. T1/P0
and T1/P1 use the identity shortcut and are exact at two. The stored pair
records preserve all paths and relaxation values. All entries and sums are
small integers exactly representable in binary32, isolating this result from
the separately unresolved rounding question.

For these two four-cell tables per side, normalization by eight total slots
gives heuristic score 3/8, one selected-assignment upper 3/8 and global exact
score 1/2. This is an illustrative finite example, not a benchmark estimate.

A future adapter can preserve U(M_L) with an explicit fixed-assignment label.
If it requires a global upper bound, solve a second assignment problem on U
and return U*, preserving both matchings and the same feasible assignment set.
The proof above justifies that mathematical repair. Implementation must also
preserve the upper direction under numeric conversion/solver arithmetic;
nearest-rounded float32 values do not supply that proof by themselves.
No deployed implementation or source patch is made by this derivation.
