"""Prepare the network-history successor with preserved predecessor content."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR=ROOT/'data/accounting-master/statement-history-integration-20261025'
assert not (HERE/'integrate.py').exists();text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-retained-history-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-statement-history-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-statement-history-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-network-history-20261025'"),
 ('af6c656c586de5684273a9e2dc546e64d6fd742fb5f35bd80dac313f8d96ef60','703ba5f86f01fc426a71e20f48ad7250eec6049bedea5aef4765c34dd7d4555a'),
 ('Version 4.34','VERSION_NEXT'),('Version 4.33','Version 4.34'),('VERSION_NEXT','Version 4.35'),
 ("'4.34'","'4.35'"),
 ('retained-statement-history-20261025/replay-observation.json','retained-network-history-20261025/replay-observation.json'),
 ("replay['cases'] == 14","replay['cases'] == 11"),
 ('accdsl-statement-history-integration','accdsl-network-history-integration'),
 ('Additive joint statement-history explanation; no whole acceptance','Additive retained network-history explanation; no whole acceptance')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["Reported openings test the assumed starting point.",
               "The full supported network retains 236 observations"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/retained-network-history-20261025'
m=json.loads((evidence/'manifest.json').read_text());locks={**m['inputs'],**m['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md',
          evidence/'annual-cash-flow-page36.png',evidence/'annual-financial-instruments-page40.png',
          ROOT/'docs/design/cases/apple/annual-2024.pdf',
          ROOT/'docs/plans/accounting-network-history-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,digest in locks.items():assert sha(ROOT/name)==digest,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
