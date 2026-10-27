#!/usr/bin/env python3
"""Close the blocked-index inquiry while preserving the individual ASU."""
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
add('79 source checks',run['checks']==79 and not run['failed'])
for name in ['result.md','author-review.md','source-ledger.json','sources/asu-2019-11.pdf']:
    add(name,(root/name).is_file())
result=(root/'result.md').read_text()
add('decision table','| Decision | Primary criterion |' in result)
add('inventory rejected','Reject completeness of the inventory' in result)
add('current ASC not promoted','Current ASC applicability or E07 closure' in result)
add('readiness','**not_ready**' in result)
add('manuscript baseline',sha(repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf')=='48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496')
failed=[x['name'] for x in checks if not x['pass']]
(root/'closeout-checks.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
