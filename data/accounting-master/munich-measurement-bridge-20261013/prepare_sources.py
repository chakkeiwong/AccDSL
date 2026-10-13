"""Capture bounded issuer excerpts and renders without altering retained sources."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

import fitz

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
SOURCE = ROOT / 'data/financial-report-benchmark/documents/munich_re/munich_re-2023-annual/original.pdf'
BASE = ROOT / 'docs/design/proposal/manuscript-munich-new-contracts-20261013'
PLAN = ROOT / 'docs/plans/accounting-munich-measurement-bridge-20261013.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    assert not (UNIT / 'baseline.json').exists()
    assert sha(SOURCE) == 'b86cccaaa0a9f0c4b1cc56fd87db770a9ca84bfb0c0222662d7295b3014d3ec9'
    assert sha(BASE / 'accounting-product-proposal.pdf') == '7063e69f66be2d14c464f09c104cb1b3cef9db64526433b969c1fa1647fe4a74'
    controls = []
    for rel in ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
                'docs/plans/accounting-continuation-requirements-20261007.md', 'data/accounting-master/next-plan.md']:
        p = ROOT / rel
        q = UNIT / 'before' / rel
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(p.read_bytes())
        controls.append({'live': rel, 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT, text=True)
    assert len(index.splitlines()) == 100
    (UNIT / 'unrelated-index-before.txt').write_text(index)
    prior = ROOT / 'data/accounting-master/munich-transition-disclosures-20261012/baseline.json'
    source_record = json.loads(prior.read_text())['source_record']
    save('baseline.json', {'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                          'baseline': str(BASE.relative_to(ROOT)), 'baseline_pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf'),
                          'source_pdf': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                          'source_record': source_record, 'controls': controls,
                          'plan': str(PLAN.relative_to(ROOT)), 'plan_sha256': sha(PLAN)})
    out = UNIT / 'source-pages'
    out.mkdir()
    pages = []
    with fitz.open(SOURCE) as doc:
        for number in [232, 233, 243, 248, 255, 256, 266]:
            page = doc[number - 1]
            text_path, image_path = out / f'page-{number}.txt', out / f'page-{number}.png'
            text_path.write_text(page.get_text())
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(image_path)
            pages.append({'pdf_page': number, 'text_path': str(text_path.relative_to(ROOT)), 'text_sha256': sha(text_path),
                          'image_path': str(image_path.relative_to(ROOT)), 'image_sha256': sha(image_path)})
        save('source-pages.json', {'source_path': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                                   'page_count': len(doc), 'pages': pages})
    print(json.dumps({'captured_pages': [p['pdf_page'] for p in pages], 'source_sha256': sha(SOURCE), 'baseline_preserved': True}))


if __name__ == '__main__':
    main()
