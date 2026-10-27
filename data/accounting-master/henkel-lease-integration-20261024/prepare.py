"""Prepare a protected manuscript successor; never modify the predecessor."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-lease-allocation-family-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-henkel-lease-20261024'

def sha(p):return sha256(p.read_bytes()).hexdigest()

def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='f1ae12ce178d44dc391862ba85522eeb442337333399b2a92829377336590138'
    edits={'accounting-product-proposal.tex':[('Version 3.73 (proposal candidate)','Version 3.74 (proposal candidate)')],
           'chapters/06-language.tex':[('unidentified by aggregate balances and their different complete or interrupted outcomes.',
             'unidentified by aggregate balances and their different complete or interrupted outcomes.\nSection~\\ref{sec:henkel-lease-measurements} tests what actual rounded lease\ndisclosures can constrain before individual contract state is known.')]}
    changed={}
    for name,pairs in edits.items():
        value=(SOURCE/name).read_text()
        for old,new in pairs:
            assert value.count(old)==1,(name,old)
            value=value.replace(old,new)
        changed[name]=value
    name='sections/family-outcome-queries.tex'
    changed[name]=(SOURCE/name).read_text()+'\n\\input{sections/henkel-lease-measurements}\n'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==169,len(hashes)
    baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),
              'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
    (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    for name,value in changed.items():(TARGET/name).write_text(value)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed),'candidate':str(TARGET.relative_to(ROOT))}))

if __name__=='__main__':main()
