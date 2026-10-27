"""Retain all eight source exhibit pages, with full-page text and renders."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:str(p.relative_to(ROOT))


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'extractions.json').exists()
    start,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
    ledger=json.loads((ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json').read_text())
    first={2022:377,2023:413,2024:427,2025:401};rows=[]
    for package in ledger['records']:
        y=package['period_year'];source=package['roles']['complete_issuer_10k']
        pdf=ROOT/source['path'];assert sha(pdf)==source['sha256']
        for exhibit,offset in [('21',0),('22.2',1)]:
            page=first[y]+offset;stem=f'{y}-ex{exhibit}';outputs=[];commands=[]
            for mode,opts in [('reading',[]),('layout',['-layout'])]:
                dest=OUT/'sources'/f'{stem}-{mode}.txt';assert not dest.exists()
                cmd=['pdftotext','-f',str(page),'-l',str(page),*opts,rel(pdf),rel(dest)]
                run=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
                commands.append(dict(command=cmd,exit_code=run.returncode,stderr=run.stderr))
                outputs.append(dict(role=mode,path=rel(dest),sha256=sha(dest)))
            dest=OUT/'rendered'/stem
            cmd=['pdftoppm','-f',str(page),'-l',str(page),'-r','110','-singlefile','-png',rel(pdf),rel(dest)]
            run=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
            commands.append(dict(command=cmd,exit_code=run.returncode,stderr=run.stderr))
            image=dest.with_name(dest.name+'.png');outputs.append(dict(role='render',path=rel(image),sha256=sha(image)))
            rows.append(dict(year=y,exhibit=exhibit,pdf_page=page,source_pdf=source['path'],source_sha256=source['sha256'],outputs=outputs,commands=commands))
    (OUT/'extractions.json').write_text(json.dumps(dict(started_at=start,receipts=rows,wall_seconds=time.monotonic()-tick,
        cpu_gpu_status='CPU only; GPU devices intentionally hidden; no models imported'),indent=2)+'\n')
    print(json.dumps(dict(pages=len(rows),outputs=sum(len(r['outputs']) for r in rows))))


if __name__=='__main__':main()
