"""Finite valid-publication conversion; expected outputs come from saved records."""
from copy import deepcopy
from pathlib import Path
import json
from successor import Auditor,PROFILE,HERE,ROOT,prior,n

class Migration:
 def __init__(self,template_id,name=None,times=None):
  self.old=n.Auditor(prior.ATT)
  self.template=deepcopy(next(e for e in self.old.packet['exchanges'] if e['id']==template_id and e['role']=='publication'))
  self.old.response(self.template)
  self.name=name or template_id;self.times=times or {}
  self.packet={'base_packet':str((prior.ATT/'portable-exchanges.json').relative_to(ROOT)),
   'base_packet_sha256':n.sha((prior.ATT/'portable-exchanges.json').read_bytes()),
   'profile':PROFILE,'evidence_mode':'bounded_documentary_profile_conversion',
   'records':{},'blobs':{},'aliases':{},'template_id':template_id,'times':self.times}
  self.a=Auditor(self.packet);self.mapping={};self.active=set()
  self.rq_old=self.template['request_ref'];self.sub_old=self.template['submission_ref']
  self.view_old=self.old.body(self.rq_old)['view_ref']
  self.evidence={h for h in self.old.closure([self.rq_old]) if self.old.reg[h]['kind']=='Evidence'}

 def blob(self,path,data=None):
  path=Path(path)
  if data is not None:
   path.parent.mkdir(exist_ok=True)
   if path.exists():assert path.read_bytes()==data,'existing_blob_differs'
   else:path.write_bytes(data)
  data=path.read_bytes();h=n.sha(data)
  meta={'path':str(path.relative_to(ROOT)),'byte_length':len(data)}
  self.packet['blobs'][h]=meta;self.a.blobs[h]=meta
  return {'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}

 def add(self,record):
  record=deepcopy(record);record['dependencies']=n.unique(n.references(record['body']))
  h=n.sha(('accdsl.portable.v1/'+record['schema']).encode()+bytes([0])+n.enc(record))
  n.need(h not in self.a.reg or self.a.reg[h]==record,'immutable_record_collision')
  self.a.reg[h]=record;self.packet['records'][h]=record;self.a.shape(record,h)
  return {'kind':record['kind'],'schema':record['schema'],'digest':h}

 def walk(self,value,derive=False):
  if isinstance(value,dict):
   if set(value)=={'kind','schema','digest'}:
    return self.derive(value) if derive else deepcopy(self.mapping.get(value['digest'],value))
   return {k:(n.unique(self.walk(v,derive)) if k=='dependency_refs' else self.walk(v,derive)) for k,v in value.items()}
  if isinstance(value,list):return [self.walk(x,derive) for x in value]
  return value

 def derive(self,ref):
  h=ref['digest']
  if h in self.mapping:return deepcopy(self.mapping[h])
  assert h not in self.active,'conversion_cycle';self.active.add(h)
  old=self.old.record(ref);record=deepcopy(old);kind=record['kind']
  record['body']=self.walk(record['body'],True);b=record['body']
  if kind=='SchemaLock':
   b['schema_blob']=self.blob(HERE/'record-schemas.json')
   b['semantic_contract_blob']=self.blob(HERE/'semantic-contract.md')
  if kind=='Profile':b['profile_id']=PROFILE
  if h==self.rq_old['digest']:
   b['workspace_key']='BankAssessmentExactTime-specification'
   b['request_id']=self.name
  if h==self.sub_old['digest']:
   rq=self.derive(self.rq_old)
   b['blob_ref']=self.blob(HERE/'request-bytes'/(self.name+'.json'),n.enc(self.a.record(rq)))
  if h in self.evidence:
   b.update({k:v for k,v in self.times.items() if k in ('available_at','ingested_at')})
  if h==self.view_old['digest']:
   b.update({k:v for k,v in self.times.items() if k in ('decision_at','system_asof')})
  record['schema']=self.a.schema['schema_ids'][kind]
  if record!=old:
   record['key']+='.exact-time.'+self.name;new=self.add(record)
  else:new=deepcopy(ref)
  self.mapping[h]=new;self.active.remove(h)
  if kind=='Profile':
   self.packet['aliases']['profile']=new;self.a.alias['profile']=new
  return deepcopy(new)

 def clone(self,ref,**changes):
  r=deepcopy(self.a.record(ref));r['key']+='.derived';r['body'].update(changes);return self.add(r)

 def submission(self,rq,suffix):
  blob=self.blob(HERE/'request-bytes'/(self.name+'.'+suffix+'.json'),n.enc(self.a.record(rq)))
  return self.clone(self.sub,blob_ref=blob)

 def build(self,reason=None):
  self.rq=self.derive(self.rq_old);self.sub=self.derive(self.sub_old)
  # Preserve the old published query and its immutable receipt beside the new one.
  before=deepcopy(self.template['world_after'])
  before['current_view_ref']=self.walk(before['current_view_ref'])
  before['accounting_heads']=self.walk(before['accounting_heads'])
  before['published_records']=sorted(set(before['published_records'])|set(self.a.closure([self.rq,self.sub])))
  self.before=before
  if reason is None:response=self.derive(self.template['response_ref'])
  else:
   r=deepcopy(self.old.record(self.template['response_ref']));b=self.walk(r['body'])
   b.update(disposition='rejected',coverage=None,unresolved=[],receipt_ref=None,commit_observation='not_committed')
   b['payload'].update(result_refs=[],additional_commit=False);b['statuses']['computation_status']='not_computed'
   b['diagnostics']=[dict(code=reason,stage='query_binding_or_validation',record_ref=None,source_locator=None,
    field_path='arguments',affected_query_branch_ids=[],dependency_path=[],observed=reason,expected_rule=PROFILE,
    retry_advice='repair_named_input_or_retry_original_bytes',blocking_diagnostic_ids=[])]
   r.update(schema=self.a.schema['schema_ids']['OperationResult'],key=r['key']+'.exact-time.'+self.name,body=b)
   response=self.add(r)
  after=deepcopy(before);body=self.a.body(response)
  if reason is None:
   after['published_records']=sorted(set(after['published_records'])|set(self.a.closure([response])))
   after['query_index'][self.a.identity(self.rq)]={'request_digest':self.rq['digest'],'response_ref':response,
    'output_ref':body['payload']['result_refs'][0],'receipt_ref':body['receipt_ref']}
  self.exchange={'id':self.name,'role':'refusal' if reason else 'publication','request_ref':self.rq,
   'submission_ref':self.sub,'response_ref':response,'world_before':before,'world_after':after}
  self.packet['exchange']=self.exchange;self.packet['expected_request_result']=reason or 'accepted'
  return self.exchange

 def replay(self):
  ex=deepcopy(self.exchange);body=deepcopy(self.a.body(ex['response_ref']))
  body['disposition']='replayed';body['payload']['additional_commit']=False
  ex.update(id=self.name+'.replay',role='exact_replay',response_ref=self.clone(ex['response_ref'],**body),
   world_before=deepcopy(ex['world_after']))
  return ex

 def save(self):
  folder=HERE/'examples';folder.mkdir(exist_ok=True)
  self.packet['reference_map']=self.mapping
  (folder/(self.name+'.json')).write_text(json.dumps(self.packet,indent=2)+'\n')
