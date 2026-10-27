"""Render the changed and adjacent pages, with navigation kept separate."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PDF=ROOT/'docs/design/proposal/manuscript-segments-20261009/accounting-product-proposal.pdf'
if (OUT/'render-manifest.json').exists():raise SystemExit('Preserve existing render')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(PDF);doc=fitz.open(PDF)
body=list(range(24,29));navigation=list(range(1,8));pages=sorted(set(body+navigation))
(OUT/'render').mkdir(exist_ok=True)
images={}
for n in pages:
    path=OUT/'render'/f'page-{n:03}.png'
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(path)
    images[str(n)]=dict(path=str(path.relative_to(ROOT)),sha256=sha(path))
sheet=Image.new('RGB',(4*250,2*355),'white');draw=ImageDraw.Draw(sheet)
for i,n in enumerate(navigation):
    im=Image.open(ROOT/images[str(n)]['path']);im.thumbnail((244,327))
    x=(i%4)*250;y=(i//4)*355
    sheet.paste(im,(x,y+20));draw.text((x+8,y+3),'PDF page '+str(n),fill='black')
path=OUT/'render/navigation.png';sheet.save(path)
record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
            pdf_path=str(PDF.relative_to(ROOT)),pdf_sha256_before=before,pdf_sha256_after=sha(PDF),pdf_pages=len(doc),
            page_numbers=pages,continuous_read_pages=body,navigation_inspection_pages=navigation,
            rendered_pages=images,contact_sheets={'navigation':dict(path=str(path.relative_to(ROOT)),sha256=sha(path))})
(OUT/'render-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(pdf_pages=len(doc),body_pages=body,navigation_pages=navigation)))
