"""Preserve Version 3.28 and inspect senior/capped participation."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript-fiscal-loss-closing-20261016'
NEXT = ROOT / 'docs/design/proposal/manuscript-capped-participation-20261016'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    started = time.monotonic()
    checks = []
    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))
    lock = json.loads((OUT / 'baseline-source-lock.json').read_text())
    for item in lock['files']:
        rel = item['path']
        before = (BASE / rel).read_text()
        after = (NEXT / rel).read_text()
        check('baseline/' + rel, sha(BASE / rel) == item['sha256'])
        check('snapshot/' + rel, sha(OUT / 'baseline-sources' / rel) == item['sha256'])
        if rel == 'accounting-product-proposal.tex':
            after = after.replace('Version 3.29 (proposal candidate)', 'Version 3.28 (proposal candidate)')
        elif rel == 'sections/awards-participation.tex':
            after = after.replace('\n\\input{sections/capped-participation}\n', '')
        check('preserved-argument/' + rel, after == before)
    all_text = '\n'.join(p.read_text() for p in NEXT.rglob('*.tex'))
    labels = re.findall(r'\\label\{([^}]+)\}', all_text)
    refs = re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}', all_text)
    duplicate = [k for k, v in Counter(labels).items() if v > 1]
    missing = sorted(set(refs) - set(labels))
    check('unique-labels', not duplicate)
    check('resolved-references', not missing)
    warnings = [s for s in (NEXT / 'accounting-product-proposal.log').read_text().splitlines()
                if any(x in s for x in ('Overfull', 'undefined', 'multiply defined', 'Missing character', 'Fatal error', 'LaTeX Error'))]
    check('material-build-diagnostics', not warnings)
    pdf = NEXT / 'accounting-product-proposal.pdf'
    doc = fitz.open(pdf)
    bounds = []
    hits = []
    for i, page in enumerate(doc):
        if 'A senior dividend and a cap change who receives' in page.get_text():
            hits.append(i + 1)
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines', []):
                for span in line.get('spans', []):
                    x0, y0, x1, y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1:
                        bounds.append(dict(page=i+1, text=span['text'][:100]))
    check('all-page-text-bounds', not bounds)
    check('capped-participation-section-found', any(p > 20 for p in hits))
    start = min(p for p in hits if p > 20)
    end = next(i+1 for i,page in enumerate(doc) if i+1 >= start and 'Those cases need their own joint' in page.get_text())
    pages = sorted({1,8} | set(range(start-2,end+2)))
    indices = [int(p.name.split('-')[-1]) for p in OUT.glob('render-attempt-[0-9][0-9]')]
    render = OUT / ('render-attempt-%02d' % (max(indices, default=0) + 1))
    render.mkdir(exist_ok=False)
    images = []
    for n in pages:
        path = render / ('page-%03d.png' % n)
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(path)
        images.append(dict(page=n, path=str(path.relative_to(ROOT)), sha256=sha(path)))
    for start in range(0, len(images), 6):
        sheet = Image.new('RGB', (1200, 1180), '#dddddd')
        draw = ImageDraw.Draw(sheet)
        for j, item in enumerate(images[start:start+6]):
            im = Image.open(ROOT / item['path']).convert('RGB')
            im.thumbnail((390, 555))
            x, y = (j % 3)*400, (j // 3)*590
            sheet.paste(im, (x, y+25))
            draw.text((x+5, y+5), 'Physical page ' + str(item['page']), fill='black')
        sheet.save(render / ('contact-%02d.png' % (start//6+1)))
    result = dict(version='3.29', pages=len(doc), pdf=str(pdf.relative_to(ROOT)), pdf_sha256=sha(pdf),
                  baseline_sources=len(lock['files']), checks=len(checks), failures=sum(not c['passed'] for c in checks),
                  detail=checks, missing_references=missing, duplicate_labels=duplicate, material_build_warnings=warnings,
                  text_bounds=bounds, rendered_pages=pages, section_pages=hits, visual_review='pending', human_acceptance='pending')
    write(OUT / 'manuscript-checks.json', result)
    write(OUT / 'render-manifest.json', dict(pdf_sha256=sha(pdf), pages=images))
    shutil.copy2(NEXT / 'accounting-product-proposal.log', OUT / 'build-transcript.log')
    write(OUT / 'manuscript-manifest.json', dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
          git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/capped-participation-20261016/check_manuscript.py',
          build_command='latexmk -lualatex -silent -g -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex',
          build_directory=str(NEXT.relative_to(ROOT)), build_exit_code=0, build_wall_seconds=None,
          build_time_note='Build completion checked from its retained transcript; exact duration is recorded separately when available.',
          interpreter=sys.executable, environment='tfgpu Python; PyMuPDF/Pillow; existing LuaLaTeX; no framework import',
          gpu_status='intentionally hidden with CUDA_VISIBLE_DEVICES=-1', random_seeds='N/A: deterministic document validation',
          data_version='protected 128 Version 3.28 sources; 3.29 senior/capped participation',
          wall_seconds=round(time.monotonic()-started, 3), plan='docs/plans/accounting-capped-participation-20261016.md',
          result=str((OUT / 'manuscript-result.md').relative_to(ROOT)),
          output_paths=[str(pdf.relative_to(ROOT)), str((OUT / 'manuscript-checks.json').relative_to(ROOT)), str((OUT / 'render-manifest.json').relative_to(ROOT))]))
    print(json.dumps({k: result[k] for k in ('version', 'pages', 'pdf_sha256', 'checks', 'failures', 'section_pages', 'rendered_pages')}))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
