from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path('data/accounting-master/r05-weight-selector-20261023')
result = json.loads((ROOT / 'reference-results.json').read_text())
assert result['status'] == 'PASS'
assert all(result['checks'].values())
assert all(result['refusals'].values())
assert result['fit_weight'] == '1/2'
assert result['selector'] == 'a_history_zero'
assert 'not interpreted as posterior belief' in (ROOT / 'proposal.md').read_text()
assert 'Statistically supported ranking' in (ROOT / 'result.md').read_text()
print(json.dumps({'status':'PASS','checks':len(result['checks']),'refusals':len(result['refusals']),'empirical_execution':False},separators=(',',':')))
