"""Fetch only historical SEC index routes named by retained official metadata."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    plan=json.loads((OUT/'source-plan.json').read_text())
    names={x['name'] for x in plan['files']} | {'CIK0000019617.json'}
    live=OUT/'sources/CIK0000019617.json'
    if live.exists():names.update(x['name'] for x in json.loads(live.read_text())['filings']['files'])
    log=OUT/'acquisitions.json';rows=json.loads(log.read_text()) if log.exists() else []
    for name in sys.argv[1:]:
        assert name in names and name not in {x['name'] for x in rows} and len(rows)<16
        url='https://data.sec.gov/submissions/'+name;p=OUT/'sources'/name
        assert not p.exists()
        cap=5242880 if name=='CIK0000019617.json' else 2097152
        args=['curl','--location','--fail-with-body','--max-time','45','--max-filesize',str(cap),'--silent','--show-error','--user-agent','AccDSL-financial-report-corpus/1.0 (public research; bounded retrieval)','--header','Accept: application/json','--dump-header',str(p)+'.headers','--output','-','--write-out','%{stderr}\nRECEIPT %{http_code} %{size_download} %{time_total}',url]
        started,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
        capped=False;count=0
        with p.with_suffix('.curl-log').open('wb') as err, p.open('xb') as dest:
            proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err)
            try:
                while True:
                    chunk=proc.stdout.read(65536)
                    if not chunk:break
                    count+=len(chunk)
                    if count>cap:
                        capped=True;proc.kill();break
                    dest.write(chunk)
                proc.wait(timeout=5)
            finally:
                if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        errtext=p.with_suffix('.curl-log').read_text()
        receipts=[x.removeprefix('RECEIPT ') for x in errtext.splitlines() if x.startswith('RECEIPT ')]
        receipt=receipts[-1] if receipts else ''
        raw=p.read_bytes() if p.exists() else b''
        r=dict(name=name,url=url,path=str(p.relative_to(ROOT)),command=args,started_at=started,wall_seconds=time.monotonic()-tick,exit_code=proc.returncode,curl_receipt=receipt,stderr=errtext,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),execution_context='trusted public-source metadata retrieval',stream_cap_bytes=cap,cap_fired=capped)
        rows.append(r);log.write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps({k:r[k] for k in ['name','exit_code','bytes','curl_receipt']}),flush=True)
        if capped or proc.returncode or not receipt.startswith('200 '):raise SystemExit(1)
        data=json.loads(raw)
        if 'filings' in data:
            assert str(data['cik']).lstrip('0')=='19617'
            data=data['filings']['recent']
        assert len(data['accessionNumber'])==len(data['filingDate'])==len(data['reportDate'])==len(data['form'])==len(data['primaryDocument'])


if __name__=='__main__':main()
