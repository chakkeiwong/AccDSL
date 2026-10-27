"""Make a labelled derived print view of retained HTML, preserving DOM text."""
from pathlib import Path
import hashlib
import json
import re

from bs4 import BeautifulSoup
import fitz

OUT=Path(__file__).resolve().parent
records=[]
for name in ["interim-note2-print", "interim-balance-print"]:
    p=OUT/"sources"/(name+".html")
    soup=BeautifulSoup(p.read_text(),"html.parser")
    before=re.sub(r"\s+","",soup.body.get_text())
    for tag in list(soup.find_all()):
        if ":" in tag.name:
            tag.unwrap()
    assert before==re.sub(r"\s+","",soup.body.get_text())
    target=OUT/"source-render"/(name+"-derived.pdf")
    story=fitz.Story(html=str(soup),user_css="body { font-family: sans-serif; font-size: 10pt; } table { width: 100%; }")
    writer=fitz.DocumentWriter(str(target))
    page=fitz.paper_rect("a4");where=page+(25,25,-25,-25)
    count=0;more=True
    while more:
        count+=1
        if count>8:raise RuntimeError("Bounded source rendering failed")
        dev=writer.begin_page(page);more,_=story.place(where);story.draw(dev);writer.end_page()
    writer.close()
    doc=fitz.open(target)
    for n,pg in enumerate(doc,1):
        pg.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(OUT/"source-render"/f"{name}-derived-{n}.png")
    records.append(dict(source_html=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(doc),pdf=str(target),pdf_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),text_preserved_after_namespace_unwrap=True))
(OUT/"source-render-receipt.json").write_text(json.dumps(dict(renderer="PyMuPDF Story; namespaces unwrapped without text change",records=records,
    scope="Derived view of retained table/paragraph markup, not an original browser screenshot; source checks use the retained HTML directly",
    prior_attempts=[dict(command="libreoffice --headless --convert-to pdf with isolated /tmp profile",execution="sandbox",exit_code=0,outcome="source file could not be loaded; no PDF"),dict(command="libreoffice --headless --infilter=HTML (StarWriter) --convert-to pdf with absolute paths and same isolated profile",execution="trusted",exit_code=0,outcome="source file could not be loaded; no PDF")]),indent=2)+"\n")
print(json.dumps([dict(name=r["pdf"],pages=r["pages"]) for r in records]))
