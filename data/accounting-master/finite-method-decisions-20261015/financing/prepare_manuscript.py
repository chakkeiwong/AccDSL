"""Create 2.96 once, preserving every predecessor source and PDF byte."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
OLD=ROOT/'docs/design/proposal/manuscript-real-package-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-financing-changes-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='fc496a3d2bb1b6453e474afbfe8ca6742ced3ecbec460bf6672bbe85a665c2c8'
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert json.loads((OUT/'independent-checks.json').read_text())['passed']
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 target=NEW/p.relative_to(OLD);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';assert 'Version 2.95' in p.read_text();p.write_text(p.read_text().replace('Version 2.95','Version 2.96'))
p=NEW/'chapters/14-financing-groups.tex';s=p.read_text();anchor=r'\section{Control and an elimination book}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,r'\input{sections/financing-changes}'+'\n\n'+anchor))
print(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'protected_sources':len(sources)}))
