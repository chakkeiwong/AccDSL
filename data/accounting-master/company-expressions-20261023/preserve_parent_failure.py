import json
from pathlib import Path
HERE=Path(__file__).resolve().parent; dest=HERE/'before-parent-selection-repair'
assert not dest.exists(); dest.mkdir()
for p in HERE.glob('*.py'): (dest/p.name).write_bytes(p.read_bytes())
(dest/'failure.json').write_text(json.dumps({'classification':'wrong test comparator parent','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-expressions-20261023/verify.py --smoke','exit_code':1,'wall_seconds':0.641,'error':'KeyError policy after correctly refused parent_path_identity','cause':'protected policy is bound to second_year_price_revision, not baseline','repair':'select unique retained path by policy parent hash; do not rebind policy','research_direction_rejected':False},indent=2)+'\n')
print(json.dumps({'preserved':str(dest)}))
