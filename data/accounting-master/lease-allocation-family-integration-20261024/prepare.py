"""Create a protected successor explaining conditional allocations behind aggregate lease balances."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-lease-shared-book-20261024-r2'
TARGET=ROOT/'docs/design/proposal/manuscript-lease-allocation-family-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
 assert not TARGET.exists(),'successor already exists'
 assert sha(SOURCE/'accounting-product-proposal.pdf')=='7cdc006cac0ad64dfc60752a7fff3bfc62a7bd725ea32b895a66002dd099dd29'
 edits={
 'accounting-product-proposal.tex':[('Version 3.72 (proposal candidate)','Version 3.73 (proposal candidate)')],
 'chapters/06-language.tex':[('one company book with explicit account allocation and funding conditions.','one company book with explicit account allocation and funding conditions.\nSection~\\ref{sec:lease-allocation-family} preserves the allocations left\nunidentified by aggregate balances and their different complete or interrupted outcomes.')]
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
 changed[name]=(SOURCE/name).read_text()+'\n\\input{sections/lease-allocation-family}\n'
 hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
 (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
 for name in hashes:
  p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
 for name,value in changed.items():(TARGET/name).write_text(value)
 print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__':main()
