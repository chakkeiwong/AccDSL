"""Independent documentary audit; never imports builder or authored expectations."""
from copy import deepcopy
from datetime import date,datetime,timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from jsonschema import Draft202012Validator,FormatChecker
from financial_checks import evaluate,num,q,Refusal as FinancialRefusal
from source_policy import sources,METHOD_SOURCES
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OPS=('group.component.commit@1','group.component.report@1')
PREFIX='accdsl.group-components.'
class Refusal(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def need(ok,code):
 if not ok:raise Refusal(code)
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(v):return hashlib.sha256(v).hexdigest()
def references(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from references(x)
 elif isinstance(v,list):
  for x in v:yield from references(x)
def blobs(v):
 if isinstance(v,dict):
  if set(v)=={'kind','algorithm','digest','byte_length'}:yield v
  else:
   for x in v.values():yield from blobs(x)
 elif isinstance(v,list):
  for x in v:yield from blobs(x)
def unique(rs):return [r for k,r in sorted({enc(r):r for r in rs}.items())]
def pairs(items):
 d={}
 for k,v in items:need(k not in d,'duplicate_key');d[k]=v
 return d
def nofloat(v):raise Refusal('float_forbidden')
def nonfinite(v):raise Refusal('nonfinite_forbidden')
def decode(raw):
 try:return json.loads(raw,object_pairs_hook=pairs,parse_float=nofloat,parse_constant=nonfinite)
 except (ValueError,UnicodeError):raise Refusal('invalid_json')
def hygiene(v):
 need(not isinstance(v,float),'float_forbidden')
 if isinstance(v,dict):
  if set(v)=={'n','d'}:
   try:num(v)
   except (ValueError,ZeroDivisionError,TypeError,FinancialRefusal):raise Refusal('noncanonical_rational')
  for x in v.values():hygiene(x)
 elif isinstance(v,list):
  for x in v:hygiene(x)
def instant(v):return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
def day(v):return date.fromisoformat(v)
def head(sr,body):
 s=body(sr);return dict(owner_key=s['owner_key'],state_ref=sr,generation=s['sequence'])
class Auditor:
 def __init__(self,attempt):
  self.attempt=attempt;self.packet=decode((attempt/'portable-exchanges.json').read_bytes())
  self.reg=self.packet['record_registry'];self.alias=self.packet['aliases'];self.blobs=self.packet['blobs']
  self.schema=decode((attempt/'record-schemas.json').read_bytes())
  self.validators={k:Draft202012Validator(v,format_checker=FormatChecker()) for k,v in self.schema['$defs'].items()}
  self.checks=[]
 def audit(self,label,fn):
  try:fn();self.checks.append(dict(check=label,passed=True))
  except Exception as e:self.checks.append(dict(check=label,passed=False,diagnostic=getattr(e,'code',type(e).__name__),detail=str(e)[:300]))
 def record(self,r):
  need(r['digest'] in self.reg,'missing_reference');x=self.reg[r['digest']]
  need(x['kind']==r['kind'] and x['schema']==r['schema'],'reference_type_mismatch');return x
 def body(self,r):return self.record(r)['body']
 def closure(self,roots):
  seen=set();active=set()
  def visit(r):
   d=r['digest']
   if d in seen:return
   need(d not in active,'dependency_cycle');active.add(d)
   for x in self.record(r)['dependencies']:visit(x)
   active.remove(d);seen.add(d)
  for r in roots:visit(r)
  return sorted(seen)
 def blob_bytes(self,b):
  need(b['digest'] in self.blobs,'missing_blob');meta=self.blobs[b['digest']];p=(ROOT/meta['path']).resolve()
  need(p.is_relative_to(ROOT),'blob_path_scope');raw=p.read_bytes()
  need(sha(raw)==b['digest'] and len(raw)==b['byte_length']==meta['byte_length'],'blob_hash_mismatch');return raw
 def shape(self,record,digest=None):
  need(set(record)=={'kind','schema','key','revision','body','dependencies'},'closed_record_shape')
  k=record['kind'];need(k in self.validators,'closed_record_shape')
  need(record['schema']==self.schema['schema_ids'][k]==PREFIX+k.lower()+'.v1','record_schema_mismatch')
  need(type(record['revision']) is int and record['revision']==0 and isinstance(record['key'],str) and bool(record['key']),'closed_record_shape')
  hygiene(record);need(not list(self.validators[k].iter_errors(record['body'])),'closed_record_shape')
  need(record['dependencies']==unique(references(record['body'])),'dependency_mismatch')
  for r in references(record['body']):self.record(r)
  for b in blobs(record['body']):self.blob_bytes(b)
  if digest:need(sha(('accdsl.portable.v1/'+record['schema']).encode()+b'\0'+enc(record))==digest,'record_digest_mismatch')
 def preservation(self):
  raw=(HERE/'predecessor-lock.json').read_bytes()
  need(sha(raw)=='17c5bed216c11851c5102b43c06338e8e0414f727b1eb2e591cc555e90979ad4','predecessor_lock_changed')
  lock=decode(raw);original=ROOT/lock['original_protection_manifest']
  need(sha(original.read_bytes())==lock['original_manifest_sha256'],'protection_manifest_changed')
  for row in decode(original.read_bytes())['files']:
   need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'protected_original_changed:'+row['path'])
   need(sha((ROOT/row['snapshot']).read_bytes())==row['sha256'],'protected_snapshot_changed:'+row['path'])
  for row in lock['predecessor_files']:need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'predecessor_changed:'+row['path'])
  need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==lock['git_commit'],'head_changed')
  idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
  need(sha(idx)==lock['index_sha256'] and len(idx.splitlines())==lock['index_entries']==100,'staged_index_changed')
 def source_checks(self):
  for s in sources():
   b=self.body(self.alias['source.'+s['key']])
   need(b['source_key']==s['key'] and b['anchors']==s['anchors'],'source_anchor_binding')
   for field,path,digest in [('raw_blob',s['path'],s['sha256']),('text_blob',s['text_path'],s['text_sha256'])]:
    need(self.blob_bytes(b[field])==(ROOT/path).read_bytes() and b[field]['digest']==digest,'source_bytes_binding')
   need([self.blob_bytes(x) for x in b['method_blobs']]==[(ROOT/p).read_bytes() for p in s['methods']],'method_binding')
  profile=self.body(self.alias['profile']);lock=self.body(profile['schema_lock_ref'])
  need(profile['profile_id']=='GroupComponents/1' and profile['operations']==list(OPS),'profile_mismatch')
  need(self.blob_bytes(lock['schema_blob'])==(self.attempt/'record-schemas.json').read_bytes(),'schema_lock_mismatch')
  need(self.blob_bytes(lock['semantic_contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'contract_lock_mismatch')
  for name,row in self.packet['input_snapshots'].items():
   need(sha((self.attempt/'inputs'/name).read_bytes())==row['sha256']==sha((ROOT/row['path']).read_bytes()),'input_snapshot_changed')
  need(self.blob_bytes(self.packet['predecessor_lock_blob'])==(HERE/'predecessor-lock.json').read_bytes(),'lock_binding')
 def information(self,root,view_ref):
  v=self.body(view_ref);allowed={enc(r) for r in v['evidence_refs']}
  need(len(allowed)==len(v['evidence_refs']),'duplicate_evidence')
  for d in self.closure([root]):
   r=self.reg[d]
   if r['kind']!='Evidence':continue
   rr=dict(kind='Evidence',schema=r['schema'],digest=d);e=r['body']
   need(enc(rr) in allowed,'evidence_not_in_view')
   need(instant(e['available_at'])<=instant(v['decision_at']),'later_information')
   need(instant(e['ingested_at'])<=instant(v['system_asof']),'later_ingestion')
   need(day(e['measurement_asof'])<=instant(v['decision_at']).date(),'future_measurement')
 def basis(self,br):
  b=self.body(br);x=self.body(b['input_ref']);m=x['method_id'];ctx=self.body(b['context_ref']);definition=self.body(b['method_ref'])
  need(definition['method_id']==m,'method_mismatch')
  need(definition['source_refs']==[self.alias['source.'+k] for k in METHOD_SOURCES[m]],'method_source_binding')
  need(self.blob_bytes(definition['contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'method_contract_binding')
  rules=self.body(b['rule_ref'])
  need(rules['source_refs']==[self.alias['source.'+s['key']] for s in sources()] and set(rules['method_ids'])==set(METHOD_SOURCES) and len(rules['method_ids'])==12,'rule_source_binding')
  self.information(br,b['view_ref'])
  evidence=self.body(b['facts_evidence_ref']);facts=decode(self.blob_bytes(evidence['content_blob']))
  admitted=deepcopy(x)
  if m=='exchangeability.assess@1':
   for field in ('subsequent_rate','subsequent_date'):admitted.pop(field)
  need(facts['facts']==admitted,'fact_evidence_binding')
  need(evidence['measurement_asof']==b['measurement_date'],'measurement_evidence_date')
  books=[self.body(r) for r in b['legal_book_refs']]
  need(len(books)==2 and len({v['owner_key'] for v in books})==2 and [v['entity_id'] for v in books]==['Parent','Subsidiary'],'legal_book_identity')
  need([v['balances'] for v in books]==facts['legal_balances'],'legal_evidence_binding')
  for v in books:
   need(v['context_ref']==b['context_ref'] and v['branch_id']==ctx['branch_id'] and v['currency']==ctx['functional_currency'],'book_context_binding')
   need(v['as_of_date']==b['measurement_date'] and v['evidence_ref']==b['facts_evidence_ref'],'legal_book_date_binding')
   need(v['owner_key']=='Legal/'+ctx['branch_id']+'/'+v['entity_id'],'legal_book_owner_binding')
   need(sum((num(t) for t in v['balances'].values()),F(0))==0,'legal_book_unbalanced')
  ctrl=self.body(b['control_ref'])
  need(ctrl['context_ref']==b['context_ref'] and ctrl['entity_refs']==b['legal_book_refs'],'control_entity_binding')
  need({k:ctrl[k] for k in ('control_start','control_end_exclusive','reporting_date')}==facts['control'],'control_evidence_binding')
  need(ctrl['reporting_date']==b['measurement_date'] and ctrl['control_start']<=b['measurement_date']<ctrl['control_end_exclusive'],'outside_reporting_perimeter')
  p,s=[v['balances'] for v in books];n=lambda k:num(x[k]);pn=lambda k:num(p[k]);sn=lambda k:num(s[k])
  currency='USD' if m=='exchangeability.assess@1' or (m=='exchangeability.transition@1' and x['transition_kind']=='foreign_operation') else 'LC'
  need(b['result_currency']==currency,'result_currency_binding')
  if m=='reciprocal.join@1':
   need(len(b['reciprocal_refs'])==2,'reciprocal_side_count')
   left,right=[self.body(r) for r in b['reciprocal_refs']]
   need([left['role'],right['role']]==['receivable','payable'],'reciprocal_role_binding')
   for i,side in enumerate((left,right)):
    need(side['book_ref']==b['legal_book_refs'][i] and side['counterparty_ref']==b['legal_book_refs'][1-i],'reciprocal_counterparty_binding')
    need(side['context_ref']==b['context_ref'] and side['branch_id']==ctx['branch_id'],'reciprocal_context_binding')
    need(side['currency']=='LC' and side['cutoff']==x['cutoff']==b['measurement_date'] and side['transaction_date']==x['transaction_date'],'reciprocal_date_binding')
   need(all(left[k]==right[k]==x[k] for k in ('economic_event_id','invoice_id','lot_id')),'reciprocal_event_binding')
   need(all(v['invoice_id']==left['invoice_id'] for v in x['allocations']),'allocation_invoice_binding')
   need(left['amount']==x['left_amount'] and right['amount']==x['right_amount'] and pn('receivable')==n('left_amount') and -sn('payable')==n('right_amount'),'reciprocal_amount_binding')
   need(x['control_start']==ctrl['control_start'] and x['control_end_exclusive']==ctrl['control_end_exclusive'],'reciprocal_control_binding')
  else:need(not b['reciprocal_refs'],'unexpected_reciprocal_sides')
  if m=='inventory.eliminate@1':
   need(b['prior_result_ref'] is None,'unexpected_prior_lot')
   need(ctrl['control_start']<=x['internal_date']<=x['external_date']<=b['measurement_date']<ctrl['control_end_exclusive'],'inventory_control_binding')
   need(pn('cash')==n('parent_cash') and pn('investment')==n('investment') and -sn('capital')==n('investment') and -pn('capital')==n('parent_opening_equity'),'inventory_opening_binding')
   need(pn('cogs')==n('original_cost') and -pn('revenue')==pn('receivable')==-sn('payable')==n('internal_price'),'inventory_internal_binding')
   need(sn('cash')==n('subsidiary_opening_cash')+n('external_proceeds') and -sn('revenue')==n('external_proceeds') and sn('cogs')==n('internal_price')*n('sold_fraction') and sn('inventory')==n('internal_price')*(1-n('sold_fraction')),'inventory_sale_binding')
   need(x['internal_event_id']!=x['external_sale_id'],'inventory_event_identity')
  elif m=='inventory.release@1':
   need(b['prior_result_ref'] is not None,'missing_prior_lot');old=self.body(b['prior_result_ref']);pb=self.body(old['basis_ref']);px=self.body(pb['input_ref'])
   need(old['method_id']=='inventory.eliminate@1' and old['status']=='resolved','invalid_prior_lot')
   need(pb['context_ref']==b['context_ref'] and pb['measurement_date']<b['measurement_date'],'prior_lot_context_date')
   need(pb['measurement_date']<x['external_date']<=b['measurement_date']<ctrl['control_end_exclusive'],'release_sale_date_binding')
   need(x['lot_id']==px['lot_id'] and x['prior_external_sale_id']==px['external_sale_id'] and x['external_sale_id']!=px['external_sale_id'],'prior_lot_event_binding')
   oldbooks=[self.body(r) for r in pb['legal_book_refs']]
   need(all(v['owner_key']==o['owner_key'] and v['revision']==o['revision']+1 for v,o in zip(books,oldbooks)),'legal_revision_binding')
   need(sn('cash')==num(oldbooks[1]['balances']['cash'])+n('external_proceeds') and -sn('revenue')==n('external_proceeds') and sn('inventory')==0,'release_legal_sale_binding')
   need(sn('cogs')==num(oldbooks[1]['balances']['inventory']) and pn('receivable')==-sn('payable')==num(px['internal_price']),'release_legal_cost_binding')
  elif b['prior_result_ref'] is not None:raise Refusal('unexpected_prior_lot')
  if m=='inflation.restate@1':
   need(x['indices'][-1]['date']==x['rate_date']==b['measurement_date'] and x['prior_presentation_date']<x['indices'][0]['date'],'index_rate_date_binding')
   need(x['rate_from']=='LC' and x['rate_to']=='USD' and x['rate_purpose']=='foreign_operation_presentation','rate_direction_purpose')
   need(pn('cash')==n('cash')+sum((num(e['amount']) for e in x['cash_income']),F(0)) and pn('inventory')==n('inventory') and -pn('debt')==n('debt') and -pn('capital')==n('capital'),'inflation_book_binding')
   need(-pn('revenue')==sum((num(e['amount']) for e in x['cash_income']),F(0)),'inflation_income_binding')
  elif m=='inflation.opening_tax@1':
   need(x['acquisition_date']<x['opening_date']<x['closing_date']==b['measurement_date'],'tax_index_date_binding')
   need(pn('inventory')==n('cost') and -pn('capital')==n('cost'),'opening_tax_book_binding')
  elif m=='goodwill.impair@1':
   need(sn('identifiable_assets')==n('identifiable_assets') and pn('investment')==n('parent_fraction')*n('identifiable_assets')+n('recognized_goodwill'),'goodwill_worksheet_binding')
   need(pn('goodwill')==sn('goodwill')==0,'notional_legal_goodwill')
  elif m=='corporate_asset.impair@1':need(pn('identifiable_assets')==sum((num(t) for t in x['assets']),F(0)),'corporate_asset_book_binding')
  elif m=='acquisition.tax@1':need(pn('investment')==n('consideration') and sn('identifiable_assets')==-sn('capital')==n('fair_value_assets'),'acquisition_book_binding')
  elif m in ('investment.taxable@1','investment.deductible@1'):need(pn('investment')==n('carrying'),'investment_book_binding')
  elif m=='exchangeability.assess@1':
   need(x['measurement_date']==x['rate_date']==b['measurement_date'],'exchange_rate_date')
   need(x['rate_from']=='LC' and x['rate_to']=='USD' and x['rate_purpose']==x['admission_purpose'],'rate_direction_purpose')
   need(x['subsequent_date']>x['measurement_date'],'subsequent_rate_date')
   need(pn('cash')==n('foreign_amount'),'exchange_book_binding')
  elif m=='exchangeability.transition@1':
   need(x['initial_date']==x['annual_period_start']==x['rate_date']==b['measurement_date'] and x['initial_date']>='2025-01-01','transition_date_binding')
   payable=x['transition_kind']=='monetary_payable'
   need((x['rate_from'],x['rate_to'],x['rate_purpose'],x['transition_destination'])==(('USD','LC','liability_settlement','opening_retained') if payable else ('LC','USD','foreign_operation_presentation','accumulated_translation')),'transition_destination_binding')
   need((-pn('payable')==n('foreign_amount')*n('old_rate')) if payable else sn('cash')==n('foreign_amount'),'transition_book_binding')
  return x
 def component(self,rr):
  r=self.body(rr);x=self.basis(r['basis_ref']);need(r['method_id']==x['method_id'],'result_method_binding')
  br=self.body(r['basis_ref']);prior=br['prior_result_ref']
  old=None
  if prior:self.component(prior);old=self.body(prior)
  try:expected=evaluate(x,old)
  except FinancialRefusal as e:raise Refusal(e.code)
  need({k:r[k] for k in expected}==expected,'independent_finance_mismatch')
  need(sum((num(v) for v in r['adjustment_journal'].values()),F(0))==0,'group_journal_unbalanced')
  need(r['status']!='unresolved' or (r['adjustment_journal']=={} and r['posting_effect']=='none'),'unresolved_posting')
 def state(self,sr):
  s=self.body(sr);ctx=self.body(s['context_ref'])
  need(s['branch_id']==ctx['branch_id'] and s['owner_key']=='Group/'+ctx['branch_id'],'group_owner_binding')
  if s['last_result_ref'] is None:need(s['sequence']==0,'initial_state_sequence')
  else:
   self.component(s['last_result_ref']);r=self.body(s['last_result_ref']);b=self.body(r['basis_ref'])
   need(r['status']=='resolved' and b['context_ref']==s['context_ref'],'state_result_binding')
   need(s['legal_book_refs']==b['legal_book_refs'],'state_book_binding')
   need(s['sequence']==(2 if r['method_id']=='inventory.release@1' else 1),'state_sequence_binding')
 def proposal(self,pr):
  p=self.body(pr);b=self.body(p['basis_ref']);r=self.body(p['result_ref']);before=self.body(p['from_state_ref']);after=self.body(p['to_state_ref']);auth=self.body(p['authorization_ref'])
  self.component(p['result_ref']);self.state(p['from_state_ref']);self.state(p['to_state_ref'])
  need(r['basis_ref']==p['basis_ref'] and before['context_ref']==after['context_ref']==b['context_ref'],'proposal_context_binding')
  need(auth['basis_ref']==p['basis_ref'] and auth['from_state_ref']==p['from_state_ref'] and auth['owner_key']==before['owner_key'],'authorization_binding')
  need(before['owner_key']==after['owner_key'] and before['branch_id']==after['branch_id'],'proposal_owner_binding')
  if r['status']=='unresolved':need(p['from_state_ref']==p['to_state_ref'],'unresolved_state_change')
  else:
   need(after==dict(before,sequence=before['sequence']+1,last_result_ref=p['result_ref'],legal_book_refs=b['legal_book_refs']),'state_transition_mismatch')
   need(before['last_result_ref']==b['prior_result_ref'],'state_prior_binding')
 def report(self,rr):
  r=self.body(rr);s=self.body(r['state_ref']);result=self.body(r['result_ref']);b=self.body(r['basis_ref'])
  self.state(r['state_ref']);need(s['last_result_ref']==r['result_ref'] and result['basis_ref']==r['basis_ref'],'report_state_binding')
  need(r['values']==dict(method_id=result['method_id'],**result['values']),'report_values_mismatch')
  tax='supplied_conditional_tax_method' if result['method_id'] in ('inflation.opening_tax@1','acquisition.tax@1','investment.taxable@1','investment.deductible@1') else 'uncomputed_separate_obligation'
  need(r['tax_status']==tax,'report_tax_claim')
 def request(self,rq,sub,world):
  r=self.body(rq);s=self.body(sub)
  need(decode(self.blob_bytes(s['blob_ref']))==self.record(rq) and self.blob_bytes(s['blob_ref'])==enc(self.record(rq)),'submission_request_binding')
  need(s['decoder_ref']==self.alias['decoder'],'decoder_binding')
  op=r['operation'];need(r['profile_ref']==self.alias['profile'] and r['signature_ref']==self.alias['signature.'+op],'request_profile_binding')
  need(r['arguments']['tag']==op and r['execution']['environment_ref']==self.alias['environment'],'request_signature_binding')
  key=enc([r['workspace_key'],r['request_id']]).decode()
  if key in world['decisions']:
   stored=world['decisions'][key];need(stored['request_digest']==rq['digest'],'identity_conflict')
   return 'replay',stored
  need(r['arguments']['value']['require_current'],'currentness_required')
  need(r['view_ref']==world['current_view_ref'],'stale_view')
  if op==OPS[0]:
   p=self.body(r['arguments']['value']['proposal_ref']);sr=p['from_state_ref'];b=self.body(p['basis_ref'])
  else:
   sr=r['arguments']['value']['state_ref'];st=self.body(sr)
   need(st['last_result_ref'] is not None,'report_unresolved_state')
   b=self.body(self.body(st['last_result_ref'])['basis_ref'])
  h=head(sr,self.body)
  need(r['expected_head']==h and world['group_heads'].get(h['owner_key'])==h,'stale_head')
  need(r['view_ref']==b['view_ref'],'request_basis_view_binding')
  for br in b['legal_book_refs']:
   book=self.body(br)
   need(world['legal_heads'].get(book['owner_key'])==dict(book_ref=br,generation=book['revision'],frozen_head_id=book['frozen_head_id']),'legal_head_binding')
  if op==OPS[0]:self.proposal(r['arguments']['value']['proposal_ref'])
  else:self.state(sr)
  return 'new',key
 def exchange(self,e):
  rq,sub,rr=e['request_ref'],e['submission_ref'],e['response_ref'];r=self.body(rq);out=self.body(rr)
  before,after=e['world_before'],e['world_after'];op=r['operation']
  need(out['submission_ref']==sub and out['request_ref']==rq and out['operation']==op and out['input_view_ref']==r['view_ref'],'response_request_binding')
  try:mode,data=self.request(rq,sub,before);code=None
  except Refusal as err:mode='refuse';data=None;code=err.code
  if mode=='refuse':
   need(out['disposition']=='rejected' and [d['code'] for d in out['diagnostics']]==[code],'refusal_binding')
   need(out['payload'] is None and out['coverage'] is None and out['unresolved']==[] and out['continuation_ref'] is None and out['receipt_ref'] is None and out['commit_observation']=='not_committed','refusal_publication')
   need(out['statuses']['computation_status']=='not_computed' and out['statuses']['mathematical_status']=='not_applicable','refusal_status')
   need(after==before,'refusal_world_mutation');return
  if mode=='replay':
   stored=self.body(data['response_ref']);expected=deepcopy(stored);expected['disposition']='replayed';expected['payload']['additional_commit']=False
   need(out==expected,'replay_result_mismatch')
   need(after==before,'replay_world_mutation')
   need(set(self.closure([data['response_ref']]))<=set(before['published_records']),'replay_missing_closure');return
  expected=deepcopy(before);payload=out['payload']
  need(payload is not None and payload['tag']==op and len(payload['result_refs'])==1 and payload['additional_commit'],'publication_payload')
  output=payload['result_refs'][0];o=self.body(output);receipt=self.body(out['receipt_ref'])
  need(out['commit_observation']=='committed' and out['continuation_ref'] is None,'publication_status')
  if op==OPS[0]:
   pr=r['arguments']['value']['proposal_ref'];p=self.body(pr);sr=p['from_state_ref'];ns=p['to_state_ref'];basis=p['basis_ref']
   need(output==p['result_ref'],'publication_result_binding')
   partial=o['status']=='unresolved';codes=o['diagnostics']
   need(receipt==dict(request_ref=rq,result_ref=output,from_state_ref=sr,to_state_ref=ns,proposal_ref=pr,status='unresolved_result_published' if partial else 'component_committed',legal_effect='none'),'receipt_binding')
   h=head(ns,self.body);expected['group_heads'][h['owner_key']]=h
   if o['adjustment_journal']:expected['journals'].append(dict(owner_key=h['owner_key'],result_ref=output,lines=o['adjustment_journal']))
  else:
   self.report(output);sr=r['arguments']['value']['state_ref'];basis=o['basis_ref'];partial=False;codes=[]
   need(o['state_ref']==sr,'report_request_binding')
   need(receipt==dict(request_ref=rq,report_ref=output,state_ref=sr,status='component_report_published',legal_effect='none'),'report_receipt_binding')
  need(out['disposition']==('partial' if partial else 'completed'),'publication_disposition')
  need(out['statuses']['mathematical_status']==('unresolved' if partial else 'defined') and out['statuses']['computation_status']==('partial' if partial else 'complete'),'publication_semantic_status')
  need([d['code'] for d in out['diagnostics']]==codes,'result_diagnostic_binding')
  need([self.body(t) for t in out['unresolved']]==[dict(code=c,required_input=c,basis_ref=basis) for c in codes],'obligation_binding')
  cov=out['coverage'];need(cov is not None and self.body(cov['domain_ref'])==dict(request_ref=rq,meaning='singleton_request_decision'),'coverage_domain_binding')
  field='unresolved' if partial else 'completed'
  need(len(cov[field])==1 and self.body(cov[field][0])==dict(domain_ref=cov['domain_ref'],predicate='this_request'),'coverage_region_binding')
  need(all(cov[k]==[] for k in ('completed','unresolved','unsupported','infeasible','cancelled') if k!=field),'coverage_not_disjoint')
  expected['published_records']=sorted(set(before['published_records'])|set(self.closure([rr])))
  expected['decisions'][data]=dict(request_digest=rq['digest'],response_ref=rr,output_ref=output,receipt_ref=out['receipt_ref'])
  need(after==expected,'atomic_world_mismatch')
  need(after['legal_heads']==before['legal_heads'] and after['unrelated_heads']==before['unrelated_heads'],'legal_or_unrelated_mutation')
 def crash(self,c):
  original=next(e for e in self.packet['exchanges'] if e['id']==c['publication_id'])
  need(c['world_before']==original['world_before'],'crash_before_binding')
  need(c['world_after']==original['world_after' if c['commit_happened'] else 'world_before'],'crash_atomicity')
  need(self.body(c['observation_ref'])==dict(submission_ref=c['submission_ref'],request_ref=c['request_ref'],observation='acknowledgement_timeout',commit_observation='unknown',receipt_ref=None,next_action='resubmit_exact_original_request'),'timeout_observation_binding')
  retry=next(e for e in self.packet['exchanges'] if e['id']==c['retry_exchange_id'])
  need(retry['request_ref']==c['request_ref']==original['request_ref'] and retry['submission_ref']==c['submission_ref']==original['submission_ref'],'retry_identity_binding')
  need(retry['world_before']==c['world_after'] and retry['world_after']==original['world_after'],'retry_convergence')
  self.exchange(retry)
 def challenge(self,c):
  try:
   scope=c['scope']
   if scope in ('component','proposal','report'):
    for d in self.closure([c['target_ref']]):self.shape(self.reg[d],d)
    getattr(self,scope)(c['target_ref'])
   elif scope=='exchange':self.exchange(c['candidate'])
   elif scope=='crash':self.crash(c['candidate'])
   elif scope=='decode':decode(self.blob_bytes(c['blob_ref']))
   elif scope=='record':self.shape(c['candidate'])
   else:raise RuntimeError('unsupported challenge scope')
  except Refusal as e:
   need(e.code==c['expected_code'],'wrong_adverse_reason:'+e.code);return
  raise Refusal('adverse_was_accepted')
 def completeness(self):
  cases=self.packet['cases'];ex=self.packet['exchanges'];crashes=self.packet['crash_worlds']
  need(len(cases)==32 and len({c['id'] for c in cases})==32,'case_coverage')
  need({c['method_id'] for c in cases}==set(METHOD_SOURCES),'method_coverage')
  need(len({e['id'] for e in ex})==len(ex),'duplicate_exchange')
  for c in cases:
   need(self.body(c['basis_ref'])['input_ref']==self.alias['input.'+c['id']],'case_input_binding')
   r=self.body(c['result_ref']);resolved=r['status']=='resolved'
   need(('report_ref' in c)==resolved,'report_coverage')
   prefixes=[c['id']]+([c['id']+'.report'] if resolved else [])
   for prefix in prefixes:
    roles={e['role'] for e in ex if e['id']==prefix or e['id'].startswith(prefix+'.') and not ('.report' in e['id'] and not prefix.endswith('.report'))}
    need({'publication','exact_replay','replay_before_freshness','identity_conflict','new_stale_view','new_stale_head','retry_after_timeout'}<=roles,'exchange_path_coverage')
    need({v['commit_happened'] for v in crashes if v['publication_id']==prefix}=={False,True},'both_acknowledgement_worlds')
  first=next(e for e in ex if e['id']=='inventory-first');later=next(e for e in ex if e['id']=='inventory-release')
  for field in ('journals','decisions'):need(later['world_before'][field]==first['world_after'][field],'prior_history_preservation')
  need(set(first['world_after']['published_records'])<=set(later['world_before']['published_records']),'prior_publication_preservation')
  expected_codes={'independent_finance_mismatch','report_values_mismatch','fact_evidence_binding','outside_basis_difference_mismatch','overallocated_invoice','duplicate_allocation','allocation_invoice_binding','reciprocal_counterparty_binding','reciprocal_event_binding','inventory_control_binding','prior_lot_event_binding','rate_direction_purpose','transition_destination_binding','authorization_binding','atomic_world_mismatch','replay_world_mutation','crash_atomicity','duplicate_key','float_forbidden','nonfinite_forbidden','noncanonical_rational','closed_record_shape'}
  need(expected_codes<={c['expected_code'] for c in self.packet['challenges']},'adverse_coverage')
 def run(self):
  self.audit('preservation.before',self.preservation);self.audit('source-and-input-bindings',self.source_checks)
  for k,s in self.schema['$defs'].items():self.audit('schema.'+k,lambda s=s:Draft202012Validator.check_schema(s))
  for d,r in self.reg.items():self.audit('record.'+r['key'],lambda r=r,d=d:self.shape(r,d))
  for c in self.packet['cases']:
   self.audit('component.'+c['id'],lambda c=c:self.component(c['result_ref']))
   self.audit('proposal.'+c['id'],lambda c=c:self.proposal(c['proposal_ref']))
   if 'report_ref' in c:self.audit('report.'+c['id'],lambda c=c:self.report(c['report_ref']))
  for e in self.packet['exchanges']:self.audit('exchange.'+e['id'],lambda e=e:self.exchange(e))
  for c in self.packet['crash_worlds']:self.audit('crash.'+c['id'],lambda c=c:self.crash(c))
  for c in self.packet['challenges']:self.audit('adverse.'+c['id'],lambda c=c:self.challenge(c))
  self.audit('complete-method-and-path-coverage',self.completeness)
  self.audit('preservation.after',self.preservation)
def main():
 started=time.monotonic();attempt=HERE/(sys.argv[1] if len(sys.argv)>1 else 'attempt-01')
 need(attempt.parent==HERE and attempt.name.startswith('attempt-'),'attempt_path_scope')
 target=attempt/'verification.json';need(not target.exists(),'verification_already_exists')
 a=Auditor(attempt);a.run();failures=[c for c in a.checks if not c['passed']]
 out=dict(status='failed' if failures else 'passed',command='python3 '+str(Path(__file__).relative_to(ROOT))+' '+attempt.name,interpreter=sys.executable,wall_seconds=time.monotonic()-started,checks=a.checks,summary=dict(checks=len(a.checks),failures=len(failures),cases=len(a.packet['cases']),exchanges=len(a.packet['exchanges']),crash_worlds=len(a.packet['crash_worlds']),adversaries=len(a.packet['challenges']),records=len(a.reg)),evidence_class='independent_documentary_no_runtime',packet_sha256=sha((attempt/'portable-exchanges.json').read_bytes()))
 target.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(status=out['status'],artifact=str(target.relative_to(ROOT)),**out['summary'],first_failures=failures[:8])))
 return 1 if failures else 0
if __name__=='__main__':sys.exit(main())
