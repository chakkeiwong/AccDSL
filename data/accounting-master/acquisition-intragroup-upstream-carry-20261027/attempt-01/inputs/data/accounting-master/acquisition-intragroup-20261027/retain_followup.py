"""Add separately retained amendment/group anchors without rewriting prior audit."""
from pathlib import Path
from hashlib import sha256
import fitz,json
H=Path(__file__).resolve().parent;R=H.parents[2];O=H/'source-inspection-02';O.mkdir(exist_ok=False)
sources=[('data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02/aasb18-appendix-d.pdf',[44,45]),
 ('data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02/aasb18-full.pdf',[51]),
 ('data/accounting-master/acquisition-period-authority-20261026/source-attempt-01/aasb2026-2-compiled.pdf',[7,21]),
 ('data/accounting-master/conversion-control-scope-20261026/source-attempt-02/aasb10-2026.pdf',[1,7,31,32])]
rows=[]
for name,pages in sources:
    p=R/name;d=fitz.open(p);q=O/p.name;q.write_bytes(p.read_bytes())
    (O/(p.stem+'.txt')).write_text('\n\n'.join('PHYSICAL PAGE '+str(i)+'\n'+d[i-1].get_text() for i in pages))
    for i in pages:
        if (p.name=='aasb18-appendix-d.pdf') or (p.name=='aasb2026-2-compiled.pdf' and i==21):
            d[i-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(O/(p.stem+'-page-'+str(i)+'.png'))
    rows.append(dict(source=name,local=str(q.relative_to(R)),sha256=sha256(p.read_bytes()).hexdigest(),pages=pages))
(O/'source-register.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
