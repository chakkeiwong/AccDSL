"""Pin accepted attempts once; no predecessor writer is imported."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('data/accounting-master/extended-method-exchanges-20261015')
assert not (HERE / 'source-lock.json').exists(), 'inputs already locked'
rows = []
for name, attempt in [('insurance', 'attempt-01'), ('group', 'attempt-01'),
                      ('bank-assessment', 'attempt-03'), ('insurance-assessment', 'attempt-02')]:
    packet_path = BASE / name / attempt / 'portable-exchanges.json'
    packet = json.loads((ROOT / packet_path).read_text())
    profile = packet.get('profile_ref') or packet['aliases']['profile']
    paths = [BASE / name / p for p in ['semantic-contract.md', 'result.md',
                                     'schema_design.py', 'verify_exchanges.py']]
    paths += [packet_path, BASE / name / attempt / 'record-schemas.json']
    rows.append({'name': name, 'attempt': attempt, 'packet': str(packet_path),
                 'profile_ref': profile,
                 'profile_id': packet['record_registry'][profile['digest']]['body']['profile_id'],
                 'files': {str(p): sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}})
lock = {'date': '2026-10-26', 'profiles': rows, 'readiness': 'not_ready',
        'plan': 'docs/plans/accounting-profile-publication-effects-20261026.md'}
(HERE / 'source-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
print(json.dumps({'locked_profiles': [r['profile_id'] for r in rows],
                  'files': sum(len(r['files']) for r in rows)}))
