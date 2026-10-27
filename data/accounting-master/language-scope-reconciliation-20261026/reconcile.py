"""Protected bounded rewrite of the language scope, with exact delta checks."""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10);BS=chr(92)
SOURCE=ROOT/'docs/design/proposal/manuscript-common-program-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-language-scope-20261026'
BASE='f4638b131bf005b67e798e9a5366d84c39940bacd3dac8584b9283d84b85b702'
CHAPTER='chapters/06-language.tex';DELIMITER=BS+'section{Types that protect meaning}'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
def expected(name,text):
 if name=='accounting-product-proposal.tex':
  assert text.count('Version 4.49 (proposal candidate)')==1
  return text.replace('Version 4.49 (proposal candidate)','Version 4.50 (proposal candidate)')
 if name==CHAPTER:
  before,after=text.split(DELIMITER,1);assert before==(HERE/'scope-before.tex').read_text()
  return (HERE/'scope-after.tex').read_text()+DELIMITER+after
 return text
def prepare():
 assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
 assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
 assert len(sources)==184
 refs=lambda s:set(re.findall(re.escape(BS+'ref{')+r'([^}]+)}',s))
 before=(HERE/'scope-before.tex').read_text();after=(HERE/'scope-after.tex').read_text()
 assert before!=after and refs(before)<=refs(after) and len(refs(before))==31
 assert json.loads((HERE/'identity-check.json').read_text())['passed']
 for name in sources:
  p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
 dump(HERE/'source-preservation.json',{'source':str(SOURCE.relative_to(ROOT)),'target':str(TARGET.relative_to(ROOT)),
  'sources':sources,'pdf_sha256':BASE,'scope_before_sha256':sha(HERE/'scope-before.tex'),'scope_after_sha256':sha(HERE/'scope-after.tex'),
  'evidence':{n:sha(HERE/n) for n in ['audit.md','content-map.md','identity-check.json']},'references_retained':31,'references_added':sorted(refs(after)-refs(before))})
 print(json.dumps({'source_files':len(sources),'references_retained':31,'references_added':sorted(refs(after)-refs(before))}))
def build():
 assert not (HERE/'build.json').exists()
 cache='/tmp/accdsl-common-program-20261026-tex-cache'
 env={'TEXMFVAR':cache,'TEXMFCACHE':cache,'CUDA_VISIBLE_DEVICES':'-1'}
 command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex'];start=time.monotonic()
 with (HERE/'build.log').open('w') as log:
  r=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=240)
 p=TARGET/'accounting-product-proposal.pdf'
 dump(HERE/'build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,
  'returncode':r.returncode,'pdf_sha256':sha(p) if p.exists() else None})
 print(json.dumps({'returncode':r.returncode}));raise SystemExit(r.returncode)
def verify():
 import fitz
 base=json.loads((HERE/'source-preservation.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
 for name,h in base['sources'].items():
  assert sha(SOURCE/name)==h and (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),name
 for name,h in base['evidence'].items():assert sha(HERE/name)==h,name
 assert sha(HERE/'scope-after.tex')==base['scope_after_sha256']
 actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
 assert actual==set(base['sources'])
 combined=NL.join((TARGET/n).read_text() for n in actual if n.endswith('.tex'))
 labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',combined))
 refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)'+re.escape('{')+r'([^}]+)}',combined))
 assert all(v==1 for v in labels.values()) and refs<=set(labels)
 def warnings(p):
  return Counter(x for x in p.read_text(errors='replace').splitlines() if any(s in x for s in ['Warning','Overfull','Underfull','Undefined','undefined','Missing character:','LaTeX Error']) or x.startswith('!'))
 old=warnings(SOURCE/'accounting-product-proposal.log');new=warnings(TARGET/'accounting-product-proposal.log');delta=new-old
 build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0
 pdf=TARGET/'accounting-product-proposal.pdf';assert sha(pdf)==build['pdf_sha256'];doc=fitz.open(pdf)
 assert 'Version 4.50' in doc[0].get_text()
 starts=[i for i,p in enumerate(doc) if 'A company model needs to keep disclosures' in ' '.join(p.get_text().split())]
 ends=[i for i,p in enumerate(doc) if 'The following table uses the preserved Core 0' in ' '.join(p.get_text().split())]
 assert len(starts)==len(ends)==1,(starts,ends)
 pages=sorted({1,*range(max(1,starts[0]),ends[0]+3)})
 for n in pages:
  doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'after-page-{n}.png')
  (HERE/f'after-page-{n}.txt').write_text(doc[n-1].get_text())
 result={'passed_preservation':True,'version':'4.50','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
  'protected_source_files':len(base['sources']),'changed_source_files':['accounting-product-proposal.tex',CHAPTER],
  'references_retained':31,'new_warnings':dict(delta),'inherited_warnings':dict(old),'review_pages':pages,'readiness':'not_ready'}
 dump(HERE/'verification.json',result);print(json.dumps(result));assert not delta,'new warning requires inspection'
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
