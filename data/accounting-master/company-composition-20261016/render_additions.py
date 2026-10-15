"""Render P5 additions for a bounded visual review; no accounting execution."""
from pathlib import Path
import hashlib
import json
import os
import time

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / 'docs/design/proposal/manuscript-company-composition-20261016/accounting-product-proposal.pdf'
OUT = HERE / 'manuscript-render-02'
PAGES = [1, 17, 18, 19, 20, 21, 22, 157, 158, 159, 160, 161, 320, 321, 322, 323]
expected = '2d9d1c2bf2eeaa17ea5eb4b1ba5e8c0c95dd33104b4e6a3bcbd7f1211980d94e'
assert hashlib.sha256(PDF.read_bytes()).hexdigest() == expected
assert not OUT.exists(), 'Preserve prior render attempts'
OUT.mkdir()
started = time.monotonic()
records = []
with fitz.open(PDF) as doc:
    assert len(doc) == 349
    for page in PAGES:
        png = OUT / f'page-{page:03d}.png'
        doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False).save(png)
        records.append({'physical_page': page, 'path': str(png.relative_to(ROOT)),
                        'sha256': hashlib.sha256(png.read_bytes()).hexdigest()})
manifest = {'pdf': str(PDF.relative_to(ROOT)), 'pdf_sha256': expected,
            'pages_total': 349, 'pages_rendered': records, 'render_scale': 1.25,
            'tool': 'PyMuPDF ' + fitz.VersionBind,
            'wall_seconds': time.monotonic() - started,
            'scope': 'Added sections and their boundaries; whole-candidate R07 remains',
            'visual_review': 'pending', 'cpu_gpu': 'CPU-only; GPU intentionally hidden'}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'rendered_pages': len(records), 'pdf_sha256': expected}))
