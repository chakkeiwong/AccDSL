from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import fitz

D = Path(__file__).resolve().parent
R = D.parents[3]
M = D/'merged'
c = json.loads((M/'baseline.json').read_text())
B, T = R/c['baseline'], R/c['candidate']
A = R/'docs/design/proposal/manuscript-reference-v554r3-20261027'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, v):
    p.write_text(json.dumps(v,indent=2)+'\n')
assert not (M/'verification.json').exists()
checks, changed, patch = [], [], []
for row in c['files']:
    assert sha(B/row['path']) == row['sha256']
    checks.append('baseline:'+row['path'])
    if sha(T/row['path']) != row['sha256']:
        changed.append(row['path'])
        if (T/row['path']).suffix != '.pdf':
            patch.extend(difflib.unified_diff((B/row['path']).read_text().splitlines(True),
                (T/row['path']).read_text().splitlines(True),fromfile='5.55/'+row['path'],tofile='5.55-R1/'+row['path']))
assert set(changed) == set(c['allowed_changes']), changed
assert sha(T/'simulation/18-computation-cases.tex') == c['repair_source_sha256']
for p in c['added_files']:
    assert (T/p).read_bytes() == (A/p).read_bytes()
checks += ['exact_changes','reviewed_chapter_exact','companion_exact']
volumes, rendered = [], []
out = M/'rendered'
out.mkdir(exist_ok=False)
for name, prefix in [('accounting-product-proposal','main'),('simulation-foundations','simulation')]:
    assert json.loads((M/'build'/f'{name}.json').read_text())['exit_code'] == 0
    log = (T/(name+'.log')).read_text(errors='replace')
    assert not re.search(r'undefined|Overfull|multiply defined',log,re.I)
    doc = fitz.open(T/(name+'.pdf'))
    assert '5.55-R1' in doc[0].get_text()
    toc = doc.get_toc()
    start = next(x[2] for x in toc if x[1].startswith('18 '))
    stop = next(x[2] for x in toc if x[1].startswith('19 '))
    pages = [1,*range(start,stop+1)] if prefix=='main' else [1,start,start+1,stop-1]
    for n in pages:
        f = out/f'{prefix}-{n:04}.png'
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(f)
        rendered.append({'volume':name,'page':n,'image':str(f.relative_to(R)),
                         'pdf_sha256':sha(T/(name+'.pdf')),'review':'not_viewed'})
    for page in doc:
        assert all(w[0]>=-1 and w[1]>=-1 and w[2]<=page.rect.width+1 and w[3]<=page.rect.height+1 for w in page.get_text('words'))
    # The repaired chapter is identical to the already reviewed branch, apart
    # from folios. Check text within each chapter to avoid assuming placement.
    prior = fitz.open(A/(name+'.pdf'))
    ptoc = prior.get_toc()
    pa = next(x[2] for x in ptoc if x[1].startswith('18 '))
    pb = next(x[2] for x in ptoc if x[1].startswith('19 '))
    def bodytext(d,a,b):
        return ['\n'.join(l for l in d[i-1].get_text().splitlines() if not l.strip().isdigit()) for i in range(a,b)]
    assert bodytext(doc,start,stop) == bodytext(prior,pa,pb)
    volumes.append({'name':name,'pages':len(doc),'sha256':sha(T/(name+'.pdf')),'chapter18':[start,stop-1]})
    checks.extend([name+':build',name+':references',name+':version',name+':rectangle',name+':reviewed_chapter_text'])
(M/'source-delta.patch').write_text(''.join(patch))
dump(M/'verification.json',{'passed':True,'checks':checks,'changed':changed,'volumes':volumes,
    'timestamp_utc':datetime.now(timezone.utc).isoformat(),'acceptance':'author review and whole-document acceptance remain separate'})
dump(M/'rendered-pages.json',rendered)
manifest = json.loads((B/'package-manifest.json').read_text())
manifest.update(candidate='5.55-R1;not_ready',manifest_self_hash='Stored outside in midpoint-reference/merged/package-record.json')
for p in c['added_files']:
    manifest['files'].append({'path':p})
for row in manifest['files']:
    p=T/row['path'];row.update(sha256=sha(p),bytes=p.stat().st_size)
dump(T/'package-manifest.json',manifest)
run=subprocess.run(['python3','-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True)
assert run.returncode==0,run.stdout+run.stderr
dump(M/'package-record.json',{'passed':True,'files':len(manifest['files']),
    'manifest_sha256':sha(T/'package-manifest.json'),'verification':json.loads(run.stdout),
    'predecessor_manifest_sha256':c['baseline_manifest_sha256']})
rel = M/'relocation';rel.mkdir(exist_ok=False)
target=Path(tempfile.mkdtemp(prefix='accdsl-v555r1-relocated-'))
for row in manifest['files']:
    p=target/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((T/row['path']).read_bytes())
shutil.copy2(T/'package-manifest.json',target/'package-manifest.json')
dump(rel/'location.json',{'target':str(target),'manifest_sha256':sha(T/'package-manifest.json')})
print(json.dumps({'passed':True,'checks':len(checks),'files':len(manifest['files']),'volumes':volumes,'rendered':[(x['volume'],x['page']) for x in rendered],'relocated':str(target)}))
