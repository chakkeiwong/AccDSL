"""Fetch only immediate official pinned helpers; no imports or installation."""
import hashlib,json,subprocess,time
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2];S=U/'sources';S.mkdir(exist_ok=True)
assert not (U/'source-receipts.json').exists(), 'Do not repeat completed fetch'
items=[]
for name in ['XmlUtil.py','FunctionIxt.py','XhtmlValidate.py']:
    p=S/name;header=S/(p.stem+'.headers')
    url='https://raw.githubusercontent.com/Arelle/Arelle/01f6a4656c2c6551d2f05f31c9d74366d133ee7e/arelle/'+name
    cmd=['curl','--location','--silent','--show-error','--max-time','25','--max-filesize','12582912','--dump-header',str(header.relative_to(R)),'--output',str(p.relative_to(R)),'--write-out','%{http_code} %{size_download}',url]
    start=time.monotonic();r=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    items.append({'url':url,'command':cmd,'exit_code':r.returncode,'curl_receipt':r.stdout,'stderr':r.stderr,'wall_seconds':round(time.monotonic()-start,3),'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,'permission_context':'trusted; prior same-host sandbox DNS failure retained in fact-identity unit'})
    (U/'source-receipts.json').write_text(json.dumps(items,indent=2)+'\n')
    print(name,r.returncode,r.stdout,flush=True)
