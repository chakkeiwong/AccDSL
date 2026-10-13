"""Add dated award-version consequences without altering prior sources."""
import hashlib,json,shutil
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
B=R/'docs/design/proposal/manuscript-apple-performance-award-20261013'
C=R/'docs/design/proposal/manuscript-apple-award-versions-20261013'
if C.exists():raise SystemExit('Candidate exists; do not overwrite.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={}
for p in sorted(B.rglob('*')):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        rel=p.relative_to(B);q=C/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);sources[str(rel)]=sha(p)
p=C/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.66','Version 2.67'))
p=C/'chapters/14-financing-groups.tex';p.write_text(p.read_text().replace(r'\input{sections/apple-performance-award}',r'\input{sections/apple-performance-award}'+'\n'+r'\input{sections/apple-award-versions}'))
shutil.copy2(U/'apple-award-versions.tex',C/'sections/apple-award-versions.tex')
bib=r'''
@misc{apple2023q1awards,
  author = {{Apple Inc.}},
  title = {Form 10-Q for the Quarter Ended 31 December 2022: {CEO} Performance Award Form},
  year = {2023},
  note = {Exhibit 10.2; retained issuer-associated HTML. Annual reference identifies the form effective 25 September 2022; blank grant notice preserved. Selected operative clauses inspected},
  url = {https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/71f9a5ec-d5f2-4f6e-9d9c-ed2f02911111.html}
}
'''
p=C/'references.bib';p.write_text(p.read_text()+bib);(U/'bibliography-additions.bib').write_text(bib)
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),
 'candidate':str(C.relative_to(R)),'source_hashes':sources},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'baseline_sources':len(sources)}))
