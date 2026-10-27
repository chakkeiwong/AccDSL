"""Prepare additive statement integration from accepted exact composition."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
engine=ROOT/'data/accounting-master/insurance-statement-bridge-20261025'
observed=json.loads((engine/'replay-observation.json').read_text())
assert observed['passed'] is True and observed['cases']==24
text=(ROOT/'data/accounting-master/insurance-fiscal-integration-20261025/integrate_v2.py').read_text()
changes=[('Version 4.29','Version 4.30'),('Version 4.28','Version 4.29'),("'4.29'","'4.30'"),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-loss-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-fiscal-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-fiscal-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-statement-20261025'"),
 ('04156849dba9c897f55526af8b39fa8a7bbfe2b8f14d678adfab43db6733cb43','25455c6ae7d84f5e058a45b4ec47b4b749f1a0b455020227299894531334f928'),
 ('fiscal-addition.tex','statement-addition.tex'),
 ('accdsl-insurance-fiscal-integration-20261025-tex-cache','accdsl-insurance-statement-integration-20261025-tex-cache'),
 ('Carry the same insurer journals across explicit calendar years.',"Explain the insurer's annual operating cash from the same journals."),
 ('The repair changes the balance conditions','The negative working-capital terms reflect'),
 ('The result demonstrates recorded-balance carry','classification validity and event completeness remain separate questions.'),
 ('Additive insurer fiscal-carry explanation; no whole acceptance','Additive fiscal insurer statement explanation; no whole acceptance'),
 ('insurance-fiscal-book-20261025/replay-observation.json','insurance-statement-bridge-20261025/replay-observation.json'),
 ("replay['cases'] == 8","replay['cases'] == 24")]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
# Use a double-quoted literal for the first locator's apostrophe.
text=text.replace("'Explain the insurer's annual operating cash from the same journals.'",'"Explain the insurer\'s annual operating cash from the same journals."')
compile(text,'integrate.py','exec');assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
locks=json.loads((engine/'source-lock.json').read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
for name,expected in list(locks.items()):assert sha(ROOT/name)==expected,name
for row in json.loads((engine/'evidence.json').read_text())['cases']:
    assert sha(ROOT/row['path'])==row['sha256'];locks[row['path']]=row['sha256']
for name,expected in json.loads((engine/'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT/name)==expected,name;locks[name]=expected
for p in [engine/'acceptance-manifest.json',ROOT/'docs/plans/accounting-insurance-statement-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
assert not (HERE/'source-lock.json').exists()
(HERE/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
print(json.dumps({'prepared_tools':True,'locked_files':len(locks)}))
