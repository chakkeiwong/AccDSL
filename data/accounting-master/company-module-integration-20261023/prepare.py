"""One-time copy of protected manuscript sources; preserves the baseline PDF."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/design/proposal/manuscript-company-language-20261023'
TARGET=ROOT/'docs/design/proposal/manuscript-company-modules-20261023'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'successor already prepared'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='8ca29eb2f2f2fbce11c2b02245e599e75493545f964782e1c450bf6690b84f6e'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),
        'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
    (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    for name in hashes:
        dest=TARGET/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((SOURCE/name).read_bytes())
    edits={
      'accounting-product-proposal.tex':[('Version 3.54 (proposal candidate)','Version 3.55 (proposal candidate)')],
      'chapters/06-language.tex':[
        ('pure typed expressions for the declared collection policy. General functions,',
         'pure typed expressions for the declared collection policy.\nSection~\\ref{sec:company-module-language} preserves their portable identities\nand specifies the additional state needed by a shared-book return method.\nThe native return extension remains design work. General functions,')],
      'chapters/07-execution.tex':[
        ('checks member-boundary recovery with exact retries.',
         'checks member-boundary recovery with exact retries.\nSection~\\ref{sec:company-module-language} separates this preservation from\ntrusted accounting replay and explains why a module must use the company\nbook\'s existing cash, tax history and inventory memory.')],
      'sections/company-family-language.tex':[
        ('portable record encoding still requires an explicit identity mapping.',
         'portable record encoding requires an explicit identity mapping;\nSection~\\ref{sec:company-module-language} supplies that mapping for these\nlegacy drafts and retains the separate verification levels.')]
    }
    for name,pairs in edits.items():
        p=TARGET/name;text=p.read_text()
        for old,new in pairs:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        p.write_text(text)
    p=TARGET/'sections/company-family-language.tex'
    p.write_text(p.read_text()+'\n\\input{sections/company-module-language}\n')
    (HERE/'confusion-map.json').write_text(json.dumps({'baseline_pages_inspected':[99,382,383],
        'findings':[{'page':382,'repair':'Replace unresolved portable-mapping claim with an exact identity and verification-level explanation.'},
                    {'page':383,'repair':'Explain shared books and native memory/tax dependencies before entering the separate group profile.'}],
        'scope':'Bounded author diagnosis, not whole-manuscript acceptance'},indent=2)+'\n')
    print(json.dumps({'baseline_sources':len(hashes),'candidate':str(TARGET.relative_to(ROOT))}))
if __name__=='__main__':main()
