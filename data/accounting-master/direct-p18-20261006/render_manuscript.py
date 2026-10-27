"""Render the proposal for document inspection; no product runtime behavior."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import sys
import time

import fitz
from PIL import Image, ImageDraw

ROOT = Path('/home/chakwong/python/AccDSL')
PDF = ROOT / 'docs/design/proposal/manuscript/accounting-product-proposal.pdf'
OUT = ROOT / 'data/accounting-master/direct-p18-20261006' / sys.argv[1]
OUT.mkdir(exist_ok=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


start = time.monotonic()
before = digest(PDF)
document = fitz.open(PDF)
pages = []
geometry = []
for i, page in enumerate(document, 1):
    path = OUT / f'page-{i:03d}.png'
    page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(path)
    pages.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path),
                  'page_number': i})
    blocks = page.get_text('blocks')
    geometry.append({'page': i, 'text_characters': len(page.get_text()),
                     'outside_page': [list(b[:4]) for b in blocks
                                      if b[0] < -0.5 or b[1] < -0.5 or
                                      b[2] > page.rect.width + 0.5 or
                                      b[3] > page.rect.height + 0.5]})

contacts = []
for offset in range(0, len(pages), 12):
    sheet = Image.new('RGB', (1640, 1810), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, record in enumerate(pages[offset:offset + 12]):
        with Image.open(ROOT / record['path']) as im:
            im.thumbnail((396, 560))
            x, y = (j % 4) * 410 + 7, (j // 4) * 600 + 30
            sheet.paste(im, (x, y))
            draw.text((x + 8, y - 19), f"PDF page {record['page_number']}", fill='black')
    path = OUT / f'contact-{offset + 1:03d}-{min(offset + 12, len(pages)):03d}.png'
    sheet.save(path)
    contacts.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path),
                     'page_numbers': list(range(offset + 1, min(offset + 12, len(pages)) + 1))})

after = digest(PDF)
assert before == after, 'PDF changed during rendering'
record = {'schema': 'accdsl.manuscript.render.v1',
          'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'command': 'python3 ' + str(Path(__file__)) + ' ' + sys.argv[1],
          'environment': platform.python_version() + '; ' + fitz.VersionBind + '; CPU rendering',
          'exit_code': 0, 'pdf_path': str(PDF.relative_to(ROOT)),
          'pdf_sha256_before': before, 'pdf_sha256_after': after,
          'pdf_page_count': len(pages), 'page_numbers': [r['page_number'] for r in pages],
          'page_hashes': {r['path']: r['sha256'] for r in pages},
          'rendered_pages': pages, 'contact_sheets': contacts,
          'geometry_diagnostic': geometry, 'wall_seconds': time.monotonic() - start,
          'script_sha256': digest(Path(__file__)),
          'scope': 'Render and geometry evidence only; human comprehension not assessed.'}
(OUT / 'render-record.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'pages': len(pages), 'contact_sheets': len(contacts),
                  'geometry_outside_page': [r['page'] for r in geometry if r['outside_page']],
                  'record': str(OUT / 'render-record.json')}))
