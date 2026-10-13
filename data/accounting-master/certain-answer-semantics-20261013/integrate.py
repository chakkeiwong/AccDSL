"""Preserve 2.70; integrate only the audited query-semantics repair."""
import hashlib,json,shutil
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
B=R/'docs/design/proposal/manuscript-apple-inline-occurrences-20261013'
C=R/'docs/design/proposal/manuscript-certain-answers-20261013'
assert not C.exists(),'Candidate exists; preserve it and inspect before editing'
assert not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
files={};changes={}
for p in sorted(B.rglob('*')):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        rel=str(p.relative_to(B));q=C/rel;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,q);files[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
def replace(rel,old,new):
    p=C/rel;t=p.read_text();assert t.count(old)==1,(rel,old)
    p.write_text(t.replace(old,new));changes.setdefault(rel,[]).append({'old':old,'new':new})
replace('accounting-product-proposal.tex','Version 2.70','Version 2.71')
replace('chapters/03-literature.tex','Sections 2--5, explains','Sections 2--6, explains')
old='every history in the declared feasible family. The family itself may omit'
new=('every history in a nonempty declared feasible family. This is Boolean\n'
     'certainty; a table of individually certain rows can lose existential\n'
     'information and must not imply that omitted rows are absent. The payable\n'
     'example in Section~\\ref{sec:query-certainty} develops this distinction.\n'
     'The family itself may omit')
replace('chapters/03-literature.tex',old,new)
anchor=r'\section{Why published statements cannot identify all transactions}'
replace('chapters/05-mathematics.tex',anchor,r'\input{sections/certain-answer-semantics}'+'\n\n'+anchor)
anchor=r'\section{Operational rule selection}'
replace('chapters/11-contracts.tex',anchor,(U/'query-proof-contract.tex').read_text()+'\n'+anchor)
shutil.copy2(U/'certain-answer-semantics.tex',C/'sections/certain-answer-semantics.tex')
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),'candidate':str(C.relative_to(R)),
 'version':'2.71','source_hashes':files,'changes':changes},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'protected_sources':len(files),'modified_source_files':list(changes)}))
