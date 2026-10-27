"""One-shot successor of protected2.92 for the production-cost section."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
OLD=ROOT/'docs/design/proposal/manuscript-error-estimate-20261014'
NEW=ROOT/'docs/design/proposal/manuscript-production-cost-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='6aa8565d8ce7c5bd396355206b7650f8593dfee1cad3a0f7d447a766d77f3af7'
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
    q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+chr(10))
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.92','Version 2.93').replace(r'\quad 14 October 2026',r'\quad 15 October 2026'))
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor=r'\subsection{Inventory and assets retain their cost histories}'
assert s.count(anchor)==1
p.write_text(s.replace(anchor,r'\input{sections/production-cost}'+chr(10)*2+anchor))
print(json.dumps({'protected_sources':len(sources),'candidate':str(NEW.relative_to(ROOT))}))
