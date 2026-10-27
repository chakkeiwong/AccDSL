"""Copy inspected tooling only; bind its edition-specific changes once."""
import hashlib
import json
from pathlib import Path
import shutil

U=Path(__file__).resolve().parent
R=U.parents[3]
P=R/'data/accounting-master/readability-repair-20261021/regression'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (U/'tooling-manifest.json').exists()
for name in ('reading_inventory.py','author_segment.py'):
    assert not (U/name).exists(),name
source=(P/'reading_inventory.py').read_text()
replacements=[
    ('ROOT = Path(__file__).resolve().parents[3]', 'ROOT = Path(__file__).resolve().parents[4]'),
    ('manuscript-origin-matched-cessation-20261017','manuscript-readability-20261022'),
    ('efceea6d417fb00108985cd43ca57844258a90eb1b809186be6a1b797c953407','b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db'),
    ('AccDSL Version3.41','AccDSL Version 3.47')]
for old,new in replacements:
    assert source.count(old)==1,old
    source=source.replace(old,new,1)
(U/'reading_inventory.py').write_text(source)
shutil.copy2(P/'author_segment.py',U/'author_segment.py')
value={'scope':'Tooling only; no page/node judgments copied',
       'changes':replacements,'files':[{'name':name,'baseline_sha256':sha(P/name),
          'current_sha256':sha(U/name)} for name in ('reading_inventory.py','author_segment.py')]}
(U/'tooling-manifest.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'copied_tools':2,'judgments_copied':0,'edition':'3.47'}))
