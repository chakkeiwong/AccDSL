"""Retain three known official PDFs; preserve each HTTP attempt."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
SOURCES=[
 ('aasb9-2026','https://standards.aasb.gov.au/sites/default/files/2026-10/AASB9_12-14_COMPfeb25_07-26.pdf'),
 ('aasb2022-9','https://aasb.gov.au/admin/file/content105/c9/AASB2022-9_12-22.pdf'),
 ('aasb18-appendix-d','https://standards.aasb.gov.au/sites/default/files/2024-06/AASB18_06-24_AppendixD_0.pdf')]


def main():
    attempt=sys.argv[1] if len(sys.argv)>1 else 'source-attempt-01'
    assert attempt in ('source-attempt-01','source-attempt-02')
    out=HERE/attempt;out.mkdir(exist_ok=False);records=[]
    for name,url in SOURCES:
        target=out/(name+'.pdf');headers=out/(name+'.headers');began=datetime.now(timezone.utc).isoformat();start=time.monotonic()
        cmd=['curl','--fail','--location','--max-time','30','--max-filesize','20971520','--silent','--show-error','--dump-header',str(headers),'--output',str(target),'--write-out','%{http_code} %{size_download} %{url_effective}',url]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        record=dict(id=name,url=url,retrieved_start_utc=began,returncode=result.returncode,response=result.stdout,stderr=result.stderr,command=cmd,wall_seconds=time.monotonic()-start)
        if target.exists():record.update(path=str(target.relative_to(HERE)),bytes=target.stat().st_size,sha256=sha256(target.read_bytes()).hexdigest(),pdf_header=target.read_bytes()[:5].decode(errors='replace'))
        records.append(record);(out/'acquisition.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k in ('id','returncode','response','bytes','sha256')}),flush=True)


if __name__=='__main__':main()
