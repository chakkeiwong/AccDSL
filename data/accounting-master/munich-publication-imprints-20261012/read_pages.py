"""Inspect at most two nominated source pages per call; preserve text and images."""
import hashlib,json,sys
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
specs=[s.rsplit(':',1) for s in sys.argv[1:]];assert 1<=len(specs)<=2
sources=json.loads((OUT/'selected-sources.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
path=OUT/'selected-pages.json';rows=json.loads(path.read_text()) if path.exists() else []
for key,num in specs:
    n=int(num);assert not any(r['document_id']==key and r['pdf_page']==n for r in rows)
    r=sources[key];pdf=ROOT/r['local_path'];assert sha(pdf)==r['sha256']
    doc=fitz.open(pdf);page=doc[n-1];folder=OUT/'pages'/key;folder.mkdir(parents=True,exist_ok=True)
    t=folder/f'page-{n}.txt';t.write_text(page.get_text())
    p=folder/f'page-{n}.png';page.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(p)
    rows.append({'document_id':key,'pdf_page':n,'pdf_pages':len(doc),'pdf_sha256':sha(pdf),
      'text':str(t.relative_to(ROOT)),'text_sha256':sha(t),'render':str(p.relative_to(ROOT)),'render_sha256':sha(p)})
    print(key,n,'pages',len(doc))
path.write_text(json.dumps(rows,indent=2)+'\n')
