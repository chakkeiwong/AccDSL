"""Record build checks and render the bounded changed-page review once."""
import hashlib
import json
from pathlib import Path
import fitz
from check_candidate import check

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'docs/design/proposal/manuscript-readability-20261022/accounting-product-proposal.pdf'
C = R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

assert not (U / 'render-manifest.json').exists()
checks = check()
before, after = fitz.open(B), fitz.open(C)
assert len(before) == len(after) == 401
text_changes = [i + 1 for i in range(len(before)) if before[i].get_text() != after[i].get_text()]
layout_changes = [i + 1 for i in range(len(before)) if before[i].get_text('words') != after[i].get_text('words')]
assert text_changes == layout_changes == [1, 88, 89]
write('candidate-checks.json', checks)
write('page-delta.json', dict(baseline_sha256=sha(B), candidate_sha256=sha(C), pages=401,
    text_changed=text_changes, word_layout_changed=layout_changes,
    scope='Exact extracted text and word-box comparison; no whole-document reading credit'))
segments = [[1, 2], [87, 88, 89, 90]]
renders = []
(U / 'rendered').mkdir()
for segment in segments:
    assert len(segment) <= 6
    for number in segment:
        dest = U / 'rendered' / f'page-{number:03d}.png'
        after[number - 1].get_pixmap(dpi=110, alpha=False).save(dest)
        renders.append(dict(page=number, path=str(dest.relative_to(R)), sha256=sha(dest), dpi=110))
write('render-manifest.json', dict(pdf_sha256=sha(C), segments=segments, renders=renders,
    status='rendered_not_yet_reviewed', provenance='PyMuPDF 110 dpi; actual viewing is recorded separately'))
print(json.dumps(dict(pages=401, text_changed=text_changes, word_layout_changed=layout_changes,
    rendered_pages=[r['page'] for r in renders], pdf_sha256=sha(C))))
