"""Protected documentary integration. No scientific evidence writers imported."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/design/proposal/manuscript-continuous-guards-v520-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-two-date-memory-v521-20261026'
PDFS={'accounting-product-proposal':'fc3ec2c79b7b2709aa45b6d7b4184b43d7e918abf4865318a93e117b6e00f50f','simulation-foundations':'eea657ed62d6339e4cd1b3f74df426d9571d28b5ce213ddbf15a48e77d81fdfd'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n')
def transform(n,t):
 if n in ('accounting-product-proposal.tex','simulation-foundations.tex'):
  assert t.count('Version 5.20')==1;return t.replace('Version 5.20','Version 5.21')
 if n=='simulation/17-continuous-methods.tex':return t+'\n\\input{simulation/two-date-memory}\n'
 return t

def prepare():
 assert not TARGET.exists()
 for n,h in PDFS.items():assert sha(SOURCE/(n+'.pdf'))==h
 assert (ROOT/'docs/AccDSL-latest.pdf').resolve()==SOURCE/'accounting-product-proposal.pdf'
 sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
 evidence={str(p.relative_to(ROOT)):sha(p) for p in (HERE.parent/'two-date-continuous-memory-20261026').rglob('*') if p.is_file() and p.suffix in ('.py','.md','.json')}
 for n in sources:
  q=TARGET/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(transform(n,(SOURCE/n).read_text()))
 (TARGET/'simulation/two-date-memory.tex').write_bytes((HERE/'two-date-memory.tex').read_bytes())
 save('source-preservation.json',{'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),'sources':sources,'evidence':evidence,'added':{'simulation/two-date-memory.tex':sha(HERE/'two-date-memory.tex')},'named_edits':['accounting-product-proposal.tex','simulation-foundations.tex','simulation/17-continuous-methods.tex']})
 print(json.dumps({'prepared':True,'sources':len(sources),'evidence':len(evidence)}))

def build():
 out=HERE/'build-attempt-01';out.mkdir(exist_ok=False)
 env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'};reports=[]
 for n in PDFS:
  cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',n+'.tex'];start=time.monotonic()
  with (out/(n+'.stdout.log')).open('w') as log:r=subprocess.run(cmd,cwd=TARGET,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  for ext in ('.log','.pdf'):
   p=TARGET/(n+ext)
   if p.exists():(out/(n+ext)).write_bytes(p.read_bytes())
  reports.append({'document':n,'command':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'pdf_sha256':sha(TARGET/(n+'.pdf')) if (TARGET/(n+'.pdf')).exists() else None})
  save('build-attempt-01/manifest.json',{'results':reports,'environment':{k:env[k] for k in ('TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES')},'cwd':str(TARGET),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-two-date-memory-integration-20261026.md','seed':'N/A document build','data':'source-preservation.json'})
  print(json.dumps(reports[-1]),flush=True)
  if r.returncode:raise SystemExit(r.returncode)

def warnings(p):
 lines=p.read_text().splitlines()
 return Counter(re.sub(r' on input line \d+','',x) for x in lines if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',x))

def verify():
 import fitz
 lock=json.loads((HERE/'source-preservation.json').read_text());checks=[]
 def ck(n,v):
  checks.append({'name':n,'pass':bool(v)})
  if not v:raise AssertionError(n)
 for n,h in lock['sources'].items():
  ck('predecessor:'+n,sha(SOURCE/n)==h);ck('retained:'+n,(TARGET/n).read_text()==transform(n,(SOURCE/n).read_text()))
 for n,h in lock['evidence'].items():ck('evidence:'+n,sha(ROOT/n)==h)
 ck('addition',sha(TARGET/'simulation/two-date-memory.tex')==lock['added']['simulation/two-date-memory.tex'])
 docs=[]
 for n in PDFS:
  log=(TARGET/(n+'.log')).read_text();ck(n+':references',not re.search(r'undefined|multiply defined',log,re.I))
  new=warnings(TARGET/(n+'.log'))-warnings(SOURCE/(n+'.log'));ck(n+':warnings',not new)
  doc=fitz.open(TARGET/(n+'.pdf'));text=[' '.join(p.get_text().split()) for p in doc]
  ck(n+':cover','Version 5.21' in text[0])
  starts=[i+1 for i,t in enumerate(text) if 'Repayment changes tomorrow' in t and len(t)>1000]
  ends=[i+1 for i,t in enumerate(text) if 'Renewing the facility' in t]
  ck(n+':addition-present',bool(starts) and bool(ends))
  a=starts[-1];b=ends[-1];ck(n+':ordered',a<=b)
  clipped=[i+1 for i,p in enumerate(doc) if any(min(q[0],q[1])<-1 or q[2]>p.rect.width+1 or q[3]>p.rect.height+1 for q in p.get_text('blocks'))]
  ck(n+':clipping',not clipped)
  folder=HERE/('render-'+n);folder.mkdir(exist_ok=True)
  pages=sorted({1,*range(a-1,b+2)})
  for page in pages:doc[page-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(folder/f'page-{page}.png')
  (HERE/(n+'-addition.txt')).write_text('\n\n'.join(f'PAGE {i}\n'+doc[i-1].get_text() for i in range(a-1,b+2)))
  docs.append({'document':n,'pages':len(doc),'body_pages':int(re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',(TARGET/(n+'.aux')).read_text()).group(1))-1 if n=='simulation-foundations' else None,'sha256':sha(TARGET/(n+'.pdf')),'new_warnings':dict(new),'clipped':clipped,'addition_pages':[a,b],'rendered_pages':pages})
 save('document-checks.json',docs);save('verification.json',{'status':'PASS','count':len(checks),'checks':checks,'protected_sources':len(lock['sources']),'protected_evidence':len(lock['evidence']),'documents':docs,'readiness':'author_review_pending'})
 print(json.dumps({'status':'PASS','count':len(checks),'documents':docs}))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
