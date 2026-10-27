# R04 — GriTS input validity and proposed adapter preconditions

20 October 2026. P15/P16/P17/P19; MC01–05, MC23–26, MC28–35.
Output: data/accounting-master/r04-grits-input-contract-20261020/.

Question: do the retained conversion and metric paths establish the valid
input domain needed by the selected metric, and what must a proposed AccDSL
adapter check before interpreting its output? Use only the retained pinned
Kensho files from r04-pubtablesv2-20261019 and r04-grits-geometry-20261020,
plus the completed source inquiries. No new downloads or dependency execution.

Evidence contract: primary evidence is exact source spans along TableCell,
from_dict, grid construction, geometry conversion and reward invocation.
Comparator is the explicit codepoint/rectangular-grid/finite bounded-reward
domain used by the inspected metric argument, not an empirical benchmark.
Use local standard-library arithmetic and hand-specified small conversion
examples solely to expose missing checks. Check finite geometry examples with
Fraction arithmetic independent of floating-point formula evaluation.
Evaluate coordinate NaN/infinity, finite overflowing/underflowing coordinates,
missing bbox, missing/None/bytes text, overlapping occupancy, negative/duplicate/
noncontiguous indices, empty/ragged grids and declared resource envelopes.
Do not simulate NumPy/SciPy/pylcs or infer their installed exception/output.

Research intent: expected failures are permissive dataclass construction,
silent defaults/overwrite, finite-input arithmetic failure and absent input
validation. A failure triggers explicit proposed adapter outcomes, not a claim
that every library caller is invalid. Promotion vetoes are equating type
annotations with runtime checks, equating finite coordinates with finite
derived arithmetic, or promoting a numeric score to financial validity.
Protected-byte change or held execution is a continuation veto. Missing actual
caller provenance limits downstream claims; it does not stop documentary repair.

Default audit: the proposed strict adapter is an optional explicit profile,
not a new global default or a redesign of GriTS. Require a declared coordinate
frame and text policy rather than choosing units/normalization. Preserve absent
versus explicit-empty text and holes versus occupied blank slots. Resource
limits must be supplied by a later reviewed workload contract, not invented
numbers. Index contiguity, grid rectangularity, occupancy nonoverlap and numeric
representation are proposed preconditions justified by the conversion formulas.
Do not reject genuine missing disclosures from the evidence store; return an
unscorable status for a metric branch while preserving original evidence.

Skeptical audit passes: retained source identities are already bound; new work
answers caller-validation gaps without rerunning completed literature or native
tests. Pre-mortem: a local formula model may be mistaken for library execution,
or arbitrary resource thresholds may become defaults. Record the local model
explicitly, use exact arithmetic where feasible and leave budgets unselected.
API function annotation scope and actual caller behavior remain distinct.

Deliver source anchors, a proposed adapter contract with typed failure states,
finite illustrations, six additive source ledgers, result/review, checks and a
separate R08 supplement. Preserve 3.44/396/not_ready, 53/6/46, unchanged HEAD/
index/empty staging and 36 tracked dirty paths. Edit only the four authorised
live controls; all other existing evidence stays frozen. Preparation,
construction, --check and --record each run once; no-argument replay is read-only.
Use standard-library Python with -B and CUDA_VISIBLE_DEVICES=-1. No installed
library, acquired source, runtime/controller, empirical campaign, commit,
outreach, publication or fees. Continue ready work after this unit.
