"""Extract/render at most two source pages per invocation; retain exact bindings."""
import hashlib,json,sys,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
pages=[int(s) for s in sys.argv[1:]];assert 1<=len(pages)<=2 and len(set(pages))==len(pages)
b=json.loads((OUT/'baseline.json').read_text());pdf=ROOT/b['source_record']['local_path']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf)==b['source_record']['sha256']
path=OUT/'selected-pages.json';rows=json.loads(path.read_text()) if path.exists() else []
assert not any(r['pdf_page'] in pages for r in rows)
doc=fitz.open(pdf)
for folder in ['text','rendered']:(OUT/folder).mkdir(exist_ok=True)
start=time.monotonic()
for n in pages:
    page=doc[n-1];text=page.get_text();t=OUT/'text'/f'page-{n}.txt';t.write_text(text)
    p=OUT/'rendered'/f'page-{n}.png';page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(p)
    rows.append({'pdf_page':n,'text':str(t.relative_to(ROOT)),'text_sha256':sha(t),
       'render':str(p.relative_to(ROOT)),'render_sha256':sha(p),'pdf_sha256':sha(pdf)})
path.write_text(json.dumps(sorted(rows,key=lambda r:r['pdf_page']),indent=2)+'\n')
print(json.dumps({'selected':pages,'pdf_pages':len(doc),'wall_seconds':time.monotonic()-start}))
