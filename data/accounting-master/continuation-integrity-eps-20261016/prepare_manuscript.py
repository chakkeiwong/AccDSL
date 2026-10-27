"""Freeze the complete 3.14 source baseline before making a minimal successor."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/design/proposal/manuscript-company-composition-20261016"
NEXT = ROOT / "docs/design/proposal/manuscript-ordered-eps-20261016"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if NEXT.exists() or (OUT / "baseline-sources").exists():
        raise SystemExit("Successor or protected source snapshot already exists; do not overwrite")
    pdf = BASE / "accounting-product-proposal.pdf"
    assert sha(pdf) == "2d9d1c2bf2eeaa17ea5eb4b1ba5e8c0c95dd33104b4e6a3bcbd7f1211980d94e"
    sources = sorted(p for p in BASE.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".lark"})
    assert len(sources) == 112
    records = []
    for source in sources:
        relative = source.relative_to(BASE)
        snapshot = OUT / "baseline-sources" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, snapshot)
        records.append(dict(path=str(relative), sha256=sha(source), bytes=source.stat().st_size))
    # The source lock exists before any successor generation.
    (OUT / "baseline-source-lock.json").write_text(json.dumps(dict(
        created_utc=datetime.now(timezone.utc).isoformat(), count=len(records),
        baseline=str(BASE.relative_to(ROOT)), candidate_pdf_sha256=sha(pdf), files=records), indent=2) + "\n")
    for source in sources:
        destination = NEXT / source.relative_to(BASE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    main_tex = NEXT / "accounting-product-proposal.tex"
    text = main_tex.read_text()
    assert text.count("Version 3.14 (proposal candidate)") == 1
    main_tex.write_text(text.replace("Version 3.14 (proposal candidate)", "Version 3.15 (proposal candidate)"))
    eps = NEXT / "sections/eps-lifecycle.tex"
    text = eps.read_text()
    anchor = "\\subsection{Actual conversion, expiry and incomplete terms}"
    assert text.count(anchor) == 1
    eps.write_text(text.replace(anchor, "\\input{sections/ordered-eps-method}\n\n" + anchor))
    appendix = NEXT / "chapters/17-portable-reference.tex"
    appendix.write_text(appendix.read_text() + "\n\\input{sections/ordered-eps-records}\n")
    for filename in ("ordered-eps-method.tex", "ordered-eps-records.tex"):
        target = NEXT / "sections" / filename
        assert not target.exists()
        shutil.copy2(OUT / filename, target)
    print(json.dumps(dict(baseline_sources=len(records), successor=str(NEXT.relative_to(ROOT)),
        changed_baseline_files=3, new_sections=2)))


if __name__ == "__main__":
    main()
