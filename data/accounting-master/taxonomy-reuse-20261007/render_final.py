"""Render the final bounded manuscript slice without changing earlier evidence."""
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PDF = ROOT / 'docs/design/proposal/manuscript-taxonomy-20261008/accounting-product-proposal.pdf'
PAGES = [1, 5, 6, 98, 99, 100, 101, 122, 123, 124, 125, 126, 127]
SCALE = 1.8


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    before = sha(PDF)
    render_dir = OUT / 'render-closeout-20261008'
    render_dir.mkdir(exist_ok=False)
    pages = {}
    with fitz.open(PDF) as document:
        page_count = len(document)
        for number in PAGES:
            output = render_dir / f'p{number}.png'
            document[number - 1].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE)).save(output)
            pages[str(number)] = {'path': str(output.relative_to(ROOT)), 'sha256': sha(output)}
    after = sha(PDF)
    if after != before:
        raise RuntimeError('PDF changed during rendering')
    record = {
        'command': ['python3', str(Path(__file__).relative_to(ROOT))],
        'renderer_script_sha256': sha(Path(__file__)),
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'pdf': str(PDF.relative_to(ROOT)), 'pdf_sha256_before': before,
        'pdf_sha256_after': after, 'pages': page_count, 'page_numbers': PAGES,
        'rendered_pages': pages, 'scale': SCALE, 'exit_code': 0,
        'environment': {'python': platform.python_version(), 'pymupdf': fitz.VersionBind,
                        'device': 'CPU renderer; no GPU/framework invocation'},
        'wall_seconds': time.monotonic() - start,
        'scope': 'Bounded title/contents/body/bibliography rendering; review recorded separately',
    }
    (OUT / 'render-final-manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['pages', 'page_numbers', 'pdf_sha256_after', 'wall_seconds']}))


if __name__ == '__main__':
    main()
