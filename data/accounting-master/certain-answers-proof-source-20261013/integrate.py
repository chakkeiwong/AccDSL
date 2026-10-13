"""Integrate only the inspected theorem/output-semantics qualification."""
import hashlib,json,shutil
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
B=R/'docs/design/proposal/manuscript-certain-answers-20261013'
C=R/'docs/design/proposal/manuscript-query-proof-20261013'
assert not C.exists(),'Candidate exists; inspect before editing'
p=R/'docs/papers/Certain answers as objects and knowledge Libkin (2016).pdf'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='ed3a343607504a2a83c709760d994052e963e56c474e500cab1d81fe9fa6db01'
files={}
for source in sorted(B.rglob('*')):
    if source.is_file() and source.suffix in {'.tex','.bib','.lark'}:
        rel=str(source.relative_to(B));dest=C/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest);files[rel]=hashlib.sha256(source.read_bytes()).hexdigest()
p=C/'accounting-product-proposal.tex';text=p.read_text()
assert text.count('Version 2.71')==1;p.write_text(text.replace('Version 2.71','Version 2.72'))
p=C/'sections/certain-answer-semantics.tex';text=p.read_text()
start='Input completeness and output meaning must also be explicit.'
end='constraints by treating unknown amounts as ordinary constants.'
assert text.count(start)==text.count(end)==1
left,rest=text.split(start);_,right=rest.split(end,1)
p.write_text(left+(U/'theorem-qualification.tex').read_text().rstrip()+right)
p=C/'references.bib';p.write_text(p.read_text()+(U/'bibliography-addition.bib').read_text())
(U/'candidate.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),
 'candidate':str(C.relative_to(R)),'version':'2.72','source_hashes':files,
 'old_qualification_start':start,'old_qualification_end':end},indent=2)+'\n')
print(json.dumps({'candidate':str(C.relative_to(R)),'protected_sources':len(files),'changed':['version','certain-answer-semantics','bibliography']}))
