# Binary32 values are estimates unless bound direction is established

20 October 2026. P15/P16/P17/P19; MC23, MC25–26, MC29–35.

Nearest binary32 conversion does not preserve mathematical lower or upper
directions. The retained caller stores both score matrices as float32 before
assignment and casts selected sums to Python float afterward. This source
choice does not itself establish certified numerical bounds. Four pinned
source spans, five realizable one-cell examples and exact rational comparisons
support the finding. No NumPy, SciPy, pylcs or acquired code was executed.

The standard-library model converts each exact rational first to a Python
binary64 float, then through struct to IEEE binary32. A one-cell grid removes
alignment/assignment ambiguity: its exact lower, optimum and upper all equal
the normalized LCS reward. The two main examples are:

| Cell strings | Exact reward | Binary32 value as an exact rational | Signed error |
|---|---|---|---|
| a / ab | 2/3 | 11184811/16777216 | +1/50331648 |
| abcdefgXXX / abcdefgYYY | 7/10 | 11744051/16777216 | -1/83886080 |

The first stored value exceeds the exact target, so it cannot remain a strict
lower bound. The second falls below it, so it cannot remain a strict upper
bound. Binary64 intermediate errors are also retained. Rewards0,1/2 and1
are exact in these examples. Exhaustive subsequence intersection checks the
short strings' LCS without executing the dependency.

The predeclared census of2k/(m+n), with1<=m,n<=24 and0<=k<=min(m,n), contains
5,476 triples and357 distinct rationals. Among triples,1,004 are exact,
3,346 round upward and1,126 downward. Among distinct rationals, the respective
counts are17,217 and123. These counts describe the finite representation
domain; they are neither error probabilities nor document-population rates.
Every case was compared with adjacent binary32 values using exact arithmetic.

An abstract example also shows loss of ordering:7/10 and7/10+2^-30 differ
mathematically but convert to the same binary32 value. No realizing grid or
installed assignment result is claimed for this abstract pair. Re-evaluating
a chosen assignment in greater precision would not by itself recover an
optimality guarantee lost when choosing from rounded weights.

The accompanying numerical-contract.md separates mathematical bounds,+computed estimates and certified intervals. Outward conversion from a known
exact rational encloses the five local rewards, but it is only one primitive.
Upstream geometry, DP additions, pruning, reductions, global-assignment scope
and solver optimality still require justified treatment. One-ULP padding of
an unverified final value is not whole-program certification. The existing
assignment-scope repair and this numeric requirement are independent.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Reject automatic strict-bound interpretation of nearest binary32 scores | Exact signed errors on one-cell rewards |35 assertions/eight altered-claim controls pass | Native conversion and reductions unexecuted | Label source values as scoped estimates until certification exists | Published benchmark results materially changed |
| Retain local outward-enclosure illustration | Exact rational containment | All357 distinct rational checks pass | Full reward/DP/solver arithmetic | Preserve proposed certification conditions | A one-ULP final repair is sufficient |
| Keep precision and thresholds unselected | Explicit unresolved numerical contract | No runtime/default admission | Deployment workload and acceptance evidence | Consolidate findings into a proposed evaluation profile | A new default or statistical ranking |

No model comparison or stochastic inference occurred. No confirmed manuscript
defect or continuation veto occurred. Candidate3.44 remains396 pages/not_ready;
53 obligations,six interactions and46 operations remain with zero whole-row
closures. Six additive ledgers and a separate R08 supplement preserve the
source-only result. Historical experiment identity and human/domain/independent
acceptance remain open.

Commands used the standard-library tfgpu interpreter, -B and
CUDA_VISIBLE_DEVICES=-1. Preparation, build_records.py, --check and --record
each run once. No-argument verify.py is safe read-only replay. No new downloads,
installation, upstream execution, empirical campaign, commit or outreach.

