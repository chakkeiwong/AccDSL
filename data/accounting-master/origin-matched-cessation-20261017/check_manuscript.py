"""Preservation, build and rendered-bound checks for this successor only."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import fitz
from PIL import Image, ImageDraw
from integrate_manuscript import BASE, NEXT, OUT, ROOT, ADDITION


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'manuscript-checks.json').exists(), 'Preserve completed checks'
    started = time.monotonic()
    checks = []
    def check(name, passed):
        checks.append(dict(name=name, passed=bool(passed)))
    lock = json.loads((OUT/'baseline-source-lock.json').read_text())
    for row in lock['files']:
        relative = row['path']
        before = (BASE/relative).read_text()
        after = (NEXT/relative).read_text()
        check('baseline/'+relative, sha(BASE/relative) == row['sha256'])
        check('snapshot/'+relative, sha(OUT/'baseline-sources'/relative) == row['sha256'])
        if relative == 'accounting-product-proposal.tex':
            after = after.replace('Version 3.41 (proposal candidate)', 'Version 3.40 (proposal candidate)')
        if relative == 'sections/partial-hedge-discontinuation.tex':
            after = after.removesuffix(ADDITION)
        check('preserved-argument/'+relative, after == before)
    check('new-section-matches-draft', (NEXT/'sections/origin-matched-cessation.tex').read_bytes() == (OUT/'cessation.tex').read_bytes())
    text = '\n'.join(p.read_text() for p in NEXT.rglob('*.tex'))
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    refs = re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}', text)
    duplicates = [key for key, count in Counter(labels).items() if count > 1]
    missing = sorted(set(refs)-set(labels))
    check('unique-labels', not duplicates)
    check('resolved-references', not missing)
    warnings = [line for line in (NEXT/'accounting-product-proposal.log').read_text().splitlines()
        if any(term in line for term in ('Overfull', 'undefined', 'multiply defined',
                                        'Missing character', 'Fatal error', 'LaTeX Error'))]
    check('material-build-diagnostics', not warnings)
    doc = fitz.open(NEXT/'accounting-product-proposal.pdf')
    terms = ['Different designation origins require their own gain histories',
             'The identical derivative cash does not make the histories interchangeable.',
             'General heterogeneous attribution remains open.']
    hits, bounds = {}, []
    for index, page in enumerate(doc):
        plain = ' '.join(page.get_text().split())
        for term in terms:
            if term in plain and index > 15:
                hits[term] = index+1
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0,y0,x1,y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        bounds.append(dict(page=index+1, text=span['text'][:90]))
    check('all-page-text-bounds', not bounds)
    for index, term in enumerate(terms):
        check('new-section-anchor-'+str(index), term in hits)
    assert all(term in hits for term in terms), hits
    pages = sorted(set([1,8,len(doc)-1,len(doc)] +
                       list(range(hits[terms[0]]-1,hits[terms[-1]]+2))))
    render = OUT/'render-attempt-01'
    render.mkdir(exist_ok=False)
    images = []
    for number in pages:
        path = render/f'page-{number:03d}.png'
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(path)
        images.append(dict(page=number,path=str(path.relative_to(ROOT)),sha256=sha(path)))
    for start in range(0,len(images),6):
        sheet = Image.new('RGB',(1200,1180),'#dddddd')
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(images[start:start+6]):
            im = Image.open(ROOT/row['path']).convert('RGB')
            im.thumbnail((390,555))
            x,y = (index%3)*400,(index//3)*590
            sheet.paste(im,(x,y+25))
            draw.text((x+5,y+5),str(row['page']),fill='black')
        sheet.save(render/f'contact-{start//6+1:02d}.png')
    pdf = NEXT/'accounting-product-proposal.pdf'
    result = dict(version='3.41',pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),pages=len(doc),
        baseline_sources=len(lock['files']),checks=len(checks),failures=sum(not c['passed'] for c in checks),
        detail=checks,missing_references=missing,duplicate_labels=duplicates,material_build_warnings=warnings,
        text_bounds=bounds,section_pages=hits,rendered_pages=pages,
        visual_review='pending; separate rendered-review.json',human_acceptance='pending')
    (OUT/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'render-manifest.json').write_text(json.dumps(dict(pdf_sha256=sha(pdf),pages=images),indent=2)+'\n')
    shutil.copy2(NEXT/'accounting-product-proposal.log',OUT/'build-transcript.log')
    build = json.loads((OUT/'build-attempt-02.json').read_text())
    assert build['exit_code'] == 0
    manifest = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        build=build,
        command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python data/accounting-master/origin-matched-cessation-20261017/check_manuscript.py',
        interpreter=sys.executable,environment='existing tfgpu Python/PyMuPDF/Pillow; no framework import',
        gpu_status='intentionally hidden by CUDA_VISIBLE_DEVICES=-1',seeds='N/A: deterministic document checks',
        data_version='protected 141 Version 3.40 sources',wall_seconds=time.monotonic()-started,
        plan='docs/plans/accounting-origin-matched-cessation-20261017.md',
        result=str((OUT/'manuscript-result.md').relative_to(ROOT)))
    (OUT/'manuscript-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('pages','pdf_sha256','checks','failures','section_pages','rendered_pages')}))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
