# Numerical meaning of a reported bound

A reported number should identify whether it is a numerical estimate, a bound
on a fixed alignment/assignment, or a bound on a global optimization target.
Source precision, rounding policy and any error allowance belong with that
meaning. A finite value and a narrow displayed decimal interval are not a
proof of enclosure.

For a one-cell grid, the exact normalized-LCS reward is q=2k/(m+n). There is
only one nonempty alignment, so mathematical L=O=U=q. The selected source
first computes a Python numeric reward and later stores pair scores in
float32 matrices. Under ordinary nearest binary32 conversion, 2/3 becomes
11184811/16777216, which exceeds 2/3 by 1/50331648. Thus a nominal lower
entry may exceed its exact target. Conversely, 7/10 becomes11744051/16777216,
which is below7/10 by1/83886080. A nominal upper entry can fall below its
target. struct-based illustrations retain the binary64 intermediate and show
the same directions. No NumPy assignment or summation is executed here.

If the exact rational q is available, outward conversion can enclose it by
the adjacent representable endpoints surrounding q. The finite illustrations
verify these endpoints exactly. That local primitive is not a whole-program
repair: approximate IoU rewards, DP additions, pruning conditions, reductions
and assignment optimization can each need separate error analysis. Moving
an untrusted final value by one ULP does not establish that all accumulated
errors are enclosed.

A proposed certified implementation would need, at minimum:

- Valid input geometry/text and a declared exact or bounded-error reward.
- Feasible alignments and assignments retained as lower-bound witnesses.
- Sound upper relaxations using outward arithmetic through every operation.
- A global upper-assignment calculation or an independent optimality certificate
  for the same feasible assignment problem, preserving upper direction.
- Sum and normalization rules with proved error/enclosure semantics, including
  empty and zero-area conventions, overflow and underflow failures.
- Fixtures distinguishing exact mathematical values, computed estimates and
  certified intervals, plus actual deployed-version validation.

Recomputing a selected assignment at higher precision can improve its evaluated
score but cannot alone prove that the selected assignment is globally optimal.
Likewise, fixing the earlier assignment-scope defect does not fix numerical
enclosure. No certified implementation, precision default, tolerance or library
change is selected in this source inquiry. The immediate proposed adapter can
retain the source's numerical values as estimates with explicit scope while
keeping certification unavailable.
