# R04 — scope of the multi-table GriTS upper bound

20 October 2026. P15/P16/P17/P19; MC23, MC25–26, MC29–35.
Output: data/accounting-master/r04-grits-assignment-bounds-20261020/.

Question: does summing pair upper bounds on an assignment selected by pair
lower scores bound the globally optimal exact table assignment, or only the
exact score on that fixed assignment? Retained current source:
kensho-technologies/grits@8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1.
No new downloads, library imports, installed execution or published-data runs.

Evidence contract: write the derivation for matrices L<=O<=U with identical
feasible one-to-one assignments. Compare the reported sum U(M_L), the fixed
assignment exact score O(M_L), and the global exact optimum max_M O(M).
The primary criterion is a valid proof or exact counterexample. Pairwise
metric correctness does not by itself establish a global assignment bound.
Do not mistake the library field name for an explicit theorem. Distinguish
what the implementation computes from any stronger interpretation.

Use the retained independent local grid_scores oracle, not acquired code, to
construct all 256 ordered pairs of binary 2x2 grids under the current selected
shortcuts. This recomputation supports a new assignment question and does not
repeat the completed predecessor lifecycle. The main new finite domain is
two-table collections drawn with repetition from 16 grids: 136 canonical
collections on each side, at most 18,496 collection pairs. Enumerate both
assignments exactly; save a witness with a unique maximizing lower-score
assignment if one exists, avoiding undocumented SciPy tie behavior. All pair
scores are small integers exactly representable in the source's float32
matrices, so quantization is not an explanation for such a witness. Do not
execute NumPy or SciPy. Reuse only the project's standard-library oracle.

Expected failure: upper scores on a chosen assignment miss an alternative
assignment whose lower score is weaker but exact score is higher. Repair is
an explicit fixed-assignment label or a separately optimized upper-bound
matrix, with proof and numerical qualification. A source or oracle mismatch
vetoes the dependent interpretation; a counterexample does not reject GriTS
or its pairwise bounds. Protected-byte changes and held execution remain
continuation vetoes. Finite-domain counts are descriptive combinatorics,
not benchmark rates or probabilities. No model ranking follows.

Default audit: binary cells and 2x2 shapes are a counterexample search domain,
not a proposed benchmark. Exact one-character equality corresponds to the
selected normalized-LCS reward. Current shortcuts and diagonal-first internal
ties must match the inspected source. Outer assignment uniqueness avoids
assuming a solver's tie rule. Integer exactness isolates bound scope from
float32 rounding; general numerical soundness remains a separate obligation.

Skeptical audit passes: source chooses lower scores then indexes upper scores
with the same assignment. The earliest mathematical test is whether the
maximizers can differ. A generic interval-matrix counterexample alone does not
prove realizability by actual table rewards, so seek actual small grids too.
Pre-mortem: omitting current shortcuts could manufacture a historical-only
failure; use current scores from the retained oracle, and independently
enumerate exact row/column substructures and table assignments.

Deliver derivation, exact witness/search record, source anchors, six additive
ledgers, result/review, checks and R08 supplement. Preserve 3.44/396/not_ready,
53/6/46, HEAD/index/empty staging and 36 tracked dirty paths. Only four existing
live controls may change. Python standard library only, -B, GPU hidden.
Each preparation/construction/check/record stage runs once; read-only replay
uses no flags. No runtime/controller, installation, empirical campaign, commit,
outreach, publication or fees. Continue the next ready source/protocol gap.
