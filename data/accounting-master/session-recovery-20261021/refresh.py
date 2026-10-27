"""Refresh live scheduling once, preserving each prior control byte-for-byte."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

U = Path(__file__).resolve().parent
R = U.parents[2]
paths = [
    'docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md',
    'data/accounting-master/next-plan.md',
]
old = '''Next: conduct the exact Version 3.46 argument review under a fresh inventory,
then continue the consequential Wang1995, Merz/Wüthrich2014 and England2019
original-source/edition inquiries. Use bounded actual-view segments, at most
six pages per segment and three images per tool call. Record specific node and
equation judgments, chapter/prefix syntheses and the final argument assessment.
'''
new = '''Next: resolve the consequential Wang1995, Merz/Wüthrich2014 and England2019
original-source/edition inquiries under
docs/plans/accounting-reserve-originals-20261021.md before the next full review.
A substantive source correction could require a new candidate; source-first
scheduling avoids invalidating a premature 401-page pass. Route-specific access
failures block their dependent claims, not independent internal work.
Then conduct the full argument review of the exact resulting candidate under a
fresh inventory. Use at most six pages per reading segment and three images per
tool call; record node/equation judgments and chapter/prefix/document syntheses.
The recovery and bounded-call discipline are recorded in
data/accounting-master/session-recovery-20261021/recovery.md.
'''
sha = lambda b: hashlib.sha256(b).hexdigest()
assert not (U / 'refresh-result.json').exists(), 'Completed refresh must not repeat'
contents = {p: (R / p).read_bytes() for p in paths}
for p, data in contents.items():
    text = data.decode()
    assert text.count(old) == 1, p
    assert 'Version 3.46, 401 pages; not_ready' in text, p
before, after = {}, {}
for p, data in contents.items():
    dest = U / 'controls-before' / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as f:
        f.write(data)
    before[p] = sha(data)
for p, data in contents.items():
    updated = data.decode().replace(old, new, 1).encode()
    (R / p).write_bytes(updated)
    dest = U / 'controls-after' / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as f:
        f.write(updated)
    after[p] = sha(updated)
    assert updated.decode().replace(new, old, 1).encode() == data
c = sqlite3.connect('file:/home/chakwong/.codex/logs_2.sqlite?mode=ro', uri=True)
rows = c.execute("SELECT id,ts,feedback_log_body FROM logs WHERE target='codex_core::responses_retry' AND level='WARN' AND feedback_log_body LIKE '%cwd=/home/chakwong/python/AccDSL}%' AND id<=614754011 ORDER BY id DESC LIMIT 14").fetchall()
events = [{'log_id': rid, 'utc': datetime.fromtimestamp(ts, timezone.utc).isoformat(),
           'error': body.split('sampling_error=', 1)[-1]} for rid, ts, body in rows]
with (U / 'transport-evidence.json').open('x') as f:
    json.dump({'scope': 'Latest 14 AccDSL retry warnings through log id 614754011',
               'provider': 'visioncoder custom endpoint; credentials and address omitted',
               'events': events}, f, indent=2)
with (U / 'refresh-result.json').open('x') as f:
    json.dump({'recorded_utc': datetime.now(timezone.utc).isoformat(),
               'before': before, 'after': after, 'exact_reversible_replacement': True,
               'whole_rows_closed': 0, 'readiness': 'not_ready'}, f, indent=2)
print(json.dumps({'controls_refreshed': len(paths), 'transport_events_retained': len(events),
                  'exact_reversible_replacement': True, 'readiness': 'not_ready'}))
