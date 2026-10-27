"""Preserve Version 3.64 while integrating conditional history families."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-temporal-network-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-conditional-history-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='74aa41a644accb12092007454db9147b65b6ee8224cc65311824f8272e9cbfec'
    edits={
      'accounting-product-proposal.tex':[('Version 3.64 (proposal candidate)','Version 3.65 (proposal candidate)')],
      'chapters/06-language.tex':[('closing times while extending the selected system across the statements.',
        'closing times while extending the selected system across the statements.\nSection~\\ref{sec:conditional-history-families} gives a finite conditional\nhistory family with symbolic openings and explicit measurement attachment.')],
      'sections/company-source-state.tex':[('\\input{sections/temporal-statement-network}',
        '\\input{sections/temporal-statement-network}\n\n\\input{sections/conditional-history-families}')],
      'sections/temporal-statement-network.tex':[(
        'Historical reconstruction must next connect these measurements to admissible\nstates and event sequences.',
        'Section~\\ref{sec:conditional-history-families} develops a finite conditional\nconnection to authored states and event sequences. Actual historical\nreconstruction still requires the corresponding source and method admission.')]
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
