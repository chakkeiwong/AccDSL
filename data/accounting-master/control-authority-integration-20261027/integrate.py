"""Protected source integration and bounded builds; no evidence writers rerun."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json, os, re, subprocess, sys, time
H=Path(__file__).resolve().parent;R=H.parents[2]
UNITS=['dated-funding-bundle-20261026','conversion-measurement-audit-20261026',
 'contingent-conversion-authority-20261026','conversion-control-scope-20261026',
 'control-boundary-repair-20261026','control-history-contract-20261026']
MAIN_NOTE=r'''
The contingent-conversion case in Section~\ref{sim:funding-measurement-control}
connects a four-party funding sequence to these classification questions.
Its supplied economic control rule is separate from accounting control and
the date at which control is obtained. Sections~\ref{sim:conversion-authority-scope}
and~\ref{sim:control-interval-evidence} explain the missing source, measurement
and interval-history evidence before a changing group perimeter can be reported.
'''
EDITS={
 'simulation/conversion-book.tex':{
  'The new holder therefore\nhas strict majority control. Before conversion the old holder controls all\nshares.':
  'Under this supplied economic governance rule, the new holder therefore\nhas strict majority control. Before conversion the old holder controls all\nshares. The separate accounting-control assessment, including potential\nrights before legal conversion, is explained in\nSection~\\ref{sim:conversion-control-scope}.'},
 'simulation/control-price.tex':{
  'supplied fiscal opening; joining issuance, intervening measurement and final\nliquidation into one accounting history remains a further composition task.':
  'supplied fiscal opening. The following sections connect the dated funding\nexchange and identify the source, measurement and control-history conditions\nneeded before issuance, conversion and final liquidation can form one\naccounting history.'}}

def digest(p):return sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def transform(name,text,base,version):
 if name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
  assert text.count('Version '+base)==1
  text=text.replace('Version '+base,'Version '+version)
 if name in EDITS:
  for old,new in EDITS[name].items():
   assert text.count(old)==1,name
   text=text.replace(old,new)
 if name=='simulation/control-price.tex':text+='\n\\input{simulation/funding-control-authority}\n'
 if name=='chapters/14-financing-groups.tex':
  anchor='\\input{sections/apple-debt}'
  assert text.count(anchor)==1;text=text.replace(anchor,MAIN_NOTE+'\n'+anchor)
 if name=='references.bib':text+='\n'+(H/'authority.bib').read_text()
 return text

def prepare():
 assert not (H/'source-preservation.json').exists()
 a=json.loads((R/'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
 base=a['current_candidate'].split(';')[0];version='5.'+str(int(base.split('.')[1])+1)
 source=(R/a['current_pdf']).parent
 target=R/('docs/design/proposal/manuscript-control-authority-v'+version.replace('.','')+'-20261027')
 assert not target.exists()
 for key in ['current_pdf','standalone_pdf']:assert digest(R/a[key])==a[key+'_sha256']
 assert (R/'docs/AccDSL-latest.pdf').resolve()==source/'accounting-product-proposal.pdf'
 sources={str(p.relative_to(source)):digest(p) for p in source.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
 evidence={}
 for unit in UNITS:
  folder=H.parent/unit
  for p in folder.rglob('*'):
   if not p.is_file() or p.suffix not in ['.py','.md','.json','.pdf']:continue
   if any(part in ['control-before','pointer-before','inputs'] for part in p.relative_to(folder).parts):continue
   evidence[str(p.relative_to(R))]=digest(p)
 for n in sources:
  q=target/n;q.parent.mkdir(parents=True,exist_ok=True)
  q.write_text(transform(n,(source/n).read_text(),base,version))
 added=target/'simulation/funding-control-authority.tex'
 added.write_bytes((H/'funding-control-authority.tex').read_bytes())
 lock=dict(source=str(source.relative_to(R)),target=str(target.relative_to(R)),base=base,version=version,
  pdfs={k:a[k+'_sha256'] for k in ['current_pdf','standalone_pdf']},sources=sources,evidence=evidence,
  added={'simulation/funding-control-authority.tex':digest(added)},
  named_edits=['accounting-product-proposal.tex','simulation-foundations.tex','simulation/conversion-book.tex','simulation/control-price.tex','chapters/14-financing-groups.tex','references.bib'])
 save(H/'source-preservation.json',lock)
 print(json.dumps({k:lock[k] for k in ['source','target','base','version']}),flush=True)

def build(attempt):
 lock=json.loads((H/'source-preservation.json').read_text());target=R/lock['target']
 out=H/attempt;out.mkdir(exist_ok=False)
 env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
 reports=[]
 for name in ['accounting-product-proposal','simulation-foundations']:
  cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',name+'.tex'];start=time.monotonic()
  with (out/(name+'.stdout.log')).open('w') as log:run=subprocess.run(cmd,cwd=target,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  for ext in ['.pdf','.log']:
   p=target/(name+ext)
   if p.exists():(out/(name+ext)).write_bytes(p.read_bytes())
  row=dict(document=name,command=cmd,returncode=run.returncode,wall_seconds=time.monotonic()-start,
   pdf_sha256=digest(target/(name+'.pdf')) if (target/(name+'.pdf')).exists() else None)
  reports.append(row);save(out/'manifest.json',dict(results=reports,cwd=str(target),
   environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
   plan='docs/plans/accounting-control-authority-integration-20261026.md',data_version='source-preservation.json',random_seeds='N/A: document build'))
  print(json.dumps(row),flush=True)
  if run.returncode:raise SystemExit(run.returncode)

def warnings(p):
 return Counter(re.sub(r' on input line \d+','',s) for s in p.read_text(errors='replace').splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined|Missing character:',s))

def verify():
 import fitz
 assert not (H/'verification.json').exists()
 lock=json.loads((H/'source-preservation.json').read_text());source=R/lock['source'];target=R/lock['target'];checks=[]
 def ck(name,condition):
  checks.append(dict(name=name,passed=bool(condition)))
  if not condition:save(H/'verification-failed.json',dict(checks=checks));raise AssertionError(name)
 for n,x in lock['sources'].items():
  ck('baseline:'+n,digest(source/n)==x)
  ck('candidate:'+n,(target/n).read_text()==transform(n,(source/n).read_text(),lock['base'],lock['version']))
 for n,x in lock['evidence'].items():ck('evidence:'+n,digest(R/n)==x)
 for n,x in lock['added'].items():ck('addition:'+n,digest(target/n)==x)
 bibkeys=set(re.findall(r'@\w+\{([^,]+),',(target/'references.bib').read_text()))
 docs=[]
 for name in ['accounting-product-proposal','simulation-foundations']:
  log=(target/(name+'.log')).read_text();ck(name+'/references',not re.search(r'undefined|multiply defined',log,re.I))
  new=warnings(target/(name+'.log'))-warnings(source/(name+'.log'));ck(name+'/new-warnings',not new)
  reachable=set()
  def visit(n):
   ck(name+'/unique/'+n,n not in reachable);reachable.add(n)
   for child in re.findall(r'\\(?:input|include)\{([^}]+)\}',(target/n).read_text()):visit(child if child.endswith('.tex') else child+'.tex')
  visit(name+'.tex');body='\n'.join((target/n).read_text() for n in reachable)
  labels=Counter(re.findall(r'\\label\{([^}]+)\}',body));refs=set(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}',body))
  ck(name+'/labels',all(x==1 for x in labels.values()) and refs<=set(labels))
  cites={key.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])*\{([^}]+)\}',body) for key in group.split(',')}
  ck(name+'/bibliography',cites<=bibkeys)
  doc=fitz.open(target/(name+'.pdf'));text=[' '.join(p.get_text().split()) for p in doc]
  ck(name+'/version','Version '+lock['version'] in text[0])
  starts=[i+1 for i,t in enumerate(text) if 'Funding the project does not yet determine its accounts' in t and len(t)>1500]
  ends=[i+1 for i,t in enumerate(text) if 'can supply the missing accounting evidence' in t]
  ck(name+'/added-span',bool(starts) and bool(ends));a=starts[-1];b=ends[-1];ck(name+'/span-order',a<=b)
  clipped=[i+1 for i,p in enumerate(doc) if any(min(x[0],x[1])<-1 or x[2]>p.rect.width+1 or x[3]>p.rect.height+1 for x in p.get_text('blocks'))]
  ck(name+'/clipping',not clipped)
  folder=H/('render-'+name);folder.mkdir(exist_ok=True);pages=sorted({1,*range(a-1,min(len(doc),b+1)+1)})
  for i in pages:doc[i-1].get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save(folder/('page-'+str(i)+'.png'))
  (H/(name+'-addition.txt')).write_text('\n\n'.join('PAGE '+str(i)+'\n'+doc[i-1].get_text() for i in range(a,b+1)))
  aux=(target/(name+'.aux')).read_text();m=re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',aux)
  docs.append(dict(document=name,pages=len(doc),body_pages=int(m.group(1))-1 if name=='simulation-foundations' and m else None,
   sha256=digest(target/(name+'.pdf')),new_warnings=dict(new),clipping=clipped,addition_pages=[a,b],rendered_pages=pages))
 save(H/'document-checks.json',docs);save(H/'verification.json',dict(status='PASS',assertions=len(checks),checks=checks,documents=docs,protected_sources=len(lock['sources']),protected_evidence=len(lock['evidence']),readiness='author_review_pending'))
 print(json.dumps(dict(status='PASS',assertions=len(checks),documents=docs)))

if __name__=='__main__':
 if sys.argv[1]=='build':build(sys.argv[2])
 else:{'prepare':prepare,'verify':verify}[sys.argv[1]]()
