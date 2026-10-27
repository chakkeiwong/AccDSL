# R04 — binary32 conversion and score-bound direction

20 October 2026. P15/P16/P17/P19; MC23, MC25–26, MC29–35.
Output: data/accounting-master/r04-grits-float-bounds-20261020/.

Question: does the selected source's binary32 score-matrix storage preserve
the direction of mathematical lower and upper bounds? Inspect only retained
code at kensho-technologies/grits@8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1.
No new acquisitions or upstream execution. Pairwise and assignment scope
remain separate from this numerical question.

Evidence contract: compare exact Fraction normalized-LCS rewards with their
ordinary Python float then binary32 representation via struct.pack/unpack.
Use one-cell grids so lower=exact=upper before representation error, and
short strings with manually checked/exhaustive-subsequence LCS. Predeclare
rewards 2/3,7/10,1/2,1 and0, plus a bounded enumeration of rational rewards
2k/(m+n) for 1<=m,n<=24 and0<=k<=min(m,n). This enumeration studies number
representation, not every realizing string or independent observations.
Record exact signed errors, nearest float bits, adjacent binary32 values and
whether conversion moved a lower above or upper below the exact value.

Primary criterion is a mathematically exact signed comparison, not tolerance
or a benchmark. struct models IEEE binary32 storage; it is not execution of
NumPy's assignment or sum. General sum/reduction and SciPy optimality behavior
remain unverified. If needed, show an illustrative abstract two-assignment
matrix whose unequal rational scores collapse to the same binary32 inputs;
label it abstract unless realized by checked cell strings. Do not turn this
into a claim about the magnitude/frequency of historical benchmark errors.

Default audit: nearest binary32 is the examined source representation, not
a proposed default. Exact arithmetic is a comparator; deployment numeric
strategy remains open. Adjacent-value outward rounding from an exact rational
is only an illustrative primitive: applying nextafter to an already uncertified
heuristic does not certify all upstream computations. A global upper needs
both valid pair intervals and upper-assignment optimization. Recomputing a
chosen assignment in higher precision cannot by itself certify its optimality.

Research intent: expected failure is upper entries rounding down or lower
entries rounding up, and collapsed ordering. Repair is an explicit numerical
estimate label or a genuinely enclosing arithmetic/solver contract. The
failure rejects strict-bound interpretation at arbitrary precision, not the
usefulness of small numerical estimates or GriTS research. Protected-byte
changes and held runtime remain continuation vetoes; a failed strict-bound
claim triggers the stated repair work.

Skeptical audit passes: one-cell grids isolate rounding from heuristics,
assignment choice, parser defaults and long reductions. Pre-mortem: confusing
the binary64 intermediate with exact rational source rewards, or treating a
single ULP padding as whole-program certification. Preserve both intermediates
and explicit exact comparator. Do not execute acquired code or install NumPy.

Deliver numerical note/proposed certification conditions, exact illustrations,
six additive ledgers, source anchors, result/review, checks and R08 supplement.
Preserve3.44/396/not_ready,53/6/46,HEAD/index/empty staging and36 tracked dirty
paths. Only four authorised live controls may change. Standard-library Python
with -B and GPU hidden. One-time lifecycle stages; no-argument replay read-only.
No runtime/controller, empirical campaign, install, commit, outreach or fees.
