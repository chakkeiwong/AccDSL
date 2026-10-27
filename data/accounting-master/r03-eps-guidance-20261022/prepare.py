"""Protect the completed manuscript and EPS evidence before source inquiry."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/readability-repair-20261022-theta'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not (U / 'protection.json').exists()
protected = dict(load(P / 'protection.json')['protected'])
for name, digest in load(P / 'completion.json')['bindings'].items():
    assert name not in protected or protected[name] == digest, name
    protected[name] = digest
protected[str((P / 'completion.json').relative_to(R))] = sha(P / 'completion.json')
for directory in ('dependent-eps-source-selection-20261017', 'r03-eps-order-discriminator-20261018', 'r03-marginal-eps-stability-20261019'):
    for path in (R / 'data/accounting-master' / directory).glob('*'):
        if path.is_file():
            name, digest = str(path.relative_to(R)), sha(path)
            assert name not in protected or protected[name] == digest, name
            protected[name] = digest
for name, digest in protected.items():
    assert sha(R / name) == digest, name
controls = load(P / 'protection.json')['controls']
status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
rows = [x for x in status.split('\0') if x]
assert len(rows) == 36 and all(x[:2] == ' M' for x in rows)
protection = dict(started_utc=datetime.now(timezone.utc).isoformat(),
    head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
    branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=R, text=True).strip(),
    index_sha256=sha(R / '.git/index'), tracked_dirty={x[3:]: sha(R / x[3:]) for x in rows},
    controls=controls, protected=protected)
for name in controls:
    dest = U / 'controls-before' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(R / name, dest)
with (U / 'protection.json').open('x') as f:
    json.dump(protection, f, indent=2)
    f.write('\n')
print(json.dumps(dict(protected_files=len(protected), tracked_dirty_preserved=len(rows))))
