"""Preserved 5.0 successor with narrow timing-contract integration."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-simulation-foundations-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-bank-exact-profile-20261026'
SCOPE=ROOT/'docs/design/proposal/manuscript-language-scope-20261026'
BASE='6a35cd61bd087fe4b1b508a74632d0a1765325cdd76b6f6104f24b0abda7b3d1'
BS=chr(92);NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+NL)
def expected(name,text):
 if name=='accounting-product-proposal.tex':
  assert text.count('Version 5.0 (proposal candidate)')==1
  return text.replace('Version 5.0 (proposal candidate)','Version 5.1 (proposal candidate)')
 if name=='sections/exact-information-time.tex':
  old='bindings are refused. This is a checked optional conversion; adoption into a\nnative profile remains a separately specified change.'
  new='bindings are refused. This optional conversion is adopted by the explicit\nbank successor in Section~'+BS+'ref{sec:exact-bank-profile}; other profiles retain\ntheir own declared semantics.'
  assert old in text;return text.replace(old,new)
 if name=='sections/exact-native-information.tex':
  old='These eleven examples exercise the information submethod; they are not eleven\nnew complete regulatory exchanges. The original profile, packet and auditor\nremain preserved. Adopting this successor as a full native profile still needs\nexplicit version and conversion semantics.'
  new='These eleven examples exercise the information submethod; they are not eleven\nnew complete regulatory exchanges. A subsequent comparison checks ten complete\nderived regulatory exchanges and four exact replays, including five intended\ntiming refusals. Its twelve adverse controls check the remaining request and\npublication obligations. The original profile, packet and auditor remain\npreserved. The separately identified profile below specifies conversion and\nreplay without changing those originals.'
  assert old in text;return text.replace(old,new)+NL+BS+'input{sections/exact-bank-profile}'+NL
 return text
def prepare():
 assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
 manifest=json.loads((HERE.parent/'simulation-monograph-20261026/candidate-source-manifest.json').read_text())
 sources={x['relative']:x['sha256'] for x in manifest['sources']}
 assert len(sources)==211 and sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 for name,h in sources.items():assert sha(SOURCE/name)==h,name
 checks=json.loads((HERE.parent/'exact-bank-profile-adoption-20261026/checks.json').read_text())
 assert checks['passed'] and checks['retained_publications']==33 and checks['timing_cases']==30
 assert (SOURCE/'chapters/06-language.tex').read_bytes()==(SCOPE/'chapters/06-language.tex').read_bytes()
 for name in sources:
  p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
 (TARGET/'sections/exact-bank-profile.tex').write_bytes((HERE/'bank-profile.tex').read_bytes())
 evidence={}
 for folder,names in [('exact-bank-profile-adoption-20261026',['checks.json','result.md','run-manifest.json','migrate.py','successor.py','verify.py','semantic-contract.md']),('exact-bank-request-conformance-20261026',['checks.json','result.md'])]:
  for name in names:
   p=HERE.parent/folder/name;evidence[str(p.relative_to(ROOT))]=sha(p)
 dump('source-preservation.json',{'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),
  'source_pdf_sha256':BASE,'sources':sources,'evidence':evidence,'added_source':'sections/exact-bank-profile.tex',
  'protected_scope_pdf_sha256':sha(SCOPE/'accounting-product-proposal.pdf'),'new_section_sha256':sha(HERE/'bank-profile.tex')})
 print(json.dumps({'protected_sources':len(sources),'simulation_sources':sum(n.startswith('simulation/') for n in sources),'candidate':'5.1'}))
def build():
 assert not (HERE/'build.json').exists()
 env={'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
 command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex'];start=time.monotonic()
 with (HERE/'build.log').open('w') as log:
  run=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
 pdf=TARGET/'accounting-product-proposal.pdf'
 dump('build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,
  'returncode':run.returncode,'pdf_sha256':sha(pdf) if pdf.exists() else None})
 print(json.dumps({'returncode':run.returncode}));raise SystemExit(run.returncode)
def verify():
 import fitz
 base=json.loads((HERE/'source-preservation.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 changed=[]
 for name,h in base['sources'].items():
  assert sha(SOURCE/name)==h,name
  assert (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),name
  if sha(TARGET/name)!=h:changed.append(name)
 for name,h in base['evidence'].items():assert sha(ROOT/name)==h,name
 assert sha(SCOPE/'accounting-product-proposal.pdf')==base['protected_scope_pdf_sha256']
 assert sha(TARGET/'sections/exact-bank-profile.tex')==base['new_section_sha256']
 actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
 assert actual==set(base['sources'])|{base['added_source']}
 # The retained standalone root is a separate document; inspect only inputs
 # reachable from this governing root, not duplicate labels across editions.
 reachable=set()
 def visit(name):
  assert name not in reachable,'repeated_source_input:'+name
  reachable.add(name);text=(TARGET/name).read_text()
  for child in re.findall(re.escape(BS)+r'(?:input|include){([^}]+)}',text):
   visit(child if child.endswith('.tex') else child+'.tex')
 visit('accounting-product-proposal.tex')
 combined=NL.join((TARGET/n).read_text() for n in reachable)
 labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',combined));refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref){([^}]+)}',combined))
 assert all(v==1 for v in labels.values()) and refs<=set(labels),'references'
 def warnings(path):
  return Counter(x for x in path.read_text(errors='replace').splitlines() if any(s in x for s in ['Warning','Overfull','Underfull','Undefined','undefined','Missing character:','LaTeX Error']) or x.startswith('!'))
 old,new=warnings(SOURCE/'accounting-product-proposal.log'),warnings(TARGET/'accounting-product-proposal.log');delta=new-old
 build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0
 pdf=TARGET/'accounting-product-proposal.pdf';assert sha(pdf)==build['pdf_sha256'];doc=fitz.open(pdf);assert 'Version 5.1' in doc[0].get_text()
 starts=[i for i,p in enumerate(doc) if 'Replacing timestamp arithmetic is useful' in ' '.join(p.get_text().split())]
 ends=[i for i,p in enumerate(doc) if 'Writing the complete method behind an event' in ' '.join(p.get_text().split())]
 assert len(starts)==1 and len(ends)==1
 pages=sorted({1,*range(starts[0],ends[0]+3)})
 for num in pages:
  doc[num-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE/f'page-{num}.png')
  (HERE/f'page-{num}.txt').write_text(doc[num-1].get_text())
 out_of_bounds=[]
 for i,page in enumerate(doc):
  for block in page.get_text('blocks'):
   x0,y0,x1,y1=block[:4]
   if min(x0,y0)<-1 or x1>page.rect.width+1 or y1>page.rect.height+1:out_of_bounds.append(i+1)
 result={'passed_preservation':True,'version':'5.1','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
  'protected_source_files':len(base['sources']),'simulation_sources_preserved':sum(n.startswith('simulation/') for n in base['sources']),
  'changed_source_files':changed,'added_source':base['added_source'],'new_warnings':dict(delta),'inherited_warnings':dict(old),
  'out_of_page_text_blocks':out_of_bounds,'review_pages':pages,'readiness':'not_ready'}
 dump('verification.json',result);print(json.dumps(result));assert not delta and not out_of_bounds
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
