"""Render the bounded liquidity addition, adjacent pages and navigation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT / 'docs/design/proposal/manuscript-liquidity-20261009'
if (OUT / 'completion.json').exists() or (OUT / 'render-manifest.json').exists():
    raise SystemExit('Preserve prior rendering before rerunning')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pdf = NEW / 'accounting-product-proposal.pdf'
digest = sha(pdf)
doc = fitz.open(pdf)
anchors = ['Apple: resources available for payment', 'Restriction changes what can be spent',
           'Security turnover differs from valuation', 'Future receipts need customers']
matched = {}
for n, page in enumerate(doc, 1):
    text = ' '.join(page.get_text().split())
    hits = [s for s in anchors if s in text]
    if hits and n > 7:
        matched[n] = hits
assert set(anchors) == {a for hits in matched.values() for a in hits}
body = list(range(min(matched) - 1, max(matched) + 2))
navigation = list(range(1, 8))
pages = navigation + body
target = OUT / 'render-final'
target.mkdir(exist_ok=False)
rendered = {}
for n in pages:
    p = target / f'page-{n:03d}.png'
    doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(p)
    rendered[str(n)] = dict(path=str(p.relative_to(ROOT)), sha256=sha(p))
contacts = {}
for name, selection in [('navigation', navigation), ('liquidity', body)]:
    sheet = Image.new('RGB', (1000, ((len(selection) + 2) // 3) * 490), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, n in enumerate(selection):
        im = Image.open(target / f'page-{n:03d}.png').convert('RGB')
        im.thumbnail((320, 452))
        x, y = (i % 3) * 333, (i // 3) * 490
        draw.text((x + 8, y + 5), f'PDF page {n}', fill='black')
        sheet.paste(im, (x + 5, y + 25))
    p = OUT / f'contact-{name}.png'
    sheet.save(p)
    contacts[name] = dict(path=str(p.relative_to(ROOT)), sha256=sha(p))
record = dict(recorded_at=datetime.now(timezone.utc).isoformat(), script_sha256=sha(Path(__file__)),
    pdf=str(pdf.relative_to(ROOT)), pdf_sha256_before=digest, pdf_sha256_after=sha(pdf),
    pages=len(doc), page_numbers=pages, continuous_read_pages=body, matched_anchors=matched,
    scale=1.5, rendered_pages=rendered, contact_sheets=contacts,
    inspection_status='Rendered; actual author inspection recorded separately')
(OUT / 'render-manifest.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(dict(pdf_sha256=digest, pages=len(doc), rendered_pages=pages)))
