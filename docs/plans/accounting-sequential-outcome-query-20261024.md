# Query possible and necessary financial outcomes of a complete native sequence

24 October 2026. S2–S4; MC08/09/10/11/16/18/24/26/28/35;
G1/G2/G3/G16; P17-08.01/.02/.03/.04/.06.

Question: which same-prefix account predicates are possible, impossible or
necessary in the complete declared settlement–sale family? Implement
SequentialOutcomeQuery/1 as a new query operation over the unchanged complete
SequentialReturnStateFamily/1 compiler and original replay. Do not alter any
frozen family implementation or substitute solver-selected middle states.

Skeptical audit passes after45 checks/eight exact probes. Comparator is full
original native state replay, not merely two equal witness values. The single
scalar comparison fragment is deliberate: arbitrary Boolean negation creates
multiple solver cells and must not be counted as one. Use disjoint elementary
regions for each predicate and complement, one convex solve per branch/region.
The same global cell and elapsed budget covers every solve; reserve per-solver
limits and preserve unvisited regions. A counterexample can refute necessity
under partial coverage; absence of one cannot establish it.

Closed request: profile, family, prefix(1 or2), type, terms, operator and
threshold. Each term has account and canonical rational dimensionless
coefficient; terms must be nonempty with distinct declared accounts. All terms
share the exact original prefix type, including currency, scale, entity/book
and event date. Operators eq/lt/le/gt/ge compare a rational threshold with that
typed sum. This query asserts no new source fact and needs no observation
premise. It selects a question on the existing conditional family. Unknown
predicates or mismatched types reject; no user code or arbitrary expression.

Retain complete request/hash, budget, parent branch manifests and every parent
premise/obligation. Each satisfiable region returns a complete witness, original
replay and independently computed query value. Each unsatisfiable region keeps
its named constraints and checked unsat conflict. Verify supplied witnesses,
including alternate valid ones, and forged predicate/value/state/conflict.
JSON round trips must pass before recording and saved replay before controls.

Classification: witnesses in Q and complement imply contingent; witness in Q
plus complete empty complement implies necessary; complete empty Q plus witness
in complement implies impossible; both complete empty imply empty_family.
Otherwise return unknown with separate proved possibility/counterexample facts.
Do not promote vacuous truth, unresolved target obligations, branch truncation
or resource stops into necessary outcomes. Answers are conditional on the
declared family; actual_history/source/accounting admission stay unknown/false.

Defaults: inherited exact rational solver and finite ceilings are reviewed
engineering reuse, not statistical policy. Deterministic comparisons require
no random-seed ranking. Primary pass is original complete replay plus exact
predicate/complement exhaustion. Vetoes are lost prefix constraints, type/time
erasure, first-witness certainty or unproved exhaustion; repair a successor
before recording. Formula/cell counts and timing explain only workload.

Tests include terminal inventory60 necessary, middle65 contingent, middle64
impossible, observation-selected middle65 necessary, profit1 varying versus
profit2 constant16, unfunded empty, open/closed endpoints, all comparators,
zero/tight budgets, branch-limit stop, missing premises, residual obligations,
false/unknown native findings, malformed types/terms/thresholds, alternative
witness and serialized replay. Do not infer numeric bounds from these tests.

Artifacts: scripts/sequential_outcome_query_v1.py, focused tests and
data/accounting-master/sequential-outcome-query-20261024. Record condition audit,
protected dependencies, complete cases, result and manifest. After checking,
audit numeric range queries on the same complete family, or select a distinct
next dependency if that audit reveals a blocker. Integrate substantive query
semantics in a protected manuscript successor. S1–S5 partial,S6 held,S7 deferred.
