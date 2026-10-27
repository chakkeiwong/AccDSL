"""Preserve the complete governing design while integrating invariant source."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BS=chr(92);NL=chr(10)
SOURCE=ROOT/'docs/design/proposal/manuscript-bank-exact-profile-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-invariant-source-20261026'
BASE='5f8fad34615ee1f0800ffe97a8cc9efc8384190727e1d6cdfdeca25ace0ee419'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+NL)
def expected(name,text):
 if name=='accounting-product-proposal.tex':
  assert text.count('Version 5.1 (proposal candidate)')==1
  return text.replace('Version 5.1 (proposal candidate)','Version 5.2 (proposal candidate)')
 if name=='chapters/06-language.tex':
  old='intent beside the inputs used in a specialized calculation. Invariant\nalgorithms are still imported typed rules, and a selected native event\ncontract retains its own implementation and applicability limits.'
  new='intent beside the inputs used in a specialized calculation. The successor\nin Section~'+BS+'ref{sec:invariant-source-authoring} also writes the current finite\nstate invariants as explicit source, using the same typed evaluators. Wider\nrule algorithms remain open, and a selected native event contract retains its\nown implementation and applicability limits.'
  assert old in text;return text.replace(old,new)
 if name=='sections/common-program-authoring.tex':
  old='invariant authoring, whole-company source completeness, accounting admission,\nproduction readiness or human acceptance.'
  new='invariant authoring, whole-company source completeness, accounting admission,\nproduction readiness or human acceptance. The following successor supplies\nexplicit source for the current finite invariant family.'
  assert old in text;return text.replace(old,new)+NL+BS+'input{sections/invariant-source-authoring}'+NL
 return text
def prepare():
 assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
 assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
 assert len(sources)==212
 e=HERE.parent/'invariant-source-authoring-20261026';checks=json.loads((e/'checks.json').read_text());assert checks['passed'] and checks['predicate_truth_variant']
 evidence={str((e/n).relative_to(ROOT)):sha(e/n) for n in ['checks.json','result.md','run-manifest.json','invariant_text.py','program_text.py','verify.py']}
 for name in sources:
  p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
 (TARGET/'sections/invariant-source-authoring.tex').write_bytes((HERE/'invariant-source.tex').read_bytes())
 dump('source-preservation.json',{'sources':sources,'source_pdf_sha256':BASE,'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),
  'evidence':evidence,'added_source':'sections/invariant-source-authoring.tex','new_section_sha256':sha(HERE/'invariant-source.tex')})
 print(json.dumps({'protected_sources':len(sources),'candidate':'5.2'}))
def build():
 assert not (HERE/'build.json').exists();start=time.monotonic()
 env={'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
 command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
 with (HERE/'build.log').open('w') as log:r=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
 pdf=TARGET/'accounting-product-proposal.pdf';dump('build.json',{'command':command,'cwd':str(TARGET),'environment':env,'returncode':r.returncode,
  'wall_seconds':time.monotonic()-start,'pdf_sha256':sha(pdf) if pdf.exists() else None})
 print(json.dumps({'returncode':r.returncode}));raise SystemExit(r.returncode)
def verify():
 import fitz
 b=json.loads((HERE/'source-preservation.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 for name,h in b['sources'].items():assert sha(SOURCE/name)==h and (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),name
 for name,h in b['evidence'].items():assert sha(ROOT/name)==h,name
 assert sha(TARGET/b['added_source'])==b['new_section_sha256']
 actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
 assert actual==set(b['sources'])|{b['added_source']}
 reachable=set()
 def visit(name):
  assert name not in reachable;reachable.add(name)
  for child in re.findall(re.escape(BS)+r'(?:input|include)\{([^}]+)}',(TARGET/name).read_text()):visit(child if child.endswith('.tex') else child+'.tex')
 visit('accounting-product-proposal.tex');combined=NL.join((TARGET/n).read_text() for n in reachable)
 labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',combined));refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)\{([^}]+)}',combined))
 assert all(x==1 for x in labels.values()) and refs<=set(labels)
 def warnings(path):return Counter(x for x in path.read_text(errors='replace').splitlines() if any(s in x for s in ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or x.startswith('!'))
 old,new=warnings(SOURCE/'accounting-product-proposal.log'),warnings(TARGET/'accounting-product-proposal.log');delta=new-old
 pdf=TARGET/'accounting-product-proposal.pdf';build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0 and sha(pdf)==build['pdf_sha256']
 doc=fitz.open(pdf);assert 'Version 5.2' in doc[0].get_text();texts=[' '.join(page.get_text().split()) for page in doc]
 starts=[i for i,x in enumerate(texts) if 'Selecting a rule by its digest preserves' in x];ends=[i for i,x in enumerate(texts) if 'This is a bounded authoring language' in x];chapter=[i for i,x in enumerate(texts) if 'A company model needs to keep disclosures' in x]
 assert len(starts)==len(ends)==len(chapter)==1
 pages=sorted({1,chapter[0]+1,chapter[0]+2,*range(starts[0],ends[0]+3)})
 for num in pages:
  doc[num-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE/f'page-{num}.png');(HERE/f'page-{num}.txt').write_text(doc[num-1].get_text())
 bounds=[i+1 for i,page in enumerate(doc) if any(min(block[0],block[1])<-1 or block[2]>page.rect.width+1 or block[3]>page.rect.height+1 for block in page.get_text('blocks'))]
 v={'passed_preservation':True,'version':'5.2','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),'protected_source_files':len(b['sources']),
  'changed_sources':[n for n,h in b['sources'].items() if sha(TARGET/n)!=h],'simulation_sources_preserved':26,'new_warnings':dict(delta),'inherited_warnings':dict(old),
  'out_of_page_text_blocks':bounds,'review_pages':pages,'readiness':'not_ready'}
 dump('verification.json',v);print(json.dumps(v));assert not delta and not bounds
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
