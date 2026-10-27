# EDD dependency and supplement result

19 October 2026. P15/P17/P19; MC01–05/23/26/28–35.
Decision: admit the bounded documentary/static findings; retain runtime and
scientific acceptance as unestablished. No manuscript change or whole-row closure.

Six official acquisitions are retained: four EDD files at
e6bb2bd509d7c89cdf1fb9608f9db9a044413bed, the ECVA index, and its actual
linked six-page supplement. The index matches title/authors and the main-paper
identifier. All four files and all supplement text were read. Rendered physical
pages 3–4 confirm Tables S1–S3 and their conditions. The large index was searched
only for the relevant entry. The predecessor's targeted main-paper inquiry is
not silently expanded into a full transitive implementation audit.

The loader uses .hdf5, matching preparation. The README's .h5 wording therefore
does not establish a loader incompatibility. The selected training loop uses
the iterator, whose final incomplete batch appends raw indices range(lack).
For a fictional permutation [4,3,2,1,0] and batch size 4, the batches are
[4,3,2,1] and [0,0,1,2], not a shuffled-prefix continuation. A one-item,
batch-size-four illustration produces indices 1 and 2 outside the dataset.
These are source-derived arithmetic examples; no actual dataset failure was
observed. The separate __getitem__ path references self.imgsizes, absent from
the inspected initializer; the selected loop does not call that path.

CustomConfig has identical Python AST to the earlier pinned PubTabNet metric:
normalised cell-token edit distance and tag/span relabel costs agree at that
syntax boundary. Whole implementations differ. EDD uses a global token
accumulator, parsed-root inputs and a wrapper without the earlier explicit
comment-removal parser/ignore-node option. Both count raw table descendants
for the denominator. No installed parser, edit-distance library, concurrency
behavior or full-input equivalence was checked. Reverse zip insertion in
format_html supplies no explicit equal-cell-count assertion.

Supplement C specifies thresholds 0.5,0.6,0.7,0.8,0.9 for Table S1. The pinned
relation_metric default is linspace(0.6,0.95,8), whose ideal decimal grid is
0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95. The grids differ. The rational witness
records ideal decimal endpoints, not literal IEEE NumPy results. An explicit
caller override could reconcile the settings; no inspected artifact identifies
the settings that generated the published table. The external Java evaluator
and parallel.py remain uninspected. The metric file's SSH demonstration was
read as text and never run.

Supplement D/Table S2 reports 13.7 minutes for TEDS evaluation of EDD outputs
using 28 parallel threads on a 28-core Xeon Platinum 8280M at 2.70 GHz. It is
not EDD inference or training time. Table S3 reports validation TEDS for five
encoder settings: S1 87.9, S2 83.3, S1S1 88.4, S2S1 88.1 and S2S2 85.4
(all-table column). These are descriptive source results. No local replication,
interval or seed comparison supports a ranking here. Sections A/B/F supply
perturbation, synthetic-style and attention examples. The supplement supplies
no correction to the previously identified split-population or TEDS wording.
Its four references are triaged, not technically read through this inquiry.

Helpers clamp each gradient element, save seven selected checkpoint fields
without RNG state, use private PyTorch parallel APIs, and assume a channel
dimension during image conversion. The requirements list four minimum bounds
and five unpinned packages; it does not identify the published environment.
NumPy is imported but not directly listed; transitive installation is unknown.
These are reproduction assumptions, not measured training failures.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept scoped source account | Six receipts,25 anchors,92 assertions pass | No protection/identity veto; six altered finite controls rejected | Dependency/runtime behavior | Preserve source observations and exact limits | Model or metric replication |
| Repair extension concern | Preparation and actual loader both use .hdf5 | Old README inference rejected | Other paths and environment | Replace incompatibility claim with documentation mismatch | All loading succeeds |
| Retain threshold discrepancy | Printed five-grid differs from eight-grid default | Whole-setting equivalence vetoed | Caller settings used for publication | Require explicit threshold provenance for reproduction | Published scores invalid |
| Preserve candidate 3.44 | No new contradiction in existing extraction qualifications | No manuscript-specific defect established | Broader literature/independent acceptance | Continue a distinct ready source gap | Survey or proposal complete |

| Inference status | Finding |
|---|---|
| Hard veto screen | No local stochastic experiment. Incorrect timing, whole-metric-equivalence and default-threshold-equivalence claims are unsupported or wrong as stated. |
| Statistically supported ranking | None established. |
| Descriptive-only differences | Published encoder and adjacency scores; source timings under their stated setup. |
| Default-readiness | No model, metric, dependency or protocol default promoted. |
| Next evidence needed | Exact experimental revision/settings/environment, checked transitive implementation, and a target-specific downstream protocol with uncertainty before any ranking. |

Engineering record: standard-library source parsing/index arithmetic passes;
no acquired code imported. Numerical/sampler validity: not evaluated.
Scientific interpretation: the narrow source observations hold; transfer to
whole financial reports, unit/entity/period correctness and accounting validity
remains unestablished. The strongest alternative explanation for threshold
drift is an explicit override or a different historical revision. A matching
experiment manifest would resolve it. Runtime results could overturn inferred
operational concerns, but cannot change the recorded source syntax.

Commands actually run in this continuation: pdftoppm -f 3 -l 4 -r 100 -png
on the retained supplement; the standard-library build_records.py once; and
verify.py --check once, with CUDA_VISIBLE_DEVICES=-1 and the tfgpu python3.
The inherited acquisition commands/timings are individually transcribed in
source-ledger.json. run-manifest.json records lifecycle, Git/environment and
elapsed time. The exact 3.44 PDF, frozen 53 obligations/six interactions/
46 operations, HEAD, index and unrelated 36 dirty paths remain protected.
