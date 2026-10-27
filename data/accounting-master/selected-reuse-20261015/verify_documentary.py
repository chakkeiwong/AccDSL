from pathlib import Path
from decimal import Decimal
import json,hashlib,subprocess,copy,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
def validate(x,s,path):
 if 'const' in s:ck(path+'/const',x==s['const'])
 if 'enum' in s:ck(path+'/enum',x in s['enum'])
 typ=s.get('type');types=typ if isinstance(typ,list) else [typ]
 kinds={'object':lambda z:isinstance(z,dict),'array':lambda z:isinstance(z,list),'string':lambda z:isinstance(z,str),'integer':lambda z:type(z)is int,'boolean':lambda z:type(z)is bool,'null':lambda z:z is None}
 if typ is not None:ck(path+'/type',any(kinds[t](x) for t in types if t in kinds))
 if isinstance(x,dict) and 'properties' in s:
  ck(path+'/closed',set(x)==set(s['required'])==set(s['properties']))
  for k,v in x.items():validate(v,s['properties'][k],path+'/'+k)
 if isinstance(x,list):
  ck(path+'/min',len(x)>=s.get('minItems',0));ck(path+'/max',len(x)<=s.get('maxItems',len(x)))
  for i,v in enumerate(x):validate(v,s['items'],path+'/'+str(i))
 if 'pattern' in s:ck(path+'/pattern',bool(re.fullmatch(s['pattern'],x)))
 if 'minimum' in s and x is not None:ck(path+'/minimum',x>=s['minimum'])
selection=json.loads((OUT/'source-selection.json').read_text())
for p in selection['source_pins']:ck('source/'+p['path'],sha(ROOT/p['path'])==p['sha256'])
ck('no-false-environment-lock',selection['environment_lock'] is None and selection['runtime_admission']=='held')
schema=json.loads((OUT/'exchange-envelope.schema.json').read_text());cases=json.loads((OUT/'exchanges.json').read_text())
for c in cases:
 name=c['case_id'];validate(c,schema,name)
 req=c['request'];ck(name+'/selection',req['selection_sha256']==sha(OUT/'source-selection.json'))
 rs={r['uri']:r for r in req['resources']};cs={r['id']:r for r in req['contexts']};us={r['id']:r for r in req['units']};records=[];unresolved=[];diagnostics=[];status='proposed'
 prior=req['control']['prior_request_digest'];r=copy.deepcopy(req);r.pop('control');identity=digest(json.dumps(r,sort_keys=True,separators=(',',':')))
 if prior is not None and prior!=identity:
  status='conflict';unresolved=[f['occurrence'] for f in req['facts']];diagnostics=['request_identity_conflict']
 else:
  resource_error='unresolved_dependency' if any(u not in rs for u in req['required_uris']) else 'resource_hash_mismatch' if any(digest(z['body'])!=z['sha256'] for z in rs.values()) else None
  for i,f in enumerate(req['facts']):
   error=resource_error
   if req['control']['cancel_after'] is not None and i>=req['control']['cancel_after']:
    error='cancelled';status='partial'
   elif not error:
    resource=rs.get(f['source_uri'])
    if resource is None:error='unresolved_dependency'
    else:
     a,b=f['source_span'];literal=json.loads(resource['body'][a:b]);ck(name+'/span/'+f['occurrence'],literal=={k:v for k,v in f.items() if k not in ['source_uri','source_span']})
    if not error and f['transform'] not in req['transforms']:error='unsupported_transform'
    if not error and f['context_id'] not in cs:error='missing_context'
    if not error and f['unit_id'] not in us:error='missing_unit'
    if not error and any(d['kind']=='typed' and d['value'] is None for d in cs[f['context_id']]['dimensions']):error='missing_typed_dimension'
   if error:
    unresolved.append(f['occurrence'])
    if error not in diagnostics:diagnostics.append(error)
    continue
   amount=None if f['nil'] else format(Decimal(f['raw'].replace(',',''))*(Decimal(10)**f['scale']),'f')
   records.append({k:f[k] for k in ['occurrence','context_id','unit_id','raw','nil','source_uri','source_span','concept','transform','scale','precision']}|{'value':amount,'review':'proposed'})
  if status!='partial' and unresolved:status='partial' if records else 'unresolved'
  if prior==identity:diagnostics.append('idempotent_replay')
 actual={'status':status,'records':records,'unresolved':unresolved,'diagnostics':diagnostics,'accounting_committed':False,'package_complete':False}
 ck(name+'/independent-expectation',actual==c['expected'])
 ck(name+'/denominator',len(records)+len(unresolved)==len(req['facts']))
ck('all-cases-distinct',len({c['case_id'] for c in cases})==11)
base=json.loads((OUT/'baseline.json').read_text());ck('candidate-preserved',sha(ROOT/base['candidate']/'accounting-product-proposal.pdf')==base['pdf_sha256'])
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'cases':len(cases),'checks':checks,'meaning':'Closed documentary shape, retained source identity and independently computed fixture expectations; no upstream runtime executed'}
(OUT/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}));assert out['passed'],[x for x in checks if not x['passed']]
