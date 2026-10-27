# TableFormer loader and configuration consumers

10 October 2026. E14/C07; MC23, MC25, MC30–35. Source inspection candidate:
`docling-ibm-models` 4.0.2, commit
`d1569fdffee1d09cb3111d6d5490991cb59d59fd`. This is the lower bound declared by
the retained Docling source, not a solved deployment lock. PyPI metadata, tag,
complete Git tree and thirteen source bodies are retained. Each source body
matches its upstream Git blob. `source-anchors.json` records twelve complete
method ranges; the observations below also identify the short module-level
declarations inspected. No upstream module was imported or executed.

The pinned Docling `TableStructureModel.__init__` selects accurate or fast,
reads that folder's `tm_config.json`, inserts `model.save_dir` and constructs
`TFPredictor`. The retained caller is in the preceding model-path unit at
`sources/docling__models__stages__table_structure__table_structure_model.py`,
lines 39–96. This is an inspected source path; installed call-chain wiring and
compatibility remain **not checked**.

`TFPredictor._load_model`, lines 173–213, constructs `TableModel04_rs` before
loading its state. It glob-matches `tableformer_*.safetensors` in `save_dir`
and takes element zero. An empty list raises; two matches are not rejected or
sorted here. The retained upstream inventory has one table weight in each
separate accurate/fast folder. The risk therefore concerns an ambiguous local
folder, not evidence of an ambiguous upstream bundle. A later adapter must
check exactly one expected matching file, verify its local content hash
against the declared asset record and preserve the config/hash pairing before
constructing the predictor. Successful state-key loading would not establish
that the intended weights were loaded. The separate `BaseModel.load` training
checkpoint routines are not invoked by this inference loader.

`Encoder04.__init__`, lines 17–35, calls `torchvision.models.resnet18()` without
an explicit weights or pretrained argument. That delegates the initialisation
choice to the selected torchvision version. The declared `>=0,<1` range does
not identify that version. Whether this call downloads a backbone is **not
checked** across that unresolved range. Likewise, the exact safetensors loader
semantics are not established by reading this caller. No global no-download
claim follows from this inspection.

The package imports `cv2` at predictor module line 10 but lists OpenCV only in
two optional extras (`pyproject.toml`, lines 45–47). The README instructs the
installer to choose one; the uv configuration declares the pair conflicting.
The earlier Docling proposals request bare `docling-ibm-models`. Future
dependency resolution must explicitly provide one OpenCV distribution; a
headless provider is a proposal for non-GUI use, not an installed default.
This does not prove that a complete installation would fail: another dependency
may already supply OpenCV. The seven base requirements include Transformers,
which explains a transitive declaration missing from the direct Docling list.
No resolver, package installation or wheel inspection ran.

Configuration consumers differ from their labels. `TableModel04_rs.__init__`,
lines 25–87, reads `train.bbox` during inference construction and caches
`predict.max_steps`. The wrapper reads and passes both `max_steps` and
`beam_size`, but the complete model `predict` method, lines 110–328, does not
read its formal `max_steps` or `k` arguments. It uses the cached step limit and
`logits.argmax(1).item()`. Thus the retained `beam_size=5` declaration does
**not** establish beam search in this exact implementation. Changing the
method argument alone does not change the inspected stopping bound.

Both retained configs have `train.bbox=true` and `predict.bbox=true`. If the
first is false, the inspected method sets both outputs to `None` and then calls
`.to` on them. That branch is wrong for a claim of supported bbox-free inference;
the source establishes the invalid operation, while its runtime manifestation
was not exercised. Keep the inspected true/true configuration as the candidate
scope and reject unsupported alternatives in future preflight. Do not delete
the `train` section on the assumption that it is irrelevant at inference time.

`common.validate_config`, lines 15–44, returns true if `model` or `preparation`
is absent. The retained inference configs lack `preparation`, so this validator
does not establish their inference completeness. `TFPredictor` uses the embedded
word map unless `dataset.prepared_data_dir` is supplied. The latter selects an
additional local JSON file. Local preflight must account for that branch and
all actual constructor inputs. No claim of exhaustive config validation follows
from the checks in this unit.

The complete constructors of CellMatcher, MatchingPostProcessor, Tag_Transformer
and BBoxDecoder were read. CellMatcher consumes `pdf_cell_iou_thres`; the
postprocessor creates another matcher. The decoder constructors call further
helpers in `utils.utils` and PyTorch. Image preparation invokes Normalize and
Resize, transposes axes and divides by 255. The retained transforms delegate
numerics to `data_management.functional`, which was not inspected in this unit.
These are explicit remaining consumer boundaries, not evidence of numerical
equivalence or preprocessing correctness. Matching and postprocessing algorithms
outside the inspected ranges likewise remain unreviewed.

The complete MIT text retains IBM's 2024 copyright, notice-inclusion condition
and warranty disclaimer. It applies to the code under that notice. The preceding
model card's CDLA-Permissive-2.0 declaration has a separate subject; code licence
inspection does not admit model distribution. Neither the TableFormer paper nor
its benchmark claims were assessed here.

Version 2.26 already requires code, dependency, model/preprocessing identities,
verified local files and explicit download policy in Section 13.13. Its generic
statement does not claim beam search or bbox-free inference. These version-specific
requirements belong in this supporting preparation record; no reader-facing
revision is needed for the bounded findings above.
