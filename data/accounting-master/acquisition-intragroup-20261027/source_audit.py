"""Retain bounded primary tax text; no source/application admission."""
from pathlib import Path
from hashlib import sha256
import fitz,json
H=Path(__file__).resolve().parent;R=H.parents[2]
OUT=H/'source-inspection-01';OUT.mkdir(exist_ok=False)
paths=[R/'docs/design/proposal/methods/preparation-20261005-v1/02-authority/sources/aasb112-compiled-sep2023.pdf']
base=R/'data/accounting-master/acquisition-period-authority-20261026'
paths += [p for p in base.rglob('*.pdf') if 'inputs' not in p.parts and 'build' not in str(p) and ('18' in p.name or '2026-2' in p.name)]
registry=[]
for p in paths:
    d=fitz.open(p)
    if '112' in p.name:pages=[1,9,12,13,14,15,16,17,18,19,20,21,22,32,33,52,53]
    else:pages=[i+1 for i,x in enumerate(d) if 'AASB 112' in x.get_text() or 'Income Taxes' in x.get_text()]
    if not pages:continue
    stem=p.stem;copy=OUT/(stem+'.pdf');copy.write_bytes(p.read_bytes())
    (OUT/(stem+'.txt')).write_text('\n\n'.join('PHYSICAL PAGE '+str(i)+'\n'+d[i-1].get_text() for i in pages))
    registry.append(dict(source=str(p.relative_to(R)),local=str(copy.relative_to(R)),sha256=sha256(p.read_bytes()).hexdigest(),pages=pages))
index=base/'index-attempt-03/accounting-index-fourth.html'
(OUT/index.name).write_bytes(index.read_bytes())
registry.append(dict(source=str(index.relative_to(R)),local=str((OUT/index.name).relative_to(R)),sha256=sha256(index.read_bytes()).hexdigest(),scope='AASB112 adjacent future-amendment rows inspected'))
(OUT/'source-register.json').write_text(json.dumps(registry,indent=2)+'\n')
print(json.dumps(registry))
