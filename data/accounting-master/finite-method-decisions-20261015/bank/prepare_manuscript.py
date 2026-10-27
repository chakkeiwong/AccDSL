"""Create the protected 2.98 successor once."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
OLD=ROOT/"docs/design/proposal/manuscript-insurance-valuation-20261015"
NEW=ROOT/"docs/design/proposal/manuscript-bank-restructuring-20261015"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="2509f4a325ca8921fe7141a53792daebfeafc5aea85ea6c2969a99e3fd1425d6"
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
assert "Version 2.97" in p.read_text()
p.write_text(p.read_text().replace("Version 2.97","Version 2.98"))
p=NEW/"sections/bank-methods.tex"
s=p.read_text()
for anchor,name in [
    ("\\newpage\n\\hypertarget{funding-capital-and-decision-policies}", "bank-restructuring"),
    ("A RegulatoryAssessment reads an accounting view", "bank-funding-settlement")]:
    assert s.count(anchor)==1
    s=s.replace(anchor,"\\input{sections/"+name+"}\n\n"+anchor)
p.write_text(s)
print(json.dumps({"candidate":str(NEW.relative_to(ROOT)),"protected_sources":len(sources)}))
