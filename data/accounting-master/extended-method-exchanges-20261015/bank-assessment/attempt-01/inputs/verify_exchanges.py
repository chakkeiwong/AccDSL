"""Independent documentary audit. No builder or authored expectations imported."""
from copy import deepcopy
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from jsonschema import Draft202012Validator,FormatChecker
from financial_checks import ledger,capital,loss,num,q,Refusal as FinancialRefusal
from source_policy import sources,MANIFEST,REVIEW

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OPS=('bank.regulatory.assess@1','bank.loss.query@1','bank.policy.describe@1')
def need(ok,code):
 if not ok:raise Refusal(code)
class Refusal(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def references(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from references(x)
 elif isinstance(v,list):
  for x in v:yield from references(x)
def blobrefs(v):
 if isinstance(v,dict):
  if set(v)=={'kind','algorithm','digest','byte_length'}:yield v
  else:
   for x in v.values():yield from blobrefs(x)
 elif isinstance(v,list):
  for x in v:yield from blobrefs(x)
def unique(rs):return [r for k,r in sorted({enc(r):r for r in rs}.items())]
def pairs(v):
 d={}
 for k,x in v:need(k not in d,'duplicate_key');d[k]=x
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

class Auditor:
 def __init__(self,attempt):
  self.attempt=attempt
  self.packet=decode((attempt/'portable-exchanges.json').read_bytes())
  self.reg=self.packet['record_registry'];self.alias=self.packet['aliases'];self.blobs=self.packet['blobs']
  self.schema=decode((attempt/'record-schemas.json').read_bytes())
  self.validators={k:Draft202012Validator(v,format_checker=FormatChecker()) for k,v in self.schema['$defs'].items()}
  self.checks=[]
 def audit(self,label,fn):
  try:fn();self.checks.append(dict(check=label,passed=True))
  except Exception as e:self.checks.append(dict(check=label,passed=False,diagnostic=getattr(e,'code',type(e).__name__),detail=str(e)[:350]))
 def record(self,r):
  need(r['digest'] in self.reg,'missing_reference');v=self.reg[r['digest']]
  need(v['kind']==r['kind'] and v['schema']==r['schema'],'reference_type_mismatch');return v
 def body(self,r):return self.record(r)['body']
 def closure(self,roots):
  seen=set();visiting=set()
  def visit(r):
   d=r['digest']
   if d in seen:return
   need(d not in visiting,'dependency_cycle');visiting.add(d)
   for rr in self.record(r)['dependencies']:visit(rr)
   visiting.remove(d);seen.add(d)
  for r in roots:visit(r)
  return sorted(seen)
 def blob_bytes(self,b):
  need(b['digest'] in self.blobs,'missing_blob');meta=self.blobs[b['digest']];p=(ROOT/meta['path']).resolve()
  need(p.is_relative_to(ROOT),'blob_path_scope');raw=p.read_bytes()
  need(sha(raw)==b['digest'] and len(raw)==b['byte_length']==meta['byte_length'],'blob_hash_mismatch');return raw
 def shape(self,record,digest=None):
  need(set(record)=={'kind','schema','key','revision','body','dependencies'},'closed_record_shape')
  kind=record['kind'];need(kind in self.validators,'closed_record_shape')
  need(record['schema']==self.schema['schema_ids'][kind],'record_schema_mismatch')
  need(type(record['revision']) is int and record['revision']==0 and isinstance(record['key'],str) and bool(record['key']),'closed_record_shape')
  need(not list(self.validators[kind].iter_errors(record['body'])),'closed_record_shape');hygiene(record)
  need(record['dependencies']==unique(references(record['body'])),'dependency_mismatch')
  for r in references(record['body']):self.record(r)
  for b in blobrefs(record['body']):self.blob_bytes(b)
  if digest:need(sha(('accdsl.portable.v1/'+record['schema']).encode()+b'\0'+enc(record))==digest,'record_digest_mismatch')
 def preservation(self):
  lock=decode((HERE/'predecessor-lock.json').read_bytes());original=ROOT/lock['original_protection_manifest']
  need(sha(original.read_bytes())==lock['original_manifest_sha256'],'protection_manifest_changed')
  for row in decode(original.read_bytes())['files']:
   need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'protected_original_changed:'+row['path'])
   need(sha((ROOT/row['snapshot']).read_bytes())==row['sha256'],'protected_snapshot_changed:'+row['path'])
  for row in lock['predecessor_files']:need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'predecessor_changed:'+row['path'])
  need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==lock['git_commit'],'head_changed')
  index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
  need(sha(index)==lock['index_sha256'] and len(index.splitlines())==lock['index_entries']==100,'staged_index_changed')
 def source_checks(self):
  for s in sources():
   b=self.body(self.alias['source.'+s['key']])
   need(self.blob_bytes(b['raw_blob'])==(ROOT/s['path']).read_bytes(),'source_bytes_binding')
   if s['sha256']:need(b['raw_blob']['digest']==s['sha256'],'source_manifest_hash')
   if s['text_path']:
    need(self.blob_bytes(b['text_blob'])==(ROOT/s['text_path']).read_bytes() and b['text_blob']['digest']==s['text_sha256'],'source_text_binding')
   else:need(b['text_blob'] is None,'source_text_binding')
   need(self.blob_bytes(b['method_blob'])==(ROOT/s['method']).read_bytes(),'method_binding')
   need((b['anchors'],b['source_role'],b['snapshot'])==(s['anchors'],s['role'],s['snapshot']),'source_anchor_binding')
  need(self.blob_bytes(self.packet['source_manifest_blob'])==(ROOT/MANIFEST).read_bytes(),'source_manifest_binding')
  need(self.blob_bytes(self.packet['source_review_blob'])==(ROOT/REVIEW).read_bytes(),'source_review_binding')
  need(sha((ROOT/REVIEW).read_bytes())=='131d2ef1448020b4e5666e2c0b6637f63bf55952369b8c5b2f94ba780ad014ad','source_review_hash')
  p=self.body(self.alias['profile']);lock=self.body(p['schema_lock_ref'])
  need(p['profile_id']=='BankAssessment/1' and p['operations']==list(OPS) and p['accounting_effect']=='none','profile_mismatch')
  need(self.blob_bytes(lock['schema_blob'])==(self.attempt/'record-schemas.json').read_bytes(),'schema_lock_mismatch')
  need(self.blob_bytes(lock['semantic_contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'contract_lock_mismatch')
  for name,row in self.packet['input_snapshots'].items():
   need((self.attempt/'inputs'/name).read_bytes()==(ROOT/row['path']).read_bytes() and sha((ROOT/row['path']).read_bytes())==row['sha256'],'input_snapshot_changed')
  need(self.blob_bytes(self.packet['predecessor_lock_blob'])==(HERE/'predecessor-lock.json').read_bytes(),'lock_binding')

 def information(self,root,view_ref):
  view=self.body(view_ref);allowed={enc(r) for r in view['evidence_refs']}
  cutoff=instant(view['decision_at']);system=instant(view['system_asof'])
  # Inspect the entire semantic input closure, including superseded vintages.
  for d in self.closure([root]):
   record=self.reg[d]
   if record['kind']!='Evidence':continue
   r=dict(kind='Evidence',schema=record['schema'],digest=d);e=record['body']
   need(enc(r) in allowed,'evidence_not_in_view')
   need(instant(e['available_at'])<=cutoff,'later_information')
   need(instant(e['ingested_at'])<=system,'later_ingestion')
   need(day(e['measurement_asof'])<=cutoff.date(),'future_measurement')
 def state(self,sr,view_ref):
  s=self.body(sr);facility=self.body(s['facility_ref'])
  need(facility['context_ref']==s['context_ref'],'context_mismatch')
  need(s['sequence']==len(s['event_refs'])==len(s['posted_journals']),'state_sequence_mismatch')
  events=[self.body(r) for r in s['event_refs']]
  dates=[day(e['event_date']) for e in events]
  need(day(s['opening_asof_date'])<=day(s['as_of_date']) and dates==sorted(dates) and all(day(s['opening_asof_date'])<=d<=day(s['as_of_date']) for d in dates),'event_date_mismatch')
  need(day(self.body(s['evidence_ref'])['measurement_asof'])==day(s['as_of_date']),'state_evidence_date_mismatch')
  try:balances,journals,unpaid=ledger(s['opening_balances'],events,facility['limit'])
  except FinancialRefusal as e:raise Refusal(str(e))
  need(balances==s['balances'],'accounting_state_mismatch')
  need(unpaid==s['unpaid_withdrawal'],'unpaid_withdrawal_mismatch')
  actual=[]
  for er,j in zip(s['event_refs'],s['posted_journals']):
   need(j['event_ref']==er,'journal_event_mismatch')
   need(len({x['account'] for x in j['lines']})==len(j['lines']),'duplicate_journal_line')
   actual.append({x['account']:x['signed_amount'] for x in j['lines']})
  need(actual==journals,'accounting_journal_mismatch')
  return s
 def expected_capital(self,br):
  b=self.body(br);ctx=b['context_ref'];v=b['view_ref'];s=self.state(b['state_ref'],v)
  need(s['context_ref']==ctx,'context_mismatch')
  need(b['assessment_date']==s['as_of_date'],'assessment_date_mismatch')
  end=day(b['period_end_exclusive']);start=day(b['period_start'])
  need(start<end and day(b['assessment_date'])==end-timedelta(days=1),'assessment_period_mismatch')
  need(start>=date(2026,1,1) and end<=date(2026,4,1),'scenario_window_mismatch')
  need(day(b['assessment_date'])<=instant(self.body(v)['decision_at']).date(),'assessment_after_decision')
  rule=self.body(b['rule_ref'])
  need(rule==self.body(self.alias['rules']),'rule_package_mismatch')
  names=['applicability_ref','eligibility_ref','exposure_ref','allowance_ref','deduction_ref']
  records={k:self.body(b[k]) for k in names}
  need(all(x['context_ref']==ctx for x in records.values()),'context_mismatch')
  self.information(br,v)
  average=None
  if b['average_ref']:
   a=self.body(b['average_ref']);need(a['context_ref']==ctx,'context_mismatch')
   need(a['measure_kind']=='regulatory_average_total_assets','average_kind_mismatch')
   need((a['period_start'],a['period_end_exclusive'])==(b['period_start'],b['period_end_exclusive']),'average_period_mismatch')
   average=a['amount']
  try:
   amounts,ratios=capital(s['balances'],records['applicability_ref']['exclusions'],records['eligibility_ref']['conditions'],{k:records['exposure_ref'][k] for k in ('reserve_venue','loan_class')},records['allowance_ref']['all_eligible_aacl'],records['deduction_ref']['goodwill_without_dtl'],average)
  except FinancialRefusal as e:raise Refusal(str(e))
  # Independent dependency map, separate from authored packet construction.
  groups={'book_equity':['state_ref'],'gross_loans':['state_ref'],'allowance':['state_ref'],'goodwill':['state_ref']}
  risk=['state_ref','rule_ref','applicability_ref','exposure_ref','deduction_ref']
  core=['state_ref','rule_ref','applicability_ref','eligibility_ref','deduction_ref']
  for k in ('cap_base','cap'):groups[k]=risk
  for k in ('admitted_allowance','excess_allowance','rwa','tier2'):groups[k]=risk+['allowance_ref']
  for k in ('cet1','tier1'):groups[k]=core
  groups['total_capital']=risk+core+['allowance_ref']
  groups['leverage_denominator']=['state_ref','rule_ref','applicability_ref','deduction_ref']+(['average_ref'] if b['average_ref'] else [])
  for k,m in amounts.items():m['dependency_refs']=unique([v]+[b[x] for x in groups[k]])
  for k,n,d in [('cet1_ratio','cet1','rwa'),('tier1_ratio','tier1','rwa'),('total_ratio','total_capital','rwa'),('leverage_ratio','tier1','leverage_denominator')]:ratios[k]['dependency_refs']=unique(amounts[n]['dependency_refs']+amounts[d]['dependency_refs'])
  return dict(basis_ref=br,amounts=amounts,ratios=ratios,distribution_permission='unresolved_not_assessed',minimum_ratio_verdict='not_assessed',accounting_effect='none')

 def expected_loss(self,qr):
  query=self.body(qr);v=query['view_ref'];measure=self.body(query['measure_ref']);law=self.body(measure['law_ref']);vintage=self.body(law['vintage_ref']);condition=self.body(query['condition_ref'])
  need(law['context_ref']==query['context_ref'],'context_mismatch');self.information(qr,v)
  need(law['dependence']=='joint_cells_no_factorization','factorized_law')
  need(all(c['default_date'] is None or day(law['origin_date'])<=day(c['default_date'])<day(law['horizon_end_exclusive']) for c in law['cells']),'joint_cell_date_mismatch')
  origin=day(query['origin_date']);start=day(query['default_window_start']);end=day(query['default_window_end_exclusive'])
  need(day(law['origin_date'])<=origin<=start<end<=day(law['horizon_end_exclusive']),'loss_window_mismatch')
  need(day(vintage['as_of_date'])<=origin<=instant(self.body(v)['decision_at']).date(),'vintage_origin_mismatch')
  need(day(self.body(vintage['evidence_ref'])['measurement_asof'])<=day(vintage['as_of_date']),'vintage_evidence_mismatch')
  if vintage['supersedes_ref']:
   old=self.body(vintage['supersedes_ref']);need(day(old['as_of_date'])<day(vintage['as_of_date']),'vintage_order_mismatch')
  if condition['kind']=='all':need(condition['survived_through'] is None and condition['evidence_ref'] is None,'condition_shape_mismatch');through=None
  else:
   need(condition['survived_through'] is not None and condition['evidence_ref'] is not None,'condition_shape_mismatch')
   through=condition['survived_through'];need(day(law['origin_date'])<=day(through)<=origin,'condition_date_mismatch')
   need(day(self.body(condition['evidence_ref'])['measurement_asof'])==day(through),'condition_evidence_date_mismatch')
  # A later vintage can retain a complete original history partition, including
  # past cells of zero mass. The query's default window selects future defaults.
  try:out=loss(law['cells'],measure['candidates'],measure['mode'],through,query['default_window_start'],query['default_window_end_exclusive'])
  except FinancialRefusal as e:raise Refusal(str(e))
  return dict(query_ref=qr,**out,dependency_refs=[qr])
 def expected_policy(self,pr):
  p=self.body(pr);v=p['view_ref'];self.information(pr,v)
  lo=self.body(p['loss_result_ref']);query=self.body(lo['query_ref'])
  need(p['context_ref']==query['context_ref'] and v==query['view_ref'],'policy_input_mismatch')
  need(lo==self.expected_loss(lo['query_ref']),'policy_loss_mismatch')
  need(len({a['action_id'] for a in p['actions']})==len(p['actions']),'duplicate_policy_action')
  need(all(num(a['limit'])>=0 for a in p['actions']),'negative_policy_limit')
  return dict(policy_ref=pr,objective=p['objective'],action_ids=[a['action_id'] for a in p['actions']],tie_break=p['tie_break'],selected_action=None,feasibility_status='not_evaluated',distribution_permission='unresolved_not_assessed',diagnostics=['policy_not_optimized','permissions_not_assessed'],accounting_effect='none')
 def expected_output(self,op,ir):
  return {OPS[0]:self.expected_capital,OPS[1]:self.expected_loss,OPS[2]:self.expected_policy}[op](ir)
 def output(self,op,ir,body):need(body==self.expected_output(op,ir),'query_output_mismatch')

 def owner_head(self,st):
  s=self.body(st);c=self.body(s['context_ref'])
  return dict(owner_key='/'.join(c[k] for k in ('bank_id','book_id','perimeter_id')),state_ref=st,generation=s['sequence'])
 def identity(self,rq):
  r=self.body(rq);return enc([r['workspace_key'],r['request_id']]).decode()
 def request(self,rq,sub,w):
  record=self.record(rq);self.shape(record,rq['digest']);r=record['body']
  need(self.blob_bytes(self.body(sub)['blob_ref'])==enc(record),'submission_bytes_mismatch')
  need(self.body(self.body(sub)['decoder_ref'])==self.body(self.alias['decoder']),'decoder_mismatch')
  key=self.identity(rq)
  if key in w['query_index']:
   old=w['query_index'][key];need(old['request_digest']==rq['digest'],'request_identity_conflict');return 'replay',old
  need(r['operation'] in OPS and r['arguments']['tag']==r['operation'],'operation_tag_mismatch')
  need(r['profile_ref']==self.alias['profile'],'profile_mismatch')
  sig=self.body(r['signature_ref']);need(sig['profile_ref']==r['profile_ref'] and sig['operation']==r['operation'] and sig['arguments_definition']=='Arguments.'+r['operation'] and sig['effects']=='read','signature_mismatch')
  expected_kind={OPS[0]:'RegulatoryAssessment',OPS[1]:'LossQueryResult',OPS[2]:'PolicyQueryResult'}[r['operation']]
  need(sig['payload_kinds']==[expected_kind],'signature_mismatch')
  need(self.body(r['execution']['environment_ref'])==self.body(self.alias['environment']),'environment_mismatch')
  need(r['execution']['budget']['operation_count']>0 and r['execution']['budget']['elapsed_seconds']>0,'budget_exhausted')
  args=r['arguments']['value'];ir=args[{OPS[0]:'basis_ref',OPS[1]:'query_ref',OPS[2]:'policy_ref'}[r['operation']]]
  need(self.body(ir)['view_ref']==r['view_ref'],'request_view_mismatch')
  if args['require_current']:need(r['view_ref']==w['current_view_ref'],'stale_view')
  if r['expected_head']:
   h=r['expected_head'];need(h['owner_key'] in w['accounting_heads'] and h==w['accounting_heads'][h['owner_key']],'stale_accounting_head')
   need(h==self.owner_head(h['state_ref']),'expected_head_mismatch')
   need(self.body(h['state_ref'])['context_ref']==self.body(ir)['context_ref'],'context_mismatch')
   if r['operation']==OPS[0]:need(h['state_ref']==self.body(ir)['state_ref'],'expected_head_mismatch')
  else:need(r['operation']!=OPS[0],'expected_head_required')
  self.expected_output(r['operation'],ir)
  return 'new',ir

 def response(self,ex):
  rq,sub,w=ex['request_ref'],ex['submission_ref'],ex['world_before'];res=self.body(ex['response_ref'])
  r=self.body(rq)
  need(res['request_ref']==rq and res['submission_ref']==sub,'response_binding_mismatch')
  if ex['response_ref']['kind']!='TransportObservation':
   need(res['operation']==r['operation'] and res['input_view_ref']==r['view_ref'],'response_binding_mismatch')
   need(res['payload']['tag']==r['operation'] and res['statuses']['structural_validity']=='valid','response_tag_mismatch')
  try:mode,data=self.request(rq,sub,w)
  except Refusal as e:
   need(res['disposition']=='rejected' and [d['code'] for d in res['diagnostics']]==[e.code],'wrong_refusal')
   need(ex['world_after']==w and res['receipt_ref'] is None and res['payload']['result_refs']==[] and not res['payload']['additional_commit'],'refusal_changed_world')
   need(res['coverage'] is None and res['unresolved']==[] and res['commit_observation']=='not_committed','refusal_envelope_mismatch')
   return
  if ex['role']=='lost_ack':
   need(mode=='replay' and ex['response_ref']['kind']=='TransportObservation','lost_ack_before_publication')
   need(res['commit_observation']=='unknown' and res['receipt_ref'] is None and ex['world_after']==w,'lost_ack_invented_result');return
  if mode=='replay':
   original=deepcopy(self.body(data['response_ref']));original['disposition']='replayed';original['payload']['additional_commit']=False
   need(res==original,'replay_output_mismatch')
   need(res['receipt_ref']==data['receipt_ref'] and res['payload']['result_refs']==[data['output_ref']],'replay_output_mismatch')
   need(ex['world_after']==w and res['commit_observation']=='committed','replay_changed_world')
   need(self.body(res['receipt_ref'])['request_ref']==rq,'replay_receipt_mismatch')
   return
  need(len(res['payload']['result_refs'])==1,'missing_query_output');outref=res['payload']['result_refs'][0];out=self.body(outref)
  self.output(r['operation'],data,out)
  kind={OPS[0]:'RegulatoryAssessment',OPS[1]:'LossQueryResult',OPS[2]:'PolicyQueryResult'}[r['operation']]
  need(outref['kind']==kind,'output_kind_mismatch')
  if r['operation']==OPS[0]:codes=sorted({d for group in ('amounts','ratios') for m in out[group].values() for d in m['diagnostics']});undefined=any(m['status']=='undefined' for m in out['ratios'].values())
  elif r['operation']==OPS[1]:codes=out['diagnostics'];undefined=False
  else:codes=[];undefined=False
  need(res['disposition']==('partial' if codes else 'completed'),'disposition_mismatch')
  need([d['code'] for d in res['diagnostics']]==codes,'result_diagnostics_mismatch')
  need(res['statuses']['mathematical_status']==('undefined' if undefined else 'unresolved' if codes else 'defined'),'mathematical_status_mismatch')
  need(res['statuses']['computation_status']==('partial' if codes else 'complete'),'computation_status_mismatch')
  need([self.body(x)['code'] for x in res['unresolved']]==codes,'obligation_mismatch')
  for o in res['unresolved']:need(self.body(o)['query_ref']==data,'obligation_target_mismatch')
  receipt=self.body(res['receipt_ref'])
  need(receipt==dict(request_ref=rq,output_ref=outref,status='query_published',accounting_effect='none'),'query_receipt_mismatch')
  need(res['commit_observation']=='committed' and res['payload']['additional_commit'],'query_publication_not_recorded')
  cover=res['coverage'];need(cover is not None and self.body(cover['domain_ref'])['request_ref']==rq,'coverage_mismatch')
  need(cover['unsupported']==cover['infeasible']==cover['cancelled']==[],'coverage_mismatch')
  need(len(cover['unresolved'] if codes else cover['completed'])==1 and (cover['completed'] if codes else cover['unresolved'])==[],'coverage_mismatch')
  region=(cover['unresolved'] if codes else cover['completed'])[0];need(self.body(region)['domain_ref']==cover['domain_ref'],'coverage_mismatch')
  self.publication_world(ex,outref,res['receipt_ref'])
 def publication_world(self,ex,outref,receipt):
  w=deepcopy(ex['world_before']);rq=ex['request_ref'];res=ex['response_ref']
  w['published_records']=sorted(set(w['published_records'])|set(self.closure([res])))
  w['query_index'][self.identity(rq)]=dict(request_digest=rq['digest'],response_ref=res,output_ref=outref,receipt_ref=receipt)
  need(ex['world_after']==w,'non_atomic_or_accounting_publication')
 def crash(self,c):
  need(c['cuts']==['before_atomic_publication','after_atomic_publication'],'crash_cut_missing')
  key=self.identity(c['request_ref']);need(key not in c['before']['query_index'] and key in c['after']['query_index'],'crash_identity_mismatch')
  need(c['output_ref']['digest'] not in c['before']['published_records'] and c['receipt_ref']['digest'] not in c['before']['published_records'],'crash_before_leaked_records')
  need(all(r['digest'] in c['after']['published_records'] for r in (c['output_ref'],c['receipt_ref'],c['response_ref'])),'crash_after_missing_records')
  ex=dict(world_before=c['before'],world_after=c['after'],request_ref=c['request_ref'],response_ref=c['response_ref'])
  self.publication_world(ex,c['output_ref'],c['receipt_ref'])

 def challenge(self,c):
  def check():
   if c['kind']=='output':return self.output(c['operation'],c['input_ref'],c['candidate'])
   if c['kind']=='input':return self.expected_output(c['operation'],c['input_ref'])
   if c['kind']=='record':return self.shape(c['candidate'])
   if c['kind']=='raw':return decode(c['raw'].encode())
   if c['kind']=='world':return self.publication_world(c['exchange'],c['output_ref'],c['receipt_ref'])
   if c['kind']=='request':return self.request(c['request_ref'],c['submission_ref'],c['world'])
   if c['kind']=='response':return self.response(c['exchange'])
   raise Refusal('unknown_challenge')
  try:out=check()
  except Refusal as e:
   need(e.code==c['expected_code'],'wrong_challenge_refusal:'+e.code);return
  need(c['expected_code']=='accepted','invalid_candidate_accepted')
  if 'expected_output' in c:need(out==c['expected_output'],'boundary_output_mismatch')

 def run(self):
  self.audit('protected_predecessors_HEAD_index',self.preservation)
  self.audit('sources_schemas_input_snapshots',self.source_checks)
  for d,r in self.reg.items():self.audit('record.'+r['key'],lambda r=r,d=d:self.shape(r,d))
  self.audit('reference_closure',lambda:self.closure([self.packet['profile_ref']]+list(self.alias.values())))
  for c in self.packet['cases']:self.audit('independent.'+c['id'],lambda c=c:self.output(c['operation'],c['input_ref'],self.body(c['output_ref'])))
  for e in self.packet['exchanges']:self.audit('exchange.'+e['id'],lambda e=e:self.response(e))
  for c in self.packet['crash_cuts']:self.audit('crash.'+c['id'],lambda c=c:self.crash(c))
  for c in self.packet['challenges']:self.audit('adverse.'+c['id'],lambda c=c:self.challenge(c))
  start_roles={'publication','exact_replay','replay_before_freshness','lost_ack','lost_ack_exact_recovery','identity_conflict','new_stale_request'}
  for ca in self.packet['cases']:
   self.audit('exchange_coverage.'+ca['id'],lambda ca=ca:need({e['role'] for e in self.packet['exchanges'] if e['id']==ca['id'] or e['id'].startswith(ca['id']+'.')}>=start_roles,'missing_exchange_role'))

def main():
 start=time.monotonic();attempt=HERE/(sys.argv[1] if len(sys.argv)>1 else sorted(p.name for p in HERE.glob('attempt-*'))[-1])
 a=Auditor(attempt);a.run();fail=[x for x in a.checks if not x['passed']]
 report=dict(total=len(a.checks),failures=len(fail),wall_seconds=time.monotonic()-start,checks=a.checks,packet_sha256=sha((attempt/'portable-exchanges.json').read_bytes()))
 n=1
 while (attempt/f'verification-{n:02}.json').exists():n+=1
 (attempt/f'verification-{n:02}.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
 if fail:print(json.dumps(fail[:8]))
 raise SystemExit(bool(fail))

if __name__=='__main__':main()
