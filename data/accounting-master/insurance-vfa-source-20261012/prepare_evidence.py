"""Retain exact historical-source pages and selected readable renders."""
import hashlib
import json
import time
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
start = time.monotonic()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = ROOT / 'docs/design/research/standards/aasb17.pdf'
assert sha(source) == '153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3'
doc = fitz.open(source)
pages = [1, 5, 6, 10, 11, 12, 13, 14, 18, 21, 29, 30, 38, 43, 44, 49, 50, 51, 52]
texts = []
for n in pages:
    p = OUT / 'text' / f'page-{n}.txt'
    p.write_text(doc[n-1].get_text())
    texts.append({'pdf_page': n, 'text': str(p.relative_to(ROOT)), 'sha256': sha(p)})
renders = []
for n in [1, 13, 14, 50, 51, 52]:
    p = OUT / 'rendered' / f'source-{n}.png'
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(p)
    renders.append({'pdf_page': n, 'render': str(p.relative_to(ROOT)), 'sha256': sha(p), 'source_pdf_sha256': sha(source)})
record = {'command': ['python3', str(Path(__file__).relative_to(ROOT))], 'source': str(source.relative_to(ROOT)),
    'source_sha256': sha(source), 'source_pages': len(doc), 'extracted_pages': texts, 'renders': renders,
    'scope': 'Nineteen selected pages; not a full 96-page standard review', 'wall_seconds': time.monotonic()-start}
(OUT / 'source-evidence.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({'extracted_pages': len(texts), 'rendered_pages': len(renders), 'wall_seconds': record['wall_seconds']}))
