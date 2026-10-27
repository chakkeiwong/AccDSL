"""Freeze 2.90 and prepare a scoped documentary successor."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
OLD=ROOT/"docs/design/proposal/manuscript-eps-lifecycle-20261014"
NEW=ROOT/"docs/design/proposal/manuscript-sector-revision-20261014"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="80fe67ccd17dfc412eaf2db7b52035a158bff9c53485e41b33b00dc70cd27120"
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/"manuscript-baseline.json").write_text(json.dumps({"baseline_pdf":str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),"baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),"candidate":str(NEW.relative_to(ROOT)),"source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]},indent=2)+chr(10))
p=NEW/"accounting-product-proposal.tex";p.write_text(p.read_text().replace("Version 2.90","Version 2.91"))
p=NEW/"chapters/02-history.tex";s=p.read_text()
anchor=r"\input{sections/source-admission}"
assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+chr(10)+chr(10)+r"\input{sections/sector-revision}"))
print(json.dumps({"protected_sources":len(sources),"candidate":str(NEW.relative_to(ROOT))}))
