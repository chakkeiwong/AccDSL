"""Retain the four exact issuer-linked PDFs with enforced streaming bounds."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    leads_path=ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/complete-filing-leads.json'
    leads=json.loads(leads_path.read_text());source=ROOT/leads['source_path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==leads['source_sha256']
    rows=[];log=OUT/'acquisitions.json';assert not log.exists()
    for entry in sorted(leads['entries'],key=lambda x:x['year']):
        url=entry['url'];assert url.startswith('https://www.jpmorganchase.com/content/dam/')
        p=OUT/'sources'/f'jpmorgan-{entry["year"]}-10k.pdf';assert not p.exists()
        cap=40*1024*1024
        args=['curl','--location','--fail-with-body','--max-time','45','--max-filesize',str(cap),'--silent','--show-error','--user-agent','AccDSL-financial-report-corpus/1.0 (public research; bounded retrieval)','--header','Accept: application/pdf','--dump-header',str(p)+'.headers','--output','-','--write-out','%{stderr}\nRECEIPT %{http_code} %{size_download} %{time_total}',url]
        tick=time.monotonic();started=datetime.now(timezone.utc).isoformat();capped=False;size=0
        with p.with_suffix('.curl-log').open('wb') as err,p.open('xb') as dest:
            proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err)
            try:
                while True:
                    chunk=proc.stdout.read(65536)
                    if not chunk:break
                    size+=len(chunk)
                    if size>cap:capped=True;proc.kill();break
                    dest.write(chunk)
                proc.wait(timeout=5)
            finally:
                if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        errtext=p.with_suffix('.curl-log').read_text();receipts=[x.removeprefix('RECEIPT ') for x in errtext.splitlines() if x.startswith('RECEIPT ')];receipt=receipts[-1] if receipts else ''
        raw=p.read_bytes()
        row=dict(year=entry['year'],url=url,path=str(p.relative_to(ROOT)),source_leads=str(leads_path.relative_to(ROOT)),command=args,started_at=started,wall_seconds=time.monotonic()-tick,exit_code=proc.returncode,curl_receipt=receipt,stderr=errtext,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),cap_bytes=cap,cap_fired=capped,pdf_header=raw.startswith(b'%PDF-'),execution_context='trusted public-source retrieval')
        rows.append(row);log.write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps({k:row[k] for k in ['year','exit_code','bytes','pdf_header']}),flush=True)
        assert proc.returncode==0 and receipt.startswith('200 ') and not capped and row['pdf_header']


if __name__=='__main__':main()
