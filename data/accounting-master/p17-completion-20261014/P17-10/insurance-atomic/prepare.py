"""Freeze predecessor and prepare scoped 2.88 source tree."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
OLD=ROOT/"docs/design/proposal/manuscript-reserving-adapter-20261014"
NEW=ROOT/"docs/design/proposal/manuscript-insurance-atomic-20261014"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="1af3ff838342d23e23924a2d5b2fe0038fb3f07a502e81c99212a3144fd11742"
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
p.write_text(p.read_text().replace("Version 2.87","Version 2.88"))
p=NEW/"sections/insurance-methods.tex"
s=p.read_text(); assert s.count(r"\input{sections/insurance-connected-groups}")==1
p.write_text(s.replace(r"\input{sections/insurance-connected-groups}",
   "\\input{sections/insurance-connected-groups}\n\\input{sections/insurance-atomic}"))
print(json.dumps({"protected_sources":len(sources),"candidate":str(NEW.relative_to(ROOT))}))
