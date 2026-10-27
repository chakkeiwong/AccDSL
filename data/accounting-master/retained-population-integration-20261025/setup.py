"""Create separate4.37 source-network composition successor."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR=ROOT/'data/accounting-master/population-overlap-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-network-history-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-population-overlap-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-population-overlap-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-retained-population-20261025'"),
 ('6f3d06678a7d3087046c1f14da99693dfad275c653a9e65617df404badf26b37','af96982e8920f3ac49867d01b72d8d4642cdbcbfebded8d30427304e144d1311'),
 ('Version 4.36','VERSION_NEXT'),('Version 4.35','Version 4.36'),('VERSION_NEXT','Version 4.37'),("'4.36'","'4.37'"),
 ('population-overlap-20261025/replay-observation.json','retained-population-overlap-20261025/replay-observation.json'),
 ("replay['cases'] == 10","replay['cases'] == 8"),
 ('accdsl-population-overlap-integration','accdsl-retained-population-integration'),
 ('Additive cash-population source and conditional overlap explanation; no whole acceptance','Additive retained source-network overlap composition; no whole acceptance')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["The overlap must also satisfy the original statement network.",
               "The resulting temporal constraints can be supplied"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/retained-population-overlap-20261025'
run=subprocess.run([sys.executable,'-B',str(evidence/'verify.py')],check=True,capture_output=True,text=True)
replay=json.loads(run.stdout);assert replay['passed'];dump(evidence/'replay-observation.json',replay)
m=json.loads((evidence/'manifest.json').read_text());locks={**m['inputs'],**m['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md',
          ROOT/'docs/plans/accounting-retained-population-overlap-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,h in locks.items():assert sha(ROOT/name)==h,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
