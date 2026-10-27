"""Freeze predecessor and prepare scoped 2.87 source tree."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
OLD=ROOT/"docs/design/proposal/manuscript-bootstrap-consistency-20261014"
NEW=ROOT/"docs/design/proposal/manuscript-reserving-adapter-20261014"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="0ce798be2097f362b76935d46fe185878a362a4d18e317caac3b296dfa751303"
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    q=NEW/p.relative_to(OLD); q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,q)
(OUT/"manuscript-baseline.json").write_text(json.dumps({
 "baseline_pdf":str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),
 "baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),"candidate":str(NEW.relative_to(ROOT)),
 "source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]},indent=2)+"\n")
p=NEW/"accounting-product-proposal.tex"
p.write_text(p.read_text().replace("Version 2.86","Version 2.87"))
p=NEW/"sections/insurance-methods.tex"
s=p.read_text(); assert s.count(r"\input{sections/bootstrap-consistency}")==1
p.write_text(s.replace(r"\input{sections/bootstrap-consistency}",
   "\\input{sections/bootstrap-consistency}\n\\input{sections/reserving-adapter}"))
print(json.dumps({"protected_sources":len(sources),"candidate":str(NEW.relative_to(ROOT))}))
