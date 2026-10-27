"""Preserve Version 3.66 while integrating conditional method families."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-typed-history-authoring-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-method-family-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='c05e14d11327f9921f7d065ffc5d7cae03208a1719fee5aaef65cb550237d49f'
    edits={
      'accounting-product-proposal.tex':[('Version 3.66 (proposal candidate)','Version 3.67 (proposal candidate)')],
      'chapters/06-language.tex':[('constraints at every event and matched declarations for conditional families.',
        'constraints at every event and matched declarations for conditional families.\nSection~\\ref{sec:conditional-method-families} connects unknown monetary\namounts to selected method prerequisites without choosing a single history.')],
      'sections/company-source-state.tex':[('\\input{sections/typed-economic-history}',
        '\\input{sections/typed-economic-history}\n\n\\input{sections/conditional-method-families}')]
    }
    changed={}
    for name,pairs in edits.items():
        text=(SOURCE/name).read_text()
        for old,new in pairs:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        changed[name]=text
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
            if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    for name,text in changed.items():(TARGET/name).write_text(text)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))


if __name__=='__main__':main()
