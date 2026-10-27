"""Author immutable documentary examples; never imports a financial checker."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import re
import shutil
import time
from schema_design import schemas,sid,OPS,EXCLUSIONS,ELIGIBILITY
from authored_cases import BOOKS,CAPITAL_CASES,LOSS_CASES,CELLS
from source_policy import sources,MANIFEST,REVIEW

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REG,ALIASES,BLOBS,EX,CASES,CHALLENGES,CRASHES={},{},{},[],[],[],[]
ART=None
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def q(v):
 x=F(v);return dict(n=str(x.numerator),d=str(x.denominator))
def wire(v):
 if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v):return q(v)
 if isinstance(v,dict):return {k:wire(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [wire(x) for x in v]
 return v
def refs(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from refs(x)
 elif isinstance(v,list):
  for x in v:yield from refs(x)
def add(kind,key,b):
 assert key not in ALIASES,key
 ds={enc(r):r for r in refs(b)}
 r=dict(kind=kind,schema=sid(kind),key=key,revision=0,body=b,dependencies=[ds[k] for k in sorted(ds)])
 d=sha(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r))
 REG[d]=r;ALIASES[key]=dict(kind=kind,schema=sid(kind),digest=d);return ALIASES[key]
def body(r):return REG[r['digest']]['body']
def blob(p):
 raw=p.read_bytes();d=sha(raw);BLOBS[d]=dict(path=str(p.relative_to(ROOT)),byte_length=len(raw))
 return dict(kind='blob',algorithm='sha256',digest=d,byte_length=len(raw))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def unique(rs):return [dict(v) for k,v in sorted({enc(r):r for r in rs}.items())]
def closure(roots):
 seen=set()
 def visit(r):
  if r['digest'] in seen:return
  seen.add(r['digest'])
  for x in REG[r['digest']]['dependencies']:visit(x)
 for r in roots:visit(r)
 return sorted(seen)
def copy_record(key,r,**changes):
 b=deepcopy(body(r));b.update(changes);return add(r['kind'],key,b)
def head(st):
 s=body(st);c=body(s['context_ref'])
 return dict(owner_key='/'.join(c[k] for k in ('bank_id','book_id','perimeter_id')),state_ref=st,generation=s['sequence'])
def world(st,v,rq):
 h=head(st)
 return dict(accounting_heads={h['owner_key']:h},journals=[],query_index={},published_records=closure([rq]),current_view_ref=v,unrelated_owners={'Other/Book':dict(generation=7,digest='0'*64)})
def identity(rq):
 r=body(rq);return enc([r['workspace_key'],r['request_id']]).decode()

def main():
 global ART
 start=time.monotonic();n=1
 while (HERE/f'attempt-{n:02}').exists():n+=1
 ART=HERE/f'attempt-{n:02}';ART.mkdir();(ART/'inputs').mkdir();(ART/'bytes').mkdir()
 for p in sorted(HERE.iterdir()):
  if p.is_file() and (p.suffix=='.py' or p.name in ('semantic-contract.md','source-reading.md')):shutil.copyfile(p,ART/'inputs'/p.name)
 write(ART/'record-schemas.json',schemas())
 lock=add('SchemaLock','schema-lock',dict(schema_blob=blob(ART/'record-schemas.json'),semantic_contract_blob=blob(ART/'inputs/semantic-contract.md'),format='jsonschema2020-12'))
 profile=add('Profile','profile',dict(profile_id='BankAssessment/1',schema_lock_ref=lock,operations=list(OPS),execution_mode='specification_example',accounting_effect='none'))
 signatures={op:add('OperationSignature','signature.'+op,dict(operation=op,profile_ref=profile,arguments_definition='Arguments.'+op,payload_kinds=[k],effects='read')) for op,k in zip(OPS,('RegulatoryAssessment','LossQueryResult','PolicyQueryResult'))}
 env=add('Environment','environment',dict(purpose='documentary_fixture',numerics='exact_rational',runtime_executed=False))
 decoder=add('Decoder','decoder',dict(media_type='application/json',canonical_encoding='accdsl.portable.v1'))
 src=[]
 for s in sources():
  src.append(add('SourceSupport','source.'+s['key'],dict(raw_blob=blob(ROOT/s['path']),text_blob=blob(ROOT/s['text_path']) if s['text_path'] else None,method_blob=blob(ROOT/s['method']),anchors=s['anchors'],source_role=s['role'],snapshot=s['snapshot'])))
 rules=add('RulePackage','rules',dict(source_refs=src,snapshot='2026-01-01',law_mode='scenario_frozen_not_actual_applicability',method_version='US_restricted_ordinary_bank_v1'))
 ctx=add('Context','context',dict(bank_id='Synthetic-US-Bank',book_id='Legal',perimeter_id='Solo',currency='USD',unit='million',accounting_basis='US_GAAP_CECL_supplied',jurisdiction='US_national_bank'))
 premise=ART/'bytes/supplied-premises.json'
 write(premise,dict(scope='synthetic_supplied_not_observed_bank',capital_date='2026-03-31',funding_facility_limit='10',probabilities='authored_not_estimated'))
 def evidence(key,date='2026-03-31',available='2026-04-01T00:00:00Z',ingested='2026-04-01T00:00:00Z'):
  return add('Evidence','evidence.'+key,dict(evidence_id=key,available_at=available,ingested_at=ingested,measurement_asof=date,content_blob=blob(premise),provenance='synthetic_supplied'))
 ev=evidence('original');cond_ev=evidence('survival','2026-09-30','2026-10-01T00:00:00Z','2026-10-01T00:00:00Z')
 new_ev=evidence('new-forecast','2026-10-01','2026-10-01T00:00:00Z','2026-10-01T00:00:00Z')
 def view(key,es,decision,prior=None):return add('View','view.'+key,dict(evidence_refs=es,decision_at=decision,system_asof=decision,mode='historical_information',revision=1 if prior else 0,supersedes_ref=prior))
 v0=view('original',[ev],'2026-04-01T00:00:00Z')
 v1=view('survival',[ev,cond_ev],'2026-10-01T00:00:00Z',v0)
 v2=view('new',[ev,cond_ev,new_ev],'2026-10-01T00:00:00Z',v1)
 app=add('Applicability','applicability',dict(context_ref=ctx,evidence_ref=ev,institution='ordinary_national_bank',exclusions={k:'absent' for k in EXCLUSIONS}))
 elig=add('StockEligibility','eligibility',dict(context_ref=ctx,evidence_ref=ev,conditions={k:'satisfied' for k in ELIGIBILITY}))
 exposure=add('ExposureClassification','exposure',dict(context_ref=ctx,evidence_ref=ev,reserve_venue='federal_reserve',loan_class='ordinary_performing_nonPCD_corporate'))
 allowance=add('AllowanceAdmission','allowance',dict(context_ref=ctx,evidence_ref=ev,all_eligible_aacl='yes',measurement='supplied_not_estimated'))
 deduction=add('DeductionAdmission','deduction',dict(context_ref=ctx,evidence_ref=ev,goodwill_without_dtl='yes'))
 states={}
 for c in BOOKS:
  key=c['id'];facility=add('FundingFacility','facility.'+key,dict(context_ref=ctx,evidence_ref=ev,limit=q(c['facility']),availability='supplied_available_not_estimated'))
  events=[add('AccountingEvent',f'event.{key}.{i}',dict(method_id=m,amount=q(a),event_date=d)) for i,(m,a,d,j) in enumerate(c['events'])]
  journals=[dict(event_ref=r,lines=[dict(account=k,signed_amount=q(a)) for k,a in sorted(e[3].items())]) for r,e in zip(events,c['events'])]
  states[key]=add('AccountingState','state.'+key,dict(context_ref=ctx,evidence_ref=ev,facility_ref=facility,opening_asof_date='2026-01-01',as_of_date='2026-03-31',sequence=len(events),opening_balances=wire(c['opening']),event_refs=events,posted_journals=journals,balances=wire(c['closing']),unpaid_withdrawal=q(c['unpaid']),frozen_head_id='frozen-'+key))

 def request(key,op,input_ref,v,st,require_current=True,request_id=None,prof=profile,expected=True):
  field={OPS[0]:'basis_ref',OPS[1]:'query_ref',OPS[2]:'policy_ref'}[op]
  r=add('OperationRequest','request.'+key,dict(operation=op,request_id=request_id or key,workspace_key='BankAssessment-specification',profile_ref=prof,signature_ref=signatures[op],view_ref=v,arguments=dict(tag=op,value={field:input_ref,'require_current':require_current}),execution=dict(mode='specification_example',budget=dict(operation_count=1000,elapsed_seconds=60),environment_ref=env),expected_head=head(st) if expected else None))
  p=ART/'bytes'/(key+'.json');p.write_bytes(enc(REG[r['digest']]))
  sub=add('Submission','submission.'+key,dict(blob_ref=blob(p),media_type='application/json',transport='authored_fixture',decoder_ref=decoder))
  return r,sub

 def response(key,rq,sub,output=None,receipt=None,disposition='completed',codes=(),math='defined'):
  partial=disposition=='partial';reject=disposition in ('rejected','unsupported')
  coverage=None;obligations=[]
  if not reject:
   dom=add('Domain','domain.'+key,dict(request_ref=rq,meaning='singleton_request_decision'))
   region=add('Region','region.'+key,dict(domain_ref=dom,predicate='this_request'))
   coverage=dict(domain_ref=dom,completed=[] if partial else [region],unresolved=[region] if partial else [],unsupported=[],infeasible=[],cancelled=[],relation='disjoint_exhaustive')
   if partial:
    for code in codes:obligations.append(add('Obligation','obligation.'+key+'.'+code,dict(code=code,required_input=code,query_ref=list(body(rq)['arguments']['value'].values())[0])))
  return add('OperationResult','result.'+key,dict(submission_ref=sub,request_ref=rq,operation=body(rq)['operation'],input_view_ref=body(rq)['view_ref'],disposition=disposition,
   statuses=dict(structural_validity='valid',mathematical_status=math,computation_status='not_computed' if reject else 'partial' if partial else 'complete',empirical_justification='not_established',capability_status='specified_only_no_runtime',accounting_validity='not_assessed',forecast_validity='not_assessed',product_readiness='not_implemented',human_acceptance='pending'),
   payload=dict(tag=body(rq)['operation'],result_refs=[output] if output else [],additional_commit=receipt is not None and disposition!='replayed'),
   diagnostics=[dict(code=c,stage='query_binding_or_validation',record_ref=None,source_locator=None,field_path='arguments',affected_query_branch_ids=[],dependency_path=[],observed=c,expected_rule='BankAssessment/1',retry_advice='repair_named_input_or_retry_original_bytes',blocking_diagnostic_ids=[]) for c in codes],
   coverage=coverage,unresolved=obligations,continuation_ref=None,commit_observation='committed' if receipt else 'not_committed',receipt_ref=receipt,evidence_mode='specification_example'))

 def exchange(key,rq,sub,res,before,after,role):
  EX.append(dict(id=key,role=role,request_ref=rq,submission_ref=sub,response_ref=res,world_before=deepcopy(before),world_after=deepcopy(after)))

 def publish(key,op,input_ref,output,v,st,codes=(),undefined=False):
  rq,sub=request(key,op,input_ref,v,st);w=world(st,v,rq)
  receipt=add('QueryPublicationReceipt','receipt.'+key,dict(request_ref=rq,output_ref=output,status='query_published',accounting_effect='none'))
  res=response(key,rq,sub,output,receipt,'partial' if codes else 'completed',codes,'undefined' if undefined else 'unresolved' if codes else 'defined')
  after=deepcopy(w);after['published_records']=sorted(set(w['published_records'])|set(closure([res])))
  after['query_index'][identity(rq)]=dict(request_digest=rq['digest'],response_ref=res,output_ref=output,receipt_ref=receipt)
  exchange(key,rq,sub,res,w,after,'publication')
  CASES.append(dict(id=key,operation=op,input_ref=input_ref,output_ref=output,request_ref=rq))
  replay_body=deepcopy(body(res));replay_body['disposition']='replayed';replay_body['payload']['additional_commit']=False
  replay=add('OperationResult','result.'+key+'.replay',replay_body)
  exchange(key+'.replay',rq,sub,replay,after,after,'exact_replay')
  stale=deepcopy(after);stale['current_view_ref']=v2 if v!=v2 else v0
  oldstate=body(st)
  zero_event=add('AccountingEvent',key+'.later-zero-event',dict(method_id='funding.draw',amount=q(0),event_date=oldstate['as_of_date']))
  later_state=copy_record(key+'.later-state',st,sequence=oldstate['sequence']+1,event_refs=oldstate['event_refs']+[zero_event],posted_journals=oldstate['posted_journals']+[dict(event_ref=zero_event,lines=[])],frozen_head_id=oldstate['frozen_head_id']+'-later')
  stale_head=head(later_state)
  stale['accounting_heads'][stale_head['owner_key']]=stale_head
  exchange(key+'.stale-replay',rq,sub,replay,stale,stale,'replay_before_freshness')
  lost=add('TransportObservation','lost-ack.'+key,dict(submission_ref=sub,request_ref=rq,observation='acknowledgement_timeout',commit_observation='unknown',receipt_ref=None,next_action='resubmit_exact_original_request'))
  EX.append(dict(id=key+'.lost-ack',role='lost_ack',request_ref=rq,submission_ref=sub,response_ref=lost,world_before=deepcopy(after),world_after=deepcopy(after)))
  exchange(key+'.recovery',rq,sub,replay,after,after,'lost_ack_exact_recovery')
  conflict,confsub=request(key+'.conflict',op,input_ref,v,st,False,request_id=key)
  conflictres=response(key+'.conflict',conflict,confsub,disposition='rejected',codes=['request_identity_conflict'])
  exchange(key+'.conflict',conflict,confsub,conflictres,after,after,'identity_conflict')
  fresh,freshsub=request(key+'.new-stale',op,input_ref,v,st)
  freshworld=world(st,v2 if v!=v2 else v0,fresh)
  freshres=response(key+'.new-stale',fresh,freshsub,disposition='rejected',codes=['stale_view'])
  exchange(key+'.new-stale',fresh,freshsub,freshres,freshworld,freshworld,'new_stale_request')
  CRASHES.append(dict(id=key,request_ref=rq,output_ref=output,receipt_ref=receipt,response_ref=res,before=w,after=after,cuts=['before_atomic_publication','after_atomic_publication']))
  return rq

 def metric_roots(b):
  roots={k:[b['view_ref'],b['state_ref']] for k in ('book_equity','gross_loans','allowance','goodwill')}
  risk=[b[k] for k in ('view_ref','state_ref','rule_ref','applicability_ref','exposure_ref','deduction_ref')]
  for k in ('cap_base','cap'):roots[k]=risk
  for k in ('admitted_allowance','excess_allowance','rwa','tier2'):roots[k]=risk+[b['allowance_ref']]
  eq=[b[k] for k in ('view_ref','state_ref','rule_ref','applicability_ref','eligibility_ref','deduction_ref')]
  for k in ('cet1','tier1'):roots[k]=eq
  roots['total_capital']=unique(eq+risk+[b['allowance_ref']])
  roots['leverage_denominator']=[b[k] for k in ('view_ref','state_ref','rule_ref','applicability_ref','deduction_ref')]+([b['average_ref']] if b['average_ref'] else [])
  return {k:unique(v) for k,v in roots.items()}

 for c in CAPITAL_CASES:
  key='capital.'+c['id'];ch=c['changes'];a,e,x,al,de=app,elig,exposure,allowance,deduction
  if 'applicability' in ch:a=copy_record(key+'.app',app,exclusions={**body(app)['exclusions'],**ch['applicability']})
  if 'eligibility' in ch:e=copy_record(key+'.elig',elig,conditions={**body(elig)['conditions'],**ch['eligibility']})
  if 'exposure' in ch:x=copy_record(key+'.exp',exposure,**ch['exposure'])
  if 'allowance' in ch:al=copy_record(key+'.allowance',allowance,all_eligible_aacl=ch['allowance'])
  if 'deduction' in ch:de=copy_record(key+'.deduction',deduction,goodwill_without_dtl=ch['deduction'])
  average=add('AverageAssets',key+'.average',dict(context_ref=ctx,evidence_ref=ev,period_start='2026-01-01',period_end_exclusive='2026-04-01',measure_kind='regulatory_average_total_assets',amount=q(c['average']))) if c['average'] is not None else None
  basis=add('AssessmentBasis',key+'.basis',dict(context_ref=ctx,state_ref=states[c['book']],view_ref=v0,rule_ref=rules,applicability_ref=a,eligibility_ref=e,exposure_ref=x,allowance_ref=al,deduction_ref=de,average_ref=average,assessment_date='2026-03-31',period_start='2026-01-01',period_end_exclusive='2026-04-01'))
  expected=wire(c['expected']);deps=metric_roots(body(basis))
  for k,value in expected['amounts'].items():value['dependency_refs']=deps[k]
  for k,ns in dict(cet1_ratio=('cet1','rwa'),tier1_ratio=('tier1','rwa'),total_ratio=('total_capital','rwa'),leverage_ratio=('tier1','leverage_denominator')).items():expected['ratios'][k]['dependency_refs']=unique(sum([deps[n] for n in ns],[]))
  output=add('RegulatoryAssessment',key+'.output',dict(basis_ref=basis,**expected,distribution_permission='unresolved_not_assessed',minimum_ratio_verdict='not_assessed',accounting_effect='none'))
  codes=sorted({code for section in expected.values() for m in section.values() for code in m['diagnostics']})
  publish(key,OPS[0],basis,output,v0,states[c['book']],codes,any(m['status']=='undefined' for m in expected['ratios'].values()))

 vint0=add('Vintage','vintage.original',dict(evidence_ref=ev,vintage_id='original',as_of_date='2026-04-01',supersedes_ref=None))
 vint1=add('Vintage','vintage.new',dict(evidence_ref=new_ev,vintage_id='new',as_of_date='2026-10-01',supersedes_ref=vint0))
 laws={}
 for key,vint,evr in [('original',vint0,ev),('new',vint1,new_ev)]:
  laws[key]=add('JointLaw','law.'+key,dict(context_ref=ctx,evidence_ref=evr,vintage_ref=vint,origin_date='2026-04-01',horizon_end_exclusive='2028-04-01',cells=wire(CELLS),support_status='complete_finite_synthetic',dependence='joint_cells_no_factorization',target='economic_discounted_cash_shortfall_not_accounting_allowance'))
 for c in LOSS_CASES:
  key='loss.'+c['id'];law=laws[c['vintage']];v=v2 if c['vintage']=='new' else v1 if c['condition'] else v0
  measure=add('Measure',key+'.measure',dict(law_ref=law,mode=c['mode'],candidates=[dict(law_id=n,weights=wire(w)) for n,w in c['candidates']],family_status='complete_declared_finite_family'))
  cond=add('Condition',key+'.condition',dict(kind='survived_through' if c['condition'] else 'all',survived_through=c['condition'],evidence_ref=cond_ev if c['condition'] else None))
  query=add('LossQuery',key+'.query',dict(context_ref=ctx,view_ref=v,measure_ref=measure,condition_ref=cond,origin_date=c['origin'],default_window_start=c['origin'],default_window_end_exclusive=c['end']))
  out=add('LossQueryResult',key+'.output',dict(query_ref=query,**wire(c['expected']),dependency_refs=[query]))
  publish(key,OPS[1],query,out,v,states['final'],c['expected']['diagnostics'])
 policy=add('PolicySpecification','policy',dict(context_ref=ctx,view_ref=v0,evidence_ref=ev,loss_result_ref=ALIASES['loss.original.output'],objective='maximize_cash_after_contractual_settlement',actions=[dict(action_id='fixed',kind='fixed_book',limit=q(0)),dict(action_id='draw',kind='secured_draw',limit=q(10)),dict(action_id='runoff',kind='contractual_runoff',limit=q(25))],constraints=dict(actual_settlements_only=True,no_fabricated_investor=True,respect_facility_limit=True,distribution_permission='unknown'),tie_break='lexicographic_action_id',failure_behavior='record_policy_failure_or_legal_default',calibration_status='not_calibrated'))
 po=add('PolicyQueryResult','policy.output',dict(policy_ref=policy,objective='maximize_cash_after_contractual_settlement',action_ids=['fixed','draw','runoff'],tie_break='lexicographic_action_id',selected_action=None,feasibility_status='not_evaluated',distribution_permission='unresolved_not_assessed',diagnostics=['policy_not_optimized','permissions_not_assessed'],accounting_effect='none'))
 publish('policy.describe',OPS[2],policy,po,v0,states['final'])

 # Adverse cases are added below before the immutable packet is written.
 build_adversaries(request,response,exchange,states,ctx,ev,v0,v1,v2,profile)
 snapshots={p.name:dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes())) for p in sorted((ART/'inputs').iterdir())}
 packet=dict(profile_ref=profile,record_registry=REG,aliases=ALIASES,blobs=BLOBS,cases=CASES,exchanges=EX,challenges=CHALLENGES,crash_cuts=CRASHES,input_snapshots=snapshots,source_manifest_blob=blob(ROOT/MANIFEST),source_review_blob=blob(ROOT/REVIEW),predecessor_lock_blob=blob(HERE/'predecessor-lock.json'),evidence_mode='specification_example_no_runtime')
 write(ART/'portable-exchanges.json',packet)
 write(ART/'build-run.json',dict(wall_seconds=time.monotonic()-start,records=len(REG),exchanges=len(EX),cases=len(CASES),challenges=len(CHALLENGES),packet_sha256=sha((ART/'portable-exchanges.json').read_bytes()),artifact=str(ART.relative_to(ROOT))))
 print(json.dumps(json.loads((ART/'build-run.json').read_text())))

def build_adversaries(request,response,exchange,states,ctx,ev,v0,v1,v2,profile):
 counter=0
 def alter(ref,path,value,label):
  def visit(v,parts):
   if not parts:return deepcopy(value)
   if isinstance(v,dict) and set(v)=={'kind','schema','digest'}:
    return add(v['kind'],label+'.'+str(len(ALIASES)),visit(body(v),parts))
   v=deepcopy(v);k=parts[0];v[k]=visit(v[k],parts[1:]);return v
  return visit(ref,list(path))
 def extended_view(ir,label):
  oldview=body(ir)['view_ref'];v=body(oldview)
  es=[dict(kind='Evidence',schema=REG[d]['schema'],digest=d) for d in closure([ir]) if REG[d]['kind']=='Evidence']
  nv=copy_record(label+'.view',oldview,evidence_refs=unique(es))
  return copy_record(label+'.input',ir,view_ref=nv)
 def input_case(name,base,path,value,code,extend=False,accept=False):
  ir=alter(base,path,value,'bad.'+name)
  if extend:ir=extended_view(ir,'bad.'+name)
  op=OPS[0] if ir['kind']=='AssessmentBasis' else OPS[1] if ir['kind']=='LossQuery' else OPS[2]
  CHALLENGES.append(dict(id=name,kind='input',operation=op,input_ref=ir,expected_code='accepted' if accept else code))
  if not accept:
   # Full refusal exchange for every typed semantic adversary.
   st=body(ir)['state_ref'] if op==OPS[0] else states['final'];v=body(ir)['view_ref']
   rq,sub=request('adverse.'+name,op,ir,v,st)
   w=world(st,v,rq);res=response('adverse.'+name,rq,sub,disposition='rejected',codes=[code])
   exchange('adverse.'+name,rq,sub,res,w,w,'semantic_refusal')
  return ir
 cap=ALIASES['capital.final.basis'];lq=ALIASES['loss.original.query'];survival=ALIASES['loss.survival.query']
 for name,path,value,code in [
  ('closing-assets-average',('average_ref','measure_kind'),'period_end_total_assets','average_kind_mismatch'),
  ('wrong-average-period',('average_ref','period_start'),'2026-02-01','average_period_mismatch'),
  ('negative-average',('average_ref','amount'),q(-1),'negative_average_assets'),
  ('wrong-perimeter',('average_ref','context_ref','perimeter_id'),'Group','context_mismatch'),
  ('wrong-assessment-date',('assessment_date',),'2026-03-30','assessment_date_mismatch'),
  ('wrong-period-end',('period_end_exclusive',),'2026-04-02','assessment_period_mismatch'),
  ('unadmitted-quarter',('period_start',),'2025-12-01','scenario_window_mismatch'),
  ('unsupported-PCD',('exposure_ref','loan_class'),'PCD','unsupported_exposure'),
  ('unsupported-nonaccrual',('exposure_ref','loan_class'),'nonaccrual','unsupported_exposure'),
  ('commercial-bank-cash',('exposure_ref','reserve_venue'),'commercial_bank','unsupported_exposure'),
  ('unsupported-market-risk',('applicability_ref','exclusions','market_risk'),'present','unsupported_regime'),
  ('unsupported-transition',('applicability_ref','exclusions','cecl_transition'),'present','unsupported_regime'),
  ('ineligible-allowance',('allowance_ref','all_eligible_aacl'),'no','unsupported_allowance'),
  ('goodwill-DTL-mismatch',('deduction_ref','goodwill_without_dtl'),'no','unsupported_deduction'),
  ('incomplete-rule-sources',('rule_ref','source_refs'),body(ALIASES['rules'])['source_refs'][:-1],'rule_package_mismatch'),
  ('wrong-posted-journal',('state_ref','posted_journals',0,'lines',0,'signed_amount'),q(-19),'accounting_journal_mismatch'),
  ('wrong-closing-book',('state_ref','balances','cash'),q(22),'accounting_state_mismatch'),
  ('unpaid-obligation-erased',('state_ref','unpaid_withdrawal'),q(9),'unpaid_withdrawal_mismatch'),
  ('event-after-book-date',('state_ref','event_refs',0,'event_date'),'2026-04-02','event_date_mismatch'),
  ('event-before-opening-date',('state_ref','event_refs',0,'event_date'),'2025-12-31','event_date_mismatch'),
  ('opening-after-book-date',('state_ref','opening_asof_date'),'2026-04-02','event_date_mismatch'),
  ('sequence-gap',('state_ref','sequence'),99,'state_sequence_mismatch'),
  ('facility-overdraw',('state_ref','facility_ref','limit'),q(-1),'facility_limit_exceeded')]:input_case(name,cap,path,value,code)
 for i in range(1,14):input_case('failed-stock-'+str(i),cap,('eligibility_ref','conditions','condition_'+str(i)),'failed','stock_eligibility_failed')
 for name,path,value,code in [
  ('future-average-evidence',('average_ref','evidence_ref','available_at'),'2026-04-01T00:00:01Z','later_information'),
  ('later-average-ingestion',('average_ref','evidence_ref','ingested_at'),'2026-04-01T00:00:01Z','later_ingestion'),
  ('future-average-measurement',('average_ref','evidence_ref','measurement_asof'),'2026-04-02','future_measurement')]:input_case(name,cap,path,value,code,True)
 input_case('missing-evidence-membership',cap,('average_ref','evidence_ref','evidence_id'),'unlisted','evidence_not_in_view')
 input_case('equal-instant-offset',cap,('average_ref','evidence_ref','available_at'),'2026-04-01T01:00:00+01:00','accepted',True,True)
 for name,path,value,code in [
  ('negative-law-weight',('measure_ref','candidates',0,'weights',0),q(-1),'invalid_probability_measure'),
  ('unnormalized-law',('measure_ref','candidates',0,'weights',0),q('1/5'),'invalid_probability_measure'),
  ('invented-unweighted-probability',('measure_ref','mode'),'unweighted_histories','measure_mode_weights'),
  ('missing-point-law',('measure_ref','candidates'),[],'measure_mode_weights'),
  ('broken-joint-shortfall',('measure_ref','law_ref','cells',0,'cash_shortfall'),q(25),'joint_shortfall_mismatch'),
  ('duplicate-joint-cell',('measure_ref','law_ref','cells',1,'cell_id'),'early','duplicate_joint_cell'),
  ('no-default-nonzero-loss',('measure_ref','law_ref','cells',2,'ead'),q(1),'no_default_loss'),
  ('negative-discount',('measure_ref','law_ref','cells',0,'discount_factor'),q(-1),'invalid_joint_cell'),
  ('default-before-law-origin',('measure_ref','law_ref','cells',0,'default_date'),'2026-03-31','joint_cell_date_mismatch'),
  ('default-at-law-horizon',('measure_ref','law_ref','cells',1,'default_date'),'2028-04-01','joint_cell_date_mismatch'),
  ('window-outside-horizon',('default_window_end_exclusive',),'2028-04-02','loss_window_mismatch'),
  ('reversed-default-window',('default_window_start',),'2029-01-01','loss_window_mismatch'),
  ('window-before-query-origin',('default_window_start',),'2026-03-31','loss_window_mismatch'),
  ('later-vintage-early-query',('measure_ref','law_ref','vintage_ref','as_of_date'),'2026-10-01','vintage_origin_mismatch'),
  ('condition-without-date',('condition_ref','kind'),'survived_through','condition_shape_mismatch'),
  ('condition-without-evidence',('condition_ref','survived_through'),'2026-03-31','condition_shape_mismatch')]:input_case(name,lq,path,value,code)
 for name,path,value,code in [
  ('future-law-evidence',('measure_ref','law_ref','evidence_ref','available_at'),'2026-04-02T00:00:00Z','later_information'),
  ('later-vintage-ingestion',('measure_ref','law_ref','vintage_ref','evidence_ref','ingested_at'),'2026-04-02T00:00:00Z','later_ingestion')]:input_case(name,lq,path,value,code,True)
 input_case('future-survival-event',survival,('condition_ref','survived_through'),'2026-10-02','condition_date_mismatch')
 input_case('wrong-survival-evidence-date',survival,('condition_ref','evidence_ref','measurement_asof'),'2026-09-29','condition_evidence_date_mismatch',True)
 input_case('negative-policy-limit',ALIASES['policy'],('actions',0,'limit'),q(-1),'negative_policy_limit')
 input_case('duplicate-policy-action',ALIASES['policy'],('actions',1,'action_id'),'fixed','duplicate_policy_action')

 def candidate(name,output,path,value):
  b=deepcopy(body(output));v=b
  for key in path[:-1]:v=v[key]
  v[path[-1]]=value
  op=OPS[0] if output['kind']=='RegulatoryAssessment' else OPS[1] if output['kind']=='LossQueryResult' else OPS[2]
  ir=b[{OPS[0]:'basis_ref',OPS[1]:'query_ref',OPS[2]:'policy_ref'}[op]]
  CHALLENGES.append(dict(id=name,kind='output',operation=op,input_ref=ir,candidate=b,expected_code='query_output_mismatch'))
 out=ALIASES['capital.final.output']
 for name,path,value in [
  ('net-loans-as-exposure',('amounts','cap_base','value'),q('588/5')),
  ('circular-cap',('amounts','admitted_allowance','value'),q('588/395')),
  ('excess-not-subtracted',('amounts','rwa','value'),q(120)),
  ('goodwill-in-RWA',('amounts','rwa','value'),q('1211/10')),
  ('double-allowance-deduction',('amounts','cet1','value'),q('96/5')),
  ('closing-assets-leverage',('amounts','leverage_denominator','value'),q('693/5')),
  ('ratio-authorizes-payout',('distribution_permission',),'permitted'),
  ('minimum-compliance-invented',('minimum_ratio_verdict',),'passed'),
  ('missing-dependency',('amounts','cet1','dependency_refs'),[]),
  ('stock-unknown-coerced',('amounts','cet1','value'),q('108/5'))]:
  candidate(name,ALIASES['capital.unknown-stock-1.output'] if name=='stock-unknown-coerced' else out,path,value)
 candidate('missing-average-zero-ratio',ALIASES['capital.missing-average.output'],('ratios','leverage_ratio','value'),q(0))
 candidate('undefined-zero-ratio',ALIASES['capital.zero.output'],('ratios','cet1_ratio','value'),q(0))
 candidate('factorized-EAD-LGD',ALIASES['loss.original.output'],('expectation_values',),[q('45/4')])
 candidate('family-mixed-mean',ALIASES['loss.law-family.output'],('expectation_values',),[q('35/2')])
 candidate('row-count-uniform-law',ALIASES['loss.unweighted.output'],('expectation_values',),[q('100/3')])
 candidate('survival-called-new-forecast',ALIASES['loss.survival.output'],('expectation_values',),[q(10)])
 candidate('economic-loss-called-allowance',ALIASES['loss.original.output'],('accounting_allowance_claim',),True)
 candidate('zero-mass-normalized',ALIASES['loss.zero-mass.output'],('expectation_values',),[q(0)])
 candidate('invented-policy-choice',ALIASES['policy.output'],('selected_action',),'draw')

 # Closed-form and byte-level adversaries are isolated candidates, not registry
 # records admitted to the profile.
 rq=ALIASES['request.capital.final']
 for name,path,value in [('unknown-request-field',('body','extra'),'invented'),('old-operation',('body','operation'),'accounting.commit@1'),('old-profile-reference',('body','profile_ref','schema'),'accdsl.bank-components-v2.profile.v1'),('old-accounting-head',('body','expected_head','state_ref','schema'),'accdsl.corporate.companystate.v1')]:
  c=deepcopy(REG[rq['digest']]);v=c
  for p in path[:-1]:v=v[p]
  v[path[-1]]=value
  CHALLENGES.append(dict(id=name,kind='record',candidate=c,expected_code='closed_record_shape'))
 c=deepcopy(REG[ALIASES['rules']['digest']]);c['body']['snapshot']='2026-02-01'
 CHALLENGES.append(dict(id='changed-law-snapshot',kind='record',candidate=c,expected_code='closed_record_shape'))
 # Typed request failures get canonical bytes and complete refusal envelopes.
 for name,changes,code in [
  ('missing-capital-head',dict(expected_head=None),'expected_head_required'),
  ('stale-accounting-head',dict(expected_head=head(states['opening'])),'stale_accounting_head'),
  ('wrong-signature',dict(signature_ref=ALIASES['signature.'+OPS[1]]),'signature_mismatch'),
  ('operation-tag-disagrees',dict(operation=OPS[1]),'operation_tag_mismatch'),
  ('request-view-disagrees',dict(view_ref=v1),'request_view_mismatch'),
  ('zero-operation-budget',dict(execution={**body(rq)['execution'],'budget':dict(operation_count=0,elapsed_seconds=60)}),'budget_exhausted'),
  ('zero-time-budget',dict(execution={**body(rq)['execution'],'budget':dict(operation_count=1000,elapsed_seconds=0)}),'budget_exhausted')]:
  rr=copy_record('request.adverse.'+name,rq,request_id='adverse.'+name,**changes)
  p=ART/'bytes'/('request-adverse-'+name+'.json');p.write_bytes(enc(REG[rr['digest']]))
  sub=add('Submission','submission.adverse.'+name,dict(blob_ref=blob(p),media_type='application/json',transport='authored_fixture',decoder_ref=ALIASES['decoder']))
  w=world(states['final'],v0,rr)
  CHALLENGES.append(dict(id=name,kind='request',request_ref=rr,submission_ref=sub,world=w,expected_code=code))
  res=response('request-adverse.'+name,rr,sub,disposition='rejected',codes=[code])
  exchange('request-adverse.'+name,rr,sub,res,w,w,'request_refusal')
 for name,raw,code in [('duplicate-JSON-key','{"x":1,"x":2}','duplicate_key'),('float-JSON','{"x":0.1}','float_forbidden'),('nonfinite-JSON','{"x":NaN}','nonfinite_forbidden')]:CHALLENGES.append(dict(id=name,kind='raw',raw=raw,expected_code=code))
 for name,path,value in [('nonreduced-rational',('body','opening_balances','cash'),dict(n='60',d='2')),('rational-leading-zero',('body','opening_balances','cash'),dict(n='030',d='1'))]:
  c=deepcopy(REG[states['final']['digest']]);v=c
  for p in path[:-1]:v=v[p]
  v[path[-1]]=value
  CHALLENGES.append(dict(id=name,kind='record',candidate=c,expected_code='noncanonical_rational' if name=='nonreduced-rational' else 'closed_record_shape'))
 primary=next(e for e in EX if e['id']=='capital.final');receipt=body(primary['response_ref'])['receipt_ref']
 rejected=next(e for e in EX if e['id']=='request-adverse.missing-capital-head')
 for field,value in [('request_ref',rq),('submission_ref',primary['submission_ref']),('operation',OPS[1]),('input_view_ref',v1)]:
  bad=deepcopy(rejected);bad['response_ref']=copy_record('bad.refusal.'+field,rejected['response_ref'],**{field:value})
  CHALLENGES.append(dict(id='refusal-binding-'+field,kind='response',exchange=bad,expected_code='response_binding_mismatch'))
 partial=next(e for e in EX if e['id']=='capital.unknown-stock-1.replay')
 for name,changes in [('replay-erases-obligations',dict(unresolved=[])),('replay-upgrades-status',dict(statuses={**body(partial['response_ref'])['statuses'],'mathematical_status':'defined'}))]:
  bad=deepcopy(partial);bad['response_ref']=copy_record('bad.'+name,partial['response_ref'],**changes)
  CHALLENGES.append(dict(id=name,kind='response',exchange=bad,expected_code='replay_output_mismatch'))
 for name,change in [('receipt-only','receipt'),('output-only','output'),('index-only','index'),('query-posted-journal','journal'),('changed-accounting-head','head'),('changed-unrelated-owner','unrelated')]:
  bad=deepcopy(primary)
  if change in ('receipt','output','index'):
   bad['world_after']=deepcopy(primary['world_before'])
   if change in ('receipt','output'):bad['world_after']['published_records'].append((receipt if change=='receipt' else out)['digest']);bad['world_after']['published_records'].sort()
   else:bad['world_after']['query_index']=deepcopy(primary['world_after']['query_index'])
  elif change=='journal':bad['world_after']['journals'].append(dict(cash=q(1),stock=q(-1)))
  elif change=='head':bad['world_after']['accounting_heads'][head(states['final'])['owner_key']]['state_ref']=states['runoff25']
  else:bad['world_after']['unrelated_owners']['Other/Book']['generation']=8
  CHALLENGES.append(dict(id=name,kind='world',exchange=bad,output_ref=out,receipt_ref=receipt,expected_code='non_atomic_or_accounting_publication'))

if __name__=='__main__':main()
