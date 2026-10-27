"""Protected successor for composed company and source-state design."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-company-returns-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-company-source-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='ee3f57c33b3471a09bda363a351e095c52a90acb8b1d5402aa19b11fd159c5df'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    edits={
        'accounting-product-proposal.tex':[('Version 3.56 (proposal candidate)','Version 3.57 (proposal candidate)')],
        'chapters/06-language.tex':[
            ('and finite shared-book execution reference. General functions,',
             'and finite shared-book execution reference. Section~\\ref{sec:company-source-state}\nconnects explicit company method selection to source-constrained partial state.\nGeneral functions,')],
        'sections/company-module-language.tex':[
            ('carry. A complete composed-company language and production integration remain\nunfinished. Broader',
             'carry. Section~\\ref{sec:company-source-state} adds a finite composed-company\ndeclaration and a separate partial-state description for actual disclosures.\nGeneral composition and production integration remain unfinished. Broader')],
        'sections/company-return-reference.tex':[
            ('It also preserves the existing six company-authoring paths. The remaining\nlanguage task is a composed-company declaration that makes each selected\nmethod, state allocation and unresolved dependency explicit. General changes',
             'It also preserves the existing six company-authoring paths. The next\nsection exposes the selected methods, source state and schedule in a finite\ncomposed-company declaration, then distinguishes the partial inputs available\nfrom actual disclosures. General changes')]
    }
    for name,pairs in edits.items():
        p=TARGET/name;text=p.read_text()
        for old,new in pairs:assert text.count(old)==1,(name,old);text=text.replace(old,new)
        p.write_text(text)
    p=TARGET/'sections/company-return-reference.tex';p.write_text(p.read_text()+'\n\\input{sections/company-source-state}\n')
    print(json.dumps({'protected_sources':len(hashes),'candidate':str(TARGET.relative_to(ROOT))}))
if __name__=='__main__':main()
