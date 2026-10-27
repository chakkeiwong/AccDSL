# Benchmark, metric and finite comparison audit

Six requests are complete; no additional acquisition in this unit. Primary
identity is PubTables-v2 arXiv2512.10888v3,2 June2026,28 physical pages.
The actual linked GriTS repository resolves to commit
8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1. Acquired grits.py/conversion.py
were read fully as text, never imported. Dataset card, actual data, bbox.py,
dependency versions and experiment manifests remain uninspected.

Text extraction warns of a mismatched EMC operator and omits physical21–28.
Those eight pages were rendered and actually read; local observations will be
labelled manual rendered reading, not quotations recovered by pdftotext.
Physical1–20 technical text, including36 references, was read in extraction;
references are bibliographic triage, not separate technical-paper reads.
Appendices C–F matter: they cover metrics/aggregation, parsing failures, training,
single-page split tables, continuation ablations/failures and qualitative results.

Question repaired after reading: rendered C.3 says Hungarian matching maximizes
the sum of individual table GriTS/TEDS scores; code fills score_matrix with
unnormalised true_positive_score. C.4 then uses cell-weighted aggregation for
GriTS. Literal maximisation of summed normalised table scores need not maximise
summed cell scores. Do not claim whole-paper/code agreement without a
discriminating construction. The source's intended interpretation or historical
implementation could differ; no observed published result is attributed to it.

Finite contract, before computation: use one-row content grids, with single
character cells and equal-character reward1, unequal-character reward0. This is
the inspected LCS cell-similarity rule. For one-row grids the only remaining
alignment is ordered column subsequence matching; a standard-library LCS count
and exhaustive increasing-subsequence oracle will independently check it.
Let A1=[a,b],B1=[a,c],A2=[a,c]+18 copies of x,B2=[a,b]+18 copies of y.
All unmatched characters differ. The predicted pair reward matrix is
[[1,2],[2,1]], with true and predicted table sizes2 and20. Enumerate the two
possible bijections. For each, compare sum of normalised pair F1=2TP/(n+m)
against sumTP, and report the common downstream denominator44. This is a
local exact deduction on four fictional tables, not execution of upstream
NumPy/SciPy/pylcs or evidence about published samples. A source/assumption
mismatch vetoes this deduction; it does not veto independent source findings.

Also check one perfect one-cell sample plus one completely wrong nine-cell
sample: macro versus cell-micro scores should differ. They are two declared
aggregation objectives, not competing estimates of one target. An optional
extra identical prediction should remain in the GriTS denominator. No numeric
proxy is upgraded into financial correctness or statistically supported ranking.

Skeptical/default audit: old and current aggregation differ; library syntax and
the paper's literal words are the comparators, not convenient default metrics.
Empty-set conventions, parse failures and span repairs require explicit scope.
The annotation filters compare PDF to author HTML and cannot prove every visual
table was originally annotated. Newer source dates do not prove contamination
absence. Split grouping/inter-collection overlap requires exact IDs, unavailable
here; no leakage inference is justified. Source scores remain descriptive.

Primary criterion: accurate scope/provenance and exact proof of any stated
finite distinction. Promotion vetoes include paper/implementation equality
without evidence, an unread appendix, or missing data presented as checked.
Continuation vetoes remain protected-state changes or held execution. No such
veto fired. Runtime/dependencies/model adoption remain held. Record six ledgers,
rendered observations, finite cases and adversarial checks, and continue the
concrete unresolved source boundary after closure.
