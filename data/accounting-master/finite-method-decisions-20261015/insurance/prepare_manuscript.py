"""Create the protected 2.97 successor once; preserve every old source byte."""
from pathlib import Path
import hashlib, json, shutil, subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
OLD=ROOT/"docs/design/proposal/manuscript-financing-changes-20261015"
NEW=ROOT/"docs/design/proposal/manuscript-insurance-valuation-20261015"
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="10af497755650076da3ee4516cea72359528ba09aedef3a1082f97e800dc00a4"
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert json.loads((OUT/"independent-checks.json").read_text())["passed"]
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    target=NEW/p.relative_to(OLD)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,target)
(OUT/"manuscript-baseline.json").write_text(json.dumps({
    "baseline_pdf":str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),
    "baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),
    "candidate":str(NEW.relative_to(ROOT)),
    "source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]
},indent=2)+"\n")
p=NEW/"accounting-product-proposal.tex"
assert "Version 2.96" in p.read_text()
p.write_text(p.read_text().replace("Version 2.96","Version 2.97"))
p=NEW/"sections/insurance-methods.tex"
s=p.read_text()
for anchor,name in [
    ("The claims-development example above supplies an estimation input", "insurance-priced-guarantee"),
    (r"\section{Reading acquisition costs in an actual report}", "insurance-acquisition-treaty")
]:
    assert s.count(anchor)==1
    s=s.replace(anchor,r"\input{sections/"+name+"}\n\n"+anchor)
s=s.replace("The preceding example supplied the acquisition assets and the net inflows",
            r"Section~\ref{sec:insurance-acquisition-incorporation} supplied the acquisition assets and the net inflows")
p.write_text(s)
print(json.dumps({"candidate":str(NEW.relative_to(ROOT)),"protected_sources":len(sources)}))
