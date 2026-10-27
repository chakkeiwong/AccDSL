"""Prepare a bounded successor using the previously checked integration pattern."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OLD=ROOT/'data/accounting-master/credit-linked-book-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(OLD/'integrate_v2.py').read_text()
changes=[
 ('Version 4.32 manuscript successor','Version 4.33 manuscript successor'),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-credit-linked-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-credit-linked-book-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-credit-linked-book-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-retained-history-20261025'"),
 ('6621655ac6cc8133e4f6533106a0c32cd4393a5575b62c9f94744875e9fad5b7','8b37990bbc97416916ae9874156ecdb4e2a286ba6d6d7cfe70e26c3fd221a878'),
 ('''ANCHOR = r"\paragraph{A member's balances can depend on state held by the group.}"''',
  '''ANCHOR = r"\paragraph{A conditional history gives a conditional opening.}"'''),
 ('Version 4.32','VERSION_SUCCESSOR'),('Version 4.31','Version 4.32'),('VERSION_SUCCESSOR','Version 4.33'),
 ("'4.32'","'4.33'"),('book-addition-v2.tex','history-addition.tex'),
 ('layout-repair-lock.json','integration-code-lock.json'),('build-v2','build'),
 ('credit-linked-book-20261025/replay-observation.json','retained-source-history-20261025/replay-observation.json'),
 ("replay['cases'] == 36","replay['cases'] == 11"),
 ('accdsl-credit-linked-book-integration','accdsl-retained-history-integration'),
 ('Additive optional exact credit book explanation; no whole acceptance','Additive source-bound conditional history explanation; no whole acceptance')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["Disclosed cash constrains a history without identifying it.",
               "The interim bridge illustrates a second distinction.",
               "Eleven complete exchanges and their semantic replay"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/retained-source-history-20261025'
manifest=json.loads((evidence/'manifest.json').read_text())
locks={**manifest['inputs'],**manifest['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md',
          ROOT/'docs/plans/accounting-retained-history-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,digest in locks.items():assert sha(ROOT/name)==digest,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','history-addition.tex','audit.md','setup.py']})
print(json.dumps({'prepared_integrator':True,'evidence_files':len(locks)}))
