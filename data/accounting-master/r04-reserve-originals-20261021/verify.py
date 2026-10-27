"""Read-only verification of bound source responses and the retained baseline."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
completion = load(U / 'completion.json')
for name, digest in completion['bindings'].items():
    assert sha(R / name) == digest, name
ledger = load(U / 'source-ledger.json')
assert sha(R / ledger['retained_related_source']['path']) == ledger['retained_related_source']['sha256']
supplement = load(U / 'assessment-supplement.json')
for field in ('baseline', 'operations', 'result'):
    binding = supplement[field]
    assert sha(R / binding['path']) == binding['sha256'], field
assessment = load(R / supplement['baseline']['path'])
operations = load(R / supplement['operations']['path'])
assert len(assessment['rows']) == 53 and len(assessment['interactions']) == 6
assert len(operations['rows']) == 46
assert assessment['readiness'] == 'not_ready'
assert all(row['full_requirement_closed'] is False for row in operations['rows'])
receipts = load(U / 'acquisition-receipts.json')['receipts']
assert len(receipts) == 19
assert all(row['request_started_utc'] is None for row in receipts)
for row in receipts:
    if row['body']:
        p = R / row['body']['path']
        assert sha(p) == row['body']['sha256'] and p.stat().st_size == row['body_bytes']
print(json.dumps({'status': 'read-only verification passed', 'bindings': len(completion['bindings']),
                  'receipts': len(receipts), 'new_technical_papers': 0, 'whole_rows_closed': 0,
                  'readiness': 'not_ready'}))
