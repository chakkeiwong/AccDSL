"""Bounded official-source acquisition; each attempt is append-only."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent

def main():
    mode,attempt=sys.argv[1:]
    out=HERE/attempt;out.mkdir(exist_ok=False)
    if mode=='pages':
        sources=[('aasb10-page','https://standards.aasb.gov.au/aasb-10-nov-2024-0'),
                 ('aasb127-page','https://standards.aasb.gov.au/aasb-127-dec-2021'),
                 ('aasb3-page','https://standards.aasb.gov.au/aasb-3-dec-2022')]
        suffix='.html'
    elif mode=='pdfs':
        sources=json.loads((HERE/'pdf-urls.json').read_text())
        suffix='.pdf'
    else:raise ValueError(mode)
    records=[]
    for sid,url in sources:
        dest=out/(sid+suffix);headers=out/(sid+'.headers')
        cmd=['curl','--fail','--location','--max-time','30','--max-filesize','20971520',
             '--silent','--show-error','--dump-header',str(headers),'--output',str(dest),
             '--write-out','%{http_code} %{size_download} %{url_effective}',url]
        started=datetime.now(timezone.utc).isoformat();t=time.monotonic()
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        row=dict(id=sid,url=url,retrieved_start_utc=started,returncode=r.returncode,
                 response=r.stdout,stderr=r.stderr,command=cmd,wall_seconds=time.monotonic()-t)
        if dest.exists():row.update(path=str(dest.relative_to(HERE)),bytes=dest.stat().st_size,sha256=sha256(dest.read_bytes()).hexdigest())
        records.append(row);(out/'acquisition.json').write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({k:v for k,v in row.items() if k not in ['command','stderr']}),flush=True)

if __name__=='__main__':main()
