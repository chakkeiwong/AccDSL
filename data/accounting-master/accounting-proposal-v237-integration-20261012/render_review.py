"""Bind final bank pages and compare their rendered bytes to Version 2.36."""
import hashlib
import json
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
PRIOR = ROOT / 'data/accounting-master/accounting-proposal-v236-integration-20261012/render-manifest.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    prior = {r['pdf_page']: r['sha256'] for r in json.loads(PRIOR.read_text())['renders']}
    (OUT / 'rendered').mkdir(exist_ok=True)
    rows = []
    with fitz.open(PDF) as doc:
        assert len(doc) == 174
        for n in range(115, 127):
            path = OUT / 'rendered' / f'page-{n}.png'
            doc[n-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(path)
            digest = sha(path)
            rows.append({'pdf_page': n, 'image': str(path.relative_to(ROOT)), 'sha256': digest, 'same_render_as_v236': digest == prior[n]})
    data = {'pdf': str(PDF.relative_to(ROOT)), 'pdf_sha256': sha(PDF), 'pages': 174, 'scale': 1.35, 'renders': rows}
    (OUT / 'render-manifest.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'pdf_sha256': data['pdf_sha256'], 'pages': data['pages'], 'renders': len(rows), 'changed_pages': [r['pdf_page'] for r in rows if not r['same_render_as_v236']]}))

if __name__ == '__main__': main()
