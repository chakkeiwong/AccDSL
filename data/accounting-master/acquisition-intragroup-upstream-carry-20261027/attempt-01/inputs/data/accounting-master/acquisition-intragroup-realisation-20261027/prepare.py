"""Retain source/precedessor bytes for a separate realisation companion."""
from pathlib import Path
from hashlib import sha256
import json,fitz
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-intragroup-20261027'
out=H/'source-inspection-01';out.mkdir(exist_ok=False)
rows=[]
for path,pages in [('data/accounting-master/p17-completion-20261014/P17-04/ppe-cost-boundary/sources/aasb102-compiled-dec2021.pdf',[1,6,7,8,9]),('docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf',[1,8,9,12,13,15])]:
    p=R/path;d=fitz.open(p);q=out/p.name;q.write_bytes(p.read_bytes())
    (out/(p.stem+'.txt')).write_text('\n\n'.join('PHYSICAL PAGE '+str(i)+'\n'+d[i-1].get_text() for i in pages))
    rows.append(dict(source=path,local=str(q.relative_to(R)),sha256=sha256(p.read_bytes()).hexdigest(),pages=pages))
(out/'source-register.json').write_text(json.dumps(rows,indent=2)+'\n')
files={R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text())}
files.update(S/p for p in ['attempt-01/source-lock.json','attempt-01/cases.json','attempt-01/verification.json','result.md'])
files.update(p for p in out.iterdir());files.update(R/x['source'] for x in rows)
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
(H/'predecessor-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
print(json.dumps(dict(protected_files=len(lock),source_rows=rows)))
