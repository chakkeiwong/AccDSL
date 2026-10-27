# Input checks required before interpreting the selected GriTS path

20 October 2026. P15/P16/P17/P19; MC01–05, MC23–26, MC28–35.

The retained current source checks ragged rows, several malformed outer
container shapes, failed HTML parsing and attempts to request location scoring
from HTML without boxes. It does not establish the full input domain required
for content, topology and location scoring. Twenty source spans at commit
8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1 were inspected across the three
already acquired files. No new downloads or installed dependency executions
were needed. The source ledger binds the selected files and their prior
identity/receipt records.

TableCell declares types but has no post-construction validation. Its from_dict
passes supplied fields directly, defaults absent text to an empty string and
ignores extra fields. Explicit None or bytes text remains that supplied value.
The content entry point constructs an object array, rather than explicitly
decoding or validating every cell. An external caller may impose stronger
preconditions; that caller was not identified by this inquiry.

Grid construction infers its extents from maximum indices, initializes holes
and assigns each supplied cell into its occupied positions. Two cells at
(0,0), first A then B, leave B in that slot. The reverse input order leaves A.
There is no overlap rejection in this path. Duplicate indices repeat an
assignment; negative indices can alias Python list positions when in range;
empty index lists reach max without a defined cell extent. A span containing
rows 0 and 2 is represented using the minimum and maximum as bounds even
though row 1 is not supplied as occupied. These are direct consequences of
the inspected assignments, not observed dataset error rates.

The defaults also have metric meaning: a content hole is an empty string,
a location hole is a zero box, and a topology hole is a unit box. An explicitly
missing bbox on an actual cell remains None and reaches argument unpacking
in BBox conversion. The proposed adapter therefore preserves absent facts,
explicit blanks and unresolved holes separately. It need not discard any of
them from the evidence store to declare a particular metric unavailable.

BBox rejects reversed axes but has no finite-coordinate check. Width, height,
area and the IoU union are calculated without range checks. The following
local standard-library expressions reproduce those elementary operations;
the acquired library was not executed. Exact Fraction arithmetic on the
actual finite float inputs provides an independent comparator.

| Identical-box or invalid-input illustration | Local floating result | Exact comparator or meaning |
|---|---|---|
| Unit box | 1 | Exact IoU 1 |
| Zero-width box | 0 | Zero-area convention required |
| Reversed axes | Rejected | Invalid geometry |
| NaN left coordinate against unit box | 0 | Nonfinite geometry; zero does not validate it |
| Infinite width | NaN | Nonfinite geometry |
| Finite coordinates -1e308 and 1e308 | NaN | Exact identical positive-area boxes have IoU 1 |
| Finite sides 1e200 | NaN from area overflow | Exact IoU 1 |
| Finite sides 1e154 | 0 from union overflow | Exact IoU 1 |
| Finite sides 1e-200 | 0 from area underflow | Exact IoU 1 |

Thus even a finite final value within [0,1] can hide arithmetic failure.
Finite-coordinate validation alone is insufficient, as is a final NaN check.
This weakens an unrestricted floating-point interpretation of the formula;
it does not invalidate set-union IoU as a mathematical definition or establish
that ordinary document coordinates cause the same failures. NumPy/SciPy
propagation and installed exceptions remain untested.

The sequential evaluator appends a successful metric before attempting the
next metric. If a later metric raises, the earlier metric can remain recorded.
No rollback is present in the inspected method. This is conditional control-flow
evidence, not an executed partial-state test. The proposed adapter stages
per-sample results and explicit unavailable statuses before a single idempotent
commit, preserving consistent denominators and retry identity.

The accompanying adapter-contract.md defines an optional strict input profile:
scalar-valid strings with recorded transformations; declared grid extents,
contiguous spans and disjoint occupancy; a shared coordinate frame; finite and
representable derived geometry; explicit zero-area conventions; supplied
resource budgets; and named unscorable outcomes. It assigns no numeric zero to
invalid input. Normalization, workload limits and deployment identities remain
unselected. Fourteen hand-specified input fixtures and a separate bytes case
check selected proposed preconditions, not a complete runtime adapter.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Preserve existing checks and document remaining gaps | Exact entry/conversion/helper spans | 98 assertions and ten altered-claim controls pass | Stronger external caller contracts | Retain explicit proposed preconditions | Every caller or dataset is invalid |
| Require arithmetic validity beyond finite endpoints | Nine local examples and exact stored-float comparison | Four finite identical-box examples disagree with exact IoU | Practical coordinate ranges and installed behavior | Leave numeric strategy and budgets for reviewed implementation evidence | Empirical failure frequency or library performance |
| Keep adapter proposal separate from adoption | Contract and finite precondition fixtures | No runtime/default promotion | Complete adapter and acceptance evidence | Audit multi-table upper-bound meaning next | Product or accounting readiness |

The new assignment question arose while tracing callers: the code optimizes
table assignment on lower scores, then sums pair upper scores on those same
selected pairs. Whether that quantity bounds the globally optimal exact
assignment is a separate mathematical obligation. It is now the next unit;
this result makes no unreviewed global-bound assertion.

No stochastic comparison occurred. The three retained source files, nine
arithmetic cases and fifteen selected input checks are not independent
empirical samples. Source validity, numerical validity and financial meaning
remain separate. No confirmed manuscript defect or continuation veto occurred.
Candidate 3.44 remains 396 pages/not_ready; all 53 obligations, six interactions
and 46 operations remain, with zero whole-row closures. Six additive ledgers
and a separate R08 supplement preserve this scope.

Execution used /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B with
CUDA_VISIBLE_DEVICES=-1, standard library only. Preparation, construction,
--check and --record run once. Safe completed-unit replay is verify.py without
flags. Existing frozen evidence, HEAD, index and unrelated dirty work survive.

