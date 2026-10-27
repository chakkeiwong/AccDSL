"""Protected documentary integration. No scientific evidence writers imported."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/design/proposal/manuscript-guarded-memory-v522-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-symbolic-regions-v523-20261026'
PDFS={'accounting-product-proposal':'c4d306db80dacaf26dbc2175585466f08a3e805249596cf010212fc019db4576','simulation-foundations':'68f9fe7d58b17e3cdb51fc6a63f8ffeda15e551a7e34c725850cf5d4d653169a'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n')
def transform(n,t):
 if n in ('accounting-product-proposal.tex','simulation-foundations.tex'):
  assert t.count('Version 5.22')==1;return t.replace('Version 5.22','Version 5.23')
 if n=='simulation/17-continuous-methods.tex':return t+'\n\\input{simulation/symbolic-regions}\n'
 if n=='simulation/guarded-memory.tex':
  for a,b in EDITS.items():
   assert t.count(a)==1,a;t=t.replace(a,b)
  return t
 return t

EDITS={
'The current evidence consequently has two parts.':'The concrete evidence at this stage has two parts.',
'Their connection is supported by the explicit mapping and local event derivation, while general symbolic certification remains a separate method problem.':'The explicit mapping and local event derivation motivate the selected symbolic certificates in Section~\\ref{sim:certified-rate-regions}; extending them to general methods remains a separate problem.',
'Their identities remain in the unresolved roster even when individual concrete jobs succeed or refuse.':'Their identities remain unresolved under this concrete checkpoint even when individual concrete jobs succeed or refuse; Section~\\ref{sim:certified-rate-regions} supplies separate certificates for the selected whole regions.',
'Source admission, symbolic region certification, efficient refinement and durable recovery require their own evidence.':'Source admission, extension beyond the selected symbolic domains, efficient refinement and durable recovery require their own evidence.'}

def prepare():
 assert not TARGET.exists()
 for n,h in PDFS.items():assert sha(SOURCE/(n+'.pdf'))==h
 assert (ROOT/'docs/AccDSL-latest.pdf').resolve()==SOURCE/'accounting-product-proposal.pdf'
 sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
 evidence={str(p.relative_to(ROOT)):sha(p) for folder in ('symbolic-method-certificate-20261026','symbolic-path-composition-20261026','exact-region-certificates-20261026') for p in (HERE.parent/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.md','.json','.gz')}
 for n in sources:
  q=TARGET/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(transform(n,(SOURCE/n).read_text()))
 (TARGET/'simulation/symbolic-regions.tex').write_bytes((HERE/'symbolic-regions.tex').read_bytes())
 save('source-preservation.json',{'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),'sources':sources,'evidence':evidence,'added':{'simulation/symbolic-regions.tex':sha(HERE/'symbolic-regions.tex')},'named_edits':['accounting-product-proposal.tex','simulation-foundations.tex','simulation/17-continuous-methods.tex','simulation/guarded-memory.tex'], 'precise_edits':EDITS})
 print(json.dumps({'prepared':True,'sources':len(sources),'evidence':len(evidence)}))

def build():
 out=HERE/'build-attempt-02';out.mkdir(exist_ok=False)
 env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'};reports=[]
 for n in PDFS:
  cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',n+'.tex'];start=time.monotonic()
  with (out/(n+'.stdout.log')).open('w') as log:r=subprocess.run(cmd,cwd=TARGET,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  for ext in ('.log','.pdf'):
   p=TARGET/(n+ext)
   if p.exists():(out/(n+ext)).write_bytes(p.read_bytes())
  reports.append({'document':n,'command':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'pdf_sha256':sha(TARGET/(n+'.pdf')) if (TARGET/(n+'.pdf')).exists() else None})
  save('build-attempt-02/manifest.json',{'results':reports,'environment':{k:env[k] for k in ('TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES')},'cwd':str(TARGET),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-symbolic-region-integration-20261026.md','seed':'N/A document build','data':'source-preservation.json'})
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
 ck('addition',sha(TARGET/'simulation/symbolic-regions.tex')==lock['added']['simulation/symbolic-regions.tex'])
 docs=[]
 for n in PDFS:
  log=(TARGET/(n+'.log')).read_text();ck(n+':references',not re.search(r'undefined|multiply defined',log,re.I))
  new=warnings(TARGET/(n+'.log'))-warnings(SOURCE/(n+'.log'));ck(n+':warnings',not new)
  doc=fitz.open(TARGET/(n+'.pdf'));text=[' '.join(p.get_text().split()) for p in doc]
  ck(n+':cover','Version 5.23' in text[0])
  starts=[i+1 for i,t in enumerate(text) if 'Proving a result for an entire rate region' in t and len(t)>1000]
  ends=[i+1 for i,t in enumerate(text) if 'crash-durable recovery require additional evidence' in t]
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
