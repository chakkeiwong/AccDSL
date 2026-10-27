"""Preserve Version3.34 and add insurance retrospective measurement."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-insurance-service-finance-origins-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-insurance-retrospective-measurement-20261016'

def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==134
    records=[]
    for p in files:
        rel=p.relative_to(BASE)
        for dest in (OUT/'baseline-sources'/rel,NEXT/rel):
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    p=NEXT/'accounting-product-proposal.tex';text=p.read_text();assert text.count('Version 3.34 (proposal candidate)')==1
    p.write_text(text.replace('Version 3.34 (proposal candidate)','Version 3.35 (proposal candidate)'))
    p=NEXT/'sections/insurance-methods.tex';text=p.read_text()
    anchor=r'\section{From transition measurements to opening equity}'
    assert text.count(anchor)==1
    p.write_text(text.replace(anchor, '\n'+r'\input{sections/insurance-retrospective-measurement}'+'\n'+anchor))
    shutil.copy2(OUT/'insurance-retrospective-measurement.tex',NEXT/'sections/insurance-retrospective-measurement.tex')
    (OUT/'build-start.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),baseline_sources=len(files)),indent=2)+'\n')
    print(json.dumps(dict(version='3.35',protected_sources=len(files),new_section=1)))

if __name__=='__main__':main()
