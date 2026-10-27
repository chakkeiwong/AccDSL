# Correct the midpoint-grid convergence claim

MC11/12/18/26/28/32–35; release C1/C4/C5/C6. Bounded unit: the complete
reference-computations chapter, currently chapter18, in selected manuscript
5.54-R2 package revision2. The protected baseline reading covers physical
187–191 and the following literature opening on192. Retain all prior packages.

The financially literate implementer should distinguish convergence of a
deterministic grid from monotonic improvement, and both from random-sample
error. Section18.2 currently says increasing n improves the discretization.
That wording can incorrectly imply decreasing breach-probability error at
every refinement. For the stated strict threshold0.3, n=4 gives3/4 while n=5
gives3/5: absolute error increases from1/20 to1/10. The mean stays89.

## Evidence contract and defaults

Question: what exactly can be guaranteed for the uniform midpoint approximation
to a threshold event, and can a recipient reproduce the chapter's cited
deterministic reference arithmetic from the selected package?

Baseline/comparator: alpha uniform on[0,1], C=90-2alpha, breach alpha>t,
equally weighted midpoints(i-1/2)/n, n a positive integer, t in[0,1].
These are the chapter's deliberately supplied teaching assumptions, not
issuer facts or forecasting defaults. Strict threshold ownership matters.
The original arithmetic writer and its accepted result remain frozen.

Primary criterion: derive the exact count and the all-t,n bound algebraically;
independently count rational boundary/interior examples; preserve every
predecessor citation and substantive mathematical statement apart from the
identified ambiguous convergence sentence. The bound is established by the
floor inequalities, never by finite samples. Reproduce the retained arithmetic
script in a separate copy and compare its complete checked values to its
accepted output. Counts, clean builds and time are explanatory only.

Promotion vetoes: incorrect strict/inclusive boundary, a grid bound described
as stochastic confidence, uninspected financial normalization, lost original
source/math, hidden worktree dependencies or changed frozen evidence.
A failed check triggers repair. Baseline drift, corrupt evidence, or the
eight-hour deadline stops the affected action; independent ready work continues.
No stochastic experiment, empirical superiority, general discontinuous-integrand
bound, production runtime or whole-book acceptance will be claimed.

## Reviewed sequence

1. Bind selected sources/PDFs, original arithmetic source/result and current
   controls; preserve the originals. Finish the complete chapter diagnosis.
2. Derive p_n(t)=1-floor(nt+1/2)/n and |p_n(t)-(1-t)|<=1/(2n).
   Count events independently for exact rational cases including endpoints,
   every midpoint boundary in selected grids, and both sides of boundaries.
   Check n=4 versus5 and zero-error n=10 versus nonzero-error n=11.
3. Repair the source in protected5.54-R3; add the short derivation and explicit
   counterexample. Include a portable reference-computations companion with
   the exact original teaching checker/result and the new grid check.
   Link the chapter's otherwise unnamed arithmetic reference to that companion.
4. Build both volumes, inspect the entire repaired chapter and adjacent pages,
   preserve all unrelated sources and old mathematics/citations, verify package
   integrity, and reproduce both documents/companion from a separate copy.
5. Guard integration against live control changes; update the master and
   pursuit records. Release remains not_ready and all original acceptance
   populations remain unchanged.

Skeptical audit: the potential wrong baseline is the current packaged manuscript,
not the older review PDF. Its wording is identical and must be pinned before
editing. A random Monte Carlo test would not answer this deterministic question;
use exact fractions and a proof instead. A larger check count would not prove
the real-threshold statement. The original script writes beside itself, so
execute only a copied version in a caller-owned new output directory. Hash
comparison alone does not validate the arithmetic; the stated counterexamples
and floor proof provide independent expectations. The plan passes within these
limits. CPU-only standard-library checks, no seeds, no new dependency installation.

Record commands, environment, wall time and exact source identities in
data/accounting-master/release-pursuit-20261027/midpoint-reference/.
Reader questions: why can the mean be right when the breach estimate is wrong;
why can a finer grid be worse; what is guaranteed for every threshold; what
changes when equality is included; why is the bound not a confidence interval?
The entire chapter was read before repair; no independent reader acceptance
is inferred from this author's diagnosis or regression.

## Concurrent successor reconciliation

The live package advanced to5.55 during the independent5.54-R3 repair.
The sector integration adds dated PAA and bank interfaces and24 files.
Its simulation chapter18 is byte-identical to the original repair baseline.
Do not select the older branch. Preserve it and its completed checks, and
merge only the reviewed chapter18 repair and five companion files onto5.55
as protected5.55-R1. All sector methods, sources and replay evidence remain
unchanged. Rebuild and reproduce both merged documents. Reuse the exact
arithmetic evidence because its code, data and mathematical target do not
change; verify copied identities. The older branch's main-only relocated
build is partial reproduction and cannot substitute for merged reproduction.

Skeptical re-audit passes: exact source comparison excludes a chapter conflict,
and the new successor preserves all447 selected files except explicit cover,
readme, dependency and chapter changes plus rebuilt PDFs. Live-pointer drift
before integration requires reconciliation rather than an overwrite.
