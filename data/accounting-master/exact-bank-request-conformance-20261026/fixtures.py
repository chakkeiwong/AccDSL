"""Derive complete finite requests without using the tested output calculator."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'exact-native-timing-20261026'))
import checker as timing
n=timing.native

class Fixture:
 def __init__(self,name,times):
  self.name=name;self.times=times;self.a=timing.Auditor(timing.ATT)
  self.original=deepcopy(self.a.reg);self.records={};self.mapping={};self.blobs={}
  self.template=deepcopy(next(e for e in self.a.packet['exchanges'] if e['id']=='capital.final'))
  request=self.a.body(self.template['request_ref'])
  self.view_digest=request['view_ref']['digest']
  self.evidence_digest=self.a.body(request['view_ref'])['evidence_refs'][0]['digest']
  self.request_digest=self.template['request_ref']['digest']

 def add(self,record):
  record=deepcopy(record);record['dependencies']=n.unique(n.references(record['body']))
  h=n.sha(('accdsl.portable.v1/'+record['schema']).encode()+bytes([0])+n.enc(record))
  ref={'kind':record['kind'],'schema':record['schema'],'digest':h}
  self.a.reg[h]=record;self.records[h]=record
  self.a.shape(record,h)
  return ref

 def derive(self,old_ref):
  h=old_ref['digest']
  if h in self.mapping:return self.mapping[h]
  record=deepcopy(self.original[h]);record['body']=self.walk(record['body'],derive=True)
  if h==self.evidence_digest:
   record['body'].update({k:v for k,v in self.times.items() if k in ['available_at','ingested_at']})
  if h==self.view_digest:
   record['body'].update({k:v for k,v in self.times.items() if k in ['decision_at','system_asof']})
  if h==self.request_digest:record['body']['request_id']='exact-timing.'+self.name
  if record['body']==self.original[h]['body']:
   self.mapping[h]=deepcopy(old_ref);return deepcopy(old_ref)
  record['key']+='.'+self.name
  self.mapping[h]=self.add(record);return self.mapping[h]

 def walk(self,value,derive=False):
  if isinstance(value,dict):
   if set(value)=={'kind','schema','digest'}:
    return self.derive(value) if derive else deepcopy(self.mapping.get(value['digest'],value))
   return {k:self.walk(v,derive) for k,v in value.items()}
  if isinstance(value,list):return [self.walk(v,derive) for v in value]
  return value

 def clone(self,ref,**changes):
  rec=deepcopy(self.a.record(ref));rec['key']+='.'+self.name+'.derived'
  rec['body'].update(changes);return self.add(rec)

 def submission(self,rq,suffix=''):
  data=n.enc(self.a.record(rq));h=n.sha(data)
  path=HERE/'request-bytes'/(self.name+suffix+'.json');path.parent.mkdir(exist_ok=True);path.write_bytes(data)
  blob={'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
  meta={'path':str(path.relative_to(ROOT)),'byte_length':len(data)}
  self.a.blobs[h]=meta;self.blobs[h]=meta
  return self.clone(self.template['submission_ref'],blob_ref=blob)

 def base_request(self):
  rq=self.derive(self.template['request_ref']);sub=self.submission(rq)
  before=self.walk(self.template['world_before'])
  before['published_records']=sorted({self.mapping.get(h,{'digest':h})['digest'] for h in before['published_records']})
  assert not before['query_index']
  self.rq,self.sub,self.before=rq,sub,before
  return rq,sub,before

 def response(self,reason=None):
  rq,sub,before=self.rq,self.sub,self.before
  original=self.a.body(self.template['response_ref']);body=self.walk(deepcopy(original))
  body.update(request_ref=rq,submission_ref=sub,input_view_ref=self.a.body(rq)['view_ref'])
  if reason:
   body.update(disposition='rejected',coverage=None,unresolved=[],receipt_ref=None,commit_observation='not_committed')
   body['payload'].update(result_refs=[],additional_commit=False)
   body['statuses'].update(computation_status='not_computed')
   body['diagnostics']=[dict(code=reason,stage='query_binding_or_validation',record_ref=None,source_locator=None,
    field_path='arguments',affected_query_branch_ids=[],dependency_path=[],observed=reason,
    expected_rule='ExactBankInformation/1',retry_advice='repair_named_input_or_retry_original_bytes',blocking_diagnostic_ids=[])]
  else:
   old_out=original['payload']['result_refs'][0]
   # Only dependency references change; numeric expectations come from the saved output.
   output=deepcopy(self.original[old_out['digest']]);output['body']=self.walk(output['body']);output['key']+='.'+self.name
   # These fields are native canonical sets, not chronological sequences.
   for group in ['amounts','ratios']:
    for value in output['body'][group].values():value['dependency_refs']=n.unique(value['dependency_refs'])
   outref=self.add(output)
   receipt=self.clone(original['receipt_ref'],request_ref=rq,output_ref=outref)
   domain=self.clone(original['coverage']['domain_ref'],request_ref=rq)
   region=self.clone(original['coverage']['completed'][0],domain_ref=domain)
   body['payload'].update(result_refs=[outref],additional_commit=True)
   body['receipt_ref']=receipt;body['coverage'].update(domain_ref=domain,completed=[region])
  rec=deepcopy(self.original[self.template['response_ref']['digest']]);rec['key']+='.'+self.name;rec['body']=body
  response=self.add(rec);after=deepcopy(before)
  if not reason:
   after['published_records']=sorted(set(after['published_records'])|set(self.a.closure([response])))
   after['query_index'][self.a.identity(rq)]={'request_digest':rq['digest'],'response_ref':response,
    'output_ref':body['payload']['result_refs'][0],'receipt_ref':body['receipt_ref']}
  return dict(id=self.name,role='refusal' if reason else 'publication',request_ref=rq,submission_ref=sub,
   response_ref=response,world_before=deepcopy(before),world_after=after)

 def original_auditor(self):
  old=n.Auditor(timing.ATT);old.reg.update(deepcopy(self.records));old.blobs.update(deepcopy(self.blobs));return old
