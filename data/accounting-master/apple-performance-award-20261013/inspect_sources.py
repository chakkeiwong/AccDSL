"""Retain exact proxy pages and derived local views; no network or browser."""
import hashlib
import json
from pathlib import Path
import fitz
from bs4 import BeautifulSoup

U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'source-views.json').exists():raise SystemExit('Source views already exist.')
S=U/'sources';S.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proxy=R/'docs/design/cases/apple/p02-v1/proxy-2025.html'
soup=BeautifulSoup(proxy.read_text(),'html.parser');records=[]
for page in (51,52,53):
    ds=[d for d in soup.find_all('div',style=lambda x:x and 'width: 800px' in x)
        if ' '.join(d.get_text(' ',strip=True).split()).endswith('2025 Proxy Statement '+str(page))]
    assert len(ds)==1,(page,len(ds))
    d=ds[0];fragment=S/f'proxy-p{page}-fragment.html';fragment.write_text(str(d))
    text=' '.join(d.get_text(' ',strip=True).split());(S/f'proxy-p{page}.txt').write_text(text+'\n')
    clean=BeautifulSoup(str(d),'html.parser')
    for tag in clean.find_all(True):
        tag.attrs={k:v for k,v in tag.attrs.items() if k in {'colspan','rowspan'}}
    html='<h1>Derived retained proxy view: printed page '+str(page)+'</h1>'+str(clean)
    view=S/f'proxy-p{page}-view.html';view.write_text(html)
    out=S/f'proxy-p{page}-view.pdf'
    story=fitz.Story(html=html,user_css='body {font-family: sans-serif; font-size: 10pt;} table {border-collapse: collapse;} td {padding:3px; border-bottom:0.5px solid #aaa;} h1 {font-size:14pt;}')
    writer=fitz.DocumentWriter(out);rect=fitz.paper_rect('a4');where=rect+ (36,36,-36,-36)
    more=1
    while more:
        device=writer.begin_page(rect);more,_=story.place(where);story.draw(device);writer.end_page()
    writer.close();doc=fitz.open(out);images=[]
    for i,p in enumerate(doc):
        im=S/f'proxy-p{page}-view-{i+1}.png';p.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(im)
        images.append({'path':str(im.relative_to(R)),'sha256':sha(im)})
    records.append({'printed_page':page,'source_fragment':str(fragment.relative_to(R)),
        'fragment_sha256':sha(fragment),'normalized_text':text,'view':str(view.relative_to(R)),
        'view_sha256':sha(view),'view_pdf':str(out.relative_to(R)),'images':images,
        'scope':'Derived view from retained HTML; not a browser screenshot.'})
filing=R/'data/accounting-master/apple-stock-plan-source-20261013/sources/filing-20220304.pdf'
doc=fitz.open(filing);pages=[]
for n in range(25,32):
    p=doc[n-1];txt=S/f'filing-p{n}.txt';txt.write_text(p.get_text())
    im=S/f'filing-p{n}.png';p.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(im)
    pages.append({'pdf_page':n,'text':str(txt.relative_to(R)),'text_sha256':sha(txt),'image':str(im.relative_to(R)),'image_sha256':sha(im)})
(U/'source-views.json').write_text(json.dumps({'proxy':str(proxy.relative_to(R)),
 'proxy_sha256':sha(proxy),'proxy_pages':records,'filing':str(filing.relative_to(R)),
 'filing_sha256':sha(filing),'filing_pages':pages},indent=2)+'\n')
print(json.dumps({'proxy_pages':[(p['printed_page'],len(p['images'])) for p in records],'filing_pages':len(pages)}))
