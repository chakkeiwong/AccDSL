from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent; R=H.parents[2]
T=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
def sha(p): return sha256(p.read_bytes()).hexdigest()
assert not (H/'layout-source-lock.json').exists()
v=json.loads((H/'verification.json').read_text()); assert v['passed']
before={str(p.relative_to(T)):sha(p) for p in T.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark','.md','.json']}
changes={
 'chapters/01-purpose.tex': (r'\section{What constitutes a useful first implementation}', r'\clearpage'+'\n'+r'\section{What constitutes a useful first implementation}'),
 'sections/selected-term-execution.tex': (r'\begingroup\raggedright'+'\nThe complete envelope, failure semantics', r'\begingroup\raggedright\begin{samepage}'+'\nThe complete envelope, failure semantics')
}
backup=H/'layout-source-before'; backup.mkdir(exist_ok=False)
for name,(old,new) in changes.items():
 p=T/name; s=p.read_text(); assert s.count(old)==1,(name,old)
 q=backup/name; q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes(p.read_bytes())
 s=s.replace(old,new,1)
 if name.startswith('sections/'):
  tail=r'\path{data/accounting-master/selected-term-bundle-20261027/attempt-02/bundle/}.'+'\n'+r'\par\endgroup'
  assert s.count(tail)==1
  s=s.replace(tail,tail.replace(r'\par\endgroup',r'\par\end{samepage}\endgroup'),1)
 p.write_text(s)
lock=dict(before=before,changed={n:sha(T/n) for n in changes},protected_verification=sha(H/'verification.json'),plan='docs/plans/accounting-specification-consolidation-20261027.md',repair='layout-repair.md')
(H/'layout-source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
print(json.dumps(dict(changed=list(changes),protected_sources=len(before))))
