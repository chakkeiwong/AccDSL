"""Protected 3.17 issue-date tax derivation; preserve the 3.16 company join."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-company-eps-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-compound-tax-20261016'

def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==116
    records=[]
    for p in files:
        rel=p.relative_to(BASE);snap=OUT/'baseline-sources'/rel;snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,snap)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    for p in files:
        dest=NEXT/p.relative_to(BASE);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    main_tex=NEXT/'accounting-product-proposal.tex';main_tex.write_text(main_tex.read_text().replace('Version 3.16 (proposal candidate)','Version 3.17 (proposal candidate)'))
    chapter=NEXT/'chapters/14-financing-groups.tex';text=chapter.read_text();anchor='\\input{sections/company-eps-join}'
    assert text.count(anchor)==1
    chapter.write_text(text.replace(anchor,anchor+'\n\n\\input{sections/compound-tax-basis}'))
    shutil.copy2(OUT/'compound-tax-basis.tex',NEXT/'sections/compound-tax-basis.tex')
    print(json.dumps(dict(protected_sources=len(records),new_section=1,successor=str(NEXT.relative_to(ROOT)))))

if __name__=='__main__':main()
