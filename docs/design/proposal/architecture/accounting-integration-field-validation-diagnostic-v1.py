"""Finite document consistency diagnostic; no runtime validation or accounting inference."""
import copy
import hashlib
import json
import platform
import sys
from pathlib import Path
B=Path('docs/design/proposal/architecture');P='accounting-integration-field-validation'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((B/n).read_text())
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
m=load(P+'-matrix-v1.json');f=load(P+'-fixtures-v1.json');v=load('accounting-integration-fixtures-v2.json');old=load('accounting-records-fixtures-v1.json');snapshot=load(P+'-inputs-v1.json');reg={**old['records'],**v['records']};checks=[]
def check(n,b):checks.append({'id':n,'passed':bool(b)})
paths=set()
def inventory(x,p):
 paths.add(p)
 if isinstance(x,dict):
  for k,z in x.items():inventory(z,p+'/'+k)
 elif isinstance(x,list):
  for z in x:inventory(z,p+'/*')
for c in v['cases']:
 for k in ['request','assessment','response']:inventory(reg[c[k]]['content'],k)
 q=reg[c['request']]['content'];e=reg[q['eligibility']]['content'];inventory(e,'eligibility_input')
 for r in q['evidence']:inventory(reg[r]['content']['observable_valuation'],'observable_valuation')
 for r in e['conditions']:
  s=json.loads(Path(r['case']['file']['path']).read_text());case=next(z for z in s['cases'] if z['id']==r['case']['case_id']);inventory(case['complete_inputs'][r['condition_id']],'source/'+r['condition_id'])
check('inventory exactly covers retained nested paths',paths=={r['path'] for r in m['rows']})
check('inventory paths unique',len(m['rows'])==len(paths))
for r in m['rows']:
 check(r['id']+' required fields',all(r.get(k) for k in ['types','required_null_behavior','groups','constraint','validation_stage','failure_outcome','binding_or_version_constraint','existing_example','source_locator']))
 check(r['id']+' known rules',all(k in m['groups'] for k in r['groups']))
for p,h in snapshot['protected_sha256'].items():check('unchanged '+p,sha(Path(p))==h)
def pins(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x:check('pin '+x['path'],Path(x['path']).is_file() and sha(Path(x['path']))==x['sha256'])
  for y in x.values():pins(y)
 elif isinstance(x,list):
  for y in x:pins(y)
pins(m);pins(f)
for x in f['cases']:
 cid=x['control']['case_id'];control=next(z for z in v['cases'] if z['id']==cid);check(x['id']+' exact control',all(x['control'][k]==control[k] for k in ['request','assessment','response']))
 mutation=x['mutation'];original=reg[mutation['original_digest']]['content'];expected=copy.deepcopy(original);parent=expected
 for key in mutation['path'][:-1]:parent=parent[key]
 if mutation['operation']=='remove':del parent[mutation['path'][-1]]
 else:parent[mutation['path'][-1]]=mutation['value']
 candidates=[z['content'] for z in x['candidate_records'].values() if z['kind']==mutation['target_kind']]
 check(x['id']+' only declared content mutation',expected in candidates)
 for h,r in x['candidate_records'].items():check(x['id']+' candidate digest '+r['kind'],h==hashlib.sha256((r['domain']+'/'+r['kind']+'\0'+canon(r['content'])).encode('ascii')).hexdigest())
 q=json.loads(x['raw_request']);check(x['id']+' request identity',x['candidate_request_digest']==hashlib.sha256(('accdsl.accounting.integration.v1/request\0'+canon(q)).encode('ascii')).hexdigest())
 outcome=x['expected'];check(x['id']+' unchanged domains',outcome['before']==outcome['after']==control['before'])
 response=outcome['response_fields'];check(x['id']+' no publication',all(response[z] is None for z in ['assessment','diagnostic_journal','diagnostic_delta','receipt','observed_state']) and response['additional_commit'] is False and response['commit_status']=='not_committed')
 check(x['id']+' input before lookup',outcome['stage']=='assessment_consistency' or (response['request'] is None and outcome['receipt_lookup_performed'] is False))
for x in f['field_local_probes']:
 good=x['control_value'];bad=x['candidate_value'];path=x['path'];g=good;b=bad
 for k in path:g=g[k];b=b[k]
 if x['id']=='S01':check('S01 explicit unknown vs string',g is None and isinstance(good['unknown_reason'],str) and isinstance(b,str))
 elif x['id']=='S02':check('S02 decimal string vs number',isinstance(g,str) and type(b) is int)
 elif x['id']=='S03':
  from datetime import date
  date.fromisoformat(g)
  try:date.fromisoformat(b); invalid=False
  except ValueError:invalid=True
  check('S03 calendar invalid',invalid)
 elif x['id']=='S04':check('S04 null vs integer route',g is None and type(b) is int)
report={'schema_version':'accdsl.proposal.field-validation.verification.v1','passed':all(x['passed'] for x in checks),'checks':len(checks),'failures':[x for x in checks if not x['passed']],'counts':{'inventory_paths':len(paths),'matched_exchanges':len(f['cases']),'field_local_probes':len(f['field_local_probes']),'protected_predecessors':len(snapshot['protected_sha256'])},'input_sha256':{str(B/n):sha(B/n) for n in [P+'-matrix-v1.json',P+'-fixtures-v1.json',P+'-inputs-v1.json',P+'-v1.md','accounting-integration-fixtures-v2.json']},'command':'PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__))+' '+sys.argv[1],'environment':platform.python_version()+' standard library; no framework imported or GPU used','scope':'Document inventory, exact mutation, digest and preservation checks only. Expected error codes/stages are specified examples, not independently derived by a full validator. Complete uncovered-predicate coverage and source exchanges remain unfinished.'}
with open(sys.argv[1],'x') as out:json.dump(report,out,indent=2);out.write('\n')
print(json.dumps({k:report[k] for k in ['passed','checks','failures','counts']}))
sys.exit(0 if report['passed'] else 1)
