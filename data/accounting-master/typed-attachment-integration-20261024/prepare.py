"""Preserve Version 3.67 and correct the selected strict quantity condition."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-method-family-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-typed-attachment-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='373db53b04aba73bf93bf7011c53111b336e3408a2c9dda86e713d25a0b863a1'
    edits={
      'accounting-product-proposal.tex':[('Version 3.67 (proposal candidate)','Version 3.68 (proposal candidate)')],
      'chapters/06-language.tex':[('constraints at every event and matched declarations for conditional families.',
        'constraints at every event and matched declarations for conditional families.\nSection~\\ref{sec:typed-history-observation-attachment} connects cash and\nquantity observations to the same complete economic history.')],
      'sections/typed-economic-history.tex':[
        ('\\subsection{Author the same family as text and as typed records}',
         '\\input{sections/typed-history-observation-attachment}\n\n\\subsection{Author the same family as text and as typed records}'),
        ('Standalone typed affine histories do not acquire an attachment method merely\nbecause both profiles can be authored in the same exchange.',
         'The separate typed attachment in Section~\\ref{sec:typed-history-observation-attachment}\nis not yet a profile of this five-profile exchange. Its complete typed records\ntherefore use the separate checked interface rather than that text grammar.')],
      'sections/conditional-method-families.tex':[
        (' 0\\leq n\\leq s,\\qquad np=R_{\\mathrm{cash}},\\qquad',
         ' 0<n\\leq s,\\qquad np=R_{\\mathrm{cash}},\\qquad')]
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
