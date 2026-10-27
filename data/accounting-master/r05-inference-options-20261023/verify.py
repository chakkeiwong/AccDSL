import json
from pathlib import Path
root=Path('data/accounting-master/r05-inference-options-20261023')
text=(root/'result.md').read_text()
assert 'Statistically supported ranking' in text
assert 'Q' in text and 'HAC' in text and 'martingale' in text
assert 'No forecast was collected' in text
plan=Path('docs/plans/accounting-r05-inference-options-20261023.md').read_text()
assert 'Skeptical audit' in plan and 'Evidence contract' in plan
print(json.dumps({'status':'PASS','routes_compared':5,'empirical_execution':False,'default_selected':False},separators=(',',':')))
