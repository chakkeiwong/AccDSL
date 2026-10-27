"""Preserve the superseded ASCII-only verification before canonicalization repair."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
dest=HERE/'before-unicode-canonical-repair'
assert not dest.exists()
dest.mkdir()
for p in HERE.glob('*.py'):
    (dest/p.name).write_bytes(p.read_bytes())
for name in ['checks.json','fixture.json','result.json','schema.json','baseline.json','example.accdsl','manifest.json']:
    (HERE/name).rename(dest/name)
(dest/'failure.json').write_text(json.dumps({
 'classification':'implementation identity mismatch outside original ASCII fixtures',
 'trigger':'path name Northstar 公司',
 'wrapper_path_digest':'3f1b966886b55ac0c9dfcd7fcb5d715b47b06d7299d3b98426a02d8cabe92337',
 'engine_path_digest':'ee32fc36ddcd2b08a3753f9c0bf0bc7ffbd3f7ce630a7074d166be96587c6b02',
 'cause':'wrapper used ensure_ascii=False; protected engine uses JSON default ensure_ascii=True',
 'prior_checks':92,'prior_record_seconds':18.423,'prior_replay_seconds':18.839,
 'repair':'use the same canonical JSON convention and add non-ASCII cross-layer identity regression',
 'direction_rejected':False},indent=2)+'\n')
print(json.dumps({'preserved':str(dest),'recording_superseded':True}))
