# Numerical interpretation review

The strongest scope objection is that struct is not NumPy. The report makes
that distinction: exact representation arithmetic establishes that ordinary
nearest binary32 cannot guarantee bound direction, while native conversion,
sum order and deployed solver behavior remain untested. The source's dtype
choice and absence of directed rounding justify keeping certification open;
they do not substitute for an installed equivalence test.

The exact target is2k/(m+n); the computed model is binary64 followed by
binary32 conversion. Both errors are retained, so the report does not call
the binary64 intermediate exact. One-cell grids ensure the two principal
counterexamples do not depend on heuristic tightness or assignment ties.
The abstract ordering example is labelled as such and makes no grid-realization
claim. All finite-census counts are combinatorial, not empirical rates.

The local enclosure primitive begins with a known exact rational. It cannot
certify an approximate IoU/DP/assignment result just by padding its last value.
The numerical contract therefore leaves full certification, deployment
precision and tolerances unselected. No practical error magnitude, historical
impact or superiority claim follows from the examples.

The finding rejects an unjustified strict-bound interpretation and leaves
the numerical metric viable as a scoped estimate. No source-protected byte
changed and no continuation veto fired. The next useful work is to consolidate
the finite metric findings with the existing R05 statistical protocol gaps,
without choosing a population or decision threshold by convenience.
