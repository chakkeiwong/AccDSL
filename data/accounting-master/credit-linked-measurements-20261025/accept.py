"""Bind the successful record and read-only replay without rerunning writers."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
for n,h in json.loads((HERE/'source-lock.json').read_text()).items(): assert sha(ROOT/n)==h,n
for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items(): assert sha(ROOT/n)==h,n
for mode,source in [('record','/tmp/accdsl-credit-linked-record-v2.log'),('replay','/tmp/accdsl-credit-linked-replay.log')]:
    p=Path(source); observation=json.loads(p.read_text().strip().splitlines()[-1])
    assert observation['passed'] and observation['cases']==9 and observation['native_refusals']==53
    assert observation['focused']==23 and observation['regressions']==44 and observation['locked_files']==334
    shutil.copyfile(p,HERE/(mode+'.log'))
dump(HERE/'replay-observation.json',observation)
names=['audit.md','verify.py','result.md','source-lock.json','evidence.json','run-manifest.json',
       'replay-observation.json','record.log','replay.log','accept.py','transient-fixtures.json',
       'attempt-01-recorder/result.md','attempt-01-recorder/verify.py','attempt-01-recorder/record.log']
dump(HERE/'acceptance-manifest.json',{'status':'accepted_bounded_read_only_representation',
    'host_book_admission':False,'accounting_admission':False,
    'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}})
print(json.dumps({'accepted':True,'cases':9,'scope':'read_only_exact_representation'}))
