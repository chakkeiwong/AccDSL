from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('data/accounting-master/r05-archive-leads-20261023')

def read_json(path: Path):
    return json.loads(path.read_text())

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = read_json(ROOT / 'archive-record.json')
assert record['requests_used'] == record['request_cap'] == 5
assert record['apple']['cdx_rows'] == 0
assert record['apple']['availability']['archived_snapshots'] == {}
assert record['jpmorgan']['capture_rows'] == 8
assert record['jpmorgan']['first_replay']['matched_retained_original'] is False
jpm = record['jpmorgan']['later_replay']
assert jpm['byte_identical_to_retained_original'] is True
assert jpm['sha256'] == jpm['retained_original_sha256']
assert jpm['size_bytes'] == jpm['retained_original_size_bytes']
assert jpm['pdf_pages'] == 358
assert record['admission_decision']['all_192_historical_admissions_remain_false'] is True
assert record['admission_decision']['historical_vintage_admission_changed'] is False
assert len(list((ROOT / 'requests').glob('*.body'))) == 5
controls = ['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md']
completion = read_json(ROOT / 'completion.json')
for name in controls:
    assert sha(Path(name)) == completion['control_snapshots_after'][name]
    assert sha(ROOT / 'controls-after' / Path(name).name) == completion['control_snapshots_after'][name]
assert sha(ROOT / 'requests/04-jpmorgan-capture-later.body') == jpm['sha256']
assert sha(Path(jpm['retained_original_path'])) == jpm['retained_original_sha256']
assert json.loads((ROOT / 'requests/02-jpmorgan-cdx.body').read_text())[1][0] == '20251119011943'
assert 'signed timestamp certificate' in '\n'.join(record['nonclaims']) or 'signed timestamp certificate' in (ROOT / 'result.md').read_text()
print(json.dumps({'status':'PASS','requests':5,'jpmorgan_byte_match':True,'pages':358,'apple_absence_claimed':False,'historical_admissions_changed':0},separators=(',',':')))
