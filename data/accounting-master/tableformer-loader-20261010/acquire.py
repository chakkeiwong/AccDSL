"""Retain bounded, tree-verified source text; never import upstream code."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
PIN = 'd1569fdffee1d09cb3111d6d5490991cb59d59fd'
TREE = json.loads((OUT / 'sources/tree.json').read_text())
assert TREE['sha'] == PIN and not TREE['truncated']
FILES = {x['path']: x for x in TREE['tree'] if x['type'] == 'blob'}
LOG = OUT / 'acquisitions.json'


def main():
    records = json.loads(LOG.read_text()) if LOG.exists() else []
    for upstream in sys.argv[1:]:
        assert upstream in FILES and (upstream.endswith(('.py','.toml','.md')) or upstream == 'LICENSE')
        assert FILES[upstream].get('size', 0) <= 1048576
        assert upstream not in {r['upstream_path'] for r in records}
        assert len(records) + 3 < 16  # PyPI, tag and tree metadata precede source acquisition
        target = OUT / 'sources' / upstream.replace('/', '__')
        assert not target.exists()
        url = f'https://raw.githubusercontent.com/docling-project/docling-ibm-models/{PIN}/{upstream}'
        start, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
        args = ['curl', '--location', '--fail-with-body', '--max-time', '45',
                '--max-filesize', '1048576', '--silent', '--show-error',
                '--dump-header', str(target) + '.headers', '--output', str(target),
                '--write-out', '%{http_code} %{size_download} %{time_total}', url]
        proc = subprocess.run(args, text=True, capture_output=True, timeout=50)
        raw = target.read_bytes() if target.exists() else b''
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        record = dict(upstream_path=upstream, url=url, commit=PIN,
                      path=str(target.relative_to(OUT.parents[2])),
                      retrieved_at=start, wall_seconds=time.monotonic() - tick,
                      exit_code=proc.returncode, curl_receipt=proc.stdout,
                      stderr=proc.stderr, bytes=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest(),
                      tree_blob_sha1=FILES[upstream]['sha'], computed_blob_sha1=git_blob,
                      tree_match=git_blob == FILES[upstream]['sha'],
                      execution_context='trusted public-source retrieval')
        records.append(record)
        LOG.write_text(json.dumps(records, indent=2) + '\n')
        print(json.dumps({k: record[k] for k in ['upstream_path','exit_code','bytes','tree_match']}), flush=True)
        assert proc.returncode == 0 and proc.stdout.startswith('200 ') and record['tree_match']


if __name__ == '__main__':
    main()
