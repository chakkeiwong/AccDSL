from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-annual-inventory-20261025'
TARGET=ROOT/'docs/design/proposal/manuscript-inventory-interfaces-20261025'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='3a0e2838a40d4447596f267de5e767daf0c56778b390a3c9162ea6277dc2e55e'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==174,len(hashes)
    baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),
        'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
    text=(SOURCE/'accounting-product-proposal.tex').read_text()
    assert text.count('Version 3.97 (proposal candidate)')==1
    (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    (TARGET/'accounting-product-proposal.tex').write_text(text.replace('Version 3.97 (proposal candidate)','Version 3.98 (proposal candidate)').replace('24 October 2026','25 October 2026'))
    name='sections/shared-return-lease-book.tex'
    (TARGET/name).write_text((SOURCE/name).read_text()+(HERE/'interfaces-addition.tex').read_text())
    print(json.dumps({'protected_sources':len(hashes),'candidate':str(TARGET.relative_to(ROOT)),'new_source_files':0}))
if __name__=='__main__':main()
