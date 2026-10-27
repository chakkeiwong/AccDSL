"""Create 2.95 once, preserving every predecessor source and PDF byte."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-corporate-portable-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-real-package-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='38c4edc2c7508e303be5c05e894768e3ab14be7c0653ae6b7cce28ded8b23a43'
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert json.loads((OUT/'independent-checks.json').read_text())['passed']
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 target=NEW/p.relative_to(OLD);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';assert 'Version 2.94' in p.read_text();p.write_text(p.read_text().replace('Version 2.94','Version 2.95'))
p=NEW/'chapters/13-reference-company.tex';p.write_text(p.read_text()+'\n\\input{sections/real-package-connection}\n')
p=NEW/'chapters/17-portable-reference.tex';s=p.read_text();anchor=r'\hypertarget{source.prepare1}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,r'\input{sections/real-package-reference}'+'\n\n'+anchor))
print(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'protected_sources':len(sources)}))
