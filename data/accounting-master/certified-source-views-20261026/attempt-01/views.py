"""Conditional immutable source-view adapter; unweighted robust policy sets only."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import importlib.util,json,re,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'company-policy-information-20261023'))
import policy_information as clocks

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
iv=load('certified_view_identity',HERE.parent/'inference-vintage-20261026/inference.py')
policy=load('certified_view_policy',HERE.parent/'certified-observation-policy-20261026/policies.py')
independent=load('certified_view_constraint',HERE.parent/'certified-observation-policy-20261026/constraint_oracle.py')
identity=iv.identity;instant=iv._time.instant
PROFILE='CertifiedSourcePolicyView/1';SLOTS=('financial_family','observation_scheme')
FLAGS=dict(source_admission=False,accounting_admission=False,actual_actor_knowledge=False,forecast_admission=False)

def need(x,msg):
 if not x:raise ValueError(msg)
def fields(x,keys,msg):need(type(x) is dict and set(x)==set(keys),msg)
def stamp(s):
 need(isinstance(s,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',s),'whole_second_UTC_only');return instant(s)
def tag(t):
 if t.get('status')=='unknown':fields(t,['status','reason'],'unknown_time_fields');need(bool(t['reason']),'unknown_reason');return None
 fields(t,['status','value'],'time_fields');need(t['status']=='known','time_status');return stamp(t['value'])
def component(record):return identity({k:record[k] for k in ['slot','information_id','source_sha256','payload','effective_at','disposition']})
def observation(record,ref,observations,trusted,event,actor=None):
 if ref.get('status')=='unknown':fields(ref,['status','reason'],'unknown_reference');need(bool(ref['reason']),'unknown_reason');return None
 fields(ref,['status','observation_sha256'],'observation_ref');need(ref['status']=='observed_synthetic','synthetic_ref')
 h=ref['observation_sha256'];need(h in observations,'observation_missing');o=observations[h];need(identity(o)==h,'observation_identity')
 need(o['component_sha256']==component(record),'observation_component');need(o['provenance']=='authored_test_clock_not_historical_evidence','observation_provenance')
 if event=='accessed':
  fields(o,['profile','component_sha256','actor','time','provenance'],'actor_access_fields');need(o['profile']=='SyntheticActorAccess/1' and o['actor']==actor,'actor_access_identity')
 else:
  fields(o,['profile','component_sha256','event','audience','time','precision','provenance'],'clock_fields');need(o['profile']=='SyntheticInformationObservation/1' and o['event']==event and o['precision']=='utc_instant' and o['audience'] in ['public','internal'],'clock_identity')
 value=stamp(o['time']);return value if h in trusted else None

def select(request,registry,sources,observations,trusted):
 """Every call rescans relevant revisions. Trusted hashes come from caller."""
 try:
  fields(request,['profile','actor','decision_at','system_asof','effective_at'],'request_fields');need(request['profile']==PROFILE,'profile');need(isinstance(request['actor'],str) and request['actor'],'actor')
  cut={k:stamp(request[k]) for k in ['decision_at','system_asof','effective_at']};need(type(registry) is dict and type(sources) is dict and type(observations) is dict,'registry_maps');need(type(trusted) is frozenset,'caller_trust_set')
  relevant={h:r for h,r in registry.items() if r.get('slot') in SLOTS};states={};reasons={};all_times={}
  for h,r in relevant.items():
   fields(r,['profile','slot','information_id','source_sha256','payload','effective_at','disposition','supersedes','access','events'],'record_fields')
   need(identity(r)==h and r['profile']=='SyntheticScenarioSource/1','record_identity');need(r['information_id']==r['slot'],'information_identity')
   sh=r['source_sha256'];need(sh in sources and isinstance(sources[sh],str) and iv.source_identity(sources[sh])==sh,'source_identity');need(r['disposition'] in ['assertion','retraction'],'disposition')
   if r['disposition']=='retraction':need(r['payload'] is None,'retraction_payload')
   elif r['slot']=='financial_family':
    fields(r['payload'],['receipt','family'],'financial_payload');need(type(r['payload']['receipt']) is int and r['payload']['receipt'] in [6,7] and r['payload']['family'] in ['mixed','committed'],'supported_financial_family')
   else:fields(r['payload'],['view'],'observation_payload');need(r['payload']['view'] in ['coarse','refined'],'supported_observation_scheme')
   effective=tag(r['effective_at']);fields(r['events'],clocks.EVENTS,'clock_coverage');need(type(r['access']) is dict,'access_map')
   access=observation(r,r['access'].get(request['actor'],{'status':'unknown','reason':'actor absent'}),observations,trusted,'accessed',request['actor'])
   times={event:observation(r,ref,observations,trusted,event) for event,ref in r['events'].items()};all_times[h]={**times,'accessed':access,'effective':effective}
   item={'slot':r['slot'],'component_sha256':component(r),'events':r['events']}
   # Shared predecessor checker retains publication vs ingestion/review distinction.
   public=clocks._clocks([item],observations,trusted,'investor_information',request['decision_at'])
   system=clocks._clocks([item],observations,trusted,'system_as_of',request['system_asof'])
   if times['authored'] is not None and access is not None:need(times['authored']<=access,'access_before_authorship')
   future=(effective is not None and effective>cut['effective_at']) or (access is not None and access>cut['decision_at']) or 'ineligible' in [public['status'],system['status']]
   unknown=effective is None or access is None or 'unresolved' in [public['status'],system['status']]
   states[h]='excluded_future' if future else 'unresolved' if unknown else 'eligible';reasons[h]={'publication':public,'system':system,'access_known':access is not None,'effective_known':effective is not None}
  ancestors={}
  for h,r in relevant.items():
   seen=set();current=r['supersedes'];child=h
   while current is not None:
    need(current in relevant,'missing_ancestry');need(current not in seen and current!=h,'replacement_cycle');seen.add(current);parent=relevant[current]
    need(parent['slot']==r['slot'] and parent['information_id']==r['information_id'],'replacement_slot')
    for event in ['authored','published','ingested','accepted','accessed']:
     a,b=all_times[current][event],all_times[child][event]
     if a is not None and b is not None:need(a<=b,'replacement_clock_reversal:'+event)
    child=current;current=parent['supersedes']
   ancestors[h]=seen
  trace={'states':states,'clock_assessments':reasons,'scope':'closed_supplied_two_slot_registry; synthetic_public_document_access'}
  if any(s=='unresolved' for s in states.values()):return {**FLAGS,'status':'unresolved','reason':'relevant_revision_timing_unknown','trace':trace}
  eligible={h for h,s in states.items() if s=='eligible'};heads=eligible-set().union(*(ancestors[h] for h in eligible)) if eligible else set();selected={};closure={}
  for slot in SLOTS:
   match=sorted(h for h in heads if relevant[h]['slot']==slot)
   if len(match)!=1:return {**FLAGS,'status':'unresolved','reason':'missing_or_conflicting_slot:'+slot,'trace':trace}
   h=match[0]
   if relevant[h]['disposition']=='retraction':return {**FLAGS,'status':'unresolved','reason':'required_slot_retracted:'+slot,'trace':trace}
   if any(states[a]!='eligible' for a in ancestors[h]):return {**FLAGS,'status':'unresolved','reason':'ancestor_not_available','trace':trace}
   selected[slot]=h;closure[slot]=sorted({h}|ancestors[h])
  f=relevant[selected['financial_family']]['payload'];o=relevant[selected['observation_scheme']]['payload'];scenario={**f,**o}
  binding={'request':deepcopy(request),'heads':selected,'ancestry':closure,'scenario':scenario,'scope':trace['scope']}
  return {**FLAGS,'status':'selected_conditional','binding':binding,'binding_sha256':identity(binding),'trace':trace}
 except (ValueError,KeyError,TypeError,AttributeError,OverflowError) as e:return {**FLAGS,'status':'invalid','reason':str(e)}

def tuples(v):return tuple(tuples(x) for x in v) if isinstance(v,list) else v

def policy_result(selection,rows,comparisons,evidence_identity):
 need(selection['status']=='selected_conditional','selected_view_required');s=selection['binding']['scenario']
 chosen=[r for r in rows if r['receipt']==s['receipt'] and (s['family']=='mixed' or r['right'])]
 got,_=policy.enumerate_policies(chosen,s['view']);wanted,_=independent.solve(chosen,s['view']);need(got==wanted,'independent_policy_mismatch')
 old=next(x for x in comparisons if all(x[k]==s[k] for k in ['receipt','family','view']));need(got=={tuples(x) for x in old['feasible_policies']},'saved_policy_mismatch');need(len(chosen)==old['world_rows'],'row_population')
 dep={'view_binding':selection['binding_sha256'],'financial_rows':evidence_identity['rows'],'observation_method':evidence_identity['observations'],'policy_method':evidence_identity['policy'],'constraint_method':evidence_identity['constraint'],'saved_comparisons':evidence_identity['comparisons']}
 return {**FLAGS,'status':'complete_conditional','scenario':s,'dependency_sha256':identity(dep),'dependencies':dep,'binding':selection['binding'],'policy_set':json.loads(json.dumps(sorted(got,key=repr))),'count':len(got),'row_ids':[r['row_id'] for r in chosen],'policy_meaning':'complete reachable robust policies; no probabilities or optimality'}

def assess(request,registry,sources,observations,trusted,rows,comparisons,evidence_identity,previous=None):
 selection=select(request,registry,sources,observations,trusted)
 if selection['status']!='selected_conditional':return selection
 result=policy_result(selection,rows,comparisons,evidence_identity)
 result['reuse']='recomputed_no_prior' if previous is None else 'same_dependency_revalidated' if previous['dependency_sha256']==result['dependency_sha256'] else 'changed_dependency_recomputed'
 return result
