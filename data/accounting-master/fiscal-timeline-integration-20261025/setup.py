"""Prepare the isolated fiscal-timeline manuscript successor."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'data/accounting-master/assessment-timeline-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-retained-population-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-assessment-timeline-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-assessment-timeline-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-fiscal-timeline-20261025'"),
 ('9e068d276e5a7dfc29df05209ac86bcd3a28f9df760dc73959da511ff2c2599c','ea41f8c19bbc3362d2e6ebd2bbea6baf354cb783b76d4b3556790a3c7cffa058'),
 ('Version 4.38','VERSION_NEXT'),('Version 4.37','Version 4.38'),('VERSION_NEXT','Version 4.39'),("'4.38'","'4.39'"),
 ('assessment-timeline-20261025/replay-observation.json','fiscal-timeline-20261025/replay-observation.json'),
 ("replay['cases'] == 8","replay['cases'] == 12"),
 ('accdsl-assessment-timeline-integration','accdsl-fiscal-timeline-integration'),
 ('Current-assessment interval and actual-turn scheduling; no whole acceptance','State-bound deferred measurement and terminal carry; no whole acceptance'),
 ("original.replace('The mixed reference leaves these', 'Version~1 of the mixed reference leaves these')",
  "original.replace('Deferred measurement\\nstill requires', 'In version~2, deferred measurement\\nstill requires')")]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["A measurement belongs to a particular book.",
               "Thirteen focused tests and 61 regressions"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/fiscal-timeline-20261025'
replay=json.loads(subprocess.check_output([sys.executable,'-B',str(evidence/'verify.py')],text=True))
assert replay['passed'];dump(evidence/'replay-observation.json',replay)
m=json.loads((evidence/'manifest.json').read_text());locks={**m['inputs'],**m['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,h in locks.items():assert sha(ROOT/name)==h,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
