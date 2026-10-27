"""One-time dependency identities for a fixed composition, not caller imports."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
names=[
 'scripts/method_requirements_v1.py','scripts/method_requirements_v2.py','scripts/method_requirements_v3.py',
 'scripts/method_input_binding_v1.py','scripts/method_monetary_effects_v1.py','scripts/method_memory_effects_v1.py',
 'scripts/native_return_state_structure_v1.py',
 'data/accounting-master/typed-monetary-effects-20261024/examples.py',
 'data/accounting-master/typed-memory-effects-20261024/examples.py',
 'data/accounting-master/company-return-schema-20261023/return_schema.py',
 'data/accounting-master/company-return-execution-20261024/native_returns.py',
 'data/accounting-master/company-return-execution-20261024/native_reports.py',
 'data/accounting-master/company-portable-authoring-20261023/portable.py',
 'data/accounting-master/company-path-admission-20261023/admission.py']
assert not (HERE/'dependency-lock.json').exists()
(HERE/'dependency-lock.json').write_text(json.dumps({name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names},indent=2)+'\n')
print(json.dumps({'dependencies':len(names)}))
