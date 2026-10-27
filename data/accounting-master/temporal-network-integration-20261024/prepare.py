"""Protect Version 3.63 and add a coherent temporal network argument."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-joint-measurements-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-temporal-network-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(),'successor exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='10ec02c15385fa3b656070b7549cf69a5e45669e169f00eb5d49d57c8253c715'
    edits={
      'accounting-product-proposal.tex':[('Version 3.63 (proposal candidate)','Version 3.64 (proposal candidate)')],
      'chapters/06-language.tex':[('jointly under explicit rounding and identity hypotheses.',
        'jointly under explicit rounding and identity hypotheses.\nSection~\\ref{sec:temporal-statement-network} preserves opening, movement and\nclosing times while extending the selected system across the statements.')],
      'sections/company-source-state.tex':[('\\input{sections/joint-source-measurements}',
        '\\input{sections/joint-source-measurements}\n\n\\input{sections/temporal-statement-network}')],
      'sections/joint-source-measurements.tex':[(
        'The next reconstruction\nstep must retain these shared measurement constraints while representing\nthe missing state and admissible event histories explicitly. Until that\nstep has its own source, accounting and computational support, the actual\nhistory remains unknown and no executable company opening is produced.',
        'Section~\\ref{sec:temporal-statement-network} first connects these measurements\nto dated stock-flow relations and a wider selected statement network.\nReconstruction must then retain those constraints while representing the\nmissing state and admissible event histories explicitly. Until that step\nhas its own source, accounting and computational support, the actual history\nremains unknown and no executable company opening is produced.')]
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
        out=TARGET/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((SOURCE/name).read_bytes())
    for name,text in changed.items():(TARGET/name).write_text(text)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))


if __name__=='__main__':main()
