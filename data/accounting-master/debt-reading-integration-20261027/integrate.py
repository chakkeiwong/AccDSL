from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from collections import Counter
import json,re,sys,subprocess,os,time
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
S=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
T=R/'docs/design/proposal/manuscript-debt-reading-v553-20261027'
NAMES=['accounting-product-proposal','simulation-foundations']
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
def transform(n,s):
 if n in [x+'.tex' for x in NAMES]:return once(s,'Version 5.52-R1','Version 5.53')
 if n=='sections/temporal-statement-network.tex':
  s=once(s,r'\subsection{The full request remains unresolved on a reported dash}',r'\subsection{The PDF-only request remains unresolved on a reported dash}')
  marker=r'\subsection{What the temporal network contributes to reconstruction}'
  s=once(s,marker,(H/'selected-reading.tex').read_text()+marker)
 if n=='sections/statement-context-relations.tex':
  s=once(s,'Two annual calculations cannot be completed under the new baseline because','Two annual calculations cannot be completed under the PDF-only baseline because')
  s=once(s,'it does not establish the missing underlying company history.','it does not establish the missing underlying company history.\nSection~\\ref{sec:debt-selected-reading} separately checks a numerical reading\nfrom the retained XBRL instance; the original PDF-only result stays unchanged.')
 if n=='sections/company-family-language.tex':
  s=once(s,'The full supported network retains 236 observations and 101 relations, but\nremains unresolved because a reported dash appears in annual debt issuance.',
   'The original PDF-only full network retains 236 observations and 101 relations,\nbut remains unresolved because a reported dash appears in annual debt issuance.\nSection~\\ref{sec:debt-selected-reading} gives the separately selected numerical\nreading and full-network result without changing this original source record.')
  s=once(s,'supported network still preserves the debt-issuance dash and its unresolved\nmeaning.',
   'supported network under the PDF-only interpretation still preserves the\ndebt-issuance dash and its unresolved meaning. The separate source reading in\nSection~\\ref{sec:debt-selected-reading} changes that selected interpretation,\nnot the cash-population identities or these preserved results.')
 if n=='README.md':
  s=once(s,'# AccDSL 5.52-R1 release-preparation candidate','# AccDSL 5.53 source-reading candidate')
  s=once(s,'This is a protected successor to 5.52.', 'This is a protected successor to 5.52-R1. It adds the independently selected\nreported-zero reading and its complete conditional source-network consequences.')
  s+='\nThis successor is verified under data/accounting-master/debt-reading-integration-20261027/.\nThe retained two executable companions are unchanged. Their checks do not\nreproduce the new source-reading/network evidence, whose exact repository paths\nand limitations are stated in the manuscript. The full evidence closure remains open.\n'
 if n=='DEPENDENCIES.md':s+='\n## Selected debt reading in 5.53\n\nThe exact repository evidence is in data/accounting-master/debt-dash-source-20261027/\nand data/accounting-master/debt-reading-network-20261027/. Original issuer PDFs,\nXBRL files and the retained standard remain separately held sources, not included\nin this package. No new redistribution clearance or full evidence-closure claim\nis made. The two included executable components retain their earlier scope.\n'
 return s
def prepare():
 assert not T.exists() and not (H/'source-lock.json').exists()
 active=read(B/'next-plan.json')['active_execution'];assert active['current_candidate']=='5.52-R1;830 pages;not_ready'
 manifest=read(S/'package-manifest.json');sources={};pdfs={}
 for row in manifest['files']:
  p=S/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
  if p.suffix=='.pdf':pdfs[row['path']]=row['sha256'];continue
  sources[row['path']]=row['sha256'];q=T/row['path'];q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix in ['.tex','.md']:q.write_text(transform(row['path'],p.read_text()))
  else:q.write_bytes(p.read_bytes())
 evidence={}
 for folder,files in [('debt-dash-source-20261027',['result.md','attempt-01/reading.json','attempt-01/verification.json','attempt-01/consequences.json','selected-binding.json']),('debt-reading-network-20261027',['result.md','attempt-01/verification.json','attempt-01/witnesses.json','attempt-01/full-result.json'])]:
  for f in files:p=B/folder/f;evidence[str(p.relative_to(R))]=sha(p)
 dump(H/'source-lock.json',dict(source=str(S.relative_to(R)),target=str(T.relative_to(R)),sources=sources,pdfs=pdfs,package_manifest=sha(S/'package-manifest.json'),evidence=evidence,inputs={n:sha(H/n) for n in ['selected-reading.tex','integrate.py']},plan='docs/plans/accounting-debt-reading-integration-20261027.md'))
 print(json.dumps(dict(prepared=True,protected_package_files=len(manifest['files']),copied_sources=len(sources),evidence=len(evidence))))
def build():
 name=sys.argv[2];attempt=sys.argv[3];assert name in NAMES;out=H/('build-'+attempt+'-'+name);out.mkdir(exist_ok=False)
 env=dict(os.environ,TEXMFVAR='/tmp/accdsl-consolidation-tex-cache',TEXMFCACHE='/tmp/accdsl-consolidation-tex-cache',CUDA_VISIBLE_DEVICES='-1')
 cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'];start=time.monotonic()
 with (out/'stdout.log').open('w') as f:p=subprocess.run(cmd,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 for ext in ['.pdf','.log']:
  q=T/(name+ext)
  if q.exists():(out/q.name).write_bytes(q.read_bytes())
 dump(out/'manifest.json',dict(command=cmd,cwd=str(T),exit_code=p.returncode,wall_seconds=time.monotonic()-start,environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},git_commit='unavailable',random_seeds='N/A document build',plan='docs/plans/accounting-debt-reading-integration-20261027.md',source_lock=sha(H/'source-lock.json'),timestamp_utc=datetime.now(timezone.utc).isoformat()))
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
 warning=lambda p:Counter(re.sub(r' on input line \d+','',s) for s in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',s))
 needles=['A second source representation supplies a reported value','occurrence f-325','network under the PDF-only','Two annual calculations cannot be completed under the PDF-only','original PDF-only full network','separately checks a numerical reading']
 for name in NAMES:
  log=(T/(name+'.log')).read_text();check(not re.search(r'undefined|multiply defined',log,re.I),name+':references')
  extra=warning(T/(name+'.log'))-warning(S/(name+'.log'));check(not extra,name+':no_new_warning:'+str(dict(extra)))
  pdf=fitz.open(T/(name+'.pdf'));texts=[' '.join(p.get_text().split()) for p in pdf];check('Version 5.53' in texts[0],name+':cover')
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
 print(json.dumps(dict(passed=True,checks=len(checks),documents=documents)))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
