#!/usr/bin/env python3
"""Close the historical 2019-10 source without a current-authority claim."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
repo=root.parents[2]
checks=[]
def add(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
run=json.loads((root/'check-run.json').read_text())
add('source checks',run['checks']==73 and not run['failed'])
for name in ['result.md','author-review.md','source-ledger.json','sources/asu-2019-10.headers']:
    add(name,(root/name).is_file())
result=(root/'result.md').read_text()
add('decision table','| Decision | Primary criterion |' in result)
add('later authority boundary','current dates and the status of a particular company' in result)
add('verified next lead','ASU 2019-05' in result)
add('readiness','**not_ready**' in result)
add('Version 2.33 frozen',sha(repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf')=='48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496')
failed=[x['name'] for x in checks if not x['pass']]
(root/'closeout-checks.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
