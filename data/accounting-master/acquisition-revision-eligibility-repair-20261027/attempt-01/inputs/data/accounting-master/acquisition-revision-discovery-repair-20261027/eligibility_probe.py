"""Unknown availability cannot make an ineligible retrospective branch possible."""
from pathlib import Path
import json
import verify as v
H=Path(__file__).resolve().parent;out=H/'eligibility-probe-01';out.mkdir(exist_ok=False)
b=v.fixture();b['payload']['revision']['available_at']['manager']=None;b['payload']['revision']['disposition']='later_event';v.bind(b)
r=v.m.view(b);ids=[a['id'] for a in r.get('alternatives',[])]
finding=dict(status='FAIL' if 'revised' in ids else 'PASS',actual_alternatives=ids,expected_alternatives=['original'],reason='The supplied disposition is a later event. Unknown availability changes whether the actor has learned it, not whether retrospective acquisition measurement is an eligible treatment.',request=b,result=r)
(out/'finding.json').write_text(json.dumps(finding,indent=2)+'\n');print(json.dumps({k:v for k,v in finding.items() if k not in ['request','result']}))
