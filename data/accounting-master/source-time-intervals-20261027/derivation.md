# Why the temporal partitions cover the declared clock families

Let x_e be a clock in exact rational UTC seconds. Each input contributes a point
x_e=a, a half-open interval a<=x_e<b, or an unknown marker with only the supported
axis bounds. Chronology adds inequalities x_a<=x_b. Eligibility of revision r is
the conjunction of its actor, system and effective cutoff inequalities G_r.
These are supplied premises about time and access, not established source facts.

Represent x_v-x_u<=c by edge(u,v,c,false), and x_v-x_u<c by its strict variant.
A cycle whose sum has negative right-hand side, or zero right-hand side with
at least one strict edge, implies 0<0 or 0<=negative and is inconsistent. The
checker sums original edge coefficients and bounds itself. It does not trust
a solver status, rewritten inequality or a guessed epsilon.

The producer runs shortest-path relaxation with ordered weights (c,-1) for a
strict edge and (c,0) otherwise. Add and compare pairs lexicographically. A
non-strict/strict contradictory cycle is negative in this ordering. In the
absence of such a cycle, labels d_v=(a_v,b_v) obey each edge. Substituting
x_v=a_v+epsilon*b_v gives an exact rational witness. For a positive ordinary
slack s=c-(a_v-a_u), choose epsilon<=s/[2(|b_v-b_u|+1)]. For zero slack the
lexicographic inequality already gives b_v-b_u<=0 for non-strict edges and
<=-1 for strict edges. A positive epsilon no greater than all such bounds
therefore satisfies every original inequality, including strict ones.
Translation by x_zero fixes the origin without changing any difference. The
independent checker then tests the actual rational witness against every edge.

For ordered guards g1,...,gm, a revision is eligible on their conjunction.
Its complement is the disjoint union !g1, g1&&!g2, ..., g1&&...&&g(m-1)&&!gm.
The complement of x_v-x_u<=c is x_u-x_v<-c; the strict complement replaces <
with <=. Recursively applying this complete partition to every relevant
revision covers all admitted clock assignments. Empty cells carry verified
cycle contradictions. Nonempty cells carry rational witnesses, and every
eligibility bit is constant on the cell by construction. A finite list of
witnesses alone would not establish that coverage.

For each leaf the selected maximal revisions, unresolved ancestry, conflicts
and retractions follow from its constant eligibility pattern. Equal outcomes
are stored once while their separate temporal proofs remain present. This is
storage sharing of the reported view; it does not merge financial histories or
assign probabilities. A budget stop carries no complete-family assertion.

The separate two-clock oracle enumerates all endpoint equalities and enough
ordered positions inside each open endpoint gap to realize every weak ordering
of its variables. It compares256 selected zero-difference systems. That finite
check catches implementation mistakes in the producer; the checked partition
and exact inequalities supply the whole-domain argument for each saved request.

Limits: replacement-clock monotonicity, ancestor availability, declared public/
private routes, six-revision scope and bounded node budget are explicit profile
premises. Different document practices need a different premise set. No theorem
about actual disclosure times, legal availability, or all temporal logics follows.
