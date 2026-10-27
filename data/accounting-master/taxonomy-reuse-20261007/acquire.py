#!/usr/bin/env python3
"""Retain bounded public taxonomy-source requests with immutable attempt receipts."""
import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('queue', type=Path)
parser.add_argument('--attempt', required=True)
parser.add_argument('--limit', type=int, default=40)
args = parser.parse_args()
queue = json.loads(args.queue.read_text())
assert 0 < args.limit <= 40
(OUT/'sources').mkdir(exist_ok=True)
for entry in queue[:args.limit]:
    key = entry['id']+'-'+args.attempt
    receipt = OUT/'sources'/(key+'.receipt.json')
    body = OUT/'sources'/(key+'.body')
    headers = OUT/'sources'/(key+'.headers')
    if receipt.exists():
        old = json.loads(receipt.read_text())
        assert old['request']['url'] == entry['url']
        assert not body.exists() or hashlib.sha256(body.read_bytes()).hexdigest() == old['sha256']
        print(key, 'retained', old['http_status'], flush=True)
        continue
    assert not body.exists()
    command = ['curl','--location','--silent','--show-error','--connect-timeout','10','--max-time','30',
               '--max-filesize','30000000','--dump-header',str(headers),'--output',str(body),
               '--write-out','%{http_code}\n%{url_effective}\n%{content_type}',entry['url']]
    start = time.monotonic()
    r = subprocess.run(command,capture_output=True,text=True,timeout=40)
    fields = r.stdout.splitlines()
    record = {'request':entry,'command':command,'recorded_at':datetime.now(timezone.utc).isoformat(),
              'wall_seconds':time.monotonic()-start,'exit_code':r.returncode,
              'http_status':int(fields[0]) if fields and fields[0].isdigit() else 0,
              'effective_url':fields[1] if len(fields)>1 else None,
              'content_type':fields[2] if len(fields)>2 else None,'stderr':r.stderr,
              'body':str(body.relative_to(ROOT)),
              'bytes':body.stat().st_size if body.exists() else 0,
              'sha256':hashlib.sha256(body.read_bytes()).hexdigest() if body.exists() else None,
              'limits':'Current source retrieval only; no historical byte, licence or accounting-validity inference'}
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(key,r.returncode,record['http_status'],record['bytes'],flush=True)
    if r.returncode in [5,6,7]:
        raise SystemExit('Network failure retained; inspect permissions before continuing')
