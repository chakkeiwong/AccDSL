"""Finite actor-visible mappings bound to complete conditional timing families."""
from pathlib import Path
from copy import deepcopy as cp
import json,sys,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'temporal-family-binding-20261027'));import family as f
load=f.t.prior.load
policy=load('bound_observation_policy',H.parent/'cross-mechanism-policy-20261027/policy.py')
oracle=load('bound_observation_oracle',H.parent/'cross-mechanism-policy-20261027/oracle.py')
identity=f.identity;need=f.need;fields=f.fields
FLAGS={**f.t.FLAGS,'posting_authorization':False}
PROFILE='BoundActorObservationPolicy/1'
ACTIONS={'profile':'SelectedPayDraw/1','first':['pay','draw'],'second':['pay','draw'],'meaning':'unchanged_certified_financial_rows'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wirekey(x):return json.dumps(x,separators=(',',':'),ensure_ascii=False)
def canonical(x):return json.loads(json.dumps(x))
class Evidence(f.Evidence):
 def __init__(self):
  super().__init__();self.dependencies={}
  for folder,attempt in [('temporal-family-binding-20261027','attempt-01'),('cross-mechanism-policy-20261027','attempt-02')]:
   p=H.parent/folder/attempt/'source-lock.json';self.dependencies[str(p.relative_to(R))]=sha(p)
   for n,h in json.loads(p.read_text()).items():need(sha(R/n)==h,'protected_dependency:'+n);self.dependencies[n]=h
  self.binding_method_identity=identity({'binding.py':sha(Path(__file__)),'dependencies':self.dependencies})

def observation_keys(row,view):
 return list(row['obs1']) if view=='refined' else row['obs1'][:1],None if row['obs2'] is None else row['obs2'][-2:]
def table(entries,wanted,label):
 need(type(entries) is list,'mapping_list:'+label);got={}
 for item in entries:
  fields(item,['key','token'],'mapping_entry:'+label);need(type(item['key']) is list,'key_list')
  need(isinstance(item['token'],str) and 0<len(item['token'])<=80,'bounded_message_token')
  k=wirekey(item['key']);need(k not in got,'duplicate_mapping_key:'+label);got[k]=item['token']
 need(set(got)==wanted,'exact_observation_key_population:'+label);return got

def prepare(b,bhash,d,dhash,e):
 f.verify(b,bhash,b['input_sha256'],e);need(isinstance(dhash,str) and identity(d)==dhash,'external_declaration_identity')
 fields(d,['profile','family_sha256','actor','first_at','second_at','actions','maps','tag_observations','trusted_tag_observations'],'declaration_fields')
 need(d['profile']=='FiniteActorObservationMap/1' and d['family_sha256']==bhash,'declared_family_binding');need(d['actor']==b['input']['request']['actor'],'declared_actor_binding')
 t1,t2=f.t.instant(d['first_at']),f.t.instant(d['second_at']);need(t1==f.t.instant(b['input']['request']['decision_at']) and t1<t2,'exact_decision_dates')
 need(d['actions']==ACTIONS,'supported_action_meanings');need(type(d['maps']) is list,'maps_list');need(type(d['tag_observations']) is dict,'tag_registry')
 trust=d['trusted_tag_observations'];need(type(trust) is list and trust==sorted(set(trust)) and set(trust)<=set(d['tag_observations']),'explicit_tag_trust')
 selected={i['outcome_sha256']:i for i in b['outcomes'] if i['outcome']['status']=='selected_conditional'}
 maps={};references=set();issues=[];rows=[]
 for m in d['maps']:
  fields(m,['outcome_sha256','source_head','source_sha256','first','second','tag'],'map_fields');oid=m['outcome_sha256'];need(oid in selected and oid not in maps,'unique_known_outcome_map');maps[oid]=m
 need(set(maps)==set(selected),'full_selected_outcome_map_population')
 for oid,item in sorted(selected.items()):
  o=item['outcome'];head=o['heads']['observation_scheme'];record=b['input']['registry'][head];m=maps[oid]
  need(m['source_head']==head and m['source_sha256']==record['source_sha256'],'map_source_binding')
  s=o['scenario'];source_rows=[r for r in e.rows if r['receipt']==s['receipt'] and (s['family']=='mixed' or r['right'])]
  k1={wirekey(observation_keys(r,s['view'])[0]) for r in source_rows};k2={wirekey(observation_keys(r,s['view'])[1]) for r in source_rows if r['obs2'] is not None}
  first=table(m['first'],k1,'first');second=table(m['second'],k2,'second');tag=m['tag'];need(type(tag) is dict,'tag_declaration')
  reveal=tag.get('reveal');need(reveal in ('never','first','second'),'tag_reveal_scope');token=None
  if reveal=='never':fields(tag,['reveal'],'hidden_tag_fields')
  else:
   fields(tag,['reveal','observation_sha256'],'visible_tag_fields');digest=tag['observation_sha256'];references.add(digest);need(digest in d['tag_observations'],'missing_tag_evidence');obs=d['tag_observations'][digest]
   fields(obs,['profile','actor','source_head','source_sha256','token','at','provenance'],'tag_observation_fields');need(identity(obs)==digest,'tag_observation_identity')
   need(obs['profile']=='SyntheticActorTag/1' and obs['provenance']=='supplied_synthetic_assumption_not_actual_knowledge','tag_observation_profile')
   need(obs['actor']==d['actor'] and obs['source_head']==head and obs['source_sha256']==record['source_sha256'],'tag_source_actor_binding')
   need(isinstance(obs['token'],str) and 0<len(obs['token'])<=80,'tag_token');token=obs['token']
   at=f.t.bounds(obs['at']);need(at is None or at[0]==at[1],'tag_point_or_unknown_only')
   if digest not in trust or at is None:issues.append({'outcome':oid,'reason':'tag_availability_unknown'})
   elif at[0]>(t1 if reveal=='first' else t2):issues.append({'outcome':oid,'reason':'tag_received_after_claimed_decision'})
   else:
    authored=b['prepared']['clocks'][head+':authored'];bound=f.t.bounds(authored['original']) if authored['trusted'] else None
    if bound is None or bound[1]>at[0]:issues.append({'outcome':oid,'reason':'tag_authorship_order_unresolved'})
  for r in source_rows:
   a,z=observation_keys(r,s['view']);row={'id':oid+'/'+r['row_id'],'support':r['row_id'],'mechanism':oid,'a1':r['a1'],'a2':r['a2'],'message1':wirekey([first[wirekey(a)],token if reveal=='first' else None]),'message2':None if z is None else [second[wirekey(z)],token if reveal in ('first','second') else ''],'status':r['status']}
   rows.append(row)
 need(references==set(d['tag_observations']),'no_unreferenced_tag_evidence')
 status='complete_conditional'
 if not b['temporal_complete']:status='unresolved_timing_budget'
 elif b['temporal']['status']=='inconsistent_clocks':status='inconsistent_clocks'
 elif any(i['outcome']['status']=='unresolved' for i in b['outcomes']):status='unresolved_observation_map'
 elif issues:status='unresolved_tag_availability'
 bound={'family_sha256':bhash,'declaration_sha256':dhash,'actor':d['actor'],'decision_times':[str(t1),str(t2)],'source_outcomes':cp(b['outcomes']),'temporal_supports':cp(b['supports']),'temporal_remainder':cp(b['remainder']),'issues':issues}
 if status!='complete_conditional':return status,bound,[],None
 # Share only identical numeric row/message constraints; retain all original supports separately.
 unique={}
 for r in rows:
  payload={k:v for k,v in r.items() if k not in ('id','mechanism')};unique[identity(payload)]=payload
 kernel_rows=[{'id':k,'mechanism':'hidden',**unique[k]} for k in sorted(unique)]
 kernel={'rows':kernel_rows,'actions':ACTIONS,'evidence_identity':e.audit_identity,'method_identity':e.binding_method_identity,'solver_reveal':'never'}
 return status,bound,rows,kernel

def verify_previous(prior,expected,e):
 need(isinstance(expected,str) and identity(prior)==expected,'external_prior_identity');need(prior['status']=='complete_conditional','complete_prior_required')
 status,binding,rows,kernel=prepare(prior['family'],prior['binding']['family_sha256'],prior['declaration'],prior['binding']['declaration_sha256'],e)
 need(status==prior['status'] and binding==prior['binding'] and rows==prior['rows'] and kernel==prior['kernel'],'prior_full_binding')
 need(prior['kernel_sha256']==identity(kernel),'prior_kernel_identity');need(all(prior[k] is False for k in FLAGS),'prior_no_admission')
 got,_=oracle.solve(kernel['rows'],('pay','draw'),('pay','draw'),'never')
 need(prior['policies']==canonical(sorted(got,key=repr)) and prior['count']==len(got),'prior_complete_policy_payload')

def evaluate(b,bhash,d,dhash,e,previous=None,expected_prior=None):
 status,bound,rows,kernel=prepare(b,bhash,d,dhash,e)
 if previous is not None:verify_previous(previous,expected_prior,e)
 base={'profile':PROFILE,**FLAGS,'status':status,'family':cp(b),'declaration':cp(d),'binding':bound,'rows':rows,'kernel':kernel,'kernel_sha256':identity(kernel) if kernel else None,'policies':None,'count':None,'reused':False,'binding_changed':previous is None or previous['binding']!=bound}
 if status!='complete_conditional':return base
 if previous is not None and kernel==previous['kernel']:
  base.update(policies=cp(previous['policies']),count=previous['count'],reused=True)
 else:
  actual=policy.solve(kernel['rows'],('pay','draw'),('pay','draw'),'never');want,_=oracle.solve(kernel['rows'],('pay','draw'),('pay','draw'),'never');need(actual==want,'independent_common_policy_set')
  base.update(policies=canonical(sorted(actual,key=repr)),count=len(actual))
 return base
