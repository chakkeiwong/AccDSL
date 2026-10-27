"""Render inspected source redlines; retain source identities and page indexes."""
from pathlib import Path
from hashlib import sha256
import json,fitz
H=Path(__file__).resolve().parent;R=H.parents[2];out=H/'source-render';out.mkdir(exist_ok=False)
P=R/'data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02'
jobs=[(H/'source-attempt-01/aasb2026-2-compiled.pdf',[16,18,48]),
      (H/'source-attempt-01/aasb20-appendix-d.pdf',[3]),
      (H/'source-attempt-02/aasb1061-appendix-c.pdf',[1])]
for p,terms in [(P/'aasb18-appendix-d.pdf',['AASB 3 Business Combinations (August 2015)','AASB 10 Consolidated Financial Statements (July 2015)','AASB 127 Separate Financial Statements (August 2015)'])]:
    d=fitz.open(p);pages=[]
    for term in terms:
        found=[i+1 for i,page in enumerate(d) if term in ' '.join(page.get_text().split())]
        assert found,(p,term);pages.append(found[0])
    jobs.append((p,pages))
rows=[]
for p,pages in jobs:
    doc=fitz.open(p)
    for n in pages:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(out/(p.stem+'-'+str(n)+'.png'))
    rows.append(dict(source=str(p.relative_to(R)),sha256=sha256(p.read_bytes()).hexdigest(),pages=pages))
(out/'index.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
