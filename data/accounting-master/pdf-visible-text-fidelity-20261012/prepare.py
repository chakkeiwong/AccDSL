"""Bound one observed cover discrepancy without changing the source corpus."""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / 'data/financial-report-benchmark/documents/hsbc/hsbc-2023-annual/original.pdf'
RETAINED = PDF.with_name('extracted-368e7bba5d1bebe28fa7c587f0e91b45e1eaa34976c693bc53db943da6602eaf.txt')
BASE = ROOT / 'docs/design/proposal/manuscript-junior-classification-20261012'
EXPECTED = '2c03736c288399da08b665d72616e45b93c99764ec47891d9c2bc8fa5175c6c5'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    started = time.monotonic()
    assert not (OUT / 'baseline.json').exists(), 'Never overwrite preserved evidence'
    assert sha(PDF) == EXPECTED
    assert sha(BASE / 'accounting-product-proposal.pdf') == '9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880'
    (OUT / 'rendered').mkdir(exist_ok=True)
    doc = fitz.open(PDF)
    page = doc[0]
    raw = page.get_text('text', sort=False)
    (OUT / 'pymupdf-page1.txt').write_text(raw)
    old = RETAINED.read_text().split('\f')[0]
    (OUT / 'retained-poppler-page1.txt').write_text(old)
    cmd = ['pdftotext', '-f', '1', '-l', '1', '-layout', str(PDF), str(OUT / 'poppler-page1.txt')]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    version = subprocess.run(['pdftotext', '-v'], capture_output=True, text=True, check=True)
    trace = []
    for span in page.get_texttrace():
        if span['seqno'] in [8, 50]:
            trace.append({k: span[k] for k in ['seqno', 'type', 'opacity', 'bbox', 'font', 'size', 'chars']} |
                         {'text': ''.join(chr(c[0]) for c in span['chars'])})
    drawings = []
    for drawing in page.get_drawings():
        if drawing['seqno'] == 49:
            drawings.append({k: drawing[k] for k in ['seqno', 'type', 'fill', 'fill_opacity']} |
                            {'rect': list(drawing['rect']), 'items': [[x[0], list(x[1]), *x[2:]] for x in drawing['items']]})
    save('paint-evidence.json', {'pdf_sha256': EXPECTED, 'pdf_page': 1, 'page_rect': list(page.rect),
        'trace': trace, 'drawings': drawings,
        'bboxlog': [{'seqno': n, 'type': page.get_bboxlog()[n][0], 'bbox': page.get_bboxlog()[n][1]} for n in [8,49,50]],
        'scope': 'Selected painting records explain this title region; no general visibility algorithm.'})
    cover = OUT / 'rendered/hsbc-annual-cover.png'
    page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False, annots=True).save(cover)
    renders = [{'role':'source cover','pdf':str(PDF.relative_to(ROOT)), 'pdf_sha256':EXPECTED,
                'pdf_page':1,'scale':1.5,'annots':True,'path':str(cover.relative_to(ROOT)), 'sha256':sha(cover)}]
    baseline_doc = fitz.open(BASE / 'accounting-product-proposal.pdf')
    for n in [143,144,145]:
        dest = OUT / f'rendered/baseline-{n}.png'
        baseline_doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False, annots=True).save(dest)
        renders.append({'role':'baseline manuscript','pdf':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),
            'pdf_sha256':sha(BASE/'accounting-product-proposal.pdf'),'pdf_page':n,'scale':1.5,
            'annots':True,'path':str(dest.relative_to(ROOT)), 'sha256':sha(dest)})
    save('initial-renders.json',renders)
    snapshots = []
    for rel in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
                'docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
        src = ROOT / rel
        dest = OUT / 'pointers-before' / rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)
        snapshots.append({'live':rel,'snapshot':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
    save('baseline.json', {'source_pdf':str(PDF.relative_to(ROOT)), 'source_sha256':EXPECTED,'source_pages':len(doc),
        'retained_extraction':str(RETAINED.relative_to(ROOT)), 'retained_extraction_sha256':sha(RETAINED),
        'baseline_pdf':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),
        'baseline_pdf_sha256':sha(BASE/'accounting-product-proposal.pdf'),
        'source_hashes':{str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}},
        'pointer_snapshots':snapshots})
    save('diagnostic-run.json', {'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':['python3',str(Path(__file__).relative_to(ROOT))], 'python':platform.python_version(),
        'pymupdf':fitz.VersionBind,'mupdf':fitz.VersionFitz,'pymupdf_options':{'format':'text','sort':False},
        'poppler_version':(version.stdout+version.stderr).strip(),'poppler_command':cmd,
        'retained_extraction_options':'Inherited corpus output; do not infer version/options from fresh run.',
        'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1; no GPU libraries/devices used.',
        'environment_overrides':{'CUDA_VISIBLE_DEVICES':os.environ.get('CUDA_VISIBLE_DEVICES')},
        'random_seeds':'N/A: deterministic document inspection', 'wall_seconds':time.monotonic()-started})
    print(json.dumps({'source_pages':len(doc),'selected_trace_spans':len(trace),'selected_drawings':len(drawings),'renders':len(renders)}))

if __name__ == '__main__':
    main()
