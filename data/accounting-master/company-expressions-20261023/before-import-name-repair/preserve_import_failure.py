import json
from pathlib import Path
HERE=Path(__file__).resolve().parent; dest=HERE/'before-import-name-repair'
assert not dest.exists(); dest.mkdir()
for p in HERE.glob('*.py'): (dest/p.name).write_bytes(p.read_bytes())
(dest/'failure.json').write_text(json.dumps({'classification':'local module namespace collision','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-expressions-20261023/verify.py --smoke','exit_code':1,'wall_seconds':0.580,'error':'ImportError: cannot import name closed from authoring','cause':'new expression authoring.py occupied sys.modules authoring before protected company engine import','repair':'rename new frontend module to expression_text; leave protected engine untouched','research_direction_rejected':False},indent=2)+'\n')
(HERE/'authoring.py').rename(HERE/'expression_text.py')
print(json.dumps({'preserved':str(dest),'renamed':'expression_text.py'}))
