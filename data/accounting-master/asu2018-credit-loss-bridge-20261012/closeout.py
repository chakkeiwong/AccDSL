#!/usr/bin/env python3
"""Close the 2018 historical bridge without current-ASC promotion."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root.parents[2]
checks = []
def add(name, ok):
    checks.append({'name':name,'pass':bool(ok)})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

run = json.loads((root/'check-run.json').read_text())
add('source checks',run['checks']==72 and not run['failed'])
for name in ['result.md','source-ledger.json','source-pages.json','render-manifest.json','sources/asu-2018-19.headers']:
    add(name,(root/name).is_file())
result = (root/'result.md').read_text()
add('decision table','| Decision | Primary criterion |' in result)
add('current boundary','Current effective dates, complete amendment chain' in result)
add('readiness','**not_ready**' in result)
add('Version 2.33 unchanged',sha(repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf')=='48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496')
failed=[x['name'] for x in checks if not x['pass']]
(root/'closeout-checks.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
