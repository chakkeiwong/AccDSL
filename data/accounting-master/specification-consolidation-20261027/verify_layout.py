from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,re,fitz
H=Path(__file__).resolve().parent; R=H.parents[2]
T=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert not (H/'verification-02.json').exists()
lock=read(H/'layout-source-lock.json'); original=read(H/'source-preservation.json'); checks=[]
def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
check(sha(H/'verification.json')==lock['protected_verification'],'build01_verification_preserved')
for n,h in lock['before'].items():check(sha(T/n)==lock['changed'].get(n,h),'layout_source:'+n)
for n in lock['changed']:
 before=(H/'layout-source-before'/n).read_text(); after=(T/n).read_text()
 for marker in [r'\clearpage',r'\begin{samepage}',r'\end{samepage}']:after=after.replace(marker,'')
 check(' '.join(before.split())==' '.join(after.split()),'only_layout_changed:'+n)
for n,h in original['evidence'].items():check(sha(R/n)==h,'evidence:'+n)
S=R/original['source']
for n,h in original['sources'].items():check(sha(S/n)==h,'baseline:'+n)
for n,h in original['pdfs'].items():check(sha(S/(n+'.pdf'))==h,'baseline_pdf:'+n)
warnings=lambda p:Counter(re.sub(r' on input line \d+','',s) for s in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',s))
documents=[]
for name in ['accounting-product-proposal','simulation-foundations']:
 out=H/('build-02-'+name); prior=H/('build-01-'+name)
 check(read(out/'run-manifest.json')['exit_code']==0,name+':build')
 check(sha(out/(name+'.pdf'))==sha(T/(name+'.pdf')),name+':saved_pdf')
 check(not warnings(out/(name+'.log'))-warnings(prior/(name+'.log')),name+':warnings')
 check(not re.search(r'undefined|multiply defined',(out/(name+'.log')).read_text(),re.I),name+':references')
 pdf=fitz.open(out/(name+'.pdf')); old=fitz.open(prior/(name+'.pdf'))
 texts=[' '.join(p.get_text().split()) for p in pdf]
 check('Version 5.52' in texts[0],name+':cover')
 check(len(pdf)==len(old),name+':page_count')
 changed=[i+1 for i in range(len(pdf)) if texts[i]!=' '.join(old[i].get_text().split())]
 if name=='simulation-foundations':check(not changed,name+':all_page_text_unchanged')
 else:
  check(set(changed)==set([15,269,270,790,791,792,793]),name+':bounded_reflow')
  check(' '.join(old[14].get_text().split()).replace('246 28 A complete','247 28 A complete')==texts[14],name+':toc_only_page_reference')
 clipped=[i+1 for i,p in enumerate(pdf) if any(min(b[0],b[1])<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1 for b in p.get_text('blocks'))]
 check(not clipped,name+':clipping')
 pages=sorted({1,*changed}); render=H/('render-02-'+name);render.mkdir(exist_ok=False)
 for n in pages:pdf[n-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(render/f'page-{n}.png')
 documents.append(dict(document=name,pages=len(pdf),sha256=sha(out/(name+'.pdf')),changed_pages=changed,rendered_pages=pages))
result=dict(passed=True,checks=checks,documents=documents,prior_verification=sha(H/'verification.json'),layout_source_lock=sha(H/'layout-source-lock.json'),independent_acceptance=False)
(H/'verification-02.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,checks=len(checks),documents=documents)))
