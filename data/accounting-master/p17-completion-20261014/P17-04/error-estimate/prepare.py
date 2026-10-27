"""One-shot protection of 2.91 and creation of the 2.92 source candidate."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
OLD=ROOT/'docs/design/proposal/manuscript-sector-revision-20261014'
NEW=ROOT/'docs/design/proposal/manuscript-error-estimate-20261014'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='a45c9368d89a10981010a60513ad2fce2508c9b6ce0cb964815a6cef63ff077f'
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
    q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.91','Version 2.92'))
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor=r'\input{sections/ppe-operations}'
assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/error-estimate}'))
print(json.dumps({'protected_sources':len(sources),'candidate':str(NEW.relative_to(ROOT))}))
