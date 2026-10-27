"""Read-only recovery check; live controls are checked against saved copies."""
import hashlib
import json
from pathlib import Path
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = json.loads((U / 'protection.json').read_text())
for name, digest in p['protected'].items():
    assert sha(R / name) == digest, name
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
assert sha(R / '.git/index') == p['index_sha256']
raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
rows = [row for row in raw.split('\0') if row]
assert {row[3:] for row in rows} == set(p['tracked_dirty'])
assert all(row[:2] == ' M' for row in rows)
for name, digest in p['tracked_dirty'].items():
    if name not in p['controls']:
        assert sha(R / name) == digest, name
for name in p['controls']:
    assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes(), name
receipts = sorted((U / 'sources').glob('*.receipt.json'))
assert len(receipts) == 11
for path in receipts:
    receipt = json.loads(path.read_text())
    ident = receipt['id']
    meta = json.loads((U / 'sources' / (ident + '.structure.json')).read_text())
    assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
    assert receipt.get('started_utc') and receipt.get('finished_utc'), ident
    assert sha(U / 'sources' / (ident + '.body')) == meta['body_sha256']
    assert sha(U / 'sources' / (ident + '.visible.txt')) == meta['visible_sha256']
print(json.dumps({'protected_files': len(p['protected']), 'tracked_dirty': len(rows),
                  'retained_sources': len(receipts), 'receipt_brackets_present': True,
                  'writes': 0}))
