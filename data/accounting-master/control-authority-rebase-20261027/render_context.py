from pathlib import Path
import json,fitz
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'readability-repair-01'
lock=json.loads((D/'source-preservation.json').read_text());T=R/lock['target']
out=H/'context-review';out.mkdir(exist_ok=False);rows=[]
for name in ['accounting-product-proposal','simulation-foundations']:
    doc=fitz.open(T/(name+'.pdf'));chosen={1}
    for i,p in enumerate(doc):
        text=' '.join(p.get_text().split())
        if 'Under this supplied economic governance rule' in text or 'connects a four-party funding sequence' in text:chosen.add(i+1)
    for i in sorted(chosen):
        doc[i-1].get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save(out/(name+'-'+str(i)+'.png'))
    rows.append(dict(document=name,pages=sorted(chosen)))
(out/'index.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
