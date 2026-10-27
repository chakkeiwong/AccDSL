"""Prepare checked additive integration tooling and exact accepted dependencies."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/group-indirect-integration-20261025/integrate.py').read_text()
replacements=[('Version 4.27','Version 4.28'),('Version 4.26','Version 4.27'),("'4.27'","'4.28'"),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-indirect-cash-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-group-indirect-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-group-indirect-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-loss-20261025'"),
 ('ba94957f48e7e20223ca05ac538ec31a11484c240035b9fcf39d7db5f409b6c6','ed05bdcda99fde928a6ae921cda176627e9d5598e0886bc2475b6368e36afc9c'),
 (r'\input{sections/company-module-language}',r"\paragraph{A member's balances can depend on state held by the group.}"),
 ('group-addition.tex','insurance-addition.tex'),
 ('accdsl-group-indirect-integration-20261025-tex-cache','accdsl-insurance-loss-integration-20261025-tex-cache'),
 ('Carry the legal cash explanations through the same internal pairs.','Map an exact insurer schedule into a proposed book.'),
 ('The adjustment T is calculated','Every generated event checks'),
 ('Wider consolidation methods','Annual closing and reopening'),
 ('Additive legal-trace/group cash explanation; no whole acceptance','Additive exact insurer posting and loss-memory explanation; no whole acceptance'),
 ('group-indirect-cash-20261025/replay-observation.json','insurance-loss-book-20261025/replay-observation.json')]
for old,new in replacements:
    assert old in text,old
    text=text.replace(old,new)
# The anchor contains an apostrophe, so use a double-quoted Python raw literal.
old="ANCHOR = r'"+replacements[4][1]+"'"
if old in text:text=text.replace(old,'ANCHOR = r"'+replacements[4][1]+'"')
text=text.replace("ANCHOR = r'\\paragraph{A member's balances can depend on state held by the group.}'",
                  'ANCHOR = r"\\paragraph{A member\'s balances can depend on state held by the group.}"')
compile(text,'integrate.py','exec')
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
engine=ROOT/'data/accounting-master/insurance-loss-book-20261025'
assert json.loads((engine/'replay-observation.json').read_text())['passed'] is True
locks=json.loads((engine/'source-lock.json').read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
for name,expected in list(locks.items()):assert sha(ROOT/name)==expected,name
for row in json.loads((engine/'evidence.json').read_text())['cases']:
    assert sha(ROOT/row['path'])==row['sha256'];locks[row['path']]=row['sha256']
for name,expected in json.loads((engine/'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT/name)==expected,name;locks[name]=expected
for p in [engine/'acceptance-manifest.json',ROOT/'docs/plans/accounting-insurance-loss-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
assert not (HERE/'source-lock.json').exists()
(HERE/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
print(json.dumps({'prepared_tools':True,'locked_files':len(locks)}))
