from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
assert not (HERE/'source-lock.json').exists(),'already captured'
prior='data/accounting-master/profile-publication-effects-20261026/'
files=[prior+n for n in ['descriptor.py','source-lock.json','checks.json','result.md','contract.md']]
files += ['scripts/'+n+'.py' for n in ['annual_program_authoring_v1','method_requirement_text_v2','method_input_binding_v2',
 'shared_state_compatibility_v1','conditional_family_text_v1','method_requirement_text_v1','method_requirements_v1']]
native=json.loads((ROOT/prior/'source-lock.json').read_text())
hashes={f:sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
for entry in native['profiles']:
    for f,h in entry['files'].items():
        assert sha256((ROOT/f).read_bytes()).hexdigest()==h,f
        hashes[f]=h
(HERE/'source-lock.json').write_text(json.dumps({'date':'2026-10-26','files':hashes,'native_profiles':native['profiles'],
 'plan':'docs/plans/accounting-profile-composition-boundary-20261026.md'},indent=2)+'\n')
print(json.dumps({'pinned_files':len(hashes)}))
