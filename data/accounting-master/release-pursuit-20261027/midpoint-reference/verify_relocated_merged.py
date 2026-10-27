from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import fitz

D = Path(__file__).resolve().parent
R = D.parents[3]
M = D/'merged'
T = R/json.loads((M/'baseline.json').read_text())['candidate']
copy = Path(json.loads((M/'relocation/location.json').read_text())['target'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, value):
    assert not p.exists(), p
    p.write_text(json.dumps(value,indent=2)+chr(10))

pages = json.loads((M/'rendered-pages.json').read_text())
assert len(pages) == 12
for row in pages:
    assert row['pdf_sha256'] == sha(T/(row['volume']+'.pdf'))
    row.update(review='author_viewed',image_sha256=sha(R/row['image']))
dump(M/'rendered-review.json',{'pages':pages,
    'scope':'Complete merged main chapter18 pages189–194; covers, next chapter opening and affected simulation pages inspected. Chapter matches the reviewed parent source and rendered text.',
    'independent_reader':'pending','whole_document_acceptance':False})

reports=[]
for name in ['accounting-product-proposal','simulation-foundations']:
    build=json.loads((M/'relocation'/f'{name}.json').read_text())
    assert build['exit_code']==0
    a,b=fitz.open(T/(name+'.pdf')),fitz.open(copy/(name+'.pdf'))
    assert len(a)==len(b)
    differences=[]
    for i in range(len(a)):
        if ' '.join(a[i].get_text().split()) != ' '.join(b[i].get_text().split()):
            differences.append(i+1)
    assert not differences,differences
    log=(copy/(name+'.log')).read_text(errors='replace')
    assert not re.search(r'undefined|Overfull|multiply defined',log,re.I)
    worktree=[]
    for line in (copy/(name+'.fls')).read_text().splitlines():
        if line.startswith('INPUT '):
            p=Path(line[6:]);p=p if p.is_absolute() else copy/p
            if p.resolve().is_relative_to(R):worktree.append(str(p))
    assert not worktree,worktree
    reports.append({'volume':name,'pages':len(a),'reference_pdf_sha256':sha(T/(name+'.pdf')),
        'copied_pdf_sha256':sha(copy/(name+'.pdf')),'all_normalized_page_text_equal':True,
        'original_worktree_tex_inputs':worktree,'build':build})
manifest=json.loads((T/'package-manifest.json').read_text())
for row in manifest['files']:
    assert sha(T/row['path'])==row['sha256']
    if not row['path'].endswith('.pdf'):
        assert sha(copy/row['path'])==row['sha256'],row['path']
out=copy/'reference-output'
cmd=['python3','-I','-B',str(copy/'companions/reference-computations/verify_reference.py'),'--output-dir',str(out)]
run=subprocess.run(cmd,cwd='/tmp',env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True,timeout=60)
assert run.returncode==0,run.stdout+run.stderr
assert json.loads((out/'result.json').read_text())==json.loads((D/'check-01/result.json').read_text())
assert (out/'grid-cases.json').read_bytes()==(D/'check-01/grid-cases.json').read_bytes()
dump(M/'relocation/result.json',{'passed':True,'reports':reports,'files':len(manifest['files']),
    'non_pdf_copied_inputs_preserved':True,'reference_companion_complete_result_equal':True,
    'reference_companion_grid_cases_equal':True,'companion_command':cmd,
    'companion_manifest':json.loads((out/'run-manifest.json').read_text()),
    'timestamp_utc':datetime.now(timezone.utc).isoformat(),
    'limits':'Existing installed environment and selected declared evidence only; no clean installation, independent acceptance or complete executable manuscript reproduction.'})
print(json.dumps({'passed':True,'volumes':[(r['volume'],r['pages']) for r in reports],
                  'files':len(manifest['files']),'reference_result_exact':True}))
