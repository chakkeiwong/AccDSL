"""Render the precise edited slice, title and affected bibliography."""
import time
import fitz
from build_candidate import OUT, ROOT, CAND, sha, save

assert not (OUT / 'completion.json').exists()
start = time.monotonic()
pdf = CAND / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
keys = ['document 2026-05961', 'document 2015-18702']
bib = [i + 1 for i, p in enumerate(doc) if any(k in ' '.join(p.get_text().lower().split()) for k in keys)]
pages = sorted(set([1, 117, 118, 119, 120, len(doc), *bib]))
rows = []
(OUT / 'rendered').mkdir(exist_ok=True)
for n in pages:
    p = OUT / 'rendered' / f'final-{n}.png'
    doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(p)
    rows.append({'pdf_page': n, 'render': str(p.relative_to(ROOT)), 'sha256': sha(p), 'pdf_sha256': sha(pdf)})
save('final-renders.json', rows)
save('render-run.json', {'pages': pages, 'wall_seconds': time.monotonic() - start, 'pdf_sha256': sha(pdf)})
print({'pages': len(doc), 'rendered': pages, 'pdf_sha256': sha(pdf)})
