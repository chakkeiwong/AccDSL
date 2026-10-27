"""Protect Version 3.62 and prepare only intended successor edits."""
from hashlib import sha256
from pathlib import Path
import json
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
SOURCE = ROOT/'docs/design/proposal/manuscript-typed-transitions-20261024'
TARGET = ROOT/'docs/design/proposal/manuscript-joint-measurements-20261024'
def sha(path): return sha256(path.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(), 'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf') == '5a3f9240b364acb6e34bc56b76c62f94ff9ce92e4cef924e7c7598bb63669e4f'
    edits = {
        'accounting-product-proposal.tex': [('Version 3.62 (proposal candidate)', 'Version 3.63 (proposal candidate)')],
        'chapters/06-language.tex': [('representation to all statement observations and their distinct relation roles.',
            'representation to all statement observations and their distinct relation roles.\nSection~\\ref{sec:joint-source-measurements} then tests selected balance relations\njointly under explicit rounding and identity hypotheses.')],
        'sections/company-source-state.tex': [('\\input{sections/statement-context-relations}',
            '\\input{sections/statement-context-relations}\n\n\\input{sections/joint-source-measurements}')],
        'sections/statement-context-relations.tex': [(
            'The current reference reports joint feasibility as uncomputed and actual\nhistory as unknown. It creates neither legal books nor the claims, lots,\ncontracts and behavioral assumptions required to continue the company.',
            'The displayed-statement reference retains joint feasibility as uncomputed\nand actual history as unknown. Section~\\ref{sec:joint-source-measurements}\nadds a separate conditional assessment of selected balance measurements.\nThat assessment creates neither legal books nor the claims, lots, contracts\nand behavioral assumptions required to continue the company.')]
    }
    changed = {}
    for name, pairs in edits.items():
        text = (SOURCE/name).read_text()
        for old,new in pairs:
            assert text.count(old) == 1, (name,old)
            text = text.replace(old,new)
        changed[name] = text
    hashes = {str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
              if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)), 'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        target = TARGET/name; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((SOURCE/name).read_bytes())
    for name,text in changed.items(): (TARGET/name).write_text(text)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))


if __name__ == '__main__': main()
