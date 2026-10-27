"""Prepare the additive successor using the reviewed integration procedure."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
engine=ROOT/'data/accounting-master/credit-linked-measurements-20261025'
assert json.loads((engine/'replay-observation.json').read_text())['passed']
text=(ROOT/'data/accounting-master/insurance-statement-integration-20261025/integrate.py').read_text()
changes=[('Version 4.30','Version 4.31'),('Version 4.29','Version 4.30'),("'4.30'","'4.31'"),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-fiscal-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-statement-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-statement-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-credit-linked-20261025'"),
 ('25455c6ae7d84f5e058a45b4ec47b4b749f1a0b455020227299894531334f928','ae30f68628d4a3c40bdf0fe6281a51ed4c9e0f3a3b853fa9d547315af3082f92'),
 ('statement-addition.tex','credit-addition.tex'),
 ('accdsl-insurance-statement-integration-20261025-tex-cache','accdsl-credit-linked-integration-20261025-tex-cache'),
 ('annual operating cash from the same journals.','Credit accrual needs shared amounts'),
 ('The negative working-capital terms reflect','One shared positive day factor preserves'),
 ('classification validity and event completeness remain separate questions.','The checked expressions establish neither choice'),
 ('Additive fiscal insurer statement explanation; no whole acceptance','Additive exact credit measurement explanation; no whole acceptance'),
 ('insurance-statement-bridge-20261025/replay-observation.json','credit-linked-measurements-20261025/replay-observation.json'),
 ("replay['cases'] == 24","replay['cases'] == 9")]
for old,new in changes:
    assert old in text,old; text=text.replace(old,new)
compile(text,'integrate.py','exec'); assert not (HERE/'integrate.py').exists()
(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
locks=json.loads((engine/'source-lock.json').read_text())
for name,h in locks.items(): assert sha(ROOT/name)==h,name
for name,h in json.loads((engine/'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT/name)==h,name; locks[name]=h
for p in [engine/'acceptance-manifest.json',ROOT/'docs/plans/accounting-credit-linked-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
(HERE/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
print(json.dumps({'prepared_tools':True,'locked_files':len(locks)}))
