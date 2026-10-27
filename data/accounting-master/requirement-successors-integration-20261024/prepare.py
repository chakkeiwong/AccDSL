"""Protect the predecessor and copy only sources for a bounded successor."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-method-requirements-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-requirement-successors-20261024'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='d012df34794bf2860acc2fc7411c4402453fed982c405d75910613c688d0a8b5'
    edits={
        'accounting-product-proposal.tex':[
            ('Version 3.59 (proposal candidate)','Version 3.60 (proposal candidate)')],
        'chapters/06-language.tex':[
            ('reusable across these profiles, with matched typed and text declarations.',
             'reusable across these profiles, with matched typed and text declarations.\n'
             'Section~\\ref{sec:requirement-successors} connects exact input binding to\n'
             'dimensional products and guarded applicability, with explicit version selection.')],
        'chapters/17-portable-reference.tex':[
            ('\\input{sections/method-requirement-language}',
             '\\input{sections/method-requirement-language}\n\n\\input{sections/requirement-successors}')],
        'sections/method-requirement-language.tex':[
            ('The next design step is to connect a declared assessment to complete method\n'
             'boundaries without allowing a partial predicate list to authorize execution.',
             'The following section extends this reference to exact record binding,\n'
             'dimensional arithmetic and guarded applicability. Complete method boundaries\n'
             'still require more than a partial predicate list before execution can proceed.')]
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
        target=TARGET/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((SOURCE/name).read_bytes())
    for name,content in changed.items():
        (TARGET/name).write_text(content)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__': main()
