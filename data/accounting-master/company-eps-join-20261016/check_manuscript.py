"""Check all preserved content, final build and changed rendered pages."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-ordered-eps-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-company-eps-20261016'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,ok): checks.append(dict(name=name,passed=bool(ok)))
    lock=json.loads((OUT/'baseline-source-lock.json').read_text())
    for item in lock['files']:
        rel=item['path']; before=(BASE/rel).read_text(); text=(NEXT/rel).read_text()
        check('baseline/'+rel,sha(BASE/rel)==item['sha256'])
        check('snapshot/'+rel,sha(OUT/'baseline-sources'/rel)==item['sha256'])
        if rel=='accounting-product-proposal.tex':
            text=text.replace('Version 3.16 (proposal candidate)','Version 3.15 (proposal candidate)')
        elif rel=='chapters/14-financing-groups.tex':
            text=text.replace('\n\n\\input{sections/company-eps-join}','')
        elif rel=='chapters/17-portable-reference.tex':
            text=text.removesuffix('\n\\input{sections/company-eps-records}\n')
        elif rel=='sections/eps-lifecycle.tex':
            text=text.replace((OUT/'early-conversion-qualification.txt').read_text(),'')
        check('inherited-content/'+rel,text==before)
    all_text='\n'.join(p.read_text() for p in NEXT.rglob('*.tex'))
    labels=re.findall(r'\\label\{([^}]+)\}',all_text)
    refs=re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}',all_text)
    duplicates=[k for k,v in Counter(labels).items() if v>1]
    missing=sorted(set(refs)-set(labels))
    check('unique-labels',not duplicates); check('resolved-references',not missing)
    warnings=[line for line in (NEXT/'accounting-product-proposal.log').read_text().splitlines() if any(s in line for s in ['Overfull','undefined','multiply defined','Missing character','Fatal error','LaTeX Error'])]
    check('material-build-warning',not warnings)
    pdf=NEXT/'accounting-product-proposal.pdf'; doc=fitz.open(pdf); bounds=[]
    for i,page in enumerate(doc):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line.get('spans',[]):
                    x0,y0,x1,y1=span['bbox']
                    if x0< -1 or y0< -1 or x1>page.rect.width+1 or y1>page.rect.height+1:
                        bounds.append(dict(page=i+1,text=span['text'][:100]))
    check('all-page-text-bounds',not bounds)
    pages=[1,8,175,176,177,178,179,332,333,334]
    render=OUT/'render-attempt-01';render.mkdir(exist_ok=False); images=[]
    for number in pages:
        path=render/('page-%03d.png'%number);doc[number-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(path)
        images.append(dict(page=number,path=str(path.relative_to(ROOT)),sha256=sha(path)))
    for start in range(0,len(images),6):
        sheet=Image.new('RGB',(1200,1180),'#dddddd');draw=ImageDraw.Draw(sheet)
        for j,rec in enumerate(images[start:start+6]):
            im=Image.open(ROOT/rec['path']).convert('RGB');im.thumbnail((390,555));x=(j%3)*400;y=(j//3)*590
            sheet.paste(im,(x,y+25));draw.text((x+5,y+5),'Physical page '+str(rec['page']),fill='black')
        sheet.save(render/('contact-%02d.png'%(start//6+1)))
    result=dict(version='3.16',pages=len(doc),pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),baseline_sources=len(lock['files']),
        checks=len(checks),failures=sum(not c['passed'] for c in checks),detail=checks,missing_references=missing,duplicate_labels=duplicates,
        material_build_warnings=warnings,text_bounds=bounds,rendered_pages=pages,visual_review='pending',human_acceptance='pending')
    (OUT/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'render-manifest.json').write_text(json.dumps(dict(pdf_sha256=sha(pdf),pages=images),indent=2)+'\n')
    shutil.copy2('/tmp/accdsl-company-eps-build.log',OUT/'build-stdout.log')
    print(json.dumps({k:result[k] for k in ['version','pages','pdf_sha256','checks','failures','material_build_warnings']}))
    if result['failures']: raise SystemExit(1)

if __name__=='__main__': main()
