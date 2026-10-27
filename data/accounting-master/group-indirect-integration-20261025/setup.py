"""Adapt the checked additive integration tooling for the next bounded passage."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
prior=ROOT/'data/accounting-master/indirect-cash-integration-20261025'
text=(prior/'integrate_v2.py').read_text()
replacements=[('Version 4.26','Version 4.27'),('Version 4.25','Version 4.26'),("'4.26'","'4.27'"),
 ('manuscript-term-authoring-20261025','manuscript-indirect-cash-20261025'),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-indirect-cash-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-group-indirect-20261025'"),
 ('d35590f4ea484616340fbcaf30eca1b69807f443d3a82f0f75b365819f955f8e','ba94957f48e7e20223ca05ac538ec31a11484c240035b9fcf39d7db5f409b6c6'),
 (r'\paragraph{Distinguish collecting a claim from assessing whether it is overdue.}',r'\input{sections/company-module-language}'),
 ('indirect-addition.tex','group-addition.tex'),
 ('accdsl-indirect-cash-integration-20261025-tex-cache','accdsl-group-indirect-integration-20261025-tex-cache'),
 ('Explain operating cash from profit under explicit classifications.','Carry the legal cash explanations through the same internal pairs.'),
 ('This identity alone leaves the nonoperating part of profit','The adjustment T is calculated'),
 ('that the full note package is complete.','Wider consolidation methods'),
 ('Additive conditional indirect-cash explanation; no whole acceptance','Additive legal-trace/group cash explanation; no whole acceptance'),
 ('declared-indirect-profit-components-20261025/replay-observation.json','group-indirect-cash-20261025/replay-observation.json'),
 ("replay['cases'] == 20","replay['cases'] == 8")]
for old,new in replacements:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
engine=ROOT/'data/accounting-master/group-indirect-cash-20261025'
assert json.loads((engine/'replay-observation.json').read_text())['passed'] is True
locks=json.loads((engine/'source-lock.json').read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
for name,expected in list(locks.items()):assert sha(ROOT/name)==expected,name
for row in json.loads((engine/'evidence.json').read_text())['cases']:
    assert sha(ROOT/row['path'])==row['sha256'];locks[row['path']]=row['sha256']
for name,expected in json.loads((engine/'acceptance-manifest.json').read_text())['artifacts'].items():
    assert sha(ROOT/name)==expected,name;locks[name]=expected
for p in [engine/'acceptance-manifest.json',ROOT/'docs/plans/accounting-group-indirect-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
assert not (HERE/'source-lock.json').exists()
(HERE/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
print(json.dumps({'prepared_tools':True,'locked_files':len(locks)}))
