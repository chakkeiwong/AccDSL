"""Retain bounded Note 33 source pages; never overwrite a completed unit."""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf"
EXPECTED = "e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    assert not (OUT / "source-manifest.json").exists(), "Preserve retained extraction"
    assert sha(PDF) == EXPECTED, "Source identity mismatch"
    (OUT / "sources").mkdir(exist_ok=True)
    (OUT / "rendered").mkdir(exist_ok=True)
    (OUT / "pointers-before").mkdir(exist_ok=True)
    pointers = []
    for rel in ["docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md", "docs/plans/accounting-continuation-requirements-20261007.md", "data/accounting-master/next-plan.md"]:
        source = ROOT / rel
        target = OUT / "pointers-before" / source.name
        assert not target.exists()
        shutil.copyfile(source, target)
        pointers.append({"live": rel, "snapshot": str(target.relative_to(ROOT)), "sha256": sha(target)})
    rows = []
    with fitz.open(PDF) as doc:
        funding = [i + 1 for i in range(50) if "The Parent Company, JPMorgan Chase & Co., is a" in doc[i].get_text()]
        assert len(funding) == 1, funding
        assert "Note 33" in doc[311].get_text() and "Parent Company" in doc[311].get_text()
        assert "Statements of cash flows" in doc[312].get_text()
        for n in sorted(funding + [312, 313]):
            page = doc[n - 1]
            reading = OUT / "sources" / f"page-{n}-reading.txt"
            layout = OUT / "sources" / f"page-{n}-layout.txt"
            render = OUT / "rendered" / f"page-{n}.png"
            reading.write_text(page.get_text())
            command = ["pdftotext", "-f", str(n), "-l", str(n), "-layout", str(PDF.relative_to(ROOT)), str(layout.relative_to(ROOT))]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(render)
            rows.append({"pdf_page": n, "printed_page": n - 2, "reading": str(reading.relative_to(ROOT)), "reading_sha256": sha(reading), "layout": str(layout.relative_to(ROOT)), "layout_sha256": sha(layout), "render": str(render.relative_to(ROOT)), "render_sha256": sha(render), "command": command})
    candidate = ROOT / "docs/design/proposal/manuscript-historical-credit-loss-20261012/accounting-product-proposal.pdf"
    manifest = {"source_pdf": str(PDF.relative_to(ROOT)), "source_pdf_sha256": EXPECTED, "edition": "Issuer-hosted 2025 Form 10-K; current selected bytes, historical availability not established", "candidate_pdf": str(candidate.relative_to(ROOT)), "candidate_pdf_sha256": sha(candidate), "pages": rows, "pointer_snapshots": pointers, "render_engine": "PyMuPDF at 1.35 scale", "wall_seconds": time.monotonic() - start, "funding_pdf_page": funding[0]}
    (OUT / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"pages": [r["pdf_page"] for r in rows], "snapshots": len(pointers), "wall_seconds": manifest["wall_seconds"]}))


if __name__ == "__main__":
    main()
