"""Protected successor for authoring and native return reference integration."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-company-modules-20261023'
TARGET=ROOT/'docs/design/proposal/manuscript-company-returns-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='bdb2c9ed668870b7be45c4e09c1faece284543df5522b999c1b1acd132fa6f01'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        d=TARGET/name;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes((SOURCE/name).read_bytes())
    edits={
      'accounting-product-proposal.tex':[('Version 3.55 (proposal candidate)','Version 3.56 (proposal candidate)')],
      'chapters/06-language.tex':[
        ('The native return extension remains design work. General functions,',
         'Section~\\ref{sec:company-return-reference} gives its matched authoring\nand finite shared-book execution reference. General functions,')],
      'sections/company-module-language.tex':[
        ('The design and exact legal-book trace specify the required repair,\nwhile native parser/schema/execution integration remains unfinished. Broader',
         'The design and exact legal-book trace specify the required repair.\nSection~\\ref{sec:company-return-reference} now supplies a closed component\nauthoring profile and a finite reference for return, tax, legal reports and\ncarry. A complete composed-company language and production integration remain\nunfinished. Broader')]
    }
    for name,pairs in edits.items():
        p=TARGET/name;text=p.read_text()
        for old,new in pairs:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        p.write_text(text)
    p=TARGET/'sections/company-module-language.tex';p.write_text(p.read_text()+'\n\\input{sections/company-return-reference}\n')
    print(json.dumps({'protected_sources':len(hashes),'candidate':str(TARGET.relative_to(ROOT))}))
if __name__=='__main__':main()
