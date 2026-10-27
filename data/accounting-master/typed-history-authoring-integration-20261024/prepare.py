"""Preserve Version 3.65 while integrating typed state and strict authoring."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-conditional-history-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-typed-history-authoring-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='ecf5fc033053bfe9a0757ceba31f29f3b7e0ee15a9b6d674c72c0ad7ba4a8cc3'
    edits={
      'accounting-product-proposal.tex':[('Version 3.65 (proposal candidate)','Version 3.66 (proposal candidate)')],
      'chapters/06-language.tex':[('history family with symbolic openings and explicit measurement attachment.',
        'history family with symbolic openings and explicit measurement attachment.\nSection~\\ref{sec:typed-economic-history} adds typed economic quantities,\nconstraints at every event and matched declarations for conditional families.')],
      'sections/company-source-state.tex':[('\\input{sections/conditional-history-families}',
        '\\input{sections/conditional-history-families}\n\n\\input{sections/typed-economic-history}')],
      'sections/conditional-history-families.tex':[(
        'These steps specify a concrete conditional connection between measurements and\nsupplied linear histories. General candidate generation, dimensional economic\nstate, nonlinear method conditions, legal-book mappings and source or treatment\nadmission still require their own evidence.',
        'These steps specify a concrete conditional connection between measurements and\nsupplied linear histories. Section~\\ref{sec:typed-economic-history} extends\nthe authored history to typed economic quantities and explicit intermediate\nconstraints. General candidate generation, broader dimensional state, nonlinear\nmethod conditions, legal-book mappings and source or treatment admission still\nrequire their own evidence.')]
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
