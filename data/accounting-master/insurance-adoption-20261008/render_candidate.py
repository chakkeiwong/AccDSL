from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT / "docs/design/proposal/manuscript-adoption-20261008"
if (OUT / "completion.json").exists():
    raise SystemExit("Closed unit")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda name, obj: (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n")
pdf = NEW / "accounting-product-proposal.pdf"
digest = sha(pdf)
doc = fitz.open(pdf)
pages = {1, 5, 6}
for n, p in enumerate(doc, 1):
    text = " ".join(p.get_text().split())
    if any(s in text for s in ["Direct verification of the operative", "This comparison uses identified editions", "Adoption dates and the restatement", "11,137,168", "archive-date leads", "Finally, Note IV.34"]):
        pages.update({n-1,n,n+1})
    if "BIBLIOGRAPHY" in text or text.startswith("Bibliography"):
        pages.add(n)
pages=sorted(n for n in pages if 1<=n<=len(doc))
target=OUT / "render-final"
target.mkdir(exist_ok=False)
rendered={}
for n in pages:
    p=target/f"page-{n:03d}.png"
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p)
    rendered[str(n)]=dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
save("render-manifest.json",dict(recorded_at=datetime.now(timezone.utc).isoformat(),pdf=str(pdf.relative_to(ROOT)),pdf_sha256_before=digest,
     pdf_sha256_after=sha(pdf),pages=len(doc),page_numbers=pages,scale=1.5,rendered_pages=rendered,
     inspection_status="Rendered; actual inspection recorded separately"))
save("build-receipt.json",dict(command="latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex",
     cwd=str(NEW.relative_to(ROOT)),execution="trusted existing LuaLaTeX font cache",exit_code=0,
     log=str((OUT/"build.log").relative_to(ROOT)),log_sha256=sha(OUT/"build.log"),pdf=str(pdf.relative_to(ROOT)),pdf_sha256=digest,pages=len(doc),
     elapsed_time="Not separately measured; unit wall interval in run manifest"))
print(json.dumps(dict(pdf_sha256=digest,pages=len(doc),rendered_pages=pages)))
