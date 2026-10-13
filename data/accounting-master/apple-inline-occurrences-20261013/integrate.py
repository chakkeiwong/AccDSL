"""Add inline value consequences to a separately preserved candidate."""
import hashlib,json,shutil
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
B=R/'docs/design/proposal/manuscript-arelle-inline-values-20261013'
C=R/'docs/design/proposal/manuscript-apple-inline-occurrences-20261013'
assert not C.exists(),'Candidate already exists; inspect before edits'
assert not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
files={}
for p in B.rglob('*'):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        rel=p.relative_to(B);q=C/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        files[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
p=C/'accounting-product-proposal.tex';t=p.read_text();assert 'Version 2.69' in t;p.write_text(t.replace('Version 2.69','Version 2.70'))
p=C/'sections/adapter-methods.tex';t=p.read_text();anchor=r'\input{sections/arelle-fact-identity}';assert t.count(anchor)==1
p.write_text(t.replace(anchor,anchor+'\n\n'+r'\input{sections/apple-inline-occurrences}'))
shutil.copy2(U/'apple-inline-occurrences.tex',C/'sections/apple-inline-occurrences.tex')
p=C/'references.bib';p.write_text(p.read_text()+(U/'bibliography-additions.bib').read_text())
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),'candidate':str(C.relative_to(R)),'version':'2.70','source_hashes':files},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'protected_sources':len(files)}))
