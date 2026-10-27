"""Acquire exactly 13 lock-bound crate sources; one bounded sequential writer."""
import hashlib
import json
import signal
import tarfile
import time
import tomllib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PARENT = ROOT / 'data/accounting-master/easyocr-python-bidi-20261011/sources/python_bidi-0.6.11.tar.gz'
CAP = 2 * 1024 * 1024

def deadline(signum, frame):
    raise TimeoutError('45-second total acquisition limit')

def fetch(label, url):
    assert urlparse(url).hostname == 'crates.io' and url.startswith('https://crates.io/api/v1/crates/')
    target = OUT / 'sources' / label
    target.parent.mkdir(parents=True, exist_ok=True)
    receipt = target.with_name(label + '.receipt.json')
    assert not target.exists() and not receipt.exists(), 'Existing receipt: preserve and investigate; no automatic retry'
    record = {'requested_url': url, 'started_at': datetime.now(timezone.utc).isoformat(),
              'execution_context': 'trusted source acquisition', 'byte_cap': CAP,
              'socket_timeout_seconds': 25, 'total_timeout_seconds': 45,
              'status': None, 'error': None, 'final_url': None}
    body = bytearray()
    tick = time.monotonic()
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(45)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'AccDSL-source-research/1.0'})
        with urllib.request.urlopen(request, timeout=25) as response:
            record.update(status=response.status, final_url=response.url, headers=dict(response.headers.items()))
            while True:
                chunk = response.read(min(65536, CAP + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > CAP:
                    raise ValueError('2 MiB response limit exceeded')
    except Exception as error:
        record['error'] = str(error)
    finally:
        signal.alarm(0)
    if body:
        target.write_bytes(body)
    record.update(bytes=len(body), wall_seconds=time.monotonic()-tick,
                  sha256=hashlib.sha256(body).hexdigest() if body else None,
                  path=str(target.relative_to(ROOT)) if body else None)
    receipt.write_text(json.dumps(record, indent=2)+'\n')
    return record

def main():
    assert hashlib.sha256(PARENT.read_bytes()).hexdigest() == '034090c597af250d699299d7e7f1e83eb016f9e47b3b707bd89ab2bdec77bce0'
    with tarfile.open(PARENT) as tar:
        locked = tomllib.loads(tar.extractfile('python_bidi-0.6.11/Cargo.lock').read().decode())['package']
    packages = [x for x in locked if x['name'] not in {'python-bidi','pyo3','unicode-bidi'}]
    assert len(packages) == 13
    assert not (OUT/'acquisition-summary.json').exists()
    rows = []
    for package in packages:
        name, version, expected = package['name'], package['version'], package['checksum']
        stem = name+'-'+version
        row = {'name': name, 'version': version, 'lock_checksum': expected, 'status': 'pending'}
        meta = fetch(stem+'.json', f'https://crates.io/api/v1/crates/{name}/{version}')
        if meta['status'] != 200 or meta['error']:
            row['status'] = 'metadata_access_blocked'
        else:
            data = json.loads((ROOT/meta['path']).read_text())['version']
            if data['crate'] != name or data['num'] != version or data['checksum'] != expected:
                row['status'] = 'metadata_identity_failure'
            else:
                archive = fetch(stem+'.crate', 'https://crates.io'+data['dl_path'])
                row['status'] = 'archive_verified' if archive['status'] == 200 and not archive['error'] and archive['sha256'] == expected and archive['bytes'] == data['crate_size'] else 'archive_access_or_identity_failure'
        rows.append(row)
        (OUT/'acquisition-progress.json').write_text(json.dumps(rows, indent=2)+'\n')
        print(json.dumps(row), flush=True)
    summary = {'packages': rows, 'verified': sum(x['status']=='archive_verified' for x in rows), 'failed': sum(x['status']!='archive_verified' for x in rows)}
    (OUT/'acquisition-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'verified':summary['verified'],'failed':summary['failed']}), flush=True)

if __name__ == '__main__':
    main()
