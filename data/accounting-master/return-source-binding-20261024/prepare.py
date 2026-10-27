"""Lock the existing source mapper, prefix replay and financial method."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
names=[
 'scripts/typed_return_transition_v1.py',
 'data/accounting-master/typed-return-composition-20261024/dependency-lock.json',
 'data/accounting-master/company-return-schema-20261023/retained_fixture.py',
 'data/accounting-master/company-return-schema-20261023/return_schema.py',
 'data/accounting-master/company-return-execution-20261024/retained_execution_context.py',
 'data/accounting-master/company-return-execution-20261024/native_returns.py',
 'data/accounting-master/company-composition-20261016/attempt-03/inputs/financial_checks.py']
assert not (HERE/'dependency-lock.json').exists()
(HERE/'dependency-lock.json').write_text(json.dumps({p:sha256((ROOT/p).read_bytes()).hexdigest() for p in names},indent=2)+'\n')
print(json.dumps({'dependencies':len(names)}))
