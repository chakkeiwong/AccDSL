"""Retain Note 20 pages alongside the frozen Note 33 comparator."""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / 'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf'
EXPECTED = 'e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    start = time.monotonic()
    assert not (OUT / 'source-manifest.json').exists()
    assert sha(PDF) == EXPECTED
    for folder in ['sources', 'rendered', 'pointers-before']:
        (OUT / folder).mkdir(exist_ok=True)
    snapshots = []
    for rel in ['docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-current.md', 'docs/plans/accounting-continuation-requirements-20261007.md', 'data/accounting-master/next-plan.md']:
        p = ROOT / rel
        target = OUT / 'pointers-before' / p.name
        assert not target.exists()
        shutil.copyfile(p, target)
        snapshots.append({'live': rel, 'snapshot': str(target.relative_to(ROOT)), 'sha256': sha(target)})
    pages = []
    with fitz.open(PDF) as doc:
        assert 'Note 20' in doc[282].get_text()
        assert 'Note 21' in doc[284].get_text()
        for n in [283, 284]:
            reading = OUT / 'sources' / f'page-{n}-reading.txt'
            layout = OUT / 'sources' / f'page-{n}-layout.txt'
            render = OUT / 'rendered' / f'page-{n}.png'
            reading.write_text(doc[n - 1].get_text())
            cmd = ['pdftotext', '-f', str(n), '-l', str(n), '-layout', str(PDF.relative_to(ROOT)), str(layout.relative_to(ROOT))]
            subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)
            doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(render)
            pages.append({'pdf_page': n, 'printed_page': n - 2, 'reading': str(reading.relative_to(ROOT)), 'reading_sha256': sha(reading), 'layout': str(layout.relative_to(ROOT)), 'layout_sha256': sha(layout), 'render': str(render.relative_to(ROOT)), 'render_sha256': sha(render), 'command': cmd})
    comparator = ROOT / 'data/accounting-master/jpmorgan-parent-note-20261012/source-ledger.json'
    candidate = ROOT / 'docs/design/proposal/manuscript-parent-cash-20261012/accounting-product-proposal.pdf'
    data = {'source_pdf': str(PDF.relative_to(ROOT)), 'source_pdf_sha256': EXPECTED, 'pages': pages, 'comparator': str(comparator.relative_to(ROOT)), 'comparator_sha256': sha(comparator), 'candidate_pdf': str(candidate.relative_to(ROOT)), 'candidate_pdf_sha256': sha(candidate), 'pointer_snapshots': snapshots, 'wall_seconds': time.monotonic() - start}
    (OUT / 'source-manifest.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'pages': [283, 284], 'snapshots': len(snapshots), 'wall_seconds': data['wall_seconds']}))

if __name__ == '__main__':
    main()
