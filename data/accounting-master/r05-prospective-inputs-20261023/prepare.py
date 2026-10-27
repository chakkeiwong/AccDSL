"""Save ordinary provenance and snapshots once; no inherited evidence edits."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
CONTROLS = ['docs/plans/accounting-master-current.md',
            'docs/plans/accounting-master-checkpoint.md',
            'docs/plans/accounting-mission-requirements.md',
            'data/accounting-master/next-plan.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert os.environ['CUDA_VISIBLE_DEVICES'] == '-1'
    assert not (U / 'start.json').exists()
    state = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    dirty = [x for x in state.split('\0') if x]
    assert all(x[:2] == ' M' for x in dirty)
    for name in CONTROLS:
        target = U / 'controls-before' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f:
            f.write((R / name).read_bytes())
    data = {'started_utc': datetime.now(timezone.utc).isoformat(),
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
            'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=R, text=True).strip(),
            'index_sha256': sha(R / '.git/index'),
            'tracked_dirty': {x[3:]: sha(R / x[3:]) for x in dirty},
            'controls': CONTROLS}
    with (U / 'start.json').open('x') as f:
        json.dump(data, f, indent=2); f.write('\n')
    print(json.dumps({'snapshots': len(CONTROLS), 'tracked_dirty': len(dirty), 'branch': data['branch']}))

if __name__ == '__main__':
    main()
