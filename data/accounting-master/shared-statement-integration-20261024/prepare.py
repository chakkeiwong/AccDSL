"""Prepare a protected manuscript successor; never modify the predecessor."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-shared-book-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-shared-statements-20261024'

def sha(p):return sha256(p.read_bytes()).hexdigest()

def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='83072e8eef516bbb62c9c9743367053ef4177bd75a22807e4fb31aa30548cca1'
    edits={'accounting-product-proposal.tex':[('Version 3.75 (proposal candidate)','Version 3.76 (proposal candidate)')],
           'chapters/06-language.tex':[('from compatible state and follows return and lease events through one declared cash balance.',
             'from compatible state and follows return and lease events through one declared cash balance.\nSection~\\ref{sec:recorded-shared-statements} reconciles the resulting recorded statements\nwhile preserving unresolved tax assessment and incomplete fiscal coverage.')]}
    changed={}
    for name,pairs in edits.items():
        value=(SOURCE/name).read_text()
        for old,new in pairs:
            assert value.count(old)==1,(name,old)
            value=value.replace(old,new)
        changed[name]=value
    name='sections/family-outcome-queries.tex'
    changed[name]=(SOURCE/name).read_text()+'\n\\input{sections/recorded-shared-statements}\n'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==171,len(hashes)
    baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),
              'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
    (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    for name,value in changed.items():(TARGET/name).write_text(value)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed),'candidate':str(TARGET.relative_to(ROOT))}))

if __name__=='__main__':main()
