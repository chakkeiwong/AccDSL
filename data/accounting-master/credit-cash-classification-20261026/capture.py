from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'source-lock.json').exists()
base=ROOT/'data/accounting-master/credit-linked-book-20261025'
files=json.loads((base/'source-lock.json').read_text())
evidence=json.loads((base/'evidence.json').read_text())
for row in evidence['cases']:files[row['path']]=row['sha256']
for p in [base/'evidence.json',base/'result.md',base/'source-lock.json',ROOT/'scripts/credit_linked_book_v1.py']:
    files[str(p.relative_to(ROOT))]=sha256(p.read_bytes()).hexdigest()
for p,h in files.items():assert sha256((ROOT/p).read_bytes()).hexdigest()==h,p
(HERE/'source-lock.json').write_text(json.dumps({'files':files,'cases':evidence['cases'],
    'plan':'docs/plans/accounting-credit-cash-classification-20261026.md'},indent=2)+chr(10))
print(json.dumps({'pinned_files':len(files),'retained_cases':len(evidence['cases'])}))
