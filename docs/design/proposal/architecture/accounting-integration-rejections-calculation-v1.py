"""Finite input-derived calculation of named proposal examples; not a runtime API."""
import collections
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
start=time.monotonic()
root=Path(__file__).resolve().parents[4]; base=root/'docs/design/proposal/architecture'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
digest=lambda d,k,c:hashlib.sha256((d+'/'+k+'\0'+canon(c)).encode('ascii')).hexdigest()
load=lambda n:json.loads((base/n).read_text())
f=load('accounting-integration-rejections-fixtures-v1.json');v=load('accounting-integration-fixtures-v2.json');l=load('accounting-records-fixtures-v1.json');inputs=load('accounting-integration-rejections-inputs-v1.json')
checks=[]; used={Path(__file__).resolve()};derived=[]
def check(k,value):checks.append({'id':k,'passed':bool(value)})
def strict(text):
 def pairs(items):
  d={}
  for k,val in items:
   if k in d:raise ValueError(k)
   d[k]=val
  return d
 return json.loads(text,object_pairs_hook=pairs)
def diag(stage,code,path,expected,observed):return dict(stage=stage,code=code,path=path,expected=expected,observed=observed)
base_request=v['records'][v['cases'][0]['request']]['content']
required_versions={'context':'schema_version','branch':'version','chart':'version','event':'version','evidence':'version','assumptions':'version','authority':'version','method':'version','state':'sequence','eligibility_input':'schema_version'}
def derive(x):
 try:q=strict(x['raw_text'])
 except ValueError as err:return [diag('parse','DUPLICATE_JSON_KEY','/request/'+str(err),'unique JSON keys',str(err))]
 available={y['claimed_digest']:y for y in x['dependencies']};resolved={};findings=[]
 def walk(value):
  if isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value):
   if value in resolved:return
   if value not in available:
    findings.append(diag('dependencies','MISSING_DEPENDENCY','/dependencies/'+value,'supplied record','unavailable'));return
   row=available[value];c=strict(row['content_text']);actual=digest(row['domain'],row['kind'],c);resolved[value]=(row['kind'],c)
   if actual!=value:findings.append(diag('dependencies','RECORD_DIGEST_MISMATCH','/dependencies/'+value,value,actual));return
   walk(c)
  elif isinstance(value,dict):
   if set(value)=={'path','sha256'}:
    p=root/value['path'];used.add(p)
    if not p.is_file() or sha(p)!=value['sha256']:findings.append(diag('dependencies','PINNED_FILE_UNAVAILABLE','/files/'+value['path'],value['sha256'],'unavailable_or_unequal'))
    return
   for key,child in value.items():walk(child)
  elif isinstance(value,list):
   for child in value:walk(child)
 walk(q)
 if findings:return sorted({canon(z):z for z in findings}.values(),key=lambda z:(z['path'],z['code']))
 expected_fields=set(base_request) if q.get('schema_version')!=1 or type(q.get('schema_version')) is bool else set(l['records'][l['cases'][-1]['lookup']['expected_request']]['content'])
 for k in sorted(set(q)-expected_fields):findings.append(diag('shape','UNEXPECTED_FIELD','/request/'+k,'field absent',q[k]))
 if type(q.get('schema_version')) is not int or q['schema_version']<0:findings.append(diag('shape','INVALID_RECORD_VERSION_TYPE','/request/schema_version','nonnegative integer excluding bool',q.get('schema_version')))
 for key,(kind,c) in resolved.items():
  field=required_versions.get(kind)
  if field and (type(c.get(field)) is not int or c[field]<0):findings.append(diag('shape','INVALID_RECORD_VERSION_TYPE','/dependencies/'+key+'/'+field,'nonnegative integer excluding bool',c.get(field)))
 e=resolved[q['eligibility']][1] if 'eligibility' in q else None
 if e:
  counts=collections.Counter(y['condition_id'] for y in e['conditions'])
  for i in range(1,11):
   cid=f'C{i:02d}';n=counts[cid]
   if n!=1:findings.append(diag('shape','MISSING_CONDITION_ID' if n==0 else 'DUPLICATE_CONDITION_ID','/eligibility/conditions/'+cid,1,n))
 if findings:return sorted(findings,key=lambda z:(z['path'],z['code']))
 if e:
  for c in e['conditions']:
   p=root/c['case']['file']['path'];used.add(p);source=next(y for y in json.loads(p.read_text())['cases'] if y['id']==c['case']['case_id']);version=source['complete_inputs'][c['condition_id']]['version']
   if c['value_version']!=version:findings.append(diag('source_versions','CONDITION_SOURCE_VERSION_MISMATCH','/eligibility/conditions/'+c['condition_id']+'/value_version',version,c['value_version']))
  if findings:return sorted(findings,key=lambda z:(z['path'],z['code']))
  for k,value in e['bindings'].items():
   if value!=q[k]:findings.append(diag('bindings','ELIGIBILITY_BINDING_MISMATCH','/eligibility/bindings/'+k,q[k],value))
 # The retained B1–B5 are checked for the finite controls as well.
 for record,field,key in [('event','branch','branch'),('opening','branch','branch'),('event','time','time'),('opening','chart','chart'),('method','authority','authority')]:
  actual=resolved[q[record]][1][field]
  if actual!=q[key]:findings.append(diag('bindings','BINDING_MISMATCH','/'+record+'/'+field,q[key],actual))
 return sorted(findings,key=lambda z:(z['path'],z['code']))
