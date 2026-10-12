"""Render final changed/adjacent pages and run bounded surface diagnostics."""
import json
import subprocess
import time
import fitz
from prepare import OUT, ROOT, BASE, sha, save
from build_candidate import CAND

assert not (OUT/'completion.json').exists()
started=time.monotonic()
pdf=CAND/'accounting-product-proposal.pdf'
doc=fitz.open(pdf)
bib=[i+1 for i,p in enumerate(doc) if i>150 and 'annual report and accounts 2023' in ' '.join(p.get_text().split()).lower()]
assert len(bib)==1, bib
pages=sorted(set([1,143,144,145,146,147]+bib))
records=[]
for n in pages:
    dest=OUT/f'rendered/final-{n}.png'
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False,annots=True).save(dest)
    records.append({'role':'final manuscript','pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
        'pdf_page':n,'scale':1.5,'annots':True,'path':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
save('final-renders.json',records)
auditor='/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py'
runs=[]
for label,base in [('before',BASE),('after',CAND)]:
    for scope,rel in [('root','accounting-product-proposal.tex'),('adapter','sections/adapter-methods.tex')]:
        name=f'surface-{scope}-{label}'
        cmd=['python3',auditor,str(base/rel),'--pdf',str(base/'accounting-product-proposal.pdf'),
            '--output-json',str(OUT/(name+'.json')),'--output-md',str(OUT/(name+'.md'))]
        p=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (OUT/(name+'-stdout.log')).write_text(p.stdout+p.stderr)
        data=json.loads((OUT/(name+'.json')).read_text())
        runs.append({'scope':scope,'version':label,'command':cmd,'exit_code':p.returncode,
            'typo_candidates':data['typo_candidates'],'long_sentence_examples':data['long_sentence_examples'],
            'duplicates':data['duplicate_labels'],'missing_reference_targets':data['missing_reference_targets']})
save('surface-comparison.json',runs)
save('render-run.json',{'command':['python3',str(OUT.relative_to(ROOT))+'/render_review.py'],
    'pymupdf_version':fitz.VersionBind,'rendered_pages':pages,'wall_seconds':time.monotonic()-started,
    'scope':'Root auditor does not expand included files; adapter section inspected separately; full author-source references checked by verify.py.'})
print(json.dumps({'final_pages':pages,'surface_scopes':len(runs),'pdf_sha256':sha(pdf)}))
