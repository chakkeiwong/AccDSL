"""Check this successor once, preserving the complete predecessor argument."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys
import time
import re
import fitz
from PIL import Image, ImageDraw
from integrate_manuscript import BASE, NEXT, OUT, ROOT, ADDITION


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (OUT/'manuscript-checks.json').exists(), 'Preserve completed checks'
    started = time.monotonic()
    checks = []
    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))
    lock = json.loads((OUT/'baseline-source-lock.json').read_text())
    for row in lock['files']:
        rel = row['path']
        before = (BASE/rel).read_text()
        after = (NEXT/rel).read_text()
        check('baseline/'+rel, sha(BASE/rel) == row['sha256'])
        check('snapshot/'+rel, sha(OUT/'baseline-sources'/rel) == row['sha256'])
        if rel == 'accounting-product-proposal.tex':
            after = after.replace('Version 3.40 (proposal candidate)', 'Version 3.39 (proposal candidate)')
        if rel == 'sections/aligned-option-components.tex':
            after = after.removesuffix(ADDITION)
        check('preserved-argument/'+rel, after == before)
    text = '\n'.join(p.read_text() for p in NEXT.rglob('*.tex'))
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    refs = re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}', text)
    duplicates = [k for k,v in Counter(labels).items() if v > 1]
    missing = sorted(set(refs)-set(labels))
    check('unique-labels', not duplicates)
    check('resolved-references', not missing)
    warnings = [s for s in (NEXT/'accounting-product-proposal.log').read_text().splitlines()
        if any(x in s for x in ('Overfull', 'undefined', 'multiply defined', 'Missing character', 'Fatal error', 'LaTeX Error'))]
    check('material-build-diagnostics', not warnings)
    doc = fitz.open(NEXT/'accounting-product-proposal.pdf')
    hits, bounds = {}, []
    terms = ['Equal option premiums can conceal a changing net time value',
             'These synthetic marks also have a simple consistency check',
             'Unmatched actual/aligned changes under B6.5.33']
    for i,page in enumerate(doc):
        plain = ' '.join(page.get_text().split())
        for term in terms:
            if term in plain and i > 15:
                hits[term] = i+1
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0,y0,x1,y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        bounds.append(dict(page=i+1, text=span['text'][:90]))
    check('all-page-text-bounds', not bounds)
    for i,term in enumerate(terms):
        check('new-section-anchor-'+str(i), term in hits)
    assert terms[0] in hits and terms[-1] in hits, hits
    pages = sorted(set([1,8,len(doc)-1,len(doc)] + list(range(hits[terms[0]]-1,hits[terms[-1]]+2))))
    render = OUT/'render-attempt-01'
    render.mkdir(exist_ok=False)
    images = []
    for n in pages:
        p = render/f'page-{n:03d}.png'
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p)
        images.append(dict(page=n,path=str(p.relative_to(ROOT)),sha256=sha(p)))
    for start in range(0,len(images),6):
        sheet = Image.new('RGB',(1200,1180),'#dddddd')
        draw = ImageDraw.Draw(sheet)
        for j,row in enumerate(images[start:start+6]):
            im = Image.open(ROOT/row['path']).convert('RGB')
            im.thumbnail((390,555))
            x,y = (j%3)*400,(j//3)*590
            sheet.paste(im,(x,y+25))
            draw.text((x+5,y+5),str(row['page']),fill='black')
        sheet.save(render/f'contact-{start//6+1:02d}.png')
    pdf = NEXT/'accounting-product-proposal.pdf'
    result = dict(version='3.40',pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),pages=len(doc),
        baseline_sources=len(lock['files']),checks=len(checks),failures=sum(not c['passed'] for c in checks),
        detail=checks,missing_references=missing,duplicate_labels=duplicates,material_build_warnings=warnings,
        text_bounds=bounds,section_pages=hits,rendered_pages=pages,visual_review='pending',human_acceptance='pending')
    (OUT/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'render-manifest.json').write_text(json.dumps(dict(pdf_sha256=sha(pdf),pages=images),indent=2)+'\n')
    shutil.copy2(NEXT/'accounting-product-proposal.log',OUT/'build-transcript.log')
    manifest = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        build_command='latexmk -lualatex -silent -g -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex',
        build_directory=str(NEXT.relative_to(ROOT)),build_exit_code=0,
        build_wall_time='not captured by asynchronous shell invocation; no duration inferred',
        command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python data/accounting-master/zero-cost-collar-20261017/check_manuscript.py',
        interpreter=sys.executable,environment='existing tfgpu Python/PyMuPDF/Pillow; no framework import',
        gpu_status='intentionally hidden by CUDA_VISIBLE_DEVICES=-1',seeds='N/A: deterministic document checks',
        data_version='protected 140 Version 3.39 sources',wall_seconds=time.monotonic()-started,
        plan='docs/plans/accounting-zero-cost-collar-20261017.md',result=str((OUT/'manuscript-result.md').relative_to(ROOT)))
    (OUT/'manuscript-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('pages','pdf_sha256','checks','failures','section_pages','rendered_pages')}))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
