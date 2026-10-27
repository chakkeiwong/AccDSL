"""Exact providers for adopted profiles; frozen legacy readers remain intact."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MASTER=HERE.parent
sys.path.insert(0,str(MASTER/'profile-composition-boundary-20261026'))
import composition as old
from schema_descriptor import SchemaBoundDescriptor
from composition_assess import assess

def sha(path):return sha256(path.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def isolated(name,folder):
 names=['financial_checks','source_policy','native','adapted_protocol','checker','projection','adapted_methods']
 saved={key:sys.modules.get(key) for key in names};paths=list(sys.path)
 try:
  for key in names:sys.modules.pop(key,None)
  sys.path.insert(0,str(folder))
  return load(name,folder/'successor.py')
 finally:
  sys.path[:]=paths
  for key,value in saved.items():
   if value is None:sys.modules.pop(key,None)
   else:sys.modules[key]=value

insurance=isolated('adopted_insurer_native',MASTER/'insurance-identity-adoption-20261026')
bank=isolated('adopted_bank_native',MASTER/'exact-bank-profile-adoption-20261026')

class AdoptedReader(SchemaBoundDescriptor):
 def __init__(self,path,kind):
  self.path=path;self.kind=kind;raw=json.loads(path.read_text())
  self.native=insurance.Auditor(raw) if kind=='insurance' else bank.Auditor(raw)
  self.raw=raw
  packet={'record_registry':self.native.reg,'aliases':self.native.alias}
  profile=self.native.alias['profile']
  name='insurance' if kind=='insurance' else 'bank-assessment'
  entry={'name':name,'packet':str(path.relative_to(ROOT)),'profile_ref':profile,
         'profile_id':self.native.body(profile)['profile_id'],'files':{str(path.relative_to(ROOT)):sha(path)}}
  super().__init__(packet,entry)
  self.config=deepcopy(self.config)
  if kind=='insurance':self.config['fields'].add('identity_profile_ref')
  self.schema_ids=deepcopy(self.native.schema['schema_ids'])
  self.exchanges={};self.origins={};self.valid_exchanges=set()
  if kind=='insurance':
   for i,exchange in enumerate(raw['exchanges']):
    key=f'exchange.{i:04d}.'+exchange['id']
    self.exchanges[key]=exchange;self.origins[id(exchange)]={'kind':'exchange','ordinal':i,'label':exchange['id']}
   # Expose original lost acknowledgements as observations, without giving the
   # caller either hidden world's commit knowledge.
   by_label={e['id']:e for e in raw['exchanges'][:672]}
   for i,crash in enumerate(self.native.p['crash_worlds']):
    exchange=deepcopy(by_label[crash['recovery_id']])
    exchange['response_ref']=crash['observation_ref']
    key=f'transport.{i:04d}.'+crash['id']
    self.exchanges[key]=exchange;self.origins[id(exchange)]={'kind':'native_transport','ordinal':i,'label':crash['id']}
  else:
   for field in ('exchange','replay'):
    if field in raw:
     exchange=raw[field];self.exchanges[field]=exchange
     self.origins[id(exchange)]={'kind':field,'label':exchange['id']}

 def schema_id(self,kind):
  old.need(kind in self.schema_ids,'unsupported_record_kind')
  return self.schema_ids[kind]

 def legacy_key(self,request):
  return old.canonical(self.pair(request)).decode()

 def describe(self,exchange):
  origin=self.origins.get(id(exchange))
  old.need(origin is not None,'unbound_provider_exchange')
  signature=sha256(old.canonical(exchange)).hexdigest()
  if signature not in self.valid_exchanges:
   if self.kind=='insurance':
    self.native.profile_contract(exchange['world_before'])
    self.native.profile_contract(exchange['world_after'])
   if exchange['response_ref']['kind']=='TransportObservation':
    old.need(self.kind=='insurance','unsupported_transport_provider')
    self.native.profile_contract(exchange['world_before'])
    for h in self.native.closure([exchange['request_ref'],exchange['submission_ref'],exchange['response_ref']]):
     self.native.shape(self.native.reg[h],h)
   elif self.kind=='insurance':self.native.exchange(exchange)
   else:self.native.response(exchange)
   self.valid_exchanges.add(signature)
  result=super().describe(exchange)
  result['schema']='PublicationEffects/2'
  result['execution_binding']={
    'financial_profile_ref':deepcopy(self.profile_ref),
    'identity_policy_ref':deepcopy(self.native.policy_ref) if self.kind=='insurance' else None,
    'schema_ids':deepcopy(self.schema_ids),
    'source_origin':deepcopy(origin),
    'native_checker':'InsuranceComponentsIdentity/1' if self.kind=='insurance' else 'BankAssessmentExactTime/1'}
  return result

class Library(old.Library):
 def __init__(self):
  lock=json.loads((HERE/'source-lock.json').read_text())
  for path,h in lock.items():old.need(sha(ROOT/path)==h,'source_lock_changed:'+path)
  super().__init__()
  self.adopted={};self.current_bank=None
  insurer=MASTER/'insurance-identity-adoption-20261026/portable-successor.json'
  self.insurance_hash=sha(insurer);reader=AdoptedReader(insurer,'insurance')
  self.adopted[self.insurance_hash]=dict(path=insurer,kind='insurance')
  self.readers[self.insurance_hash]=reader;self.exchanges[self.insurance_hash]=reader.exchanges
  self.entries[self.insurance_hash]={'name':'insurance-identity','packet':str(insurer.relative_to(ROOT))}
  self.bank_hashes={}
  for path in sorted((MASTER/'exact-bank-profile-adoption-20261026/examples').glob('*.json')):
   h=sha(path);self.adopted[h]=dict(path=path,kind='bank')
   self.entries[h]={'name':'bank-exact-time','packet':str(path.relative_to(ROOT))}
   self.bank_hashes[path.stem]=h

 def select(self,stage):
  key=stage['packet_sha256']
  if key not in self.adopted:return super().select(stage)
  spec=self.adopted[key]
  if spec['kind']=='insurance':reader=self.readers[key]
  else:
   if self.current_bank is None or self.current_bank[0]!=key:
    old.need(sha(spec['path'])==key,'source_packet_changed')
    self.current_bank=(key,AdoptedReader(spec['path'],'bank'))
   reader=self.current_bank[1]
  old.need(stage['exchange_id'] in reader.exchanges,'unresolved_exchange_import')
  exchange=reader.exchanges[stage['exchange_id']]
  return reader,exchange,reader.describe(exchange)

def compile_text(source,library):
 plan,spans=old.parse(source)
 return {'plan':plan,'source_map':spans,'assessment':assess(plan,library)}
