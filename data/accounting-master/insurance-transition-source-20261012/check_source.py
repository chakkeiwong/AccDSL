"""Check retained source identities, exact anchors, and access dispositions."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
start = time.monotonic()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
def ck(name, passed): checks.append({'name': name, 'passed': bool(passed)})
b = json.loads((OUT / 'baseline.json').read_text())
for p, h in b['inputs'].items(): ck('protected ' + p, sha(ROOT / p) == h)
for row in b['pointer_snapshots']:
    ck('before snapshot ' + row['live'], sha(ROOT / row['snapshot']) == row['sha256'])
e = json.loads((OUT / 'source-evidence.json').read_text())
ck('source identity', e['source_sha256'] == b['inputs'][e['source']])
ck('exact selected page inventory', set(e['selected_read_pages']) == {1, 5, *range(57, 65)})
ck('text identities', all(sha(ROOT / p) == h for p, h in e['text_hashes'].items()))
anchors = json.loads((OUT / 'source-anchors.json').read_text())
for a in anchors:
    s = ' '.join((ROOT / a['text_path']).read_text().split())
    i = a['normalized_start']; excerpt = a['exact_normalized_excerpt']
    ck('exact source anchor ' + a['provision'], s[i:i+len(excerpt)] == excerpt)
ck('unique anchors', len({a['provision'] for a in anchors}) == len(anchors) == 25)
ck('render bindings', all(sha(ROOT / r['path']) == r['sha256'] and
   r['source_sha256'] == e['source_sha256'] for r in e['renders']))
access = json.loads((OUT / 'acquisition.json').read_text())
ck('four bounded requests', len(access) == 4)
ck('two index responses and two failed PDF probes', [r['status'] for r in access] == [200, 200, 404, 404])
ck('response identities', all(sha(ROOT / r['body']) == r['body_sha256'] for r in access))
ck('failed dependency responses not admitted as PDF', all(not (ROOT/r['body']).read_bytes().startswith(b'%PDF') for r in access[2:]))
ck('no invented numerical or issuer result', not list(OUT.glob('*finite*')) and not e['dependency_text_acquired'])
failed = [r['name'] for r in checks if not r['passed']]
result = {'checks': checks, 'passed': len(checks)-len(failed), 'failed': failed,
          'wall_seconds': time.monotonic()-start,
          'scope': 'Source and preservation checks; accounting interpretation is separately reviewed in source-reading.md.'}
(OUT/'source-checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed']}))
raise SystemExit(bool(failed))
