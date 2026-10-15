from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-insurance-branches-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-company-composition-20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='ff035c08ffaa7c70f6e086bb85a05a019ec43db00057da76d264270633b11f15'
assert json.loads((P/'attempt-03/validation-01.json').read_text())['failed']==0
assert not NEW.exists()
files=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in files:
 target=NEW/p.relative_to(OLD);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
baseline=dict(pdf=str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),pdf_sha256=sha(OLD/'accounting-product-proposal.pdf'),
 candidate=str(NEW.relative_to(ROOT)),source_files=[dict(path=str(p.relative_to(OLD)),sha256=sha(p)) for p in files])
(P/'manuscript-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 3.13 (proposal candidate) \quad 15 October 2026','Version 3.14 (proposal candidate) \quad 16 October 2026'))
for name,anchor,addition in [
 ('chapters/13-reference-company.tex',r'\section{Apple: source labels do not identify exposure}',r'\input{sections/company-composition}'),
 ('chapters/08-modules.tex',r'\input{sections/standards-methods}',r'\input{sections/corporate-residual-transitions}'),
 ('chapters/17-portable-reference.tex',r'\input{sections/real-package-reference}',r'\input{sections/company-composition-reference}')]:
 p=NEW/name;s=p.read_text();assert s.count(anchor)==1;p.write_text(s.replace(anchor,addition+'\n\n'+anchor))
print(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'protected_sources':len(files)}))
