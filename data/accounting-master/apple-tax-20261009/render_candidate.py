"""Render the changed passages and navigation from the built candidate."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT / 'docs/design/proposal/manuscript-tax-20261009'
if (OUT / 'completion.json').exists():
    raise SystemExit('Closed unit')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda n, d: (OUT / n).write_text(json.dumps(d, indent=2) + '\n')
pdf = NEW / 'accounting-product-proposal.pdf'
digest = sha(pdf)
doc = fitz.open(pdf)
pages = set(range(1, 8))
anchors = [
    'Apple: recognising tax and settling the obligation',
    'The deferred balance illustrates the second relation',
    'Uncertain tax positions do not supply a payment distribution',
    'Retaining those unknowns',
]
matched = {}
for n, page in enumerate(doc, 1):
    text = ' '.join(page.get_text().split())
    hits = [s for s in anchors if s in text]
    if hits and n > 7:
        matched[str(n)] = hits
        pages.update({n - 1, n, n + 1})
pages = sorted(n for n in pages if 1 <= n <= len(doc))
target = OUT / 'render-final'
target.mkdir(exist_ok=False)
rendered = {}
for n in pages:
    p = target / f'page-{n:03d}.png'
    doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(p)
    rendered[str(n)] = dict(path=str(p.relative_to(ROOT)), sha256=sha(p))
contacts = {}
for name, selection in [('navigation', list(range(1, 8))),
                        ('tax', [n for n in pages if n > 7])]:
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
save('render-manifest.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
    pdf=str(pdf.relative_to(ROOT)), pdf_sha256_before=digest, pdf_sha256_after=sha(pdf),
    pages=len(doc), page_numbers=pages, matched_anchors=matched, scale=1.5,
    rendered_pages=rendered, contact_sheets=contacts,
    inspection_status='Rendered; actual author inspection recorded separately'))
save('build-receipt.json', dict(
    command='latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex',
    cwd=str(NEW.relative_to(ROOT)), execution='trusted existing font cache',
    exit_code=0, sandbox_attempt=dict(exit_code=12, log='data/accounting-master/apple-tax-20261009/sandbox-build-attempt/build.log', reason='LuaLaTeX had no writable font cache'), exit_evidence='Completed tool session 66061 returned exit_code 0',
    log=str((OUT / 'build.log').relative_to(ROOT)), log_sha256=sha(OUT / 'build.log'),
    pdf=str(pdf.relative_to(ROOT)), pdf_sha256=digest, pages=len(doc),
    elapsed_time='Not separately measured; full unit interval in manifest'))
print(json.dumps(dict(pdf_sha256=digest, pages=len(doc), rendered_pages=pages)))
