# SequentialOutcomeQuery/1

The closed request contains profile,family,prefix,type,terms,operator,threshold.
family is the entire SequentialReturnStateFamily/1 definition. prefix is1 or2.
Each term names a distinct original account and a canonical rational,
dimensionless coefficient. All account types exactly match the query type,
including original event date, entity, legal book, currency dimensions and
scale. The rational threshold has that same query type. Operators are
eq,lt,le,gt,ge. No callback or arbitrary expression language is admitted.

This request asks a question; it introduces no new observation or source premise.
Compile the complete parent with all prefix constraints, branches, domains,
observations and target obligations. For each branch, divide the query and its
complement into disjoint elementary regions. Equality uses equal,less,greater;
each inequality uses itself and its exact opposite weak/strict inequality.
Each region is one convex cell. A shared max_cells and elapsed budget spans
every region. Solver timeout,resource and formula limits remain operative.
Zero resources or unvisited regions never establish emptiness.

Every feasible region retains a complete assignment, original full two-event
replay and a Fraction-computed query value. Every infeasible region retains a
named unsat core with a separate unsat recheck. Region truth is independently
checked against the original replayed account sum. The result verifier accepts
alternative valid witnesses and alternative valid cores while rejecting altered
state, predicate, value, identity or false proof. JSON round trips are tested.

Witnesses in both parts establish contingent. A satisfying witness and checked
empty complement establish necessary. A counterexample and checked empty
predicate establish impossible. Both parts empty yields empty_family, with
necessity not applicable. Otherwise the conclusion is unknown; separate fields
preserve any proved possibility or counterexample. A counterexample can refute
necessity before all regions are visited. No probability or numeric bound is
inferred from witnesses or counts.

Every premise and target obligation survives. Missing premises prevent query
solving. If target obligations remain, decided properties describe only the
relaxed candidate family; actual outcome remains unknown. All execution,
commit,method/source/accounting-admission flags stay false. Native unsupported,
unresolved or invalid conditions preserve their original consequences.

The first test run exposed a mistaken test expectation: the chosen supposed
forged core was itself unsatisfiable because terminal inventory is identically
60. Accepting that smaller valid proof was correct. The test now supplies only
the satisfiable nonnegative-proceeds constraint. No frozen implementation or
accepted result was changed to satisfy it.

Remaining: arbitrary histories, richer queries, numeric whole-family bounds,
actual source-state admission, broader modules and independent conformance.
