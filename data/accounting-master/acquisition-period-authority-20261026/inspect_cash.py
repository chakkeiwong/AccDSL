from pathlib import Path
import fitz,json
H=Path(__file__).resolve().parent;R=H.parents[2]
p=H/'cash-source-attempt-02/aasb107-2026.pdf';doc=fitz.open(p)
out=H/'cash-inspection';out.mkdir(exist_ok=False);rows=[]
for i,page in enumerate(doc):
    text=page.get_text();(out/('page-'+str(i+1)+'.txt')).write_text(text)
    if i==0 or any(term in text for term in ['Changes in ownership interests','aggregate cash flows arising','conversion of debt to equity']):rows.append(dict(page=i+1,text=text))
(out/'selection.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(pages=len(doc),selected=rows)))
p=R/'data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02/aasb18-full.pdf';doc=fitz.open(p)
print(json.dumps(dict(aasb18_C1_physical=[i+1 for i,page in enumerate(doc) if 'AusC1.1' in page.get_text() and 'C1\n' in page.get_text()])))
