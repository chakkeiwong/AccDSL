"""Bind each synthetic occurrence to its actual lexical fixture bytes."""
from pathlib import Path
import copy,json,hashlib,shutil
OUT=Path(__file__).resolve().parent
assert not (OUT/'exchanges-before-closure.json').exists()
shutil.copy2(OUT/'exchanges.json',OUT/'exchanges-before-closure.json')
cases=json.loads((OUT/'exchanges.json').read_text())
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
for c in cases:
 req=c['request']
 if c['case_id']=='A02':req['facts'][0]['raw']='';c['expected']['records'][0]['raw']=''
 body='Synthetic documentary source; no issuer or parser output.\n'
 for f in req['facts']:
  row={k:v for k,v in f.items() if k not in ['source_uri','source_span']}
  start=len(body);line=canonical(row);body+=line+'\n';f['source_span']=[start,start+len(line)]
 body+=canonical({'contexts':req['contexts'],'units':req['units']})+'\n'
 if req['resources']:
  req['resources'][0]['body']=body;req['resources'][0]['sha256']=sha(body)
  if c['case_id']=='A05':req['resources'][0]['body']+='unexpected modification\n'
 for rec in c['expected']['records']:
  f=next(x for x in req['facts'] if x['occurrence']==rec['occurrence'])
  rec['source_uri']=f['source_uri'];rec['source_span']=f['source_span'];rec['concept']=f['concept']
  rec['transform']=f['transform'];rec['scale']=f['scale'];rec['precision']=f['precision']
 if c['case_id']=='A10':
  r=copy.deepcopy(req);r.pop('control');req['control']['prior_request_digest']=sha(canonical(r))
(OUT/'exchanges.json').write_text(json.dumps(cases,indent=2)+'\n')
def obj(props):return {'type':'object','additionalProperties':False,'required':list(props),'properties':props}
def arr(item):return {'type':'array','items':item}
string={'type':'string'};nullable={'type':['string','null']};integer={'type':'integer'}
span={'type':'array','items':{'type':'integer','minimum':0},'minItems':2,'maxItems':2}
dimension=obj({'axis':string,'kind':{'enum':['typed','explicit']},'value':nullable})
context=obj({'id':string,'entity':string,'perimeter':string,'period_kind':{'const':'duration'},'start':string,'end_exclusive':string,'dimensions':arr(dimension)})
unit=obj({'id':string,'measure':string})
fact=obj({'occurrence':string,'source_uri':string,'source_span':span,'concept':string,'raw':string,'transform':string,'scale':integer,'precision':integer,'context_id':string,'unit_id':string,'nil':{'type':'boolean'}})
record=obj({k:fact['properties'][k] for k in ['occurrence','context_id','unit_id','raw','nil','source_uri','source_span','concept','transform','scale','precision']}|{'value':nullable,'review':{'const':'proposed'}})
req=obj({'id':string,'selection_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'resources':arr(obj({'uri':string,'body':string,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})),'required_uris':arr(string),'contexts':arr(context),'units':arr(unit),'transforms':arr(string),'facts':arr(fact),'control':obj({'cancel_after':{'type':['integer','null'],'minimum':0},'prior_request_digest':nullable,'prior_receipt':nullable})})
expected=obj({'status':{'enum':['proposed','unresolved','partial','conflict']},'records':arr(record),'unresolved':arr(string),'diagnostics':arr(string),'accounting_committed':{'const':False},'package_complete':{'const':False}})
schema=obj({'schema':{'const':'DocumentaryAdapterExchange/1'},'case_id':string,'evidence_class':{'const':'authored_expected_not_runtime'},'request':req,'expected':expected})
schema.update({'$schema':'https://json-schema.org/draft/2020-12/schema','title':'DocumentaryAdapterExchange/1'})
(OUT/'exchange-envelope.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
print(json.dumps({'cases':len(cases),'nested_schema_closed':True,'source_spans_bound':True,'nil_raw_preserved_empty':True}))
