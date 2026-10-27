from fixtures import *
import json
base={'available_at':'2026-04-01T00:00:00.0000001Z','ingested_at':'2026-04-01T00:00:00.0000001Z',
 'decision_at':'2026-04-01T00:00:00.0000001Z','system_asof':'2026-04-01T00:00:00.0000001Z'}
for name,changes,expected in [('equal',{},None),('later',{'available_at':'2026-04-01T00:00:00.0000002Z'},'later_information')]:
 f=Fixture(name,{**base,**changes});f.base_request()
 try:f.a.request(f.rq,f.sub,f.before);actual=None
 except n.Refusal as e:actual=e.code
 assert actual==expected,(name,actual,expected)
 ex=f.response(expected);f.a.response(ex)
 print(json.dumps({'case':name,'request':actual or 'new','complete_response_valid':True,'derived_records':len(f.records)}))
