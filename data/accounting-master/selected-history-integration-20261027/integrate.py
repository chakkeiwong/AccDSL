from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from collections import Counter
import json,re,sys,subprocess,os,time
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
S=R/'docs/design/proposal/manuscript-release-v553r1-20261027'
T=R/'docs/design/proposal/manuscript-selected-history-v554-20261027'
NAMES=['accounting-product-proposal','simulation-foundations']
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
def transform(n,s):
 if n in [x+'.tex' for x in NAMES]:return once(s,'Version 5.53-R1','Version 5.54')
 if n=='sections/temporal-statement-network.tex':
  marker=r'\subsection{What the temporal network contributes to reconstruction}'
  s=once(s,marker,(H/'selected-history.tex').read_text()+marker)
 if n=='sections/company-family-language.tex':
  marker=r'\paragraph{A conditional history gives a conditional opening.}'
  s=once(s,marker,r"""The selected numerical source reading also constrains the two supplied
histories through the explicit composition in
Section~\ref{sec:selected-reading-history}. Their 180 unresolved obligations,
separate contexts and monetary scale remain attached. The conditional-opening
interface below still requires its own complete inputs and premises.

"""+marker)
 if n=='README.md':
  s=once(s,'# AccDSL 5.53-R1 source-reading candidate','# AccDSL 5.54 selected-history candidate')
  s=once(s,'This is a protected successor to 5.53.', 'This is a protected successor to 5.53-R1.')
  s=once(s,'It adds the independently selected', 'It preserves the independently selected')
  s=once(s,'This protected successor incorporates the checked initial-pairing/common-loss',
    'The protected 5.53-R1 predecessor incorporated the checked initial-pairing/common-loss')
  s=once(s,'package and relocation results are recorded under release-pursuit-20261027/',
    'package and relocation results are recorded under data/accounting-master/release-pursuit-20261027/')
  s+='\nVersion 5.54 adds the checked selected-reading/history composition and\nits 180 unresolved obligations. spec/source-opening-compatibility-v1.md\nspecifies the supported native joins and the separately added attachment API.\nCurrent source/build/package/relocation evidence is recorded under\ndata/accounting-master/selected-history-integration-20261027/. The historical\nbuild-environment.json retains the earlier toolchain observation; current\ncommands and timings are in this successor execution record. The new adapter\nand its complete requests/results remain repository dependencies, outside\nthe two included runnable components. Full executable evidence closure and\nindependent acceptance remain open.\n'
 if n=='DEPENDENCIES.md':
  s+='\n## Selected history composition in 5.54\n\nThe added reference is spec/source-opening-compatibility-v1.md. Its native\nopening/continuation/report/carry evidence is retained under\ndata/accounting-master/source-opening-compatibility-20261027/; the separate\nselected-reading attachment, requests/results and independent exact checks are\nin data/accounting-master/selected-reading-history-20261027/. Neither those\nimplementations nor issuer sources are added to the document package. The\nexisting two executable components have unchanged scope. Current build and\nrelocation manifests are in data/accounting-master/selected-history-integration-20261027/.\nThe bundled build-environment.json is the historical predecessor observation.\n'
 return s
def prepare():
 assert not T.exists() and not (H/'source-lock.json').exists()
 active=read(B/'next-plan.json')['active_execution'];assert active['current_candidate']=='5.53-R1;833 pages;not_ready'
 manifest=read(S/'package-manifest.json');sources={};pdfs={}
 assert sha(S/'package-manifest.json')=='19e99f5c2631fe72d000a9a691b186d229cad01bbd844a93e74cbf29a199b4bc'
 assert len(manifest['files'])==410
 for row in manifest['files']:
  p=S/row['path'];assert p.is_file() and not p.is_symlink()
  assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],row['path']
 for row in manifest['files']:
  p=S/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
  if p.suffix=='.pdf':pdfs[row['path']]=row['sha256'];continue
  sources[row['path']]=row['sha256'];q=T/row['path'];q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix in ['.tex','.md']:q.write_text(transform(row['path'],p.read_text()))
  else:q.write_bytes(p.read_bytes())
 q=T/'spec/source-opening-compatibility-v1.md'
 assert not q.exists();q.write_bytes((H/'source-opening-compatibility-v1.md').read_bytes())
 evidence={}
 for folder,files in [
  ('selected-reading-history-20261027',['result.md','compose.py','independent_check.py','expected.md','attempt-01/request.json','attempt-01/result.json','attempt-01/checks.json','attempt-01/controls.json','attempt-01/independent-checks.json','attempt-01/source-lock.json','attempt-01/run-manifest.json']),
  ('source-opening-compatibility-20261027',['result.md','compatibility.md','dependency-lock.json','attempt-01/checks.json','attempt-01/cases.json']),
  ('release-pursuit-20261027/opening-repair',['result.md','verification.json','package-record.json','relocation-01/result.json'])]:
  for f in files:
   path=B/folder/f;evidence[str(path.relative_to(R))]=sha(path)
 for folder,filename in [('selected-reading-history-20261027','attempt-01/source-lock.json'),('source-opening-compatibility-20261027','dependency-lock.json')]:
  for n,h in read(B/folder/filename).items():
   assert sha(R/n)==h,n
   assert n not in evidence or evidence[n]==h,n
   evidence[n]=h
 checks=read(B/'selected-reading-history-20261027/attempt-01/checks.json')
 assert checks['passed'] and checks['target_obligations']==180
 links={}
 for label,name in [('AccDSL-latest','accounting-product-proposal'),('AccDSL-simulation-foundations','simulation-foundations')]:
  for ext in ['.pdf','.tex']:
   path=R/'docs'/(label+ext);assert path.is_symlink() and path.resolve()==S/(name+ext)
   links[str(path.relative_to(R))]=os.readlink(path)
 dump(H/'source-lock.json',dict(source=str(S.relative_to(R)),target=str(T.relative_to(R)),sources=sources,pdfs=pdfs,package_manifest=sha(S/'package-manifest.json'),evidence=evidence,inputs={n:sha(H/n) for n in ['selected-history.tex','source-opening-compatibility-v1.md','integrate.py']},stable_links=links,plan='docs/plans/accounting-selected-history-integration-20261027.md'))
 print(json.dumps(dict(prepared=True,protected_package_files=len(manifest['files']),copied_sources=len(sources),added_reference=1,evidence=len(evidence))))
