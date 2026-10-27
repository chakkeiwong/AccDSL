"""Protect Version 3.61 and create only the intended Version 3.62 edits."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-collection-state-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-typed-transitions-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='2b357a213e573d7cdfdcfcc1055afafb9cedfb10df7ec2d5e2b0628658aa97ed'
    edits={
        'accounting-product-proposal.tex':[('Version 3.61 (proposal candidate)','Version 3.62 (proposal candidate)')],
        'chapters/06-language.tex':[('identity order, signed totals and state-domain findings before monetary effects.',
            'identity order, signed totals and state-domain findings before monetary effects.\nSection~\\ref{sec:typed-return-transitions} carries the same example through\ntyped calculations, atomic state updates and exact source-bound replay.')],
        'chapters/17-portable-reference.tex':[('\\input{sections/collection-state-requirements}',
            '\\input{sections/collection-state-requirements}\n\n\\input{sections/typed-return-transitions}')],
        'sections/collection-state-requirements.tex':[(
            'A complete\nmethod must still validate its full raw state, define typed monetary effects,\napply them atomically, recompute proposed changes and satisfy reporting and\ncarry conditions. That next work connects the checked prerequisites to financial\ntransitions without treating a partial pass as permission to execute.',
            'The next section connects these prerequisites to a selected return transition:\ncomplete raw-state structure, exact monetary effects, atomic memory updates and\nfull proposal recomputation. Reporting and annual carry retain their own method\nconditions, and source correspondence remains distinct from authority.')]
    }
    changed={}
    for name,pairs in edits.items():
        content=(SOURCE/name).read_text()
        for old,new in pairs:
            assert content.count(old)==1,(name,old)
            content=content.replace(old,new)
        changed[name]=content
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
            if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        target=TARGET/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((SOURCE/name).read_bytes())
    for name,content in changed.items():(TARGET/name).write_text(content)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__':main()
