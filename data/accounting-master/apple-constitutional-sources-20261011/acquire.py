"""One bounded acquisition writer; never overwrite a retained response."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent / 'sources'
TARGETS = [
 ('governance-index', 'html', 'https://investor.apple.com/leadership-and-governance/default.aspx'),
]

def main():
 OUT.mkdir(parents=True, exist_ok=True)
 for name, ext, url in TARGETS:
  body, headers, receipt = (OUT / (name + suffix) for suffix in ['.' + ext, '.headers', '.receipt.json'])
  if any(p.exists() for p in [body, headers, receipt]):
   print(json.dumps({'target':name,'status':'preserved_existing_skip'}), flush=True)
   continue
  start=time.monotonic()
  command=['curl','--location','--silent','--show-error','--connect-timeout','10','--max-time','35','--dump-header',str(headers),'--output',str(body),'--write-out','%{http_code} %{url_effective}',url]
  run=subprocess.run(command, capture_output=True, text=True)
  data=body.read_bytes() if body.exists() else b''
  record={'requested_url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'command':command,'curl_exit':run.returncode,'http_and_final_url':run.stdout.strip(),'stderr':run.stderr[:2000],'elapsed_seconds':time.monotonic()-start,'path':str(body),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'pdf_signature':data.startswith(b'%PDF'),'provenance':'Governance page identified in the retained 2025 proxy; the default.aspx route is a discovery hypothesis. No document link was admitted from the empty web-tool responses.'}
  receipt.write_text(json.dumps(record,indent=2)+'\n')
  print(json.dumps({k:record[k] for k in ['requested_url','curl_exit','http_and_final_url','bytes','pdf_signature']}), flush=True)

if __name__=='__main__': main()
