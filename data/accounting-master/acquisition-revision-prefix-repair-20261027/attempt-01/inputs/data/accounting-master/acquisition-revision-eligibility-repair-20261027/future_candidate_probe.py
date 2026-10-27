"""An unavailable financially unsupported revision must not erase the prior view."""
from pathlib import Path
import json
import verify as v
H=Path(__file__).resolve().parent;out=H/'future-candidate-probe-01';out.mkdir(exist_ok=False)
b=v.fixture(cutoff='2026-01-10T00:00:00Z');rp=b['payload']['revised']['payload']
next(x for x in rp['acquired_items'] if x['id']=='equipment')['recognised_balance']='300/1'
next(x for x in b['payload']['revision']['dependent_adjustments'] if x['field']=='equipment')['after']='300/1'
v.bind(b);r=v.m.view(b)
finding=dict(status='FAIL' if r['status']!='original_view' else 'PASS',actual_status=r['status'],expected_status='original_view',reason='Future revised measurements would require a negative-excess method. That candidate is not yet discovered at this query; the earlier complete original report must remain available.',request=b,result=r)
(out/'finding.json').write_text(json.dumps(finding,indent=2)+'\n');print(json.dumps({k:v for k,v in finding.items() if k not in ['request','result']}))
