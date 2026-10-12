"""Render changed bank pages and adjacent material; audit the chapter source."""
import json
import subprocess
import time
import fitz
from prepare import OUT, ROOT, BASE, sha, save
from build_candidate import CAND

assert not (OUT/'completion.json').exists()
start=time.monotonic();pdf=CAND/'accounting-product-proposal.pdf';d=fitz.open(pdf)
pages=[1,115,116,117,118,119]
renders=[]
for n in pages:
    p=OUT/f'rendered/final-{n}.png'
    d[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(p)
    renders.append({'pdf_page':n,'render':str(p.relative_to(ROOT)),'sha256':sha(p),'pdf_sha256':sha(pdf)})
save('final-renders.json',renders)
auditor='/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py'
surfaces=[]
for label,base in [('before',BASE),('after',CAND)]:
    cmd=['python3',auditor,str(base/'chapters/15-banking.tex'),'--pdf',str(base/'accounting-product-proposal.pdf'),
        '--output-json',str(OUT/f'surface-{label}.json'),'--output-md',str(OUT/f'surface-{label}.md')]
    p=subprocess.run(cmd,capture_output=True,text=True,check=True)
    (OUT/f'surface-{label}-stdout.log').write_text(p.stdout+p.stderr)
    surfaces.append({'version':label,'command':cmd,'exit_code':p.returncode})
save('render-run.json',{'command':['python3',str(OUT.relative_to(ROOT))+'/render_review.py'],
    'pymupdf':fitz.VersionBind,'scale':1.5,'pages':pages,'surface_runs':surfaces,'wall_seconds':time.monotonic()-start})
print(json.dumps({'rendered_pages':pages,'pdf_pages':len(d),'pdf_sha256':sha(pdf)}))
