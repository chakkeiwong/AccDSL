"""Repair the review range without replacing successful structural checks."""
from pathlib import Path
from hashlib import sha256
import json,fitz
H=Path(__file__).resolve().parent;R=H.parents[2]
T=R/'docs/design/proposal/manuscript-acquisition-design-v528-20261027'
out=H/'bounded-render-01';out.mkdir(exist_ok=False);rows=[]
prior=json.loads((H/'verification.json').read_text());assert prior['status']=='PASS'
for d in prior['documents']:
    n=d['document'];p=T/(n+'.pdf');assert sha256(p.read_bytes()).hexdigest()==d['sha256']
    pdf=fitz.open(p);texts=[' '.join(page.get_text().split()) for page in pdf]
    starts=[i+1 for i,t in enumerate(texts) if 'Suppose the financing arrangement eventually gives the creditor control of the debtor.' in t]
    ends=[i+1 for i,t in enumerate(texts) if 'they do not replace it.' in t]
    assert len(starts)==len(ends)==1 and 1<=ends[0]-starts[0]<8
    pages=[1]+list(range(starts[0],ends[0]+1));folder=out/n;folder.mkdir()
    for i in pages:pdf[i-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(folder/f'page-{i}.png')
    (out/(n+'.txt')).write_text('\n\n'.join('PAGE '+str(i)+'\n'+pdf[i-1].get_text() for i in pages))
    rows.append(dict(document=n,pdf_sha256=d['sha256'],addition_pages=[starts[0],ends[0]],rendered_pages=pages))
(out/'verification.json').write_text(json.dumps(dict(status='PASS',documents=rows,repair='The prior title locator matched the contents entry because the body heading wraps. Unique opening/final prose now selects the actual added pages. Structural preservation/reference/warning checks remain valid; neither writer reran.'),indent=2)+'\n')
print(json.dumps(rows))
