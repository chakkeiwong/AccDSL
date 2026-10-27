"""Extract known two-column source pages without block-order interleaving."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:str(p.relative_to(ROOT))
PAGES={2022:[3,11,21,38,39,40,41,42,43],2023:[3,11,21,40,41,42,43,44,45],
       2024:[3,12,23,44,45,46,47,48,49],2025:[3,11,21,39,40,41,42,43,44]}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'column-extractions.json').exists()
    started,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
    ledger=json.loads((ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json').read_text())
    (OUT/'columns').mkdir(exist_ok=True)
    receipts=[]
    for row in ledger['records']:
        y=row['period_year'];src=row['roles']['complete_issuer_10k'];pdf=ROOT/src['path']
        assert sha(pdf)==src['sha256']
        for p in PAGES[y]:
            parts=[];commands=[]
            for name,x in [('left',0),('right',306)]:
                dest=OUT/'columns'/f'{y}-p{p}-{name}.txt'
                assert not dest.exists()
                cmd=['pdftotext','-f',str(p),'-l',str(p),'-r','72','-x',str(x),'-y','0','-W','306','-H','750','-layout',rel(pdf),rel(dest)]
                run=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
                parts.append(dest.read_text().replace('\f','').strip())
                commands.append(dict(command=cmd,text=rel(dest),sha256=sha(dest),exit_code=run.returncode,stderr=run.stderr))
            dest=OUT/'columns'/f'{y}-p{p}.txt'
            assert not dest.exists()
            dest.write_text('\n\n'.join(parts)+'\n')
            receipts.append(dict(year=y,pdf_page=p,source_pdf=src['path'],source_sha256=src['sha256'],
                text=rel(dest),sha256=sha(dest),columns=commands,
                composition='left column then right column, trim outer whitespace only; printed footer excluded'))
    (OUT/'column-extractions.json').write_text(json.dumps(dict(started_at=started,receipts=receipts,
        wall_seconds=time.monotonic()-tick,cpu_gpu_status='CPU only; GPU devices intentionally hidden'),indent=2)+'\n')
    print(json.dumps(dict(pages=len(receipts),column_extractions=2*len(receipts))))


if __name__=='__main__':main()
