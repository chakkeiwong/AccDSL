"""Add the conditional performance method to protected V2.65 sources."""
import hashlib,json,shutil
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
B=R/'docs/design/proposal/manuscript-apple-stock-plan-20261013'
C=R/'docs/design/proposal/manuscript-apple-performance-award-20261013'
if C.exists():raise SystemExit('Candidate exists; do not overwrite.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={}
for p in sorted(B.rglob('*')):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        rel=p.relative_to(B);q=C/rel;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,q);sources[str(rel)]=sha(p)
p=C/'accounting-product-proposal.tex'
p.write_text(p.read_text().replace('Version 2.65','Version 2.66'))
p=C/'chapters/14-financing-groups.tex'
p.write_text(p.read_text().replace(r'\input{sections/apple-stock-plan}',r'\input{sections/apple-stock-plan}'+'\n'+r'\input{sections/apple-performance-award}'))
shutil.copy2(U/'apple-performance-award.tex',C/'sections/apple-performance-award.tex')
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),
 'candidate':str(C.relative_to(R)),'source_hashes':sources},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'protected_sources':len(sources)}))
