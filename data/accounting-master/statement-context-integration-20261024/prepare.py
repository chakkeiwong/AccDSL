"""Preserve Version 3.57 while preparing its full-context successor."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-company-source-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-statement-context-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='dcaab818fa6048b0a8beefd990c0f0f8f821dc70519358d9d80c8437afbfcb8d'
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    edits={
        'accounting-product-proposal.tex':[('Version 3.57 (proposal candidate)','Version 3.58 (proposal candidate)')],
        'chapters/06-language.tex':[
            ('connects explicit company method selection to source-constrained partial state.\nGeneral functions,',
             'connects explicit company method selection to source-constrained partial state.\nSection~\\ref{sec:statement-context-relations} extends the retained source\nrepresentation to all statement observations and their distinct relation roles.\nGeneral functions,')],
        'sections/company-source-state.tex':[
            ('balances and a forged executable result. General source\nbinders, admissible state reconstruction, broader accounting methods and independent acceptance\nof the governing design remain unfinished.',
             'balances and a forged executable result. The next section extends the\nsource description beyond current balance captions while preserving the\ndifference between displayed relations and latent company state. General source\nbinders, admissible state reconstruction, broader accounting methods and independent acceptance\nof the governing design remain unfinished.')]
    }
    for name,pairs in edits.items():
        p=TARGET/name;text=p.read_text()
        for old,new in pairs:assert text.count(old)==1,(name,old);text=text.replace(old,new)
        p.write_text(text)
    p=TARGET/'sections/company-source-state.tex';p.write_text(p.read_text()+'\n\\input{sections/statement-context-relations}\n')
    print(json.dumps({'protected_sources':len(hashes),'candidate':str(TARGET.relative_to(ROOT))}))
if __name__=='__main__':main()
