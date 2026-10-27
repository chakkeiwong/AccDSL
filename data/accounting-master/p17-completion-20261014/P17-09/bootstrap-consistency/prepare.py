"""Preserve 2.85 and prepare a scoped documentary successor."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
OLD = ROOT / "docs/design/proposal/manuscript-reserving-bootstrap-20261014"
NEW = ROOT / "docs/design/proposal/manuscript-bootstrap-consistency-20261014"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert sha(OLD/"accounting-product-proposal.pdf") == "fa2d2a38f0c9ea2d420f7b346ff8f5496d0d9680b6aa8d89322ef05db82a5638"
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT) == (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert not NEW.exists()
sources = sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    q = NEW/p.relative_to(OLD)
    q.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,q)
baseline = {"baseline_pdf": str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),
            "baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),
            "candidate":str(NEW.relative_to(ROOT)),
            "source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]}
(OUT/"manuscript-baseline.json").write_text(json.dumps(baseline,indent=2)+"\n")
p=NEW/"accounting-product-proposal.tex"
p.write_text(p.read_text().replace("Version 2.85","Version 2.86"))
p=NEW/"sections/insurance-methods.tex"
s=p.read_text()
assert s.count(r"\input{sections/reserving-bootstrap}")==1
p.write_text(s.replace(r"\input{sections/reserving-bootstrap}",
                       "\\input{sections/reserving-bootstrap}\n\\input{sections/bootstrap-consistency}"))
snap=OUT/"before"
snap.mkdir()
for name in ["source-support","claim-support","backward-snowball","forward-snowball","citation-venue","omissions"]:
    shutil.copy2(ROOT/("docs/design/research/"+name+".json"),snap/(name+".json"))
src=OUT/"sources/steinmetz2024-published.pdf"
dst=ROOT/"docs/papers/Bootstrap Consistency for the Mack Bootstrap Steinmetz (2024).pdf"
assert src.read_bytes().startswith(b"%PDF") and not dst.exists()
shutil.copy2(src,dst)
print(json.dumps({"protected_sources":len(sources),"candidate":str(NEW.relative_to(ROOT))}))
