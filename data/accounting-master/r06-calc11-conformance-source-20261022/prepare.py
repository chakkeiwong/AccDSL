"""Prepare the new source inquiry once, preserving the completed review."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/readability-repair-20261022-theta/regression'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not (U / 'protection.json').exists(), 'Preparation is one-time'
p, c = load(P / 'protection.json'), load(P / 'completion.json')
assert c['status'] == 'author_diagnosis_complete_no_new_defects_acceptance_pending'
protected = dict(p['protected'])
protected.update(c['bindings'])
protected[str((P / 'completion.json').relative_to(R))] = sha(P / 'completion.json')
for name, digest in protected.items():
    assert sha(R / name) == digest, name
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
assert sha(R / '.git/index') == p['index_sha256']
rows = [x for x in subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True).split('\0') if x]
assert {x[3:] for x in rows} == set(p['tracked_dirty']) and all(x[:2] == ' M' for x in rows)
for name, digest in p['tracked_dirty'].items():
    if name not in p['controls']:
        assert sha(R / name) == digest, name
for name in p['controls']:
    target = U / 'controls-before' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write((R / name).read_bytes())
p['protected'] = protected
p['tracked_dirty'] = {name: sha(R / name) for name in p['tracked_dirty']}
p['predecessor_completion'] = str((P / 'completion.json').relative_to(R))
with (U / 'protection.json').open('x') as stream:
    json.dump(p, stream, indent=2)
    stream.write('\n')
(U / 'sources').mkdir(exist_ok=False)
print(json.dumps({'protected_files': len(protected), 'controls_snapshotted': len(p['controls']), 'tracked_dirty_preserved': len(rows)}))
