"""Prepare the additive Version4.34 successor from a preserved integrator."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR=ROOT/'data/accounting-master/retained-history-integration-20261025'
assert not (HERE/'integrate.py').exists()
text=(PRIOR/'integrate.py').read_text()
changes=[
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-credit-linked-book-20261025'","SOURCE = ROOT / 'docs/design/proposal/manuscript-retained-history-20261025'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-retained-history-20261025'","TARGET = ROOT / 'docs/design/proposal/manuscript-statement-history-20261025'"),
 ('8b37990bbc97416916ae9874156ecdb4e2a286ba6d6d7cfe70e26c3fd221a878','af6c656c586de5684273a9e2dc546e64d6fd742fb5f35bd80dac313f8d96ef60'),
 ('Version 4.33','VERSION_NEXT'),('Version 4.32','Version 4.33'),('VERSION_NEXT','Version 4.34'),
 ("'4.33'","'4.34'"),('history-addition.tex','addition.tex'),
 ('retained-source-history-20261025/replay-observation.json','retained-statement-history-20261025/replay-observation.json'),
 ("replay['cases'] == 11","replay['cases'] == 14"),
 ('accdsl-retained-history-integration','accdsl-statement-history-integration'),
 ('Additive source-bound conditional history explanation; no whole acceptance','Additive joint statement-history explanation; no whole acceptance')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
start=text.index('    phrases = [');end=text.index('    locations = ',start)
text=text[:start]+'''    phrases = ["Another statement can reject a cash-compatible history.",
               "The reported opening balance sheet and equity movements"]
'''+text[end:]
compile(text,'integrate.py','exec');(HERE/'integrate.py').write_text(text)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
evidence=ROOT/'data/accounting-master/retained-statement-history-20261025'
manifest=json.loads((evidence/'manifest.json').read_text());locks={**manifest['inputs'],**manifest['outputs']}
for p in [evidence/'manifest.json',evidence/'replay-observation.json',evidence/'result.md',
          ROOT/'docs/plans/accounting-statement-history-integration-20261025.md']:
    locks[str(p.relative_to(ROOT))]=sha(p)
for name,digest in locks.items():assert sha(ROOT/name)==digest,name
dump(HERE/'source-lock.json',locks)
dump(HERE/'integration-code-lock.json',{n:sha(HERE/n) for n in ['integrate.py','addition.tex','audit.md','setup.py']})
print(json.dumps({'integrator_prepared':True,'evidence_files':len(locks)}))