for x in f['cases']:
 ds=derive(x);derived.append({'id':x['id'],'derived_diagnostics':ds});check(x['id']+' derived diagnostics',ds==x['diagnostics'])
 r=x['response'];check(x['id']+' rejection outcome',r['status']=='rejected' and r['reason_codes']==[d['code'] for d in ds])
 check(x['id']+' all unvalidated outputs null',all(r[k] is None for k in ['request','assessment','diagnostic_journal','diagnostic_delta','receipt','observed_state']))
 check(x['id']+' no additional commit',r['commit_status']=='not_committed' and r['additional_commit'] is False)
 check(x['id']+' complete unchanged world',set(x['before'])=={'identity_index','committed_journals','selected_state','committed_receipts'} and x['before']==x['after'])
 check(x['id']+' no downstream processing',not any(x[k] for k in ['receipt_lookup_performed','freshness_checked','accounting_assessed']))
 check(x['id']+' status boundary',r['statuses']=={'structural_validity':'invalid','mathematical_status':'unresolved','computation_status':'not_computed','empirical_justification':'not_established','capability_status':'specified_only_no_runtime','accounting_validity':'not_assessed','human_acceptance':'pending'})
 sub=f['validated_records'][x['submission']];check(x['id']+' raw preservation',sub['content']=={'wire_format':'ASCII_JSON','raw_text':x['raw_text']})
 check(x['id']+' response identity',x['response_digest']==digest(x['domain'],'response',r))
 if x['id']!='J01':check(x['id']+' candidate fingerprint',x['claimed_request_digest']==digest(x['domain'],'request',strict(x['raw_text'])))
for k,row in f['validated_records'].items():
 check('diagnostic record '+k,k==digest(row['domain'],row['kind'],row['content']) and row['kind'] in {'submission','response'})
for c in f['controls']:
 check(c['id']+' validation',derive(c)==[])
 source=v if c['id']!='K03' else l;case=next(x for x in source['cases'] if x['id']==c['source']['case_id']);response=source['records'][case['response'] if c['id']!='K03' else case['responses'][-1]]['content']
 check(c['id']+' retained response',c['response']==response);check(c['id']+' unchanged state',c['before']==c['after'])
check('valid explicit unknown stays unresolved',v['records'][v['cases'][1]['assessment']]['content']['status']=='unresolved' and f['controls'][1]['response']['request'] is not None)
positive=f['controls'][2];corrupt=f['cases'][-1];receipt=positive['response']['receipt'];rp=l['records'][receipt]['content']
check('R06 exact committed comparator',positive['before']==l['cases'][-1]['after'] and positive['after']==l['cases'][-1]['after_lookup'])
check('corrupt replay same bytes and fingerprint',corrupt['raw_text']==positive['raw_text'] and corrupt['claimed_request_digest']==positive['claimed_request_digest']==rp['request'])
check('same existing receipt and complete world',corrupt['before']==positive['before'] and receipt in corrupt['before']['committed_receipts'])
check('lookup-first discriminant',receipt in corrupt['before']['identity_index'].values() and positive['response']['status']=='replayed' and corrupt['response']['receipt'] is None)
check('R01–R06 references preserved',f['preserved_predecessor_exchanges']==v['predecessor_exchanges'])
check('seventeen comparator outcomes retained',len(v['cases'])==17)
for item in inputs['predecessors']:
 p=root/item['path'];check('predecessor '+item['path'],p.is_file() and sha(p)==item['sha256'])
for p in [base/'accounting-integration-rejections-contract-v1.md',base/'accounting-integration-rejections-fixtures-v1.json',base/'accounting-integration-rejections-inputs-v1.json',base/'accounting-integration-fixtures-v2.json',base/'accounting-records-fixtures-v1.json']:used.add(p)
for item in f['imports']:
 p=root/item['path'];check('import '+item['path'],sha(p)==item['sha256'])
report={'schema_version':'accdsl.accounting.integration.rejections.verification.v1','passed':all(x['passed'] for x in checks),'checks':checks,'derived_cases':derived,'input_hashes':[{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in sorted(used)],'manifest':{'git_commit':'unavailable: project .git marker is not a usable repository','command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/accounting-integration-rejections-calculation-v1.py OUTPUT.json','actual_argv':sys.argv,'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'standard-library CPU only; no GPU framework imported or device detection','data_version':'pinned synthetic integration-v2 and retained records-v1','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan_file':'data/accounting-master/runs/20261005T164323-68702696/P16/approved-plan.json','result_file':'data/accounting-master/deliverables/P16/result.md','output_paths':[sys.argv[1]]},'limits':['Finite named predicates only; not an exhaustive integration validator or runtime module.','Processing flags describe specified behavior; no real receipt-store instrumentation.','Accounting and empirical validity and human acceptance are not established.']}
output=Path(sys.argv[1]);output.open('x').write(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failures':[x for x in checks if not x['passed']]}))
sys.exit(0 if report['passed'] else 1)
