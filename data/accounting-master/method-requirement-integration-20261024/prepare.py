"""Copy protected sources after checking all intended textual anchors."""
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-statement-context-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-method-requirements-20261024'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='51d95618e2b5cc57ac896bcad72719f7416e605d509e66b5fb1abee839b2a10b'
    edits={
        'accounting-product-proposal.tex':[
            ('Version 3.58 (proposal candidate)','Version 3.59 (proposal candidate)')],
        'chapters/06-language.tex':[
            ('representation to all statement observations and their distinct relation roles.\nGeneral functions,',
             'representation to all statement observations and their distinct relation roles.\n'
             'Section~\\ref{sec:method-requirement-language} makes selected method prerequisites\n'
             'reusable across these profiles, with matched typed and text declarations.\n'
             'General functions,')],
        'chapters/17-portable-reference.tex':[
            ('by the manuscript\'s dependency index.\n\n\\input{sections/ordered-eps-records}',
             'by the manuscript\'s dependency index.\n\n'
             '\\input{sections/method-requirement-language}\n\n'
             '\\input{sections/ordered-eps-records}')]
    }
    changed={}
    for name,pairs in edits.items():
        text=(SOURCE/name).read_text()
        for old,new in pairs:
            assert text.count(old)==1,(name,old)
            text=text.replace(old,new)
        changed[name]=text
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
            if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes((SOURCE/name).read_bytes())
    for name,text in changed.items():
        (TARGET/name).write_text(text)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed),
                      'candidate':str(TARGET.relative_to(ROOT))}))


if __name__=='__main__':
    main()
