"""Create a protected successor explaining complete-family outcome queries."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-outcome-query-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-evidence-archive-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
 assert not TARGET.exists(),'successor already exists'
 assert sha(SOURCE/'accounting-product-proposal.pdf')=='1c8825d136ff23342b4143d89a5be76202df9d80f7208a0acb439044e1cf222b'
 edits={
 'accounting-product-proposal.tex':[('Version 3.70 (proposal candidate)','Version 3.71 (proposal candidate)')],
 'chapters/06-language.tex':[('or necessary, and how exact finite bounds retain those alternatives.','or necessary, and how exact finite bounds retain those alternatives.\nSection~\\ref{sec:simulator-evidence-archive} preserves complete definitions and\nresults across restart while separating stored evidence from verified execution.')]
 }
 # Check the exact existing wording before constructing the successor.
 pointer=edits['chapters/06-language.tex'][0]
 assert (SOURCE/'chapters/06-language.tex').read_text().count(pointer[0])==1
 changed={}
 for name,pairs in edits.items():
  value=(SOURCE/name).read_text()
  for old,new in pairs:
   assert value.count(old)==1,(name,old)
   value=value.replace(old,new)
  changed[name]=value
 name='sections/family-outcome-queries.tex'
 changed[name]=(SOURCE/name).read_text()+'\n\\input{sections/simulator-evidence-archive}\n'
 hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
 (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
 for name in hashes:
  p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
 for name,value in changed.items():(TARGET/name).write_text(value)
 print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__':main()
