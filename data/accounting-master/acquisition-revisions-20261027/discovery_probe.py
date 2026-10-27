"""One new discriminating case; never rerun the accepted verifier."""
from pathlib import Path
import json
import verify as v
H=Path(__file__).resolve().parent;out=H/'discovery-probe-01';out.mkdir(exist_ok=False)
b=v.fixture(cutoff='2026-01-10T00:00:00Z');b['payload']['revision']['available_at']['manager']=None;v.bind(b)
r=v.m.view(b)
expected=['original'];actual=[x['id'] for x in r.get('alternatives',[])]
finding=dict(status='FAIL' if actual!=expected else 'PASS',expected_alternatives=expected,actual_alternatives=actual,reason='Discovery is15 January; availability cannot precede discovery. A10 January cutoff therefore cannot include revised information even when exact availability is unknown.',request=b,result=r)
(out/'finding.json').write_text(json.dumps(finding,indent=2)+'\n');print(json.dumps({k:v for k,v in finding.items() if k not in ['request','result']}))
