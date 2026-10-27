# Exact TableFormer package and loader preparation

10 October 2026. E14/C07; MC23/30–35; G8/G9/G10/G14/G17.
Question: how does an exact `docling-ibm-models` candidate load the now-inventoried
TableFormer configuration/weights, and which further source/dependency/terms
obligations follow? Baseline: frozen Docling source and model metadata units,
Version 2.26; declared dependency `>=4.0.2,<5`. Inspect 4.0.2 as the upstream
lower-bound hypothesis, not as an installed, recommended or historically used
version. If it cannot compute the caller's intended operation, record that
mismatch and inspect a justified repair rather than silently changing baseline.

Primary criterion: official version metadata, exact source tag/commit and
licence, complete relevant `TFPredictor` constructor, checkpoint selection,
backbone initialization and dependency declarations with retained anchors.
Promotion vetoes: tag/version mismatch; treating a range or lower bound as a
solved lock; assuming a filename is used without checking its consumer; source
inspection presented as inference or GPU evidence. Continuation veto: corrupted
baseline or unavailable source necessary to the specific claim; restrict that
claim and continue independent work. Diagnostics are source branches/imports
only. No runtime, quality, speed, complete transitive lock or distribution claim.
Artifact: `data/accounting-master/tableformer-loader-20261010/`.

Skeptical/default audit: the lower bound may no longer match the caller or
current weights. Verify version identity and checkpoint format before inspecting
further internals. PyPI metadata is a declaration, not executed wheel evidence.
Use the official repository URL from metadata, resolve its tag to a commit, and
verify source Git blobs where available. A code MIT label cannot be extended to
model weights. Existing exact model config/hash metadata remains separate from
local bytes. These safeguards make the bounded plan answer its stated source
question without a proxy promotion criterion.

Execution: verify 1485 prior references and preserve four live pointers. Retrieve
version-specific PyPI JSON (metadata only), exact official Git tag/tree and
relevant source text, at most 16 distinct URLs, 1 MB and 45 seconds per request.
No wheel/sdist, installation, model weight, model import, GPU or extraction.
Source routes follow metadata/tree/imports; no guessed unchanged retries.
One trusted retry is allowed after a sandbox network failure; other failures
need a new premise. Use existing CPU Python with CUDA_VISIBLE_DEVICES=-1.
Read full relevant methods, trace their callers and report unresolved downstream
consumers. Record evidence and limitations, update controls and freeze results;
integrate prose only if a material current omission is found. Continue to exact
OCR assets or other feasible tasks after closeout.

Pre-mortem: `pretrained=False` may apply to one branch but not another, or a
constructor may load a backbone before its table checkpoint. Inspect the actual
branch and preserve its conditions. File-existence checks may silently choose
the wrong checkpoint; compare candidate selection to the retained two-weight
inventory and keep model-content verification open.

Resume audit, 10 October: HEAD, branch `main`, active controls and pending unit
agree with the handoff. The checkpoint glob selects its first match; the base
package declares OpenCV only as an extra despite the predictor's direct import.
Finish the constructor helpers and image/config consumers within the remaining
five source URLs. Keep torchvision and safetensors semantics explicitly
unresolved until an exact dependency candidate is inspected. No source-only
check will be described as executed inference or runtime call-chain validation.
The plan survives this audit: source identity and local preparation obligations
are answerable without installing the candidate or weakening the runtime hold.
