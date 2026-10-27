"""Add explicit loss admission before the first run, retaining the original freeze."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
data=json.loads((OUT/'authored-cases.json').read_text())
for case in data['cases']:
    case['request']['findings']['baseline_reserve_recoverable']=True
    case['request']['discontinuation']['findings']['continuing_reserve_recoverable']=True
dest=OUT/'authored-cases-v2.json';assert not dest.exists()
dest.write_text(json.dumps(data,indent=2)+'\n')
lock=json.loads((OUT/'input-lock.json').read_text())
files=[ROOT/i['path'] for i in lock['files']]+[OUT/'input-lock.json',dest,OUT/'admission-audit.md',Path(__file__).resolve()]
(OUT/'input-lock-v2.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
print(json.dumps(dict(cases=len(data['cases']),locked_files=len(files),financial_targets_changed=False)))
