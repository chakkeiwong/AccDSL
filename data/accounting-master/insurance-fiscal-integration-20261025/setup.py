"""Prepare fiscal integration only after accepted full replay."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
engine=ROOT/'data/accounting-master/insurance-fiscal-book-20261025'
observed=json.loads((engine/'replay-observation.json').read_text())
assert observed['passed'] is True and observed['cases']==8
text=(ROOT/'data/accounting-master/insurance-loss-integration-20261025/integrate.py').read_text()
changes=[('Version 4.28','Version 4.29'),('Version 4.27','Version 4.28'),("'4.28'","'4.29'"),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-group-indirect-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-loss-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-loss-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-fiscal-20261025'"),
 ('ed05bdcda99fde928a6ae921cda176627e9d5598e0886bc2475b6368e36afc9c','04156849dba9c897f55526af8b39fa8a7bbfe2b8f14d678adfab43db6733cb43'),
 ('insurance-addition.tex','fiscal-addition.tex'),
 ('accdsl-insurance-loss-integration-20261025-tex-cache','accdsl-insurance-fiscal-integration-20261025-tex-cache'),
 ('Map an exact insurer schedule into a proposed book.','Carry the same insurer journals across explicit calendar years.'),
 ('Every generated event checks','The repair changes the balance conditions'),
 ('Annual closing and reopening','actual fiscal completeness'),
 ('Additive exact insurer posting and loss-memory explanation; no whole acceptance','Additive insurer fiscal-carry explanation; no whole acceptance'),
 ('insurance-loss-book-20261025/replay-observation.json','insurance-fiscal-book-20261025/replay-observation.json')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
compile(text,'integrate.py','exec');assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
locks=json.loads((engine/'source-lock.json').read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
for name,expected in list(locks.items()):assert sha(ROOT/name)==expected,name
for row in json.loads((engine/'evidence.json').read_text())['cases']:
    assert sha(ROOT/row['path'])==row['sha256'];locks[row['path']]=row['sha256']
for name,expected in json.loads((engine/'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT/name)==expected,name;locks[name]=expected
for p in [engine/'acceptance-manifest.json',ROOT/'docs/plans/accounting-insurance-fiscal-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
assert not (HERE/'source-lock.json').exists()
(HERE/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
print(json.dumps({'prepared_tools':True,'locked_files':len(locks)}))
