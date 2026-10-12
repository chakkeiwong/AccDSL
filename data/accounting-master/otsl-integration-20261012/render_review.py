"""Render edited passages, transitions, title and new reference locations."""
import time
import fitz
from build_candidate import ROOT, OUT, CAND, sha, save
assert not (OUT/'completion.json').exists()
start=time.monotonic();pdf=CAND/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
pages=[1,149,150,151,152,179,180,183]
assert len(doc)==183
rows=[];(OUT/'rendered').mkdir(exist_ok=True)
for n in pages:
    q=OUT/'rendered'/f'final-{n}.png';doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(q)
    rows.append({'pdf_page':n,'render':str(q.relative_to(ROOT)),'sha256':sha(q),'pdf_sha256':sha(pdf)})
save('final-renders.json',rows)
save('render-run.json',{'pages':pages,'wall_seconds':time.monotonic()-start,'pdf_sha256':sha(pdf)})
print({'pages':len(doc),'rendered':pages,'pdf_sha256':sha(pdf)})
