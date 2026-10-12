"""Prepare at most two readable pages per call, with PDF and image bindings."""
import hashlib
import json
import sys
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
args=sys.argv[1:]; before=bool(args and args[0]=='--before')
if before: args=args[1:]
pages=[int(n) for n in args]; assert 1<=len(pages)<=2
kind='before' if before else 'final'
folder='manuscript-transition-20261012' if before else 'manuscript-transition-bases-20261012'
pdf=ROOT/'docs/design/proposal'/folder/'accounting-product-proposal.pdf'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
doc=fitz.open(pdf); parent=OUT/(kind+'-rendered');parent.mkdir(exist_ok=True)
record=OUT/(kind+'-renders.json')
rows=json.loads(record.read_text()) if record.exists() else []
assert not any(r['pdf_page'] in pages for r in rows)
for n in pages:
    assert 1<=n<=len(doc)
    p=parent/f'page-{n}.png';doc[n-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(p)
    t=parent/f'page-{n}.txt';t.write_text(doc[n-1].get_text())
    rows.append({'pdf_page':n,'render':str(p.relative_to(ROOT)),'sha256':sha(p),
                 'text':str(t.relative_to(ROOT)),'text_sha256':sha(t),'pdf_sha256':sha(pdf)})
record.write_text(json.dumps(sorted(rows,key=lambda r:r['pdf_page']),indent=2)+'\n')
print(json.dumps({'kind':kind,'pages':pages,'pdf_pages':len(doc)}))
