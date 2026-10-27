"""Freeze and render the bounded baseline without shadowing stdlib inspect."""
from pathlib import Path
from hashlib import sha256
import json,re
import fitz
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-common-program-20261026';NL=chr(10);BS=chr(92)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def main():
 assert not (HERE/'baseline.json').exists()
 pdf=SOURCE/'accounting-product-proposal.pdf';assert sha(pdf)=='f4638b131bf005b67e798e9a5366d84c39940bacd3dac8584b9283d84b85b702'
 chapter=SOURCE/'chapters/06-language.tex';text=chapter.read_text()
 before,after=text.split(BS+'section{Types that protect meaning}',1)
 (HERE/'scope-before.tex').write_text(before)
 refs=re.findall(re.escape(BS+'ref{')+r'([^}]+)}',before)
 labels={}
 for p in SOURCE.rglob('*.tex'):
  body=p.read_text()
  for label in re.findall(re.escape(BS+'label{')+r'([^}]+)}',body):labels[label]=p
 mapped={label:{'file':str(labels[label].relative_to(SOURCE)),'sha256':sha(labels[label])} for label in refs}
 dump(HERE/'reference-map.json',mapped)
 d=fitz.open(pdf)
 for n in [98,99,100,101]:
  d[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'before-page-{n}.png')
  (HERE/f'before-page-{n}.txt').write_text(d[n-1].get_text())
 dump(HERE/'baseline.json',{'source':str(SOURCE.relative_to(ROOT)),'pdf_sha256':sha(pdf),'chapter_sha256':sha(chapter),
  'scope_sha256':sha(HERE/'scope-before.tex'),'rest_sha256':sha256(after.encode()).hexdigest(),'references':refs,
  'read_pages':[98,99,100,101],'actual_chapter':7})
 print(json.dumps({'chapter':7,'pages':[98,99,100,101],'scope_references':len(refs),'baseline_frozen':True}))
if __name__=='__main__':main()
