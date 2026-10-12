"""Render the protected insurance passage before editing its successor."""
import hashlib
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
pdf = ROOT / 'docs/design/proposal/manuscript-otsl-20261012/accounting-product-proposal.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == 'b13be68b6c5de2027f9f7a773dee70361feedb2c4b46a65bf81836e98418513e'
(OUT / 'rendered').mkdir(exist_ok=True)
d = fitz.open(pdf);rows = []
for n in [135, 136, 137]:
    p = OUT / 'rendered' / f'baseline-{n}.png'
    d[n-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(p)
    rows.append({'pdf_page': n, 'render': str(p.relative_to(ROOT)), 'sha256': sha(p), 'pdf_sha256': sha(pdf)})
(OUT / 'baseline-renders.json').write_text(json.dumps(rows, indent=2)+'\n')
print('Rendered three protected baseline pages')
