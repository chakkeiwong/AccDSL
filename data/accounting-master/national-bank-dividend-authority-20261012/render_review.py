"""Render the final changed slice, boundary and source references."""
import json
import time
import fitz
from build_candidate import OUT, ROOT, CAND, sha, save

assert not (OUT / 'completion.json').exists()
start = time.monotonic()
pdf = CAND / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
keys = ['payment of dividends', 'modifications to the enhanced']
bibliography = [i + 1 for i, p in enumerate(doc) if any(k in ' '.join(p.get_text().lower().split()) for k in keys)]
pages = sorted(set([1, 115, 116, 117, 118, *bibliography]))
rows = []
for n in pages:
    path = OUT / 'rendered' / f'final-{n}.png'
    doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(path)
    rows.append({'pdf_page': n, 'render': str(path.relative_to(ROOT)), 'sha256': sha(path),
                 'pdf_sha256': sha(pdf), 'scale': 1.5})
save('final-renders.json', rows)
save('render-run.json', {'command': ['python3', str(__file__)], 'pages': pages,
                         'wall_seconds': time.monotonic() - start, 'pdf_sha256': sha(pdf)})
print(json.dumps({'pages': len(doc), 'rendered': pages, 'pdf_sha256': sha(pdf)}))
