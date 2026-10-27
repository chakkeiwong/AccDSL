"""Preserve Version3.26 and add the mixed performance/billing composition."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-onerous-contract-sequence-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-mixed-contract-billing-20261016'

def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==126
    records=[]
    for p in files:
        rel=p.relative_to(BASE)
        for dest in (OUT/'baseline-sources'/rel,NEXT/rel):
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    p=NEXT/'accounting-product-proposal.tex';text=p.read_text();assert text.count('Version 3.26 (proposal candidate)')==1
    p.write_text(text.replace('Version 3.26 (proposal candidate)','Version 3.27 (proposal candidate)'))
    p=NEXT/'sections/corporate-residuals.tex';text=p.read_text()
    anchor=r'\hypertarget{unfinished-production-carries-component-specific-completion}'
    assert text.count(anchor)==1
    p.write_text(text.replace(anchor,r'\input{sections/mixed-contract-billing}'+'\n\n'+anchor))
    shutil.copy2(OUT/'mixed-contract-billing.tex',NEXT/'sections/mixed-contract-billing.tex')
    (OUT/'build-start.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),baseline_sources=len(files)),indent=2)+'\n')
    print(json.dumps(dict(version='3.27',protected_sources=len(files),new_section=1)))

if __name__=='__main__':main()
