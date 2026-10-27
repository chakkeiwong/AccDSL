# Audit exact numeric ranges over the complete native sequence

24 October 2026. S2–S4; MC08/09/11/16/18/24/26/28/35,
G1/G3/G16 and P17-08.01/.02/.03/.04/.06.

Question: can the existing exact rational objective solver deliver correct
whole-family lower/upper bounds and endpoint attainment for typed financial
expressions without losing intermediate constraints or unvisited branches?
Comparator: original complete sequence replay, hand-derived inventory and
profit formulas, and exact satisfiability of better-value/endpoint queries.

Skeptical audit: do not read min/max of retained witnesses as a range. Existing
solver bounds are per compiled branch; global bounds require combining every
complete branch and retaining all endpoint assumptions. Strict domains may
have an unattained infimum/supremum. Even certified local bounds from visited
branches cannot be global when another branch is unvisited. Unresolved target
obligations keep conclusions on the relaxed candidate family. A convex hull
of disjoint ranges is an envelope, not proof every interior value is attainable.

Audit source-level closure, optimizer, no-better, attainment, unbounded and
resource behavior before extending the public interface. Probe inventory1
[65,80], inventory2{60}, profit1[-19,-4], profit2{16}; open endpoints,
intermediate observation, unfunded empty, variable sale proceeds, partial
branch budgets and zero limits. Check endpoint witnesses through original
complete native replay. If any mismatch appears, preserve failure evidence and
repair in a successor; do not alter a frozen solver or hide the mismatch.

Promotion criterion: each global bound is justified across all parent branches,
exact strict endpoints are preserved and attained endpoints replay. Lost
constraints, optimistic certification, unsupported infinity evidence or missing
replay veto promotion. A bad candidate triggers repair, not a global stop.
Counts/timing are explanatory. No stochastic ranking, probabilities, general
nonlinear bounds, actual-history admission or forecast accuracy is concluded.

Defaults: inherited explicit rational solver budgets are engineering ceilings;
topology and numeric domains are hypothetical examples. Preserve source hashes,
derivation, complete probes and result in sequential-range-audit-20261024. After
the audit write a justified range-interface plan or repair the failed condition,
then integrate checked query semantics in a protected successor to Version3.69.
