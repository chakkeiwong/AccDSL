"""Bind a static source reading; never import or execute retained upstream code."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import time

started = time.perf_counter()
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = "docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/arelle__ModelInstanceObject.py"
EXPECTED = "097d4c252ea800c55c221eb67f9694ca689ee5c7bcd19ae38698941f966e8059"
PDF = "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"
PDF_HASH = "afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80"

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

assert digest(SOURCE) == EXPECTED, "Pinned upstream source changed"
assert digest(PDF) == PDF_HASH, "Reading candidate changed"
selection_path = "data/accounting-master/selected-reuse-20261015/source-selection.json"
selection = json.loads((ROOT / selection_path).read_text())
assert selection["selected_native"]["commit"] == "01f6a4656c2c6551d2f05f31c9d74366d133ee7e"
assert selection["selected_native"]["options"]["entrypointFile"] == "archive/aapl-20240928_htm.xml"
lines = (ROOT / SOURCE).read_text().splitlines(keepends=True)
spans = [
    (392, 400, "def value(self)"),
    (308, 346, "fixedOrDefaultAttrValue"),
    (349, 368, "defaultXmlLang"),
    (370, 376, "def isNil(self)"),
    (413, 456, "roundValue"),
    (403, 410, "def fractionValue(self)"),
    (680, 697, "collapseWhitespace"),
    (700, 766, "num *= negate"),
]
anchors = []
for first, last, marker in spans:
    excerpt = "".join(lines[first - 1:last])
    assert marker in excerpt, (first, last, marker)
    anchors.append({"first_line": first, "last_line": last,
                    "sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
                    "marker": marker})
inputs = [SOURCE, selection_path,
          "data/accounting-master/selected-reuse-20261015/exchanges.json",
          "data/accounting-master/selected-reuse-20261015/exchange-envelope.schema.json",
          "data/accounting-master/selected-reuse-20261015/manuscript-insert.md",
          "data/accounting-master/source-protocol-reuse-refresh-20261016/reuse-successor.md",
          "docs/plans/accounting-reuse-field-boundary-20261018.md"]
result = {
    "schema": "StaticSourceBoundaryManifest/1", "date": "2026-10-18",
    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "command": "python3 data/accounting-master/reuse-field-boundary-20261018/verify_boundary.py",
    "environment": {"python": platform.python_version(), "libraries": "stdlib only; no upstream code imported"},
    "cpu_gpu": "CPU-only static file inspection; no scientific framework imported or GPU accessed",
    "data_version": "selected Arelle commit 01f6a4656c2c6551d2f05f31c9d74366d133ee7e",
    "random_seeds": "N/A: deterministic documentary integrity check",
    "inputs": [{"path": p, "sha256": digest(p)} for p in inputs],
    "anchors": anchors,
    "candidate": {"path": PDF, "sha256": PDF_HASH, "disposition": "unchanged"},
    "result": {"path": str((OUT / "source-boundary.md").relative_to(ROOT)),
               "sha256": digest(str((OUT / "source-boundary.md").relative_to(ROOT)))},
    "script_sha256": digest(str(Path(__file__).relative_to(ROOT))),
    "wall_seconds": time.perf_counter() - started,
    "status": "static bindings checked; runtime translation and acceptance pending",
}
(OUT / "run-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print("Pinned source/candidate and eight excerpt bindings verified; no runtime or manuscript change.")
