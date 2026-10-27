"""Prepare a protected manuscript successor; never modify the predecessor."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-henkel-lease-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-shared-book-20261024'

def sha(p):return sha256(p.read_bytes()).hexdigest()

def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='f5ead5e8933b3faf323b460de160edb875bfca9732a43e7fc21e40bc1dd7cea0'
    edits={'accounting-product-proposal.tex':[('Version 3.74 (proposal candidate)','Version 3.75 (proposal candidate)')],
           'chapters/06-language.tex':[('disclosures can constrain before individual contract state is known.',
             'disclosures can constrain before individual contract state is known.\nSection~\\ref{sec:shared-return-lease-book} then distinguishes a common caller\nfrom compatible state and follows return and lease events through one declared cash balance.')]}
    changed={}
    for name,pairs in edits.items():
        value=(SOURCE/name).read_text()
        for old,new in pairs:
            assert value.count(old)==1,(name,old)
            value=value.replace(old,new)
        changed[name]=value
    name='sections/family-outcome-queries.tex'
    changed[name]=(SOURCE/name).read_text()+'\n\\input{sections/shared-return-lease-book}\n'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==170,len(hashes)
    baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),
              'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
    (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    for name,value in changed.items():(TARGET/name).write_text(value)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed),'candidate':str(TARGET.relative_to(ROOT))}))

if __name__=='__main__':main()
