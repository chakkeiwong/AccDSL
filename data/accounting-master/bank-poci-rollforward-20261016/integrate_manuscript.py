"""Create protected Version 3.25 with POCI interest and credit revisions."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-partial-hedge-discontinuation-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-bank-poci-rollforward-20261016'


def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==124
    records=[]
    for source in files:
        rel=source.relative_to(BASE)
        for target in (OUT/'baseline-sources'/rel,NEXT/rel):
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    main=NEXT/'accounting-product-proposal.tex'
    assert main.read_text().count('Version 3.24 (proposal candidate)')==1
    main.write_text(main.read_text().replace('Version 3.24 (proposal candidate)','Version 3.25 (proposal candidate)'))
    chapter=NEXT/'sections/bank-methods.tex'
    anchor='For a non-derecognized loan modification,'
    assert chapter.read_text().count(anchor)==1
    chapter.write_text(chapter.read_text().replace(anchor, r'\input{sections/bank-poci-rollforward}'+ chr(10)*2+anchor))
    shutil.copy2(OUT/'bank-poci-rollforward.tex',NEXT/'sections/bank-poci-rollforward.tex')
    (OUT/'build-start.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),baseline_sources=len(files)),indent=2)+'\n')
    print(json.dumps(dict(version='3.25',protected_sources=len(files),new_section=1)))


if __name__=='__main__':main()
