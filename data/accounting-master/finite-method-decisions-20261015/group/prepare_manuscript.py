"""Create the protected2.99 group-binding successor once."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
OLD=ROOT/"docs/design/proposal/manuscript-bank-restructuring-20261015"
NEW=ROOT/"docs/design/proposal/manuscript-group-bindings-20261015"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/"accounting-product-proposal.pdf")=="39f54220018fececdd6498f28346158dff3115c332dde38b7e15686116e689f0"
assert json.loads((OUT/"independent-checks.json").read_text())["passed"]
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob("*") if p.is_file() and p.suffix in [".tex",".bib",".lark"])
for p in sources:
    dest=NEW/p.relative_to(OLD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(OUT/"manuscript-baseline.json").write_text(json.dumps({
    "baseline_pdf":str((OLD/"accounting-product-proposal.pdf").relative_to(ROOT)),
    "baseline_pdf_sha256":sha(OLD/"accounting-product-proposal.pdf"),"candidate":str(NEW.relative_to(ROOT)),
    "source_files":[{"path":str(p.relative_to(OLD)),"sha256":sha(p)} for p in sources]},indent=2)+"\n")
p=NEW/"accounting-product-proposal.tex";p.write_text(p.read_text().replace("Version 2.98","Version 2.99"))
p=NEW/"sections/groups-fx-methods.tex";s=p.read_text()
anchor="\\input{sections/group-fx-disposal}\n"
assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n\\input{sections/group-bindings}\n"))
print(json.dumps({"candidate":str(NEW.relative_to(ROOT)),"protected_sources":len(sources)}))
