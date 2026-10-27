# Midpoint convergence repair integrated with the sector successor

The checked candidate is **5.55-R1**, with 837 main pages and 265 total /
244 body simulation pages. It merges the numerical reference repair onto
5.55, preserving the dated insurance and bank work. It remains **not_ready**.
The earlier5.54-R3 branch is preserved but is not the selected successor.

Plan: docs/plans/accounting-midpoint-reference-20261027.md.
Requirements: MC11/12/18/26/28/32–35; C1/C4/C5/C6.
Package: docs/design/proposal/manuscript-reference-v555r1-20261027/.
Final verification and reproduction: merged/verification.json and
merged/relocation/result.json. Guarded selection is recorded separately in
merged/advancement.json; the existence of this result does not by itself
assert that selection has already occurred.

## Mathematical correction

Section18.2 now distinguishes eventual convergence from monotonic improvement.
For the strict threshold alpha>3/10, midpoint grids give3/4 at n=4 and3/5
at n=5. Absolute error therefore increases from1/20 to1/10. A second
counterexample goes from zero error at n=10 to3/110 at n=11.

For all real t in[0,1] and positive integers n, the chapter derives
p_n(t)=1-floor(nt+1/2)/n and absolute error at most1/(2n). The proof uses
the floor inequalities; it does not infer a continuous-domain theorem from
sample cases. Equality at a midpoint remains outside the strict breach event.
The narrow-region no-hit calculation now explicitly assumes independent draws.
All other substantive mathematics and citations remain; the new result is
a local elementary derivation under the existing illustrative uniform law.

## Reproduction and preservation

The new standard-library companion reproduces the complete169-check historical
arithmetic result and checks6,552 rational threshold/boundary cases. All case
records and both counterexamples match from a separate copied package. Existing
output directories are refused without changing them. A deliberately altered
expected input is rejected before an output directory is created. The original
historical writer and result remain unchanged; only a copied writer is executed.

All460 merged source/build checks pass. The452-file package contains the six
unchanged5.55 companions plus the numerical reference companion. The six
predecessor components retain their recorded reproduction evidence; they were
not unnecessarily rerun. The repaired main chapter189–194 was read in full,
with covers, following opening and affected simulation pages:12 exact page
bindings. Both merged PDFs reproduce every normalized page text from a
separate /tmp copy, with no original-worktree TeX input, unresolved reference,
overfull box or changed copied non-PDF input. PDF byte identity is recorded
separately from text equivalence because generated metadata can differ.

The original repair baseline and plan hash precede the later concurrent-merge
extension. Those original identities remain historical; merged/baseline.json
binds the selected5.55 files and extended plan. The initially prepared5.54-R3
package and its completed main-only relocated build remain available, without
claiming that branch has a completed two-volume reproduction. Procedural command
escaping and TOC-level errors were corrected before their affected writes;
they supplied no numerical evidence and no original source was overwritten.

## Decision

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Select the merged internal candidate after guarded control checks | Exact counterexamples, floor proof, complete copied arithmetic and both document reproductions pass | No remaining source, reference, changed-input or financial-comparison failure; six sector-predecessor components unchanged | Whole manuscript, wider source/applicability and independent acceptance are unfinished | Reconcile master and perform final timed release assessment against original conditions | Broad MC closure, stochastic accuracy, general grid convergence, accounting compliance or production readiness |

Author-review.md separates comprehension, mathematics, sources and typography.
The strongest alternative explanation is a comparator sharing an implementation
mistake; direct event counts and fixed expected fractions discriminate that
case, while the universal bound is proved independently. No stochastic ranking
or empirical comparison is performed. The bounded repair invalidates a possible
monotonic interpretation, not the simulation research direction.

Ordered whole-manuscript reading remains on protected5.52-R2 through physical192.
Local successor regression does not advance that frontier. All original acceptance
populations and later runtime/empirical duties remain unchanged.
