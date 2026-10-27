"""Prepare a separate successor; never rewrite an accepted integration."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'data/accounting-master/retained-population-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-population-overlap-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-retained-population-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-retained-population-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-assessment-timeline-20261025'"),
 ('af96982e8920f3ac49867d01b72d8d4642cdbcbfebded8d30427304e144d1311','9e068d276e5a7dfc29df05209ac86bcd3a28f9df760dc73959da511ff2c2599c'),
 ('Version 4.37','VERSION_NEXT'),('Version 4.36','Version 4.37'),('VERSION_NEXT','Version 4.38'),("'4.37'","'4.38'"),
 ('retained-population-overlap-20261025/replay-observation.json','assessment-timeline-20261025/replay-observation.json'),
 ('accdsl-retained-population-integration','accdsl-assessment-timeline-integration'),
 ('Additive retained source-network overlap composition; no whole acceptance','Current-assessment interval and actual-turn scheduling; no whole acceptance'),
 (r'\paragraph{A conditional history gives a conditional opening.}',r'\paragraph{Available inputs do not establish a saved past calculation.}'),
 ("return original.replace(ANCHOR, addition + '\\n\\n' + ANCHOR)","return original.replace('The mixed reference leaves these', 'Version~1 of the mixed reference leaves these').replace(ANCHOR, addition + '\\n\\n' + ANCHOR)")]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["An assessment closes the interval it measures.",
               "Twelve focused tests and 49 regression tests"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/assessment-timeline-20261025'
replay=json.loads(subprocess.check_output([sys.executable,'-B',str(evidence/'verify.py')],text=True))
assert replay['passed'];dump(evidence/'replay-observation.json',replay)
m=json.loads((evidence/'manifest.json').read_text());locks={**m['inputs'],**m['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,h in locks.items():assert sha(ROOT/name)==h,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
