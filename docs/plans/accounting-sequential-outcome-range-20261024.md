# Exact finite financial-outcome ranges for complete native sequences

24 October 2026. S2–S4; MC08/09/11/16/18/24/26/28/35;
G1/G3/G16; P17-08.01/.02/.03/.04/.06.

Implement SequentialOutcomeRange/1 as a new closed query: profile,family,prefix,
type,terms. Reuse the checked scalar query's exact type/term validation by an
explicit internal equality-to-zero question; this supplies no new family
constraint. Compile the unchanged complete parent and optimize the same typed
same-prefix account sum separately in every original branch.

Skeptical audit passes after118 checks/10 probes. A feasible branch has finite
numeric input intervals and affine output, so finite endpoints are the supported
fragment. A claimed unbounded endpoint is a veto, not a returned certified
infinity. Optimize closure for a candidate bound, require original no-better
proof and original endpoint-attainment proof, and replay any attained witness
through the original complete native sequence. A strict unattained endpoint
is a valid infimum/supremum; never materialize it as an admissible state.

One explicit max_cells/elapsed budget spans all branches. Solver time/resource
and formula limits remain. A feasible witness can establish nonemptiness before
all branch ranges are known. Global bounds require every branch checked
infeasible or certified finite at both ends. Partial results may show explored
branch bounds with a clear nonglobal status. Never infer the whole range from
one branch or from selected witness extrema. Aggregate minimum/maximum and
attainment only across complete branch evidence. The result is an exact outer
envelope, not proof every interior value is attainable. Empty family has no
range and zero budget remains unknown.

Evidence contract: original native complete replay, exact hand-derived totals,
no-better and attainment queries are primary. Lost constraints, wrong dated
types, false bound proof or global certification under partial search veto
promotion and trigger repair; frozen input corruption is a continuation veto.
Counts/timing explain workload only. No probability, actual-state admission,
forecast accuracy, arbitrary nonlinear/unbounded coverage or default-policy
ranking is concluded. Explicit inherited budgets are engineering ceilings.

Preserve all parent premises and target obligations. Missing premises halt.
Residual obligations label candidate-family bounds and leave actual outcomes
unknown. Alternative valid endpoint witnesses and infeasibility cores are
accepted after exact checking. Forged bound values, attainment, native state,
coverage and conflict evidence reject. JSON round trips and saved replay must
pass before controls advance.

Focused cases: inventory1[65,80], inventory2{60}, profit1[-19,-4], profit2{16},
open endpoints, observation singleton, proceeds-dependent profit[-24,76],
unfunded empty, tight/zero budgets, branch limit, malformed type/terms, unresolved
findings/premises, remaining obligations and result tampering. Keep the existing
119-method query/parent suite as relevant regression evidence.

Artifacts: scripts/sequential_outcome_range_v1.py, focused tests,
data/accounting-master/sequential-outcome-range-20261024. Record condition audit,
full requests/results, protected inputs and manifest. Then integrate both query
operations and their financial interpretation into a protected successor to
Version3.69; refresh coverage and select a distinct next simulator dependency.
