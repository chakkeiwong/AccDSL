"""Bounded public text/metadata retrieval; no model or package downloads."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    label,url=sys.argv[1:3]
    assert label.endswith(('.json','.py','.md','.txt','.in')) or label=='LICENSE'
    assert url.startswith(('https://api.github.com/','https://raw.githubusercontent.com/','https://www.jaided.ai/'))
    log=OUT/'acquisitions.json';rows=json.loads(log.read_text()) if log.exists() else []
    assert len(rows)<12 and url not in {x['url'] for x in rows}
    p=OUT/'sources'/label;assert not p.exists()
    args=['curl','--location','--fail-with-body','--max-time','45','--max-filesize','1048576','--silent','--show-error','--dump-header',str(p)+'.headers','--output',str(p),'--write-out','%{http_code} %{size_download} %{time_total}',url]
    started,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
    proc=subprocess.run(args,capture_output=True,text=True,timeout=50)
    raw=p.read_bytes() if p.exists() else b''
    r=dict(url=url,path=str(p.relative_to(ROOT)),command=args,started_at=started,wall_seconds=time.monotonic()-tick,exit_code=proc.returncode,curl_receipt=proc.stdout,stderr=proc.stderr,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),execution_context='trusted public-source retrieval')
    if len(sys.argv)>3 and proc.returncode==0:
        upstream=sys.argv[3];tree=json.loads((OUT/'sources/craft-tree.json').read_text())
        item=next(x for x in tree['tree'] if x['path']==upstream)
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        r.update(upstream_path=upstream,commit=tree['sha'],upstream_blob=item['sha'],computed_blob=blob,tree_match=blob==item['sha'])
    rows.append(r);log.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ['path','exit_code','bytes']}|{'tree_match':r.get('tree_match')}))
    assert proc.returncode==0 and proc.stdout.startswith('200 ') and r.get('tree_match',True)


if __name__=='__main__': main()
