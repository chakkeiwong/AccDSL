"""Render retained annual pages and a labelled derived interim print view."""
from pathlib import Path
import hashlib
import json
import re
from bs4 import BeautifulSoup
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
if (OUT/'completion.json').exists():raise SystemExit('Closed unit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
annual=ROOT/'docs/design/cases/apple/annual-2024.pdf'
doc=fitz.open(annual)
images=[]
for n in [28,37,45,48,49]:
    p=OUT/'source-render'/f'annual-{n:03}.png'
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(p)
    images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),original_pdf_page=n))
p=OUT/'sources/interim-selected-print.html'
soup=BeautifulSoup(p.read_text(),'html.parser')
before=re.sub(r'\s+','',soup.body.get_text())
for tag in list(soup.find_all()):
    if ':' in tag.name:tag.unwrap()
assert before==re.sub(r'\s+','',soup.body.get_text())
target=OUT/'source-render/interim-selected-derived.pdf'
story=fitz.Story(html=str(soup),user_css='body { font-family: sans-serif; font-size: 11pt; } h1 { font-size: 14pt; }')
writer=fitz.DocumentWriter(str(target));page=fitz.paper_rect('a4');where=page+(30,30,-30,-30)
more=True;count=0
while more:
    count+=1
    if count>5:raise RuntimeError('Source view exceeds bound')
    dev=writer.begin_page(page);more,_=story.place(where);story.draw(dev);writer.end_page()
writer.close();derived=fitz.open(target)
for n,pg in enumerate(derived,1):
    dst=OUT/'source-render'/f'interim-selected-{n:03}.png'
    pg.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(dst)
    images.append(dict(path=str(dst.relative_to(ROOT)),sha256=sha(dst),derived_pdf_page=n))
receipt=dict(annual_source=str(annual.relative_to(ROOT)),annual_sha256=sha(annual),annual_pages=[28,37,45,48,49],
    records=[dict(source_html=str(p),sha256=sha(p),pdf=str(target),pdf_sha256=sha(target),pages=len(derived),text_preserved_after_namespace_unwrap=True)],
    rendered_images=images,scope='Original annual pages and a derived interim print view; not an original SEC browser screenshot; no network')
(OUT/'source-render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(original_pages=5,derived_pages=len(derived))))
