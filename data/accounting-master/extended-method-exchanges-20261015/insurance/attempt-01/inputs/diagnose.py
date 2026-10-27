"""Focused exact comparison before building a documentary packet."""
from pathlib import Path
import json
import sys
import time
from financial_checks import evaluate,wire
from fixtures import examples

start=time.monotonic(); checks=[]
for c in examples():
    try:
        r=evaluate(wire(c['input']),wire(c['opening']))
        for k in ('status','diagnostics','closing','detail'):
            expected=wire(c[k]); checks.append(dict(case=c['id'],field=k,passed=r[k]==expected,**({} if r[k]==expected else dict(actual=r[k],expected=expected))))
    except Exception as e: checks.append(dict(case=c['id'],passed=False,error=str(e)))
target=Path(__file__).resolve().parent/sys.argv[1]
result=dict(checks=checks,passed=all(c['passed'] for c in checks),wall_seconds=time.monotonic()-start,mode='exact_diagnostic_no_GPU_framework')
with target.open('x') as f: json.dump(result,f,indent=2); f.write('\n')
print(json.dumps(dict(passed=result['passed'],checks=len(checks),failed=[dict(case=c['case'],field=c.get('field'),error=c.get('error')) for c in checks if not c['passed']],artifact=str(target))))
raise SystemExit(0 if result['passed'] else 1)
