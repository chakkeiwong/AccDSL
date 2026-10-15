"""Author documentary exchanges; no independent calculation imported."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json,hashlib,shutil,time
from authored_cases import OPENING,EVENTS,EXPECTED_REPORTS
from schema_design import schemas,sid,ACCOUNTS
from migration_design import SPECS,projection,map_closed_result,projection_schema
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_bytes(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False).encode()+b'\n')
def refs(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from refs(x)
 elif isinstance(v,list):
  for x in v:yield from refs(x)
def vec(b):return {k:str(F(b.get(k,0))) for k in ACCOUNTS}
def main():
 started=time.monotonic();i=1
 while (HERE/f'attempt-{i:02}').exists():i+=1
 assert i<=5,'Refresh the evidence contract before further attempts'
 art=HERE/f'attempt-{i:02}';(art/'inputs').mkdir(parents=True);(art/'bytes').mkdir()
 for p in sorted(HERE.iterdir()):
  if p.suffix in ['.py','.md']:shutil.copyfile(p,art/'inputs'/p.name)
 schema=schemas();dump(art/'record-schemas.json',schema);reg={};alias={};blobs={}
 def blob(path):
  b=path.read_bytes();d=digest(b);meta=dict(path=str(path.relative_to(ROOT)),sha256=d,byte_length=len(b));blobs[d]=meta;return meta
 def add(kind,key,body):
  assert key not in alias;deps={enc(x):x for x in refs(body)}
  r=dict(kind=kind,schema=sid(kind),key=key,body=body,dependencies=[deps[k] for k in sorted(deps)])
  d=digest(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r));reg[d]=r;alias[key]=dict(kind=kind,schema=sid(kind),digest=d);return alias[key]
 def body(r):return reg[r['digest']]['body']
 def closure(roots):
  found=set()
  def visit(r):
   if r['digest'] in found:return
   found.add(r['digest'])
   for d in reg[r['digest']]['dependencies']:visit(d)
  for r in roots:visit(r)
  return sorted(found)
 lock=add('SchemaLock','lock',dict(schema=blob(art/'record-schemas.json'),contract=blob(art/'inputs/semantic-contract.md')))
 source=add('SourceSupport','source',dict(pdf=blob(ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf'),
  text=blob(ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'),reading=blob(art/'inputs/source-reading.md'),
  anchors=['IFRS10.20-24,B86-B96','IAS27.10','IAS7.14,16,17,31-35,42A-43','IFRS15.B21-B27','IAS2.16','IAS12.7-8,24,39,46-51,58','IAS32.28-32'],status='historical_conditional_not_current_admission'))
 profile=add('Profile','profile',dict(name='CompanyComposition/1',lock=lock,source=source,execution='documentary_only',sector='nonfinancial_corporate',interest_cash_policy='operating'))
 view=add('View','view',dict(profile=profile,revision=0,information_mode='archival_synthetic'))
 initial=deepcopy(OPENING);initial['books']={e:vec(b) for e,b in initial['books'].items()};initial.update(sequence=0,flows=[])
 initial_ref=add('State','opening',initial);states=[initial_ref]
 world=dict(head=initial_ref,view=view,receipts=[],proposals=[],decisions={},published=closure([initial_ref,view]),unaffected={'Other/Legal':'unchanged'})
 def request(key,operation,args,head,view_ref=view,identity=None):
  r=add('Request','request.'+key,dict(identity=identity or key,operation=operation,profile=profile,view=view_ref,head=head,arguments=args))
  path=art/'bytes'/(key+'.json');path.write_bytes(enc(reg[r['digest']]));blob(path);return r
 def result(key,r,status='completed',outputs=None,diagnostic=None):return add('Result','result.'+key,dict(request=r,status=status,diagnostic=diagnostic,outputs=outputs or []))
 exchanges=[];transitions=[];recoveries=[]
 for i,x in enumerate(EVENTS,1):
  key=x['id'];opening=states[-1];event=add('Event','event.'+key,x['event']);basis=add('Basis','basis.'+key,dict(opening=opening,event=event,view=view,profile=profile,event_identity=key))
  authorization=add('Authorization','authorization.'+key,dict(basis=basis,posting_permitted=True,facts='supplied_synthetic'))
  closing=deepcopy(body(opening));closing.update(deepcopy(x['changes']));closing.update(date=x['event']['date'],sequence=i)
  journals={e:vec(x['journals'].get(e,{})) for e in ['P','S']}
  closing['books']={e:{k:str(F(body(opening)['books'][e][k])+F(journals[e][k])) for k in ACCOUNTS} for e in ['P','S']}
  closing['flows'] += [dict(f,date=x['event']['date']) for f in x['cash']]
  closing_ref=add('State','state.'+key,closing);states.append(closing_ref)
  proposal=add('Proposal','proposal.'+key,dict(basis=basis,authorization=authorization,closing=closing_ref,journals=journals,cash=x['cash']))
  for op,args,out in [('authorize',dict(basis=basis),authorization),('propose',dict(basis=basis,authorization=authorization),proposal)]:
   rq=request(key+'.'+op,op,args,opening);res=result(key+'.'+op,rq,outputs=[out]);exchanges.append(dict(id=key+'.'+op,request=rq,result=res,before=deepcopy(world),after=deepcopy(world)))
  rq=request(key+'.commit','commit',dict(proposal=proposal),opening)
  receipt=add('Receipt','receipt.'+key,dict(request=rq,proposal=proposal,opening=opening,closing=closing_ref,generation=i))
  res=result(key+'.commit',rq,outputs=[receipt]);after=deepcopy(world);after['head']=closing_ref
  after['receipts'].append(receipt);after['proposals'].append(proposal);after['decisions'][key+'.commit']=dict(request=rq,result=res,receipt=receipt)
  after['published']=sorted(set(after['published'])|set(closure([receipt,res])))
  transition=dict(id=key+'.commit',request=rq,result=res,before=deepcopy(world),after=deepcopy(after))
  exchanges.append(transition);transitions.append(transition);recoveries.append(dict(request=rq,not_committed=deepcopy(world),committed=deepcopy(after),transport_observation='commit_unknown'))
  world=after
 reports=[]
 for key,r in EXPECTED_REPORTS.items():
  opening=states[0 if key!='h2' else 8];closing=states[r['through']];args=dict(opening=opening,closing=closing,start=r['start'],end=r['end'])
  rr=add('Report','report.'+key,dict(**args,group=r['group'],legal=r['legal'],scope='joined_finite_company_conditional'))
  rq=request('report.'+key,'report',args,world['head']);res=result('report.'+key,rq,outputs=[rr])
  ex=dict(id='report.'+key,request=rq,result=res,before=deepcopy(world),after=deepcopy(world));exchanges.append(ex);reports.append(ex)
 refusals=[
  ('redeem','original_rights_unchanged',None,'original_rights_missing','partial'),
  ('returns','handling_is_selling_cost',None,'handling_classification_missing','partial'),
  ('wages','service_received',None,'service_finding_missing','partial'),
  ('depreciate-h1','systematic_basis',None,'depreciation_basis_missing','partial'),
  ('internal-sale','buyer_amount','139','reciprocal_amount_mismatch','rejected'),
  ('external-h1','fraction','2','sale_amount_invalid','rejected'),
  ('internal-settle','payee_amount','139','reciprocal_cash_mismatch','rejected'),
  ('tax-h1','rate',None,'tax_rate_missing','partial'),
  ('tax-h1','temporary_difference_inventory_complete',None,'tax_temporary_difference_inventory_complete_missing','partial'),
  ('tax-h1','outside_basis_no_foreseeable_reversal',None,'tax_outside_basis_no_foreseeable_reversal_missing','partial'),
  ('nci-purchase','control_retained',False,'control_loss_requires_other_method','rejected'),
  ('nci-purchase','same_rights_per_share',None,'ownership_rights_missing','partial')]
 for n,(key,field,val,code,status) in enumerate(refusals):
  t=next(t for t in transitions if t['id']==key+'.commit');base=body(body(t['request'])['arguments']['proposal'])['basis'];b=deepcopy(body(base));e=deepcopy(body(b['event']));e['parameters'][field]=val
  label=f'adverse.{n}';b['event']=add('Event',label+'.event',e);b['event_identity']=label;br=add('Basis',label+'.basis',b)
  rq=request(label,'authorize',dict(basis=br),b['opening']);res=result(label,rq,status,diagnostic=code)
  exchanges.append(dict(id=label,request=rq,result=res,before=t['before'],after=t['before']))
 # Immutable identity replay at a later head/view, and conflicting bytes.
 replay_cases=[];later_view=add('View','view.later',dict(profile=profile,revision=1,information_mode='archival_synthetic'))
 for t in transitions:
  late=deepcopy(world);late['view']=later_view;late['published']=sorted(set(late['published'])|set(closure([later_view])))
  changed=deepcopy(body(t['request']));changed['head']=world['head'];changed['view']=later_view
  conflict=add('Request','conflict.'+t['id'],changed)
  replay_cases.append(dict(request=t['request'],later_world=late,stored_result=t['result'],conflicting_request=conflict))
 migrations=[];migration_schemas={}
 def must(ok,code,status='rejected'):
  assert ok,(code,status)
 for key,spec in SPECS.items():
  path=ROOT/spec['packet'];old=json.loads(path.read_text());sr=old['case_states'][spec['case']][spec['index']]
  migration_schemas[key]=projection_schema(json.loads((path.parent/'record-schemas.json').read_text()),key)
  t=next(t for t in old['transitions'] if t['opening_ref']==sr and t['method']==spec['method'])
  b=old['record_registry'][t['basis_ref']['digest']]['body'];event=old['record_registry'][b['event_ref']['digest']]['body']
  migrations.append(dict(subset=key,source_packet=blob(path),source_state_ref=sr,source_closing_ref=t['closing_ref'],
   source_schema=blob(path.parent/'record-schemas.json'),event=event,projected=projection(old,sr,key,must),
   expected_after=map_closed_result(old,t['closing_ref'],key)))
 dump(art/'migration-schemas.json',migration_schemas);blob(art/'migration-schemas.json')
 challenges=[]
 for t in transitions:
  for field in ['head','receipts','proposals','decisions','published','unaffected']:
   w=deepcopy(t['after']);w[field]=deepcopy(t['before'][field]) if field!='unaffected' else {'Other/Legal':'changed'}
   challenges.append(dict(id=t['id']+'.partial-'+field,kind='atomic',transition=t['id'],candidate=w,code='atomic_publication_mismatch'))
 for ex in reports:
  rr=body(ex['result'])['outputs'][0];rb=body(rr)
  for field in ['cash','profit','nci_profit','parent_equity','current_tax','deferred_tax','operating_receipts','operating_payments','financing_payments','interest_paid']:
   bad=deepcopy(rb);bad['group'][field]=str(F(bad['group'][field])+1)
   challenges.append(dict(id=ex['id']+'.'+field,kind='report',request=ex['request'],candidate=bad,code='report_financial_mismatch'))
 for t in transitions:
  prop=body(body(t['request'])['arguments']['proposal']);bad=deepcopy(prop)
  bad['journals']['P']['cash']=str(F(bad['journals']['P']['cash'])+1);bad['journals']['P']['capital']=str(F(bad['journals']['P']['capital'])-1)
  challenges.append(dict(id=t['id']+'.balanced-wrong-journal',kind='proposal',candidate=bad,code='proposal_financial_mismatch'))
 for key,spec in SPECS.items():
  m=next(m for m in migrations if m['subset']==key);bad=deepcopy(m['projected']);bad['owner']['entity_id']='P'
  challenges.append(dict(id='migration.'+key+'.rename',kind='migration_target',subset=key,candidate=bad,code='migration_projection_mismatch'))
 for label,patch,code in [('wrong-book',{'entities':['S','P']},'owner_mismatch'),('policy',{'same_policies':False},'group_admission_missing'),
   ('reporting-date',{'same_calendar':False},'group_admission_missing'),('investment-entity',{'noninvestment_entity':False},'group_admission_missing')]:
  bad=deepcopy(initial);bad.update(patch);challenges.append(dict(id='opening.'+label,kind='opening',candidate=bad,code=code))
 packet=dict(profile='CompanyComposition/1',record_registry=reg,aliases=alias,blobs=blobs,states=states,
  exchanges=exchanges,transitions=transitions,reports=reports,recoveries=recoveries,replays=replay_cases,
  initial_world=transitions[0]['before'],final_world=world,migrations=migrations,validation_challenges=challenges,build_wall_seconds=time.monotonic()-started,
  input_snapshots={p.name:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in sorted((art/'inputs').iterdir())},runtime_executed=False)
 dump(art/'portable-exchanges.json',packet)
 print(json.dumps(dict(attempt=str(art.relative_to(ROOT)),records=len(reg),transitions=len(transitions),reports=len(reports),exchanges=len(exchanges))))
if __name__=='__main__':main()
