"""Inherit and protect the completed exact-note inquiry once."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/r06-duplicates-guidance-20261023'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not (U / 'protection.json').exists()
spec = importlib.util.spec_from_file_location('prior_authored_check', P / 'verify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
p, checks = module.check()
completion = load(P / 'completion.json')
for name, digest in completion['bindings'].items():
    assert sha(R / name) == digest, name
p['protected'].update(completion['bindings'])
p['protected'][str((P / 'completion.json').relative_to(R))] = sha(P / 'completion.json')
p['predecessor_completion'] = str((P / 'completion.json').relative_to(R))
p['started_utc'] = datetime.now(timezone.utc).isoformat()
p['tracked_dirty'] = {name: sha(R / name) for name in p['tracked_dirty']}
for name in p['controls']:
    target = U / 'controls-before' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write((R / name).read_bytes())
with (U / 'protection.json').open('x') as stream:
    json.dump(p, stream, indent=2)
    stream.write('\n')
(U / 'sources').mkdir(exist_ok=False)
print(json.dumps({'protected_files': len(p['protected']), 'controls_snapshotted': 4,
                  'predecessor': 'verified complete; unchanged'}))
