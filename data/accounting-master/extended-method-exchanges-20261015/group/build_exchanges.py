"""Author immutable GroupComponents/1 examples. No financial checker imported."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import time
from authored_cases import CASES
from schema_design import schemas,sid,OPS,METHODS,ACCOUNTS
from source_policy import sources,METHOD_SOURCES
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REG,ALIASES,BLOBS,EX,CRASHES,CHALLENGES,ROWS={},{},{},[],[],[],[]
ART=None
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(v):return hashlib.sha256(v).hexdigest()
def q(v):
 x=F(v);return dict(n=str(x.numerator),d=str(x.denominator))
def wire(v):
 if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v):return q(v)
 if isinstance(v,dict):return {k:wire(x) for k,x in v.items()}
 if isinstance(v,list):return [wire(x) for x in v]
 return v
def references(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from references(x)
 elif isinstance(v,list):
  for x in v:yield from references(x)
def unique(rs):return [r for k,r in sorted({enc(r):r for r in rs}.items())]
def add(kind,key,b):
 assert key not in ALIASES,key
 r=dict(kind=kind,schema=sid(kind),key=key,revision=0,body=b,dependencies=unique(references(b)))
 d=sha(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r))
 REG[d]=r;ALIASES[key]=dict(kind=kind,schema=sid(kind),digest=d);return ALIASES[key]
def body(r):return REG[r['digest']]['body']
def copy_record(key,r,**changes):return add(r['kind'],key,dict(deepcopy(body(r)),**changes))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def blob(p):
 raw=p.read_bytes();d=sha(raw);BLOBS[d]=dict(path=str(p.relative_to(ROOT)),byte_length=len(raw))
 return dict(kind='blob',algorithm='sha256',digest=d,byte_length=len(raw))
def closure(roots):
 seen=set()
 def visit(r):
  if r['digest'] in seen:return
  seen.add(r['digest'])
  for x in REG[r['digest']]['dependencies']:visit(x)
 for r in roots:visit(r)
 return sorted(seen)
def head(sr):
 s=body(sr);return dict(owner_key=s['owner_key'],state_ref=sr,generation=s['sequence'])
def identity(rq):
 r=body(rq);return enc([r['workspace_key'],r['request_id']]).decode()
def legal_balances(c):
 """Authored legal snapshots; debit-positive, with all unspecified accounts zero."""
 x=c['input'];m=x['method_id'];p={};s={}
 if m=='reciprocal.join@1':
  p=dict(receivable=x['left_amount'],capital=str(-F(x['left_amount'])))
  s=dict(payable=str(-F(x['right_amount'])),cash=x['right_amount'])
 elif m=='inventory.eliminate@1':
  p=dict(cash='90',investment='50',receivable='100',revenue='-100',cogs='60',capital='-200')
  s=dict(cash='110',inventory='60',payable='-100',capital='-50',revenue='-60',cogs='40')
 elif m=='inventory.release@1':
  p=dict(cash='90',investment='50',receivable='100',retained='-40',capital='-200')
  s=dict(cash='190',payable='-100',capital='-50',retained='-20',revenue='-80',cogs='60')
 elif m=='inflation.restate@1':
  p=dict(cash='130' if c['id']=='inflation-timed' else '100',inventory='60',debt='-80',capital='-80',revenue='-30' if c['id']=='inflation-timed' else '0')
 elif m=='inflation.opening_tax@1':p=dict(inventory='40',capital='-40')
 elif m=='goodwill.impair@1':p=dict(investment='200',capital='-200');s=dict(identifiable_assets='200',capital='-200')
 elif m=='corporate_asset.impair@1':p=dict(identifiable_assets='240',capital='-240')
 elif m=='acquisition.tax@1':p=dict(investment='150',capital='-150');s=dict(identifiable_assets='150',capital='-150')
 elif m in ('investment.taxable@1','investment.deductible@1'):
  p=dict(investment=x['carrying'],capital=str(-F(x['carrying'])));s=dict(cash='100',capital='-100')
 elif m=='exchangeability.assess@1':p=dict(cash='1000',capital='-1000')
 elif x['transition_kind']=='monetary_payable':p=dict(cash='1000',payable='-1000')
 else:p=dict(investment='1000',capital='-1000');s=dict(cash='1000',capital='-1000')
 return [wire({k:p.get(k,'0') for k in ACCOUNTS}),wire({k:s.get(k,'0') for k in ACCOUNTS})]
def main():
 global ART
 started=time.monotonic();n=1
 while (HERE/f'attempt-{n:02}').exists():n+=1
 ART=HERE/f'attempt-{n:02}';ART.mkdir();(ART/'inputs').mkdir();(ART/'bytes').mkdir()
 for p in sorted(HERE.iterdir()):
  if p.is_file() and (p.suffix=='.py' or p.name in ('source-reading.md','semantic-contract.md','diagnostic-repairs.md')):shutil.copyfile(p,ART/'inputs'/p.name)
 write(ART/'record-schemas.json',schemas())
 lock=add('SchemaLock','schema-lock',dict(schema_blob=blob(ART/'record-schemas.json'),semantic_contract_blob=blob(ART/'inputs/semantic-contract.md'),format='jsonschema2020-12'))
 profile=add('Profile','profile',dict(profile_id='GroupComponents/1',schema_lock_ref=lock,operations=list(OPS),execution_mode='specification_example',scope='finite_group_component_histories_not_combined_statements'))
 signatures={op:add('OperationSignature','signature.'+op,dict(operation=op,profile_ref=profile,arguments_definition='Arguments.'+op,payload_kinds=['ComponentResult' if i==0 else 'ComponentReport'],effects='accounting_transaction' if i==0 else 'read')) for i,op in enumerate(OPS)}
 env=add('Environment','environment',dict(purpose='documentary_fixture',numerics='exact_rational',runtime_executed=False))
 decoder=add('Decoder','decoder',dict(media_type='application/json',canonical_encoding='accdsl.portable.v1'))
 src={}
 for s in sources():src[s['key']]=add('SourceSupport','source.'+s['key'],dict(source_key=s['key'],raw_blob=blob(ROOT/s['path']),text_blob=blob(ROOT/s['text_path']),method_blobs=[blob(ROOT/p) for p in s['methods']],anchors=s['anchors'],scope='retained_historical_not_current_law'))
 rules=add('RulePackage','rules',dict(source_refs=list(src.values()),method_ids=list(METHODS),law_mode='historical_scenario_frozen_not_actual_applicability'))
 definitions={m:add('MethodDefinition','method.'+m,dict(method_id=m,source_refs=[src[k] for k in METHOD_SOURCES[m]],contract_blob=blob(ART/'inputs/semantic-contract.md'),scope='conditional_finite_supplied_facts',legal_book_effect='none')) for m in METHODS}

 def request(key,op,arg,view,st,request_id=None,expected=None):
  rq=add('OperationRequest','request.'+key,dict(operation=op,request_id=request_id or key,workspace_key='GroupComponents-specification',profile_ref=profile,signature_ref=signatures[op],view_ref=view,arguments=dict(tag=op,value={('proposal_ref' if op==OPS[0] else 'state_ref'):arg,'require_current':True}),execution=dict(mode='specification_example',budget=dict(operation_count=1000,elapsed_seconds=60),environment_ref=env),expected_head=expected or head(st)))
  return rq,submission(key,rq)
 def submission(key,rq):
  p=ART/'bytes'/(key+'.json');p.write_bytes(enc(REG[rq['digest']]))
  return add('Submission','submission.'+key,dict(blob_ref=blob(p),media_type='application/json',transport='authored_fixture',decoder_ref=decoder))
 def response(key,rq,sub,output=None,receipt=None,disposition='completed',codes=(),basis=None):
  partial=disposition=='partial';reject=disposition=='rejected';coverage=None;obs=[]
  if not reject:
   dom=add('Domain','domain.'+key,dict(request_ref=rq,meaning='singleton_request_decision'))
   region=add('Region','region.'+key,dict(domain_ref=dom,predicate='this_request'))
   coverage=dict(domain_ref=dom,completed=[] if partial else [region],unresolved=[region] if partial else [],unsupported=[],infeasible=[],cancelled=[],relation='disjoint_exhaustive')
   obs=[add('Obligation','obligation.'+key+'.'+code,dict(code=code,required_input=code,basis_ref=basis)) for code in codes] if partial else []
  return add('OperationResult','response.'+key,dict(submission_ref=sub,request_ref=rq,operation=body(rq)['operation'],input_view_ref=body(rq)['view_ref'],disposition=disposition,statuses=dict(structural_validity='valid',mathematical_status='not_applicable' if reject else 'unresolved' if partial else 'defined',computation_status='not_computed' if reject else 'partial' if partial else 'complete',empirical_justification='not_established',capability_status='specified_only_no_runtime',accounting_validity='not_assessed',forecast_validity='not_assessed',product_readiness='not_implemented',human_acceptance='pending'),payload=None if reject else dict(tag=body(rq)['operation'],result_refs=[output],additional_commit=True),diagnostics=[dict(code=code,stage='group_binding_or_validation',record_ref=None,source_locator=None,field_path='arguments',affected_query_branch_ids=[],dependency_path=[],observed=code,expected_rule='GroupComponents/1',retry_advice='repair_named_input_or_retry_exact_original',blocking_diagnostic_ids=[]) for code in codes],coverage=coverage,unresolved=obs,continuation_ref=None,commit_observation='not_committed' if reject else 'committed',receipt_ref=receipt,evidence_mode='specification_example'))
 def exchange(key,role,rq,sub,res,before,after):
  EX.append(dict(id=key,role=role,request_ref=rq,submission_ref=sub,response_ref=res,world_before=deepcopy(before),world_after=deepcopy(after)))
 def publish(key,op,arg,output,view,st,newst,books,v1,basis=None,codes=(),base_world=None):
  rq,sub=request(key,op,arg,view,st)
  before=dict(group_heads={body(st)['owner_key']:head(st)},legal_heads={body(b)['owner_key']:dict(book_ref=b,generation=body(b)['revision'],frozen_head_id=body(b)['frozen_head_id']) for b in books},unrelated_heads={'Other/Legal':dict(generation=9,digest='0'*64)},journals=[],decisions={},published_records=closure([st,*books]),current_view_ref=view)
  if base_world is not None:
   for field in ('journals','decisions'):before[field]=deepcopy(base_world[field])
   before['published_records']=sorted(set(before['published_records'])|set(base_world['published_records']))
  if op==OPS[0]:
   receipt=add('PublicationReceipt','receipt.'+key,dict(request_ref=rq,result_ref=output,from_state_ref=st,to_state_ref=newst,proposal_ref=arg,status='unresolved_result_published' if codes else 'component_committed',legal_effect='none'))
  else:receipt=add('ReportReceipt','receipt.'+key,dict(request_ref=rq,report_ref=output,state_ref=st,status='component_report_published',legal_effect='none'))
  res=response(key,rq,sub,output,receipt,'partial' if codes else 'completed',codes,basis)
  after=deepcopy(before)
  if op==OPS[0]:
   after['group_heads'][body(st)['owner_key']]=head(newst)
   if body(output)['adjustment_journal']:after['journals'].append(dict(owner_key=body(st)['owner_key'],result_ref=output,lines=body(output)['adjustment_journal']))
  after['published_records']=sorted(set(before['published_records'])|set(closure([res])))
  after['decisions'][identity(rq)]=dict(request_digest=rq['digest'],response_ref=res,output_ref=output,receipt_ref=receipt)
  exchange(key,'publication',rq,sub,res,before,after)
  replay_body=deepcopy(body(res));replay_body['disposition']='replayed';replay_body['payload']['additional_commit']=False
  replay=add('OperationResult','response.'+key+'.replay',replay_body)
  exchange(key+'.replay','exact_replay',rq,sub,replay,after,after)
  stale=deepcopy(after);stale['current_view_ref']=v1
  exchange(key+'.replay-after-view-change','replay_before_freshness',rq,sub,replay,stale,stale)
  conflicting=deepcopy(body(rq));conflicting['execution']['budget']['operation_count']+=1
  conflict=add('OperationRequest','request.'+key+'.conflict',conflicting);csub=submission(key+'.conflict',conflict)
  cres=response(key+'.conflict',conflict,csub,disposition='rejected',codes=['identity_conflict'])
  exchange(key+'.conflict','identity_conflict',conflict,csub,cres,after,after)
  sr,ss=request(key+'.new-stale',op,arg,view,st)
  stale_before=deepcopy(before);stale_before['current_view_ref']=v1
  sres=response(key+'.new-stale',sr,ss,disposition='rejected',codes=['stale_view'])
  exchange(key+'.new-stale','new_stale_view',sr,ss,sres,stale_before,stale_before)
  hr,hs=request(key+'.wrong-head',op,arg,view,st,expected=dict(head(st),generation=body(st)['sequence']+1))
  hres=response(key+'.wrong-head',hr,hs,disposition='rejected',codes=['stale_head'])
  exchange(key+'.wrong-head','new_stale_head',hr,hs,hres,before,before)
  for committed in (False,True):
   ck=key+('.lost-ack-committed' if committed else '.lost-ack-uncommitted')
   ob=add('TransportObservation','transport.'+ck,dict(submission_ref=sub,request_ref=rq,observation='acknowledgement_timeout',commit_observation='unknown',receipt_ref=None,next_action='resubmit_exact_original_request'))
   CRASHES.append(dict(id=ck,publication_id=key,request_ref=rq,submission_ref=sub,observation_ref=ob,commit_happened=committed,world_before=deepcopy(before),world_after=deepcopy(after if committed else before),retry_exchange_id=ck+'.retry'))
   exchange(ck+'.retry','retry_after_timeout',rq,sub,replay if committed else res,after if committed else before,after)
  return rq,res,receipt,before,after

 states={};results={};contexts={};worlds={}
 for c in CASES:
  key=c['id'];x=wire(c['input']);m=x['method_id'];branch='inventory-history' if key.startswith('inventory-') else key
  if branch not in contexts:contexts[branch]=add('Context','context.'+branch,dict(group_id='Synthetic-Group',perimeter_id='Parent-Subsidiary',branch_id=branch,functional_currency='LC',presentation_currency='USD',unit='illustrative_million',authority='historical_EU_scenario_not_actual_admission'))
  ctx=contexts[branch]
  d='2027-12-31' if key=='inventory-release' else c['input'].get('initial_date','2026-12-31')
  facts_path=ART/'bytes'/('facts.'+key+'.json')
  # The later rate is an explanatory candidate, expressly not admitted evidence.
  admitted=deepcopy(x)
  if m=='exchangeability.assess@1':
   for field in ('subsequent_rate','subsequent_date'):admitted.pop(field)
  control=dict(control_start=c['input'].get('control_start','2024-01-01'),control_end_exclusive=c['input'].get('control_end_exclusive','2028-01-01'),reporting_date=d)
  balances=legal_balances(c)
  write(facts_path,dict(facts=admitted,legal_balances=balances,control=control,scope='synthetic_supplied_not_actual_company',group_measurements='supplied_worksheet_not_legal_goodwill'))
  ev=add('Evidence','evidence.'+key,dict(evidence_id=key,available_at=d+'T12:00:00Z',ingested_at=d+'T13:00:00Z',measurement_asof=d,content_blob=blob(facts_path),provenance='synthetic_supplied'))
  prior=c['prior'];old_view=body(body(results[prior])['basis_ref'])['view_ref'] if prior else None
  evs=body(old_view)['evidence_refs']+[ev] if old_view else [ev]
  view=add('View','view.'+key,dict(evidence_refs=evs,decision_at=d+'T14:00:00Z',system_asof=d+'T14:00:00Z',mode='historical_information',revision=body(old_view)['revision']+1 if old_view else 0,supersedes_ref=old_view))
  v1=add('View','view.'+key+'.later',dict(deepcopy(body(view)),revision=body(view)['revision']+1,supersedes_ref=view,system_asof=d+'T15:00:00Z',decision_at=d+'T15:00:00Z'))
  books=[add('LegalBook','book.'+key+'.'+who,dict(entity_id=who,owner_key='Legal/'+branch+'/'+who,book_id='Legal',revision=1 if prior else 0,as_of_date=d,currency='LC',branch_id=branch,context_ref=ctx,evidence_ref=ev,balances=bal,frozen_head_id=key+'-'+who+'-frozen')) for who,bal in zip(('Parent','Subsidiary'),balances)]
  ctrl=add('ControlAssessment','control.'+key,dict(context_ref=ctx,entity_refs=books,**control,assessment='supplied_control',reporting_alignment='same_reporting_date_and_policies_supplied'))
  sides=[]
  if m=='reciprocal.join@1':
   for i,role in enumerate(('receivable','payable')):sides.append(add('ReciprocalSide','side.'+key+'.'+role,dict(context_ref=ctx,book_ref=books[i],counterparty_ref=books[1-i],economic_event_id='internal-event-17',invoice_id='invoice-17',lot_id='lot-17',currency='LC',cutoff=d,transaction_date=c['input']['transaction_date'],branch_id=branch,role=role,amount=x['left_amount' if i==0 else 'right_amount'])))
  inp=add('MethodInput','input.'+key,x)
  currency='USD' if m=='exchangeability.assess@1' or (m=='exchangeability.transition@1' and c['input']['transition_kind']=='foreign_operation') else 'LC'
  basis=add('MethodBasis','basis.'+key,dict(context_ref=ctx,view_ref=view,rule_ref=rules,method_ref=definitions[m],input_ref=inp,facts_evidence_ref=ev,legal_book_refs=books,control_ref=ctrl,reciprocal_refs=sides,prior_result_ref=results[prior] if prior else None,measurement_date=d,result_currency=currency,source_status='synthetic_facts_historical_rules'))
  output=add('ComponentResult','component.'+key,dict(basis_ref=basis,method_id=m,**wire(c['expected'])))
  st=states[prior] if prior else add('GroupState','state.'+key+'.opening',dict(context_ref=ctx,owner_key='Group/'+branch,branch_id=branch,sequence=0,last_result_ref=None,legal_book_refs=books,component_scope='isolated_method_history'))
  resolved=c['expected']['status']=='resolved'
  newst=add('GroupState','state.'+key+'.closing',dict(deepcopy(body(st)),sequence=body(st)['sequence']+1,last_result_ref=output,legal_book_refs=books)) if resolved else st
  auth=add('PostingAuthorization','authorization.'+key,dict(basis_ref=basis,from_state_ref=st,owner_key=body(st)['owner_key'],legal_book_effect='none',authority='authored_documentary_admission_not_professional_review'))
  proposal=add('ComponentProposal','proposal.'+key,dict(basis_ref=basis,result_ref=output,from_state_ref=st,to_state_ref=newst,authorization_ref=auth))
  pub=publish(key,OPS[0],proposal,output,view,st,newst,books,v1,basis,c['expected']['diagnostics'],worlds.get(prior))
  worlds[key]=pub[4]
  states[key]=newst;results[key]=output
  row=dict(id=key,method_id=m,basis_ref=basis,result_ref=output,from_state_ref=st,to_state_ref=newst,proposal_ref=proposal,publication_id=key)
  if resolved:
   report=add('ComponentReport','report.'+key,dict(state_ref=newst,result_ref=output,basis_ref=basis,scope='component_only_no_combined_company_claim',values=dict(method_id=m,**wire(c['expected']['values'])),tax_status='supplied_conditional_tax_method' if m in ('inflation.opening_tax@1','acquisition.tax@1','investment.taxable@1','investment.deductible@1') else 'uncomputed_separate_obligation'))
   publish(key+'.report',OPS[1],newst,report,view,newst,newst,books,v1,basis,base_world=pub[4])
   row['report_ref']=report
  ROWS.append(row)
 # Adverse packets are authored below; they do not change any positive record.
 build_adversaries()
 packet=dict(profile='GroupComponents/1',record_registry=REG,aliases=ALIASES,blobs=BLOBS,cases=ROWS,exchanges=EX,crash_worlds=CRASHES,challenges=CHALLENGES,predecessor_lock_blob=blob(HERE/'predecessor-lock.json'),input_snapshots={p.name:dict(path=str((HERE/p.name).relative_to(ROOT)),sha256=sha(p.read_bytes())) for p in sorted((ART/'inputs').iterdir())})
 write(ART/'portable-exchanges.json',packet)
 write(ART/'build-note.json',dict(command='python3 '+str(Path(__file__).relative_to(ROOT)),interpreter=sys.executable,wall_seconds=time.monotonic()-started,cases=len(ROWS),exchanges=len(EX),crash_worlds=len(CRASHES),challenges=len(CHALLENGES),records=len(REG),evidence_mode='documentary_not_runtime'))
 print(json.dumps(dict(attempt=str(ART.relative_to(ROOT)),cases=len(ROWS),exchanges=len(EX),crash_worlds=len(CRASHES),challenges=len(CHALLENGES),records=len(REG))))

def build_adversaries():
 rows={r['id']:r for r in ROWS}
 def put(obj,path,value):
  for key in path[:-1]:obj=obj[key]
  obj[path[-1]]=deepcopy(value)
 def clone(root,changes,label):
  replacements={}
  for rr,path,value in changes:
   target=replacements.setdefault(rr['digest'],deepcopy(body(rr)));put(target,path,value)
  memo={}
  def walk(v):
   if isinstance(v,dict):
    if set(v)=={'kind','schema','digest'}:return visit(v)
    return {k:walk(x) for k,x in v.items()}
   if isinstance(v,list):return [walk(x) for x in v]
   return v
  def visit(rr):
   d=rr['digest']
   if d in memo:return memo[d]
   old=body(rr);new=walk(replacements.get(d,old))
   memo[d]=rr if new==old else add(rr['kind'],'adverse.'+label+'.'+REG[d]['key'],new)
   return memo[d]
  return visit(root)
 def challenge(label,scope,root,changes,code):
  changed=clone(root,changes,label)
  CHALLENGES.append(dict(id=label,scope=scope,target_ref=changed,expected_code=code))
 def inp(label,key,path,value,code,coherent=True):
  row=rows[key];br=row['basis_ref'];b=body(br);ir=b['input_ref'];changes=[(ir,path,value)]
  if coherent:
   er=b['facts_evidence_ref'];eb=body(er);oldpath=ROOT/BLOBS[eb['content_blob']['digest']]['path'];f=json.loads(oldpath.read_text())
   put(f['facts'],path,value);p=ART/'bytes'/('adverse.facts.'+label+'.json');write(p,f)
   changes.append((er,['content_blob'],blob(p)))
  challenge(label,'component',row['result_ref'],changes,code)
 for key,row in rows.items():
  # Every supported result is challenged independently of input validity.
  result=body(row['result_ref']);values=deepcopy(result['values'])
  def perturb(v):
   for k,x in v.items():
    if isinstance(x,dict) and set(x)=={'n','d'}:v[k]=q(F(int(x['n']),int(x['d']))+1);return True
    if isinstance(x,dict) and perturb(x):return True
    if x is None:v[k]=q(0);return True
    if isinstance(x,bool):v[k]=not x;return True
   return False
  assert perturb(values),key
  challenge('wrong-finance.'+key,'component',row['result_ref'],[(row['result_ref'],['values'],values)],'independent_finance_mismatch')
  if 'report_ref' in row:
   rp=row['report_ref'];rv=deepcopy(body(rp)['values']);assert perturb(rv)
   challenge('wrong-report.'+key,'report',rp,[(rp,['values'],rv)],'report_values_mismatch')
 inp('unbound-input','outside-taxable',['difference'],q(59),'fact_evidence_binding',False)
 inp('wrong-taxable-difference','outside-taxable',['difference'],q(59),'outside_basis_difference_mismatch')
 inp('wrong-deductible-difference','outside-deductible',['difference'],q(59),'outside_basis_difference_mismatch')
 inp('overallocated-invoice','join-split',['allocations',0,'amount'],q(41),'overallocated_invoice')
 inp('duplicate-allocation','join-split',['allocations',1,'allocation_id'],'part-40','duplicate_allocation')
 inp('wrong-allocation-invoice','join-split',['allocations',0,'invoice_id'],'other-invoice','allocation_invoice_binding')
 inp('negative-index','inflation-static',['indices',0,'index'],q(0),'nonpositive_index')
 inp('wrong-index-date','inflation-static',['indices',1,'date'],'2026-12-30','index_rate_date_binding')
 inp('wrong-rate-date','exchange-limited',['rate_date'],'2026-12-30','exchange_rate_date')
 inp('wrong-rate-direction','exchange-limited',['rate_from'],'USD','rate_direction_purpose')
 inp('wrong-rate-purpose','exchange-limited',['admission_purpose'],'imports','rate_direction_purpose')
 inp('transition-to-period','transition-payable',['transition_destination'],'accumulated_translation','transition_destination_binding')
 inp('transition-wrong-opening','transition-payable',['annual_period_start'],'2025-02-01','transition_date_binding')
 inp('precontrol-inventory','inventory-first',['internal_date'],'2023-12-31','inventory_control_binding')
 inp('same-external-sale','inventory-release',['external_sale_id'],'external-sale-40percent','prior_lot_event_binding')
 inp('wrong-release-lot','inventory-release',['lot_id'],'lot-other','prior_lot_event_binding')
 inp('early-release-date','inventory-release',['external_date'],'2026-12-31','release_sale_date_binding')
 inp('bad-goodwill-ratio','goodwill-partial',['notional_goodwill'],q(60),'not_proportional_goodwill')
 inp('bad-asset-floor','corporate-floor',['floors',0],q(41),'invalid_asset_floor')
 inp('bad-significance','exchange-significant',['amount_obtainable'],q(0),'inconsistent_significance')
 row=rows['join-split'];br=row['basis_ref'];b=body(br);left,right=b['reciprocal_refs']
 for label,rr,path,value,code in [
  ('wrong-counterparty',left,['counterparty_ref'],b['legal_book_refs'][0],'reciprocal_counterparty_binding'),
  ('wrong-reciprocal-event',right,['economic_event_id'],'another-event','reciprocal_event_binding'),
  ('wrong-legal-book-date',b['legal_book_refs'][0],['as_of_date'],'2026-12-30','legal_book_date_binding'),
  ('wrong-control-date',b['control_ref'],['control_start'],'2027-01-01','control_evidence_binding'),
  ('wrong-result-currency',br,['result_currency'],'USD','result_currency_binding'),
  ('later-fact',b['facts_evidence_ref'],['available_at'],'2027-01-01T00:00:00Z','later_information'),
  ('later-ingestion',b['facts_evidence_ref'],['ingested_at'],'2027-01-01T00:00:00Z','later_ingestion')]:
  challenge(label,'component',row['result_ref'],[(rr,path,value)],code)
 pr=rows['inventory-first']['proposal_ref'];auth=body(pr)['authorization_ref']
 challenge('wrong-posting-owner','proposal',pr,[(auth,['owner_key'],'Legal/inventory-history/Parent')],'authorization_binding')
 unknown=rows['goodwill-unknown'];upr=unknown['proposal_ref']
 challenge('unknown-state-moves','proposal',upr,[(upr,['to_state_ref'],rows['goodwill-partial']['to_state_ref'])],'proposal_context_binding')
 for label,field,code in [('dropped-publication','published_records','atomic_world_mismatch'),('dropped-decision','decisions','atomic_world_mismatch'),('legal-book-mutation','legal_heads','atomic_world_mismatch'),('dropped-journal','journals','atomic_world_mismatch')]:
  e=deepcopy(next(e for e in EX if e['id']=='inventory-first'));e['world_after'][field]=deepcopy(e['world_before'][field])
  if field=='legal_heads':next(iter(e['world_after'][field].values()))['generation']+=1
  CHALLENGES.append(dict(id=label,scope='exchange',candidate=e,expected_code=code))
 e=deepcopy(next(e for e in EX if e['id']=='inventory-first.replay'));e['world_after']['journals']=[]
 CHALLENGES.append(dict(id='replay-mutation',scope='exchange',candidate=e,expected_code='replay_world_mutation'))
 cr=deepcopy(next(c for c in CRASHES if c['id']=='inventory-first.lost-ack-committed'));cr['world_after']['decisions']={}
 CHALLENGES.append(dict(id='torn-lost-ack',scope='crash',candidate=cr,expected_code='crash_atomicity'))
 for label,raw,code in [('duplicate-json',b'{"a":1,"a":2}','duplicate_key'),('float-json',b'{"a":1.5}','float_forbidden'),('nonfinite-json',b'{"a":NaN}','nonfinite_forbidden')]:
  path=ART/'bytes'/('adverse.'+label+'.json');path.write_bytes(raw)
  CHALLENGES.append(dict(id=label,scope='decode',blob_ref=blob(path),expected_code=code))
 rec=deepcopy(REG[rows['outside-taxable']['result_ref']['digest']]);rec['body']['values']['deferred_tax']={'n':'24','d':'2'}
 CHALLENGES.append(dict(id='unreduced-rational',scope='record',candidate=rec,expected_code='noncanonical_rational'))
 rec=deepcopy(REG[rows['outside-taxable']['result_ref']['digest']]);rec['body']['extra']='hidden'
 CHALLENGES.append(dict(id='extra-result-field',scope='record',candidate=rec,expected_code='closed_record_shape'))
if __name__=='__main__':main()
