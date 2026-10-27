# Geometry evidence and pre-calculation audit

All six acquisitions succeeded. Complete bbox.py, pyproject.toml,
environment.yml and historical docs/rect.rst were read. Current HTML reading
was limited to coordinate/validity context and include_rect/intersect/get_area
sections plus version/footer metadata. The historical tag1.21.1 resolves to
tree0f01aafb9514be278b301c0f1b00d88209b01ac6, not a commit identifier.
The retained historical document's blob is83849346d6ccbd981ce3080654903292b0ea59e5.
Tag route plus tree/blob verification supplies immutable content identity;
do not relabel the tree SHA as a commit. Historical implementation bodies and
installed binaries remain uninspected. This narrows the earlier follow-up's
"exact-commit" wording to the actual tree/blob evidence obtained.

The1.21.1 documentation explicitly says include_rect computes the smallest
rectangle containing both and replaces the receiver. Intersect returns the
common rectangular area; get_area computes its area. The original source
constructs separate Rect copies for intersection and inclusion. Under this
documented recipe it computes intersection area divided by enclosure area,
not the paper's set-union IoU in general. The current helper computes coordinate
overlap lengths and the current metric uses areaA+areaB-intersection. Constructor
checks reject reversed axes but do not explicitly reject NaN/infinity; the
Protocol permits callers to provide other representations. The result will
state the valid finite coordinate domain, not claim general input validation.

Before calculation, select nine integer-coordinate cases: offset squares
([0,0,2,2],[1,1,3,3]); crossing rectangles([0,1,4,2],[1,0,2,4]); relative-span
topology boxes([0,-1,1,2],[-1,0,2,1]); containment; disjoint; touching; equal
vertical extent; identical; and a zero-width box paired with a positive box.
The topology boxes both contain the reference grid square and correspond to
vertical/horizontal3-cell spans, so this mismatch is relevant to topology as
well as absolute locations. No financial or empirical samples are used.

Compute exact intersection, union and enclosure areas using Fraction. Independently
enumerate integer unit squares belonging to each rectangle and compare set
intersection/union cardinalities. For positive intersection, enclosure contains
the union, so intersection/enclosure<=intersection/union; strict inequality
holds when enclosure has positive excess area. Equality cases and zero-area
behavior must also be retained; zero/zero set IoU is undefined and receives
no invented mathematical value. A local source-equivalent early-zero expression
can be checked as an implementation convention only. The nine cases do not
estimate dataset frequency or reconstruct benchmark scores.

Skeptical audit passes: historical documentation resolves the contract for the
declared dependency version but does not certify installed behavior. Neither
current package ranges nor original environment pins prove actual experiment
versions. Six negative controls will alter geometry results or promote runtime/
historical evidence. No dependencies run; standard-library local arithmetic
and AST inspection only. Candidate3.44 remains unchanged unless a concrete
claim defect is found; its existing metric/accounting qualifications remain
consistent with these findings. No continuation veto fired.
