"""Retain bounded public metadata/source bytes without installing packages."""
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def main():
    label, url = sys.argv[1:3]
    assert '/' not in label and label not in {'.', '..'}
    assert urlparse(url).scheme == 'https'
    assert urlparse(url).hostname in {'pypi.org', 'files.pythonhosted.org', 'raw.githubusercontent.com', 'api.github.com'}
    target = OUT / 'sources' / label
    target.parent.mkdir(parents=True, exist_ok=True)
    receipt = target.with_name(target.name + '.receipt.json')
    assert not target.exists() and not receipt.exists(), 'Preserve existing response'
    cap = 2 * 1024 * 1024
    record = {'requested_url': url, 'started_at': datetime.now(timezone.utc).isoformat(),
              'command': ['python3', str(Path(__file__).relative_to(ROOT)), label, url],
              'byte_cap': cap, 'execution_context': 'trusted public source acquisition',
              'status': None, 'final_url': None, 'error': None}
    started = time.monotonic()
    body = bytearray()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AccDSL-source-research/1.0', 'Accept': '*/*'})
        with urllib.request.urlopen(req, timeout=25) as response:
            record.update(status=response.status, final_url=response.url, headers=dict(response.headers.items()))
            while True:
                chunk = response.read(min(65536, cap + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > cap:
                    raise ValueError('Response exceeds 2 MiB cap; incomplete body retained')
    except Exception as error:
        record['error'] = str(error)
    if body:
        target.write_bytes(body)
    record.update(wall_seconds=time.monotonic()-started, bytes=len(body),
                  sha256=hashlib.sha256(body).hexdigest() if body else None,
                  path=str(target.relative_to(ROOT)) if body else None)
    receipt.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k: record[k] for k in ['status', 'bytes', 'sha256', 'error', 'path']}))
    if record['status'] != 200 or record['error']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
