"""Create a separate additive successor; never rerun frozen writers."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR=ROOT/'data/accounting-master/network-history-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-statement-history-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-network-history-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-network-history-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-population-overlap-20261025'"),
 ('703ba5f86f01fc426a71e20f48ad7250eec6049bedea5aef4765c34dd7d4555a','6f3d06678a7d3087046c1f14da99693dfad275c653a9e65617df404badf26b37'),
 ('Version 4.35','VERSION_NEXT'),('Version 4.34','Version 4.35'),('VERSION_NEXT','Version 4.36'),
 ("'4.35'","'4.36'"),
 ('retained-network-history-20261025/replay-observation.json','population-overlap-20261025/replay-observation.json'),
 ("replay['cases'] == 11","replay['cases'] == 10"),
 ('accdsl-network-history-integration','accdsl-population-overlap-integration'),
 ('Additive retained network-history explanation; no whole acceptance','Additive cash-population source and conditional overlap explanation; no whole acceptance')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["Cash classifications can overlap without revealing their members.",
               "The monetary constraints preserve this distinction"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/population-overlap-20261025'
r=subprocess.run([sys.executable,'-B',str(evidence/'verify.py')],check=True,capture_output=True,text=True)
replay=json.loads(r.stdout);assert replay['passed'];dump(evidence/'replay-observation.json',replay)
m=json.loads((evidence/'manifest.json').read_text());locks={**m['inputs'],**m['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md',
          ROOT/'data/accounting-master/cash-population-reconciliation-20261025/result.md',
          ROOT/'docs/plans/accounting-population-overlap-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,digest in locks.items():assert sha(ROOT/name)==digest,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
