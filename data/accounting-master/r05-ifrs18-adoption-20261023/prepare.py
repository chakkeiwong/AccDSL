"""One-time protection; no controller, acquired code or model execution."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
OLD = R / 'data/accounting-master/r05-cashflow-transition-20261023'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U / 'protection.json').exists() and not (U / 'controls-before').exists()
    inherited, complete = load(OLD / 'protection.json'), load(OLD / 'completion.json')
    protected = dict(inherited['protected'])
    protected.update(complete['bindings'])
    protected[str((OLD / 'completion.json').relative_to(R))] = sha(OLD / 'completion.json')
    for name, digest in protected.items():
        assert sha(R / name) == digest, name
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == inherited['head'] and sha(R / '.git/index') == inherited['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [row for row in raw.split('\0') if row]
    assert all(row[:2] == ' M' for row in rows)
    assert {row[3:] for row in rows} == set(inherited['tracked_dirty'])
    dirty = {row[3:]: sha(R / row[3:]) for row in rows}
    for name, digest in inherited['tracked_dirty'].items():
        if name not in inherited['controls']:
            assert dirty[name] == digest
    for name in inherited['controls']:
        target = U / 'controls-before' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f:
            f.write((R / name).read_bytes())
    with (U / 'protection.json').open('x') as f:
        json.dump({'started_utc': datetime.now(timezone.utc).isoformat(),
                   'head': head, 'branch': inherited['branch'], 'index_sha256': inherited['index_sha256'],
                   'tracked_dirty': dirty, 'controls': inherited['controls'], 'protected': protected,
                   'predecessor_completion': str((OLD / 'completion.json').relative_to(R))}, f, indent=2)
        f.write('\n')
    print(json.dumps({'protected_files': len(protected), 'tracked_dirty_paths': len(dirty), 'control_snapshots': 4}))


if __name__ == '__main__':
    main()
