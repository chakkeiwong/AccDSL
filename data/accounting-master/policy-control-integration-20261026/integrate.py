"""Protected source integration; no accepted scientific evidence writer reruns."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/design/proposal/manuscript-symbolic-regions-v523-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-policy-control-v524-20261026'
PDFS={'accounting-product-proposal':'72a4d0df518e21b083769a89eb627fe8d6711fd7f63895fade97388ce947c12c','simulation-foundations':'49460236d071823d2c100a4d305344597f1666d3413445c94a932770ad326e7b'}
ADDED={'simulation/certified-policies.tex':'certified-policies.tex','simulation/conversion-scope.tex':'conversion-scope.tex'}
OLD='Binding the certified leaves to the observation map and checking decisions that must agree across indistinguishable histories remains the next step.'
NEW='Section~\\ref{sim:certified-observation-policies} binds these leaves to the supplied observation map and checks decisions that must agree across indistinguishable histories. Binding that map to actual source revisions and actor access remains a separate requirement.'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n')
def transform(n,t):
 if n in ('accounting-product-proposal.tex','simulation-foundations.tex'):
  assert t.count('Version 5.23')==1;return t.replace('Version 5.23','Version 5.24')
 if n=='simulation/17-continuous-methods.tex':return t+'\n\\input{simulation/certified-policies}\n'
 if n=='simulation/26-finite-finance.tex':return t+'\n\\input{simulation/conversion-scope}\n'
 if n=='references.bib':return t+'\n'+(HERE/'added-references.bib').read_text()
 if n=='simulation/symbolic-regions.tex':assert t.count(OLD)==1;return t.replace(OLD,NEW)
 return t

def prepare():
 assert not TARGET.exists()
 for n,h in PDFS.items():assert sha(SOURCE/(n+'.pdf'))==h
 assert (ROOT/'docs/AccDSL-latest.pdf').resolve()==SOURCE/'accounting-product-proposal.pdf'
 sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
 evidence={str(p.relative_to(ROOT)):sha(p) for folder in ('certified-observation-policy-20261026','conversion-control-scope-20261026') for p in (HERE.parent/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.png','.pyc')}
 for x in json.loads((HERE/'citation-support.json').read_text()):
  assert sha(ROOT/x['path'])==x['sha256'];evidence[x['path']]=x['sha256'];evidence[x['acquisition_record']]=sha(ROOT/x['acquisition_record'])
 for n in sources:
  p=TARGET/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(transform(n,(SOURCE/n).read_text()))
 for n,f in ADDED.items():(TARGET/n).write_bytes((HERE/f).read_bytes())
 save('source-preservation.json',{'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),'sources':sources,'evidence':evidence,'added':{n:sha(HERE/f) for n,f in ADDED.items()},'integration_inputs':{f:sha(HERE/f) for f in [*ADDED.values(),'added-references.bib','citation-support.json']},'named_edits':['accounting-product-proposal.tex','simulation-foundations.tex','simulation/17-continuous-methods.tex','simulation/26-finite-finance.tex','references.bib','simulation/symbolic-regions.tex'],'precise_sentence_edit':{'old':OLD,'new':NEW}})
 print(json.dumps({'prepared':True,'sources':len(sources),'evidence':len(evidence)}))

def build():
 attempt=sys.argv[2] if len(sys.argv)>2 else '01';assert attempt in ('01','02','03');out=HERE/('build-attempt-'+attempt);out.mkdir(exist_ok=False)
 env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'};reports=[]
 for n in PDFS:
  cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',n+'.tex'];start=time.monotonic()
  with (out/(n+'.stdout.log')).open('w') as log:r=subprocess.run(cmd,cwd=TARGET,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  for ext in ('.log','.pdf'):
   p=TARGET/(n+ext)
   if p.exists():(out/(n+ext)).write_bytes(p.read_bytes())
  reports.append({'document':n,'command':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'pdf_sha256':sha(TARGET/(n+'.pdf')) if (TARGET/(n+'.pdf')).exists() else None})
  save('build-attempt-'+attempt+'/manifest.json',{'results':reports,'environment':{k:env[k] for k in ('TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES')},'cwd':str(TARGET),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-policy-control-integration-20261026.md','seed':'N/A document build','data':'source-preservation.json','result':'result.md'})
  print(json.dumps(reports[-1]),flush=True)
  if r.returncode:raise SystemExit(r.returncode)

def warnings(p):
 return Counter(re.sub(r' on input line \d+','',x) for x in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',x))

def verify():
 import fitz
 lock=json.loads((HERE/'source-preservation.json').read_text());checks=[]
 def ck(n,v):
  checks.append({'name':n,'pass':bool(v)})
  if not v:raise AssertionError(n)
 for n,h in lock['sources'].items():
  ck('predecessor:'+n,sha(SOURCE/n)==h);ck('retained:'+n,(TARGET/n).read_text()==transform(n,(SOURCE/n).read_text()))
 for n,h in lock['evidence'].items():ck('evidence:'+n,sha(ROOT/n)==h)
 for n,h in lock['added'].items():ck('addition:'+n,sha(TARGET/n)==h)
 for n,h in lock['integration_inputs'].items():ck('input:'+n,sha(HERE/n)==h)
 bib=(TARGET/'references.bib').read_text();keys=re.findall(r'@\w+\{([^,]+),',bib)
 ck('unique-bibliography-keys',len(keys)==len(set(keys)))
 for x in json.loads((HERE/'citation-support.json').read_text()):
  ck('primary:'+x['key'],sha(ROOT/x['path'])==x['sha256'] and x['url'] in bib and x['key'] in keys)
 docs=[]
 for n in PDFS:
  log=(TARGET/(n+'.log')).read_text();ck(n+':references',not re.search(r'undefined|multiply defined',log,re.I))
  new=warnings(TARGET/(n+'.log'))-warnings(SOURCE/(n+'.log'));ck(n+':warnings',not new)
  doc=fitz.open(TARGET/(n+'.pdf'));texts=[' '.join(p.get_text().split()) for p in doc]
  ck(n+':cover','Version 5.24' in texts[0]);aux=(TARGET/(n+'.aux')).read_text()
  sections={}
  for title,end in [('A feasible action for each world is not yet a policy','These are exact calculations for the selected synthetic information structure.'),('Conversion also changes the accounting question','actual accounting correctness or complete standards coverage.')]:
   starts=[i+1 for i,t in enumerate(texts) if title in t and len(t)>1000]
   ends=[i+1 for i,t in enumerate(texts) if end in t];ck(n+':section:'+title,bool(starts) and bool(ends))
   sections[title]=[starts[-1],ends[-1]];ck(n+':ordered:'+title,starts[-1]<=ends[-1])
  clipped=[i+1 for i,p in enumerate(doc) if any(min(q[0],q[1])<-1 or q[2]>p.rect.width+1 or q[3]>p.rect.height+1 for q in p.get_text('blocks'))];ck(n+':clipping',not clipped)
  folder=HERE/('render-'+n);folder.mkdir(exist_ok=True);pages=sorted({1,*[i for a,b in sections.values() for i in range(a,b+1)]})
  for i in pages:doc[i-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(folder/f'page-{i}.png')
  (HERE/(n+'-additions.txt')).write_text('\n\n'.join(f'PAGE {i}\n'+doc[i-1].get_text() for i in pages))
  docs.append({'document':n,'pages':len(doc),'body_pages':int(re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))-1 if n=='simulation-foundations' else None,'sha256':sha(TARGET/(n+'.pdf')),'new_warnings':dict(new),'clipped':clipped,'addition_pages':sections,'rendered_pages':pages})
 save('document-checks.json',docs);save('verification.json',{'status':'PASS','count':len(checks),'checks':checks,'protected_sources':len(lock['sources']),'protected_evidence':len(lock['evidence']),'documents':docs,'readiness':'author_review_pending'})
 print(json.dumps({'status':'PASS','count':len(checks),'documents':docs}))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
