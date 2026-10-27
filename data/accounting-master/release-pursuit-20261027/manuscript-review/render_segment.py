"""Render the next bounded ordered segment without marking it read."""
import hashlib,json,sys
from pathlib import Path
import fitz
D=Path(__file__).resolve().parent; R=D.parents[3]
start,end=map(int,sys.argv[1:3]); assert 1<=end-start+1<=6
j=json.loads((D/'manuscript-release-prep-v552r2-20261027-inventory.json').read_text())
v=next(x for x in j['volumes'] if x['name']=='accounting-product-proposal')
segments=[s for s in j['read_segments'] if s['volume']==v['name']]
assert segments[-1]['pages'][-1]+1==start
p=R/v['pdf']; assert hashlib.sha256(p.read_bytes()).hexdigest()==v['pdf_sha256']
doc=fitz.open(p); records=[]
for n in range(start,end+1):
    q=D/'rendered-main'/f'{n:04}.png'; assert not q.exists()
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(q)
    records.append(dict(page=n,sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
with (D/f'render-bindings-{start:04}-{end:04}.json').open('x') as f:
    json.dump(dict(pdf=v['pdf'],pdf_sha256=v['pdf_sha256'],pages=records),f,indent=2)
print(json.dumps(dict(rendered=len(records),first=start,last=end)))
