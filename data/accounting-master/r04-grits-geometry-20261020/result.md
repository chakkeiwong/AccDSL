# GriTS geometry denominator: result

20 October2026. P15/P17/P19; MC01–05/23/26/28–35. The source question is
resolved within the documented dependency contract, with installed/historical
execution kept separate.

Original-author environment.yml at16d124f616109746b7785f03085100f1f6247575
pins Python3.10.9 and PyMuPDF1.21.1. It is a recipe, not proof of any historical
run's environment. Current PyMuPDF documentation describes include_rect as
the smallest rectangle containing both inputs. The same definition appears
in docs/rect.rst at tag1.21.1. Its acquired Git blob
83849346d6ccbd981ce3080654903292b0ea59e5 matches the retained tag tree
0f01aafb9514be278b301c0f1b00d88209b01ac6. The latter is a tree identity,
not a resolved commit. Both the current and historical sources are retained;
the historical one supplies the applicable documentary semantics.

The paper's target is intersection-over-union of two rectangles. Original
source instead forms Rect(bbox1).include_rect(bbox2) and uses its area as the
denominator. Under the exact-version documented operation, it computes the
intersection area divided by the enclosing-rectangle area. That is **wrong
relative to the stated IoU target** in general. It is a distinct bounded
similarity, whose relation to IoU is explicit below; renaming it does not
establish equality. Actual installed PyMuPDF behavior was not run or certified.

For finite ordered rectangles A,B, write I=area(A intersection B),
U=area(A)+area(B)-I, and E=area(the smallest rectangle containing both).
The union is contained in that rectangle, so U<=E. If I>0, then I/E<=I/U,
with strict inequality whenever E>U. When the rectangles are disjoint or touch
only at an edge, both ratios are zero if their denominators are positive.
The shared area is unaffected by semi-open boundary conventions. Empty/empty
set IoU is undefined; the code's early-zero choice remains a convention.

| Exact case | I | U | E | Original documented formula I/E | IoU I/U |
|---|---:|---:|---:|---:|---:|
| Offset2x2 squares | 1 | 7 | 9 | 1/9 | 1/7 |
| Crossing length4 rectangles | 1 | 7 | 16 | 1/16 | 1/7 |
| Vertical/horizontal3-cell relative spans | 1 | 5 | 9 | 1/9 | 1/5 |

The relative-span boxes [0,-1,1,2] and[-1,0,2,1] both contain the reference
unit grid cell. They are valid topology representations, so the distinction
can affect GriTS_Top as well as absolute-location similarity. Nine declared
integer-coordinate cases also preserve containment, disjoint, touching,
equal-height, identical and zero-width examples. Independent enumeration of
unit squares verifies intersection and union areas. The counts describe only
these fictional cases; no dataset error rate or benchmark correction follows.

The complete newer bbox.py at8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1
computes coordinate overlap lengths and their product. The already retained
metric uses area1+area2-intersection. This is the set-union formula for finite
ordered coordinates with correctly supplied areas. BBox rejects reversed axes
but does not explicitly enforce finiteness; its Protocol can be implemented
by other objects. No general malformed/nonfinite-input or installed-runtime
claim follows. The newer package requires Python>=3.10, NumPy>=1.26,
pylcs>=0.1.1, lxml>=4.9 and SciPy>=1.15,<2; those are ranges, not exact
installed identities. The pylcs source remains a concrete next dependency.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Reject original denominator equality to IoU | Exact dependency documentation plus source and geometric proof | Three strict finite witnesses;85 assertions pass; six altered records rejected | Native implementation/installed correspondence and historical data | Preserve source-specific mismatch | All historical results wrong or numerically corrected |
| Retain current helper's finite-box formula | Complete source read and independent set-area checks | Stated finite ordered-coordinate domain required | Nonfinite inputs and supplied area integrity | Record preconditions; inspect pylcs source separately | Complete reusable-runtime validation |
| Preserve3.44 | Existing extraction/accounting distinction holds | No confirmed manuscript defect | Independent/domain/human evidence | Add R08 supplement and refresh four controls | Whole-row closure or readiness promotion |

No stochastic comparison was run; source scores are neither re-estimated nor
ranked. Six bounded HTTPS acquisitions,29 source anchors and four verified
file blobs are recorded. Source reading covers all three small code/config
files and historical rect.rst, with selected relevant current-document spans.
The implementation/native core is explicitly uninspected. Only local
standard-library arithmetic and AST inspection ran; GPU devices were hidden.

The mismatch concerns one implementation expression relative to its claimed
target. It does not invalidate grid-similarity theory, the bounded current
helper formula or the broader research direction. It would trigger a
source-version-aware repair before selecting that original path for runtime.
No global continuation veto fired. 3.44 stays396 pages/not_ready;53 obligations,
six interactions and46 operations remain, with zero whole-row closures.

The fixed four-request wrapper saved actual invocations and receipts. Two
additional bounded requests resolved the stated dependency's historical API.
source-ledger.json records commands and hashes; run-manifest.json records the
lifecycle environment, elapsed time and output locations. Local construction,
--check,--record and no-flag replay use the designated Python with -B and
CUDA_VISIBLE_DEVICES=-1. Completed stages are one-time; safe future replay
is verify.py without flags.
