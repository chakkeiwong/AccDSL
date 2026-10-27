"""Original annual pages and explicitly derived, text-preserving interim views."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import fitz

OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
if (OUT/'completion.json').exists(): raise SystemExit('Closed unit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'\s+','',s)
record=json.loads((OUT/'source-claim-supplement.json').read_text())
annual=ROOT/'docs/design/cases/apple/annual-2024.pdf'
doc=fitz.open(annual); images=[]
for n in [28,30,34,36,37,40,41,46,47]:
    p=OUT/'source-render'/f'annual-{n:03}.png'
    if not p.exists():doc[n-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(p)
    images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),original_pdf_page=n))
original=BeautifulSoup((ROOT/'docs/design/cases/apple/interim-2025q1.html').read_text(),'html.parser')
blocks=[]; preserved=[]


def table_html(index):
    table=original.find_all('table')[index]; rows=[]
    for tr in table.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        cells=[c for c in cells if c]
        merged=[];i=0
        while i<len(cells):
            if cells[i]=='$':merged.append('$ '+cells[i+1]);i+=2
            else:merged.append(cells[i]);i+=1
        if not merged:continue
        if len(merged)==1:
            rows.append('<tr><td colspan="3">'+html.escape(merged[0])+'</td></tr>');continue
        if len(merged)==2:
            assert merged[0].startswith('December'),merged
            merged=['']+merged
        assert len(merged)==3,(index,merged)
        rows.append('<tr>'+''.join('<td'+(' style="width:62%"' if n==0 else ' style="width:19%;text-align:right"')+'>'+html.escape(c)+'</td>' for n,c in enumerate(merged))+'</tr>')
    result='<table>'+''.join(rows)+'</table>'
    assert norm(table.get_text())==norm(BeautifulSoup(result,'html.parser').get_text())
    preserved.append(dict(id='HTML table '+str(index),all_cell_text_in_order=True,columns=3))
    return result


def paragraph(q):return '<p>'+html.escape(' '.join(q.split()))+'</p>'


for ident in ['interim.calendar','interim.note.6','interim.hedging','interim.liquidity','interim.market_risk']:
    source=record['notes'].get(ident) or record['dependencies'][ident]
    q=source['quote']
    if ident=='interim.hedging':
        a=q.index('December 28,\n2024',q.index('The notional amounts'))
        b=q.index('91,493',a)+len('91,493')
        assert norm(q[a:b])==norm(original.find_all('table')[21].get_text())
        body=paragraph(q[:a])+table_html(21)+paragraph(q[b:])
    elif ident=='interim.note.6':
        a=q.index('Term Debt')
        body=paragraph(q[:a])+paragraph(q[a:])
    else:body=paragraph(q)
    assert norm(BeautifulSoup(body,'html.parser').get_text())==norm(q)
    blocks.append('<h2>'+html.escape(ident)+' — retained text span '+str(source['start'])+'–'+str(source['end'])+'</h2>'+body)
    preserved.append(dict(id=ident,complete_excerpt_text_preserved=True))
for index,title in [(14,'Interim balance sheet — USD millions, except shares in thousands and par value'),
                    (16,'Interim cash-flow statement — USD millions')]:
    blocks.append('<h2>'+html.escape(title)+'</h2>'+table_html(index))
view=('<html><body><h1>Apple Q1 FY2025 — derived debt source view</h1>'
      '<p>This local view reflows retained SEC HTML/text for inspection. It is not an original filing page or a new acquisition. Table columns and all source text in each displayed excerpt are preserved.</p>'
      +''.join(blocks)+'</body></html>')
src=OUT/'sources/interim-debt-print.html';src.write_text(view)
dst=OUT/'source-render/interim-debt-derived.pdf'
story=fitz.Story(html=view,user_css='body {font-family:sans-serif;font-size:10.5pt;} h1 {font-size:15pt;} h2 {font-size:12pt;} table {width:100%;font-size:9pt;} td {padding:3pt;} p {margin-bottom:8pt;}')
writer=fitz.DocumentWriter(str(dst));page=fitz.paper_rect('a4');where=page+(30,30,-30,-30)
more=True;count=0
while more:
    count+=1
    if count>12:raise RuntimeError('Derived view exceeded planned page bound')
    dev=writer.begin_page(page);more,_=story.place(where);story.draw(dev);writer.end_page()
writer.close();derived=fitz.open(dst)
for n,pg in enumerate(derived,1):
    p=OUT/'source-render'/f'interim-debt-{n:03}.png'
    pg.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p)
    images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),derived_pdf_page=n))
receipt=dict(recorded_at=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
    source_supplement_sha256=sha(OUT/'source-claim-supplement.json'),annual_source=str(annual.relative_to(ROOT)),annual_sha256=sha(annual),
    annual_pages=[28,30,34,36,37,40,41,46,47],interim_original_sha256=sha(ROOT/'docs/design/cases/apple/interim-2025q1.html'),
    derived_html=str(src.relative_to(ROOT)),derived_html_sha256=sha(src),derived_pdf=str(dst.relative_to(ROOT)),derived_pdf_sha256=sha(dst),derived_pages=len(derived),
    text_preservation=preserved,rendered_images=images,scope='Original annual pages; explicitly derived interim prose/tables. No network or browser screenshot claim.')
(OUT/'source-render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(annual_pages=9,derived_pages=len(derived))))
