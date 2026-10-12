"""Bound public-source retrieval; preserve bytes even for failed source responses."""
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

OUT=Path(__file__).resolve().parent
key,url=sys.argv[1:]
assert key.replace('-','').isalnum()
receipt=OUT/f'sources/{key}-receipt.json'
assert not receipt.exists(), 'Do not silently repeat a source attempt'
body=OUT/f'sources/{key}.body';headers=OUT/f'sources/{key}.headers'
assert not body.exists() and not headers.exists()
cmd=['curl','--silent','--show-error','--location','--connect-timeout','10','--max-time','25',
    '--dump-header',str(headers),'--output',str(body),'--write-out','%{json}',url]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.monotonic()
p=subprocess.run(cmd,capture_output=True,text=True)
try:metrics=json.loads(p.stdout)
except json.JSONDecodeError:metrics={'unparsed_stdout':p.stdout}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
r={'url':url,'command':cmd,'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'wall_seconds':time.monotonic()-clock,'exit_code':p.returncode,'stderr':p.stderr,
    'http_code':metrics.get('http_code'),'url_effective':metrics.get('url_effective'),
    'size_download':metrics.get('size_download'),'content_type':metrics.get('content_type'),
    'body':body.name,'body_sha256':sha(body),'headers':headers.name,'headers_sha256':sha(headers),
    'interpretation':'Pending content inspection; HTTP success is not authority acceptance.'}
receipt.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['url','exit_code','http_code','url_effective','size_download','content_type','stderr']}))
raise SystemExit(p.returncode)
