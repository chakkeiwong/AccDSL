# Exact EasyOCR English asset and loader review

11 October 2026. E14/C07; MC23, MC25, MC30–35. The inspected candidate is
EasyOCR 1.7.2, official tag `v1.7.2`, commit
`c4f3cd7225efd4f85451bd8b4a7646ae9a092420`. PyPI metadata and `setup.py`
agree on the version. The official tree is complete. Twelve retained source
bodies match Git blobs. Three complete Reader method ranges and module-level
config, release and loader lines are retained. This exact candidate is within
Docling's declared `>=1.7,<2.0` range; it is not an installed or recommended
lock. No source module or model was executed.

Docling's pinned `EasyOcrModel.__init__`, lines 214–230, passes native `en`,
`recog_network=standard`, its model directory and `download_enabled` into
`easyocr.Reader`. When an artifact path is supplied but the option's model
directory is absent, Docling substitutes an `EasyOcr` subfolder and disables
downloads. The proposed non-executable configuration supplies its own directory
and false download flag; that separate directory takes precedence. The Reader
constructor defaults `detect_network=craft`. Its `['en']` standard branch
selects `recognition_models['gen2']['english_g2']`, not `latin_g2`.

The exact selected release assets are:

| Role | Local filename | Source release | Archive bytes | Upstream MD5 for extracted file |
| --- | --- | --- | ---: | --- |
| Detector | `craft_mlt_25k.pth` | `pre-v1.1.6`, `craft_mlt_25k.zip` | 77,251,756 | `2f8227d2def4037cdb3b34389dcf9ec1` |
| Recognizer | `english_g2.pth` | `v1.3`, `english_g2.zip` | 14,040,947 | `5864788e1821be9e454ec108d61b887d` |

The official GitHub release metadata confirms the named archive assets and
sizes but gives no digest. The MD5 strings come from pinned `easyocr/config.py`
for **extracted** files, not archive hashes. No archive or checkpoint bytes were
downloaded, so neither MD5 nor SHA-256 has been checked locally. MD5 is the
upstream compatibility check, not an adequate provenance assertion for
untrusted bytes. A later local asset record needs trusted acquisition origin and
an independently recorded strong hash before the checkpoint is loaded.

Reader creates both `model_storage_directory` and a separate
`user_network_directory`; it appends the latter to `sys.path` even when the
standard recognizer is selected. Setting `download_enabled=False` does not make
the constructor read-only. The model selection branches raise `FileNotFoundError`
for absent or MD5-mismatched selected files when downloads are disabled. If
downloads are enabled, they retrieve ZIPs and check extracted MD5. Docling's
`download_models` helper has different behaviour: its defaults include CRAFT,
English and **Latin** recognition files; it skips any existing file without
checking a hash. Prefetch and Reader selection must not be conflated.

The pinned package contains `character/en_char.txt` and `dict/en.txt` in its
source tree. Reader references them via `BASE_PATH`, and `MANIFEST.in` declares
the character/dictionary directory patterns. The actual built wheel/sdist was
not inspected, so package inclusion at install time is unverified. The Reader
uses these files during character setup/recognizer construction; a local weight
folder alone is not the complete runtime input.

Both selected checkpoint loaders call `torch.load(..., weights_only=False)`
(`detection.py` lines 74–85 and `recognition.py` lines 153–184). Therefore a
matching MD5 is not a safe trust boundary for arbitrary local checkpoint bytes.
Future runtime work must use a trusted source and independent byte identity;
the current review neither installs nor deserializes the files. Exact PyTorch
dependency versions remain unsolved. PyPI and pinned `requirements.txt` declare
twelve dependencies with no version bounds other than
`torchvision>=0.5`; these are declarations, not a resolved installation.

The package source and PyPI metadata declare Apache License 2.0, and the full
agreement is retained. The README credits an external CRAFT implementation and
pretrained model. Neither release metadata body provides a standalone model
license or checksum. The code licence cannot be silently extended to both
model weights or to their redistribution. Upstream CRAFT rights and intended
distribution conditions remain a separate E14 source question. No paid or
professional review is needed before finishing feasible source research.

Section 13.13 of Version 2.26 already requires engine/model identity, verified
local files, explicit download policy and unresolved page outcomes. It does not
claim that this EasyOCR setup has run. The exact file, dependency and trust
requirements belong in this supporting record; no manuscript change is needed
for this bounded unit. OCR quality on the accounting corpus remains untested.
