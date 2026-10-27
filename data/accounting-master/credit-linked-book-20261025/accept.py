"""Bind the completed record and exact read-only replay once."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
for n,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/n)==h,n
for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/n)==h,n
for mode in ['record','replay']:
    p=Path('/tmp/accdsl-credit-book-'+mode+'.log');o=json.loads(p.read_text().strip().splitlines()[-1])
    assert o['passed'] and o['cases']==36 and o['focused']==17 and o['regressions']==72 and o['locked_files']==406
    shutil.copyfile(p,HERE/(mode+'.log'))
dump(HERE/'replay-observation.json',o)
names=['audit.md','verify.py','examples.py','result.md','source-lock.json','evidence.json',
       'run-manifest.json','record.log','replay.log','replay-observation.json','accept.py']
dump(HERE/'acceptance-manifest.json',{'status':'accepted_optional_read_only_projection',
    'accounting_admission':False,'posting_authorized':False,
    'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}})
print(json.dumps({'accepted':True,'cases':36,'scope':'optional_exact_book_projection'}))
