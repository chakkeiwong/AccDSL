# Mathematical and source comparison audit

20 October 2026. Six requests complete; no additional acquisitions in this unit.
Read all 15 pages of arXiv2203.12555v3 (23 May 2023), including Sections2–4
and all18 references. There is no appendix in this revision. Physical7–9 were
rendered and read to check equations3–6, the grid-cell representation, the
factored procedure and the bound argument. The complete src/grits.py at author
commit16d124f616109746b7785f03085100f1f6247575 was read as text. Only
eval.py's compute_metrics and summary/printing/eval_tsr_sample spans266–331
and394–485 were read; the rest of that caller and its dependencies are not
claimed inspected. The prior Kensho factored_2dmss/lcs_similarity/iou spans
274–437 were inspected as the version-specific comparator.

The source defines exact 2D-MSS in equations3–6, then Section3.5 calls the
feasible heuristic lower bound GriTS. Preserve both definitions: a claim that
the heuristic always equals the exact optimum is wrong; using its lower bound
as the reported metric follows Section3.5. For any increasing row/column
alignment and cell rewards in[0,1], its score L is feasible and L<=OPT. The
row relaxation allows a separate optimal column subsequence for each row pair;
every joint alignment is feasible for that relaxation, so OPT<=Ur. Transposing
gives OPT<=Uc. Hence L<=OPT<=min(Ur,Uc). Scaling all by2/(|A|+|B|) preserves
the bound for nonempty total grids. Empty-input conventions are a separate
implementation choice. These are local derivations of the inspected argument,
not an independent reading of cited NP-hardness or RowColAlign sources.

The original cell-content function uses SequenceMatcher(None,a,b) and sums
matching-block sizes; this needs a discriminator against the paper's LCS
target. Before computation, use the fixed strings aaa/abaa, tide/diet and
the reversed pair, and x repeated200 times versus y followed by x repeated200
times. Compare against a standard-library integer LCS DP. For the short strings,
independently enumerate all subsequences; for the repetitive string pair, the
200-character x subsequence attains the minimum-length upper bound. Call only
Python's standard-library SequenceMatcher, never the acquired module. Record
its actual Python/source identity and autojunk default. Any disagreement is
evidence about these expressions and this environment, not an execution of
the original package or a reconstruction of the historical experiment.

Also predeclare a 2x2 one-character-grid witness: A=[[a,b],[b,a]] and
B=[[b,a],[a,b]]. Use binary exact-match rewards, which equal normalised LCS
for one-character cells. Reconstruct the nested DP locally with the inspected
diagonal/up/left tie preference and compare it to exhaustive enumeration of
all increasing row and column index pairs. Check all256 pairs of binary2x2
grids as a finite domain, with no random search and no larger sweep. Preserve
the explicit witness even if it disproves tightness. Check each relaxation
against an independent exhaustive one-dimensional oracle. This is a bounded
mathematical check, not a dataset benchmark or a ranking experiment.

For the current wrapper's first shortcut, same-shape m-by-n grids admit only
the identity alignment at full size; every other alignment has at most
mn-min(m,n) cells. Identity reward at least that bound is therefore optimal.
For its second shortcut with equal column count n and k selected row pairs,
identity-column score S>=kn-1 implies each row-pair identity score>=n-1,
since all other pairs contribute at most n. Every nonidentity column alignment
for an individual row pair has at most n-1 entries. Thus each inner relaxed
score equals its identity-column score, so Ur=S and the feasible score meets
a valid upper bound. These arguments require bounded nonnegative rewards;
the callbacks themselves and floating arithmetic are not validated here.

Skeptical audit: no runtime equivalence, metric ranking, financial correctness,
statistical result or target-domain default follows. A zero heuristic score
would not invalidate the bound, only universal tightness. A string mismatch
would invalidate original-source equality to the claimed LCS reward, not all
grid matching or the newer unexecuted pylcs implementation. Original geometry
uses Rect.include_rect while the newer wrapper uses area1+area2-intersection;
exact dependency semantics remain uninspected and need their own source inquiry.
The primary criterion is exact objective/quantity separation with reproducible
finite evidence. A failed bound or oracle discrepancy blocks that numerical
claim until repaired; protected-byte or held-execution violation stops the unit.
