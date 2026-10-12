"""Render and bind the final local passage and navigation pages."""
import json
import time
import fitz
from build_candidate import ROOT, OUT, CAND, sha, save

assert not (OUT / 'completion.json').exists()
start = time.monotonic()
pdf = CAND / 'accounting-product-proposal.pdf';doc = fitz.open(pdf)
pages = [1, 5, 135, 136, 137, 138, 139, len(doc)]
rows = []
for n in pages:
    p = OUT / 'rendered' / f'final-{n}.png'
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(p)
    rows.append({'pdf_page':n,'render':str(p.relative_to(ROOT)),'sha256':sha(p),'pdf_sha256':sha(pdf)})
save('final-renders.json', rows)
save('render-run.json', {'command':['python3','data/accounting-master/insurance-vfa-integration-20261012/render_review.py'],
    'pages':pages,'pdf_sha256':sha(pdf),'wall_seconds':time.monotonic()-start})
print(json.dumps({'pages':len(doc),'renders':len(rows),'pdf_sha256':sha(pdf)}))
