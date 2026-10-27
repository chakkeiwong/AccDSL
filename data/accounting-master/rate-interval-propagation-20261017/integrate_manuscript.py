from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=ROOT/'docs/design/proposal/manuscript-source-protocol-reuse-refresh-20261016'
NEXT=ROOT/'docs/design/proposal/manuscript-rate-interval-propagation-20261017'


def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==138
    records=[]
    for p in files:
        rel=p.relative_to(BASE)
        for dest in (OUT/'baseline-sources'/rel,NEXT/rel):
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    p=NEXT/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.37 (proposal candidate)')==1
    p.write_text(s.replace('Version 3.37 (proposal candidate)','Version 3.38 (proposal candidate)').replace('16 October 2026','17 October 2026'))
    p=NEXT/'sections/dated-credit-schedules.tex'
    p.write_text(p.read_text()+'\n'+r'\input{sections/rate-interval-propagation}'+'\n')
    shutil.copy2(OUT/'rate-interval-propagation.tex',NEXT/'sections/rate-interval-propagation.tex')
    (OUT/'build-start.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),baseline_sources=len(files)),indent=2)+'\n')
    print(json.dumps(dict(version='3.38',protected_sources=len(files),new_sections=1)))


if __name__=='__main__':main()
