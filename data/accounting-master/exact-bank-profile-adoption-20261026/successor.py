"""Explicit documentary successor; native financial methods remain pinned."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'exact-native-timing-20261026'))
import checker as prior
import adapted_methods
n=prior.native
PROFILE='BankAssessmentExactTime/1'

class Auditor(prior.Auditor):
 def __init__(self,packet):
  super().__init__(prior.ATT)
  self.legacy_validators=self.validators;self.legacy_schema=self.schema
  self.legacy_alias=deepcopy(self.alias);self.legacy_profile=deepcopy(self.alias['profile'])
  self.schema=n.decode((HERE/'record-schemas.json').read_bytes())
  self.validators={k:n.Draft202012Validator(v,format_checker=n.FormatChecker()) for k,v in self.schema['$defs'].items()}
  for h,record in packet['records'].items():
   n.need(h not in self.reg or self.reg[h]==record,'immutable_record_collision')
  self.reg.update(deepcopy(packet['records']));self.blobs.update(deepcopy(packet['blobs']))
  self.alias=deepcopy(self.alias);self.alias.update(deepcopy(packet['aliases']))
  self.packet=packet

 def shape(self,record,digest=None):
  # Old immutable records remain independently shape-checked as old records.
  kind=record['kind'];schema=record['schema']
  if kind in self.legacy_schema['schema_ids'] and schema==self.legacy_schema['schema_ids'][kind] and schema!=self.schema['schema_ids'][kind]:
   selected_schema,selected_validators=self.schema,self.validators
   try:
    self.schema,self.validators=self.legacy_schema,self.legacy_validators
    return n.Auditor.shape(self,record,digest)
   finally:self.schema,self.validators=selected_schema,selected_validators
  return n.Auditor.shape(self,record,digest)

 def profile_contract(self):
  record=self.record(self.alias['profile']);self.shape(record,self.alias['profile']['digest']);p=record['body']
  n.need(record['schema']==self.schema['schema_ids']['Profile'] and p['profile_id']==PROFILE,'successor_profile_mismatch')
  n.need(p['operations']==list(n.OPS) and p['accounting_effect']=='none' and p['execution_mode']=='specification_example','successor_profile_semantics')
  lock_record=self.record(p['schema_lock_ref']);self.shape(lock_record,p['schema_lock_ref']['digest']);lock=lock_record['body']
  n.need(self.blob_bytes(lock['schema_blob'])==(HERE/'record-schemas.json').read_bytes(),'successor_schema_lock_mismatch')
  n.need(self.blob_bytes(lock['semantic_contract_blob'])==(HERE/'semantic-contract.md').read_bytes(),'successor_contract_lock_mismatch')

 def request(self,rq,sub,w):
  self.profile_contract();record=self.record(rq);self.shape(record,rq['digest'])
  n.need(record['schema']==self.schema['schema_ids']['OperationRequest'],'successor_request_schema')
  n.need(record['body']['profile_ref']==self.alias['profile'],'successor_request_profile')
  sig=self.record(record['body']['signature_ref']);self.shape(sig,record['body']['signature_ref']['digest'])
  n.need(sig['schema']==self.schema['schema_ids']['OperationSignature'],'successor_signature_schema')
  r=record['body'];s=sig['body']
  n.need(r['operation'] in n.OPS and r['arguments']['tag']==r['operation'],'operation_tag_mismatch')
  n.need(s['profile_ref']==r['profile_ref'] and s['operation']==r['operation'] and s['arguments_definition']=='Arguments.'+r['operation'] and s['effects']=='read','signature_mismatch')
  expected={n.OPS[0]:'RegulatoryAssessment',n.OPS[1]:'LossQueryResult',n.OPS[2]:'PolicyQueryResult'}
  n.need(s['payload_kinds']==[expected[r['operation']]],'signature_mismatch')
  self.shape(self.record(sub),sub['digest'])
  return super().request(rq,sub,w)

 def response(self,exchange):
  for h in self.closure([exchange['response_ref']]):self.shape(self.reg[h],h)
  return super().response(exchange)

 expected_capital=adapted_methods.expected_capital
 expected_loss=adapted_methods.expected_loss
