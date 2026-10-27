"""One-time draft anchor-boundary repair after inspecting generated quotations."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
target = U / 'source-ledger.json'
log = U / 'anchor-repair.json'
assert not log.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(target)
d = json.loads(target.read_text())
text = (U / 'sources/01-variables.visible.txt').read_text()
lines = text.splitlines()
norm = lambda s: ' '.join(s.split())
repairs = {'V-identical': ([1815, 1848], [1807, 1835]),
           'V-single': ([1850, 1870], [1851, 1865]),
           'V-sequence': ([1871, 1893], [1866, 1893]),
           'V-errata': ([3871, 3922], [3865, 3922])}
for a in d['anchors']:
    if a['id'] not in repairs:
        continue
    old, (first, last) = repairs[a['id']]
    assert a['visible_lines'] == old
    quote = norm('\n'.join(lines[first - 1:last]))
    prefix = norm('\n'.join(lines[:first - 1]))
    start = len(prefix) + bool(prefix)
    assert norm(text)[start:start + len(quote)] == quote
    a.update(visible_lines=[first, last], quote=quote,
             normalized_character_span=[start, start + len(quote)])
target.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
with log.open('x') as f:
    json.dump({'before_sha256': before, 'after_sha256': sha(target),
               'repairs': repairs, 'reason': 'Include complete governing definitions/header and avoid mid-sentence starts; no source bytes or scientific verdict changed.'}, f, indent=2)
    f.write('\n')
print(json.dumps({'draft_anchor_bounds_repaired': len(repairs), 'source_bytes_changed': False}))
