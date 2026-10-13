"""Bounded legitimate source discovery; preserve every response and exact command."""
import hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
label,url=sys.argv[1:];assert label.replace('-','').isalnum();S=U/'sources';S.mkdir(exist_ok=True)
receipt=S/(label+'.receipt.json');assert not receipt.exists(),'Do not repeat recorded request'
body=S/(label+'.body');header=S/(label+'.headers')
cmd=['curl','--location','--silent','--show-error','--max-time','25','--max-filesize','12582912','--dump-header',str(header.relative_to(R)),'--output',str(body.relative_to(R)),'--write-out','%{http_code}\n%{url_effective}\n%{content_type}\n%{size_download}',url]
start=time.monotonic();r=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
a={'url':url,'command':cmd,'exit_code':r.returncode,'curl_receipt':r.stdout,'stderr':r.stderr,'wall_seconds':round(time.monotonic()-start,3),'retrieved_at':datetime.now(timezone.utc).isoformat(),'path':str(body.relative_to(R)),'sha256':hashlib.sha256(body.read_bytes()).hexdigest() if body.exists() else None,'permission_context':'trusted network request; no Arelle or other external program API work'}
receipt.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'label':label,'exit_code':r.returncode,'receipt':r.stdout,'bytes':body.stat().st_size if body.exists() else None}))
