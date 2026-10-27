"""Read-only restart check; no completed predecessor stage is rerun."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = json.loads((U / 'protection.json').read_text())
for name, digest in p['protected'].items():
    assert sha(R / name) == digest, name
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
assert sha(R / '.git/index') == p['index_sha256']
rows = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True).split('\0')
rows = [x for x in rows if x]
assert {x[3:] for x in rows} == set(p['tracked_dirty'])
assert all(x[:2] == ' M' for x in rows)
for name, digest in p['tracked_dirty'].items():
    assert sha(R / name) == digest, name
for name in p['controls']:
    assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes()
for receipt in sorted((U / 'sources').glob('*.receipt.json')):
    value = json.loads(receipt.read_text())
    assert value['exit_code'] == 0 and value['metrics']['http_code'] == 200
    stem = receipt.name.removesuffix('.receipt.json')
    body = U / 'sources' / (stem + '.body')
    structure = json.loads((U / 'sources' / (stem + '.structure.json')).read_text())
    assert sha(body) == structure['body_sha256']
    assert sha(U / 'sources' / (stem + '.visible.txt')) == structure['visible_sha256']
print(json.dumps({'restart_integrity': 'pass', 'protected_files': len(p['protected']),
                  'tracked_dirty_paths': len(rows), 'completed_acquisitions': 6,
                  'completed_stages_repeated': False}))
