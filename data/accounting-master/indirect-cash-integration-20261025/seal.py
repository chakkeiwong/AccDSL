"""Bind accepted engine evidence before creating the manuscript candidate."""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENGINE = ROOT / 'data/accounting-master/declared-indirect-profit-components-20261025'
def sha(p): return sha256(p.read_bytes()).hexdigest()
assert not (HERE / 'source-lock.json').exists()
replay = json.loads((ENGINE / 'replay-observation.json').read_text())
assert replay['passed'] and replay['cases'] == 20
locks = json.loads((ENGINE / 'source-lock.json').read_text())
for name, expected in list(locks.items()):
    assert sha(ROOT / name) == expected, name
for row in json.loads((ENGINE / 'evidence.json').read_text())['cases']:
    assert sha(ROOT / row['path']) == row['sha256'], row['name']
    locks[row['path']] = row['sha256']
for name, expected in json.loads((ENGINE / 'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT / name) == expected, name
    locks[name] = expected
for p in [ENGINE / 'acceptance-manifest.json', ROOT / 'docs/plans/accounting-indirect-cash-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))] = sha(p)
(HERE / 'source-lock.json').write_text(json.dumps(locks, indent=2) + '\n')
print(json.dumps({'locked': len(locks), 'accepted_cases': replay['cases']}))
