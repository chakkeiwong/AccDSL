"""Create the next additive manuscript; refuse to overwrite an existing one."""
import hashlib
import json
import shutil
from pathlib import Path
U=Path(__file__).resolve().parent; R=U.parents[2]
B=R/'docs/design/proposal/manuscript-apple-award-versions-20261013'
C=R/'docs/design/proposal/manuscript-arelle-fact-identity-20261013'
assert not C.exists(), 'Candidate already exists; inspect rather than overwrite'
assert not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
files={}
for p in B.rglob('*'):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        rel=p.relative_to(B); q=C/rel; q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,q); files[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
p=C/'accounting-product-proposal.tex'; t=p.read_text(); assert 'Version 2.67' in t
p.write_text(t.replace('Version 2.67','Version 2.68'))
p=C/'sections/adapter-methods.tex'; t=p.read_text()
anchor='Each adapter therefore pins code, dependency, model and taxonomy versions,'
assert t.count(anchor)==1
p.write_text(t.replace(anchor,r'\input{sections/arelle-fact-identity}'+'\n\n'+anchor))
shutil.copy2(U/'arelle-fact-identity.tex',C/'sections/arelle-fact-identity.tex')
p=C/'references.bib'; p.write_text(p.read_text()+(U/'bibliography-additions.bib').read_text())
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),'candidate':str(C.relative_to(R)),'version':'2.68','source_hashes':files},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'protected_sources':len(files),'new_section':'arelle-fact-identity'}))
