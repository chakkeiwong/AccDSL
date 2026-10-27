"""Bind the final affected bank pages to the candidate PDF."""
import hashlib
import json
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / "docs/design/proposal/manuscript-parent-cash-20261012/accounting-product-proposal.pdf"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory = OUT / "rendered"
    directory.mkdir(exist_ok=True)
    rows = []
    with fitz.open(PDF) as doc:
        assert len(doc) == 174
        for n in range(115, 127):
            path = directory / f"page-{n}.png"
            doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(path)
            rows.append({"pdf_page": n, "image": str(path.relative_to(ROOT)), "sha256": sha(path)})
    manifest = {"pdf": str(PDF.relative_to(ROOT)), "pdf_sha256": sha(PDF), "pages": 174, "scale": 1.35, "renders": rows}
    (OUT / "render-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"pdf_sha256": manifest["pdf_sha256"], "pages": manifest["pages"], "renders": len(rows)}))


if __name__ == "__main__":
    main()
