"""Create protected Version 3.26 with contract-cost impairment and onerous obligations."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-bank-poci-rollforward-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-onerous-contract-sequence-20261016'


def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==125
    records=[]
    for source in files:
        rel=source.relative_to(BASE)
        for target in (OUT/'baseline-sources'/rel,NEXT/rel):
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    main=NEXT/'accounting-product-proposal.tex'
    assert main.read_text().count('Version 3.25 (proposal candidate)')==1
    main.write_text(main.read_text().replace('Version 3.25 (proposal candidate)','Version 3.26 (proposal candidate)'))
    chapter=NEXT/'sections/corporate-residual-transitions.tex'
    anchor='The same history discipline applies to repeated revenue modifications.'
    assert chapter.read_text().count(anchor)==1
    chapter.write_text(chapter.read_text().replace(anchor, r'\input{sections/onerous-contract-sequence}'+ chr(10)*2+anchor))
    old_term='supports a contract\nasset of 50'
    assert chapter.read_text().count(old_term)==1
    chapter.write_text(chapter.read_text().replace(old_term,'supports a contract-cost\nasset of 50'))
    shutil.copy2(OUT/'onerous-contract-sequence.tex',NEXT/'sections/onerous-contract-sequence.tex')
    (OUT/'build-start.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),baseline_sources=len(files)),indent=2)+'\n')
    print(json.dumps(dict(version='3.26',protected_sources=len(files),new_section=1)))


if __name__=='__main__':main()
