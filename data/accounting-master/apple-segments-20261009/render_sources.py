"""Render original annual pages and an explicitly derived interim reading view."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'source-render-receipt.json').exists():
    raise SystemExit('Preserve existing source renders')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = json.loads((OUT / 'source-claim-supplement.json').read_text())
checks = json.loads((OUT / 'table-checks.json').read_text())
render = OUT / 'source-render'
render.mkdir(exist_ok=True)
pdf_path = ROOT / source['sources']['annual']['original_path']
doc = fitz.open(pdf_path)
pages = [24,25,26,32,37,38,39,42,49,50]
images = []
for page in pages:
    path = render / f'annual-{page:03}.png'
    doc[page-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(path)
    images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),original_pdf_page=page))

def table(index, title, groups):
    rows = []
    for label, values in groups:
        rows.append('<tr><td>' + html.escape(label) + '</td>' + ''.join(
            '<td>' + html.escape(str(v)) + '</td>' for v in values) + '</tr>')
    return '<h2>' + html.escape(title) + '</h2><table>' + ''.join(rows) + '</table>'

rows = checks['source_rows']
names = list(source['tables']['interim.sales']['rows'])
segment = []
for name in names:
    segment.append((name + ' — net sales', rows['interim.segment.'+name+'.sales']['values']))
    segment.append((name + ' — operating income', rows['interim.segment.'+name+'.income']['values']))
bridge = [(label, rows['interim.bridge.'+kind]['values']) for kind,label in
          [('segment','Segment operating income'),('rd','Research and development expense'),
           ('other','Other corporate expenses, net'),('consolidated','Total operating income')]]
q = source['notes']['interim.note.10']['quote']
view = ('<html><body><h1>Apple Q1 FY2025 — derived Note 10 reading view</h1>'
        '<p>Local reflow of pinned SEC HTML. The source text follows all tables verbatim; '
        'this is not an original filing page or new filing.</p>'
        '<p>All figures are issuer displayed USD millions. Columns are the three months ended '
        '28 December 2024 and 30 December 2023.</p>'
        + table(26,'Reportable segments: five regions, two measures',segment)
        + table(27,'Operating income bridge',bridge)
        + '<h2>Complete retained note text</h2><pre>' + html.escape(q) + '</pre></body></html>')
view_path = OUT/'sources/interim-segments-print.html';view_path.write_text(view)
pdf_out = render/'interim-segments-derived.pdf'
story = fitz.Story(html=view,user_css='body{font-family:sans-serif;font-size:10pt}h1{font-size:16pt}h2{font-size:12pt} table{width:100%;border-collapse:collapse}td{padding:3pt;border-bottom:0.3pt solid #999}td:not(:first-child){text-align:right}pre{font-family:monospace;font-size:9pt;white-space:pre-wrap}')
writer = fitz.DocumentWriter(str(pdf_out)); page = fitz.paper_rect('a4-l'); where=page+(32,32,-32,-32)
more=True;count=0
while more:
    count+=1
    if count>10:raise RuntimeError('Derived reading view exceeds ten pages')
    dev=writer.begin_page(page);more,_=story.place(where);story.draw(dev);writer.end_page()
writer.close()
derived=fitz.open(pdf_out)
for n,p in enumerate(derived,1):
    path=render/f'interim-segments-{n:03}.png'
    p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(path)
    images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),derived_pdf_page=n))
receipt=dict(recorded_at=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
             source_supplement_sha256=sha(OUT/'source-claim-supplement.json'),
             table_checks_sha256=sha(OUT/'table-checks.json'),annual_pdf_sha256=sha(pdf_path),annual_pages=pages,
             interim_original_sha256=sha(ROOT/source['sources']['interim']['original_path']),
             derived_html=str(view_path.relative_to(ROOT)),derived_html_sha256=sha(view_path),
             derived_pdf=str(pdf_out.relative_to(ROOT)),derived_pdf_sha256=sha(pdf_out),
             derived_pages=len(derived),rendered_images=images,
             scope='Original annual PDF page images plus derived interim note reading view; full note text and audited positional tables, not original HTML pagination')
(OUT/'source-render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(annual_pages=len(pages),derived_pages=len(derived))))
