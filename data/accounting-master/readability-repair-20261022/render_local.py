"""Render bounded local review segments; rendering alone records no reading."""
import hashlib
import json
from pathlib import Path
import fitz

U = Path(__file__).resolve().parent
R = U.parents[2]
pdf = R / 'docs/design/proposal/manuscript-readability-20261022/accounting-product-proposal.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == '28ece05611ea3bf831b7092961daf906d92bd1d5eddbe95748bdc551f039f0c3'
segments = [[1], list(range(27, 30)), list(range(73, 79)),
            list(range(97, 103)), list(range(169, 173)), list(range(212, 216))]
out = U / 'rendered'
out.mkdir(exist_ok=False)
doc = fitz.open(pdf)
records = []
for segment in segments:
    assert len(segment) <= 6
    for page in segment:
        path = out / f'page-{page:03}.png'
        doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(path)
        records.append(dict(page=page, path=str(path.relative_to(R)), sha256=sha(path)))
with (U / 'render-manifest.json').open('x') as f:
    json.dump(dict(pdf=str(pdf.relative_to(R)), pdf_sha256=sha(pdf),
                   segments=segments, renders=records, reading_status='pending'), f, indent=2)
    f.write('\n')
print(json.dumps(dict(rendered_pages=len(records), reading_status='pending')))
