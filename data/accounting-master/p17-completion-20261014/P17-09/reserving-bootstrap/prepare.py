"""Prepare documentary evidence; no stochastic fitting or production runtime."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
OLD=ROOT/'docs/design/proposal/manuscript-query-resolution-20261014'
NEW=ROOT/'docs/design/proposal/manuscript-reserving-bootstrap-20261014'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2)+'\n')
assert sha(OLD/'accounting-product-proposal.pdf')=='12979f23fbac7ea69d3b2fe55917e8fd6a1a4e3d15243c4e455effc3c9a87943'
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
save(OUT/'manuscript-baseline.json',{'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]})
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.84','Version 2.85'))
snap=OUT/'before';snap.mkdir()
for name in ['source-support','claim-support','backward-snowball','forward-snowball','citation-venue','omissions']:
 shutil.copy2(ROOT/('docs/design/research/'+name+'.json'),snap/(name+'.json'))
papers=[('england2001-addendum.pdf','Addendum to Analytic and Bootstrap Estimates of Prediction Errors in Claims Reserving England (2001).pdf'),('england2019-lifetime.pdf','On the Lifetime and One-Year Views of Reserve Risk England (2019).pdf')]
for src,dst in papers:
 p=OUT/'sources'/src;assert p.read_bytes().startswith(b'%PDF');q=ROOT/'docs/papers'/dst;assert not q.exists();shutil.copy2(p,q)
save(OUT/'source-manifest.json',{'date':'2026-10-14','sources':[{'path':str((ROOT/'docs/papers'/dst).relative_to(ROOT)),'sha256':sha(ROOT/'docs/papers'/dst)} for _,dst in papers],'notes':'Institutional2001 working version and2019 accepted manuscript; not exact-version equivalence to journal articles. Raw failed retrieval bodies preserved.'})
print(json.dumps({'protected_sources':len(sources),'candidate':str(NEW.relative_to(ROOT)),'ledgers_preserved':6}))