def build():
 name=sys.argv[2];attempt=sys.argv[3];assert name in NAMES;out=H/('build-'+attempt+'-'+name);out.mkdir(exist_ok=False)
 env=dict(os.environ,TEXMFVAR=str(T/('.tex-cache-'+name)),TEXMFCACHE=str(T/('.tex-cache-'+name)),CUDA_VISIBLE_DEVICES='-1')
 Path(env['TEXMFVAR']).mkdir(exist_ok=True)
 cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'];start=time.monotonic()
 with (out/'stdout.log').open('w') as f:p=subprocess.run(cmd,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 for ext in ['.pdf','.log']:
  q=T/(name+ext)
  if q.exists():(out/q.name).write_bytes(q.read_bytes())
 dump(out/'manifest.json',dict(command=cmd,cwd=str(T),exit_code=p.returncode,wall_seconds=time.monotonic()-start,environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},git_commit='unavailable',random_seeds='N/A document build',plan='docs/plans/accounting-selected-history-integration-20261027.md',source_lock=sha(H/'source-lock.json'),timestamp_utc=datetime.now(timezone.utc).isoformat()))
 print(json.dumps(dict(document=name,exit_code=p.returncode,seconds=time.monotonic()-start)),flush=True);raise SystemExit(p.returncode)
def verify():
 import fitz
 assert not (H/'verification.json').exists();lock=read(H/'source-lock.json');checks=[];documents=[]
 def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
 for n,h in lock['sources'].items():
  check(sha(S/n)==h,'baseline:'+n)
  if (S/n).suffix in ['.tex','.md']:check((T/n).read_text()==transform(n,(S/n).read_text()),'exact_transform:'+n)
  else:check(sha(T/n)==h,'copied_bytes:'+n)
  if n.endswith('.tex'):
   a,b=(S/n).read_text(),(T/n).read_text();pat=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}'
   check(Counter(m.group(0) for m in re.finditer(pat,a,re.S))<=Counter(m.group(0) for m in re.finditer(pat,b,re.S)),'display_preserved:'+n)
   pat=r'\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}'
   check(Counter(re.findall(pat,a))<=Counter(re.findall(pat,b)),'citations_preserved:'+n)
 for n,h in lock['pdfs'].items():check(sha(S/n)==h,'baseline_pdf:'+n)
 for n,h in lock['evidence'].items():check(sha(R/n)==h,'evidence:'+n)
 for n,h in lock['inputs'].items():check(sha(H/n)==h,'integration_input:'+n)
 check(sha(S/'package-manifest.json')==lock['package_manifest'],'baseline_package_manifest')
 check((T/'spec/source-opening-compatibility-v1.md').read_bytes()==(H/'source-opening-compatibility-v1.md').read_bytes(),'exact_added_reference')
 warning=lambda p:Counter(re.sub(r' on input line \d+','',s) for s in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',s))
 needles=['The selected reading can constrain a supplied history','Both candidates satisfy their declared constraints.','All 180 unresolved obligations remain attached','SelectedReadingHistoryAttachment/1','The selected numerical source reading also constrains']
 for name in NAMES:
  log=(T/(name+'.log')).read_text();check(not re.search(r'undefined|multiply defined',log,re.I),name+':references')
  extra=warning(T/(name+'.log'))-warning(S/(name+'.log'));check(not extra,name+':no_new_warning:'+str(dict(extra)))
  pdf=fitz.open(T/(name+'.pdf'));texts=[' '.join(p.get_text().split()) for p in pdf];check('Version 5.54' in texts[0],name+':cover')
  pages={1};anchors={}
  if name==NAMES[0]:
   for needle in needles:
    hits=[i+1 for i,t in enumerate(texts) if needle in t];check(bool(hits),'found:'+needle);anchors[needle]=hits
    for n in hits:pages.update(range(max(1,n-1),min(len(pdf),n+2)+1))
  else:
   baseline=fitz.open(S/(name+'.pdf'));check(len(pdf)==len(baseline),'companion_pages')
   check(all(texts[i]==' '.join(baseline[i].get_text().split()) for i in range(1,len(pdf))),'companion_body_unchanged')
  clipped=[i+1 for i,p in enumerate(pdf) if any(min(b[0],b[1])<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1 for b in p.get_text('blocks'))];check(not clipped,name+':clipping')
  out=H/('render-'+name);out.mkdir(exist_ok=False)
  for n in sorted(pages):pdf[n-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(out/f'page-{n}.png')
  documents.append(dict(document=name,pages=len(pdf),sha256=sha(T/(name+'.pdf')),rendered_pages=sorted(pages),anchors=anchors))
 dump(H/'verification.json',dict(passed=True,checks=checks,documents=documents,author_review='pending',independent_acceptance=False))
 print(json.dumps(dict(passed=True,checks=len(checks),documents=[{k:d[k] for k in ['document','pages','sha256','rendered_pages']} for d in documents])))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
