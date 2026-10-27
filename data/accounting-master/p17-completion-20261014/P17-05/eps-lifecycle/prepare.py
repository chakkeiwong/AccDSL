"""Freeze 2.89 and prepare a scoped documentary successor."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
OLD=ROOT/"docs/design/proposal/manuscript-bank-prudential-20261014"
NEW=ROOT/"docs/design/proposal/manuscript-eps-lifecycle-20261014"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="cee2973969d744c36890c032adb04154efbadf7ee595c342465711245cfc8086"
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/"manuscript-baseline.json").write_text(json.dumps({"baseline_pdf":str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),"baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),"candidate":str(NEW.relative_to(ROOT)),"source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]},indent=2)+chr(10))
p=NEW/"accounting-product-proposal.tex";p.write_text(p.read_text().replace("Version 2.89","Version 2.90"))
p=NEW/"chapters/14-financing-groups.tex";s=p.read_text()
anchor=r"\input{sections/apple-eps-ownership}"
assert s.count(anchor)==1
p.write_text(s.replace(anchor,r"\input{sections/eps-lifecycle}"+chr(10)+chr(10)+anchor))
print(json.dumps({"protected_sources":len(sources),"candidate":str(NEW.relative_to(ROOT))}))
