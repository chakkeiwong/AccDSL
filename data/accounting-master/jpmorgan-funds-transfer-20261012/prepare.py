"""Retain complete bounded source pages and the protected manuscript baseline."""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PDF=ROOT/'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf'
EXPECTED='e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c'
BASE=ROOT/'docs/design/proposal/manuscript-visible-text-20261012'
BASE_HASH='f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    start=time.monotonic()
    assert not (OUT/'source-manifest.json').exists()
    assert sha(PDF)==EXPECTED and sha(BASE/'accounting-product-proposal.pdf')==BASE_HASH
    (OUT/'sources').mkdir(exist_ok=True)
    (OUT/'rendered').mkdir(exist_ok=True)
    doc=fitz.open(PDF)
    records=[]
    for n in [6,294]:
        page=doc[n-1]
        raw=OUT/f'sources/page-{n}-reading.txt'
        layout=OUT/f'sources/page-{n}-layout.txt'
        render=OUT/f'rendered/source-{n}.png'
        raw.write_text(page.get_text('text',sort=False))
        cmd=['pdftotext','-f',str(n),'-l',str(n),'-layout',str(PDF),str(layout)]
        subprocess.run(cmd,capture_output=True,check=True,timeout=30)
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(render)
        records.append({'pdf_page':n,'printed_page':n-2,'raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),
            'layout':str(layout.relative_to(ROOT)),'layout_sha256':sha(layout),
            'render':str(render.relative_to(ROOT)),'render_sha256':sha(render),'command':cmd})
    bdoc=fitz.open(BASE/'accounting-product-proposal.pdf')
    br=[]
    for n in [115,116]:
        dest=OUT/f'rendered/baseline-{n}.png'
        bdoc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(dest)
        br.append({'pdf_page':n,'render':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
    pointers=[]
    for rel in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
        'docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
        dest=OUT/'pointers-before'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,dest)
        pointers.append({'live':rel,'snapshot':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
    version=subprocess.run(['pdftotext','-v'],capture_output=True,text=True,check=True)
    save('source-manifest.json',{'pdf':str(PDF.relative_to(ROOT)),'sha256':EXPECTED,'pages':records,
        'baseline_pdf':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':BASE_HASH,
        'baseline_renders':br,'pointer_snapshots':pointers,
        'source_hashes':{str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}},
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':['python3',str(Path(__file__).relative_to(ROOT))],
        'environment':{'python':platform.python_version(),'pymupdf':fitz.VersionBind,'mupdf':fitz.VersionFitz,
            'poppler':(version.stdout+version.stderr).strip(),'CUDA_VISIBLE_DEVICES':os.environ.get('CUDA_VISIBLE_DEVICES')},
        'wall_seconds':time.monotonic()-start,'render_scale':1.5,
        'scope':'Issuer assertions in retained 2025 Form 10-K; current-law verification and historical availability not established.'})
    print(json.dumps({'source_pages':[6,294],'baseline_pages':[115,116],'source_sha256':EXPECTED}))

if __name__=='__main__':main()
