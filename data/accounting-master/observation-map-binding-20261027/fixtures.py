"""Source-bound synthetic declarations; expected outcomes fixed before full execution."""
from copy import deepcopy as cp
import json
import binding as m
SAVED=m.H.parent/'temporal-family-binding-20261027/attempt-01/cases.json'
FAMILIES={r['case']:r['reused'] for r in json.loads(SAVED.read_text())}

def declaration(b,e,swapped=False,reveal='never',collision=False,rename=False,tag_time=None):
 d={'profile':'FiniteActorObservationMap/1','family_sha256':m.identity(b),'actor':b['input']['request']['actor'],'first_at':b['input']['request']['decision_at'],'second_at':'2026-01-03T00:00:00Z','actions':cp(m.ACTIONS),'maps':[],'tag_observations':{},'trusted_tag_observations':[]}
 for i,item in enumerate(b['outcomes']):
  if item['outcome']['status']!='selected_conditional':continue
  o=item['outcome'];s=o['scenario'];h=o['heads']['observation_scheme'];r=b['input']['registry'][h]
  rows=[x for x in e.rows if x['receipt']==s['receipt'] and (s['family']=='mixed' or x['right'])]
  first={tuple(x['obs1']) if s['view']=='refined' else (x['obs1'][0],) for x in rows};second={tuple(x['obs2'][-2:]) for x in rows if x['obs2'] is not None}
  def first_token(k):
   if len(k)==1:out='L' if k[0]=='low' else 'H'
   else:out='L' if k[0]=='low' else 'X' if k[1] else 'H'
   if swapped and i==1:out={'H':'X','X':'H','L':'L'}[out]
   return 'renamed_'+out if rename else out
  entry={'outcome_sha256':item['outcome_sha256'],'source_head':h,'source_sha256':r['source_sha256'],'first':[{'key':list(k),'token':first_token(k)} for k in sorted(first,key=repr)],'second':[{'key':list(k),'token':'trigger='+str(k[0])+';covers='+str(k[1])} for k in sorted(second,key=repr)],'tag':{'reveal':'never'}}
  if reveal!='never':
   obs={'profile':'SyntheticActorTag/1','actor':d['actor'],'source_head':h,'source_sha256':r['source_sha256'],'token':'same' if collision else 'channel'+str(i),'at':cp(tag_time) if tag_time else {'kind':'point','value':d['first_at'] if reveal=='first' else d['second_at']},'provenance':'supplied_synthetic_assumption_not_actual_knowledge'}
   digest=m.identity(obs);d['tag_observations'][digest]=obs;d['trusted_tag_observations'].append(digest);entry['tag']={'reveal':reveal,'observation_sha256':digest}
  d['maps'].append(entry)
 d['trusted_tag_observations'].sort();return d

def suite(e):
 def case(name,family='baseline',count=4,reuse=True,status='complete_conditional',**kw):
  b=cp(FAMILIES[family]);return {'name':name,'family':b,'declaration':declaration(b,e,**kw),'expected_count':count,'expected_reuse':reuse,'expected_status':status}
 out=[case('baseline'),case('same_meaning_correction','same_meaning_new_source'),case('different_actor','changed_actor_same_semantics'),case('changed_message_labels',rename=True,reuse=False),case('two_same_meaning_sources','two_source_supports_one_policy'),case('swapped_hidden','two_source_supports_one_policy',swapped=True,count=0,reuse=False),case('swapped_first_tag','two_source_supports_one_policy',swapped=True,reveal='first',count=16,reuse=False),case('swapped_second_tag','two_source_supports_one_policy',swapped=True,reveal='second',count=0,reuse=False),case('swapped_colliding_first_tag','two_source_supports_one_policy',swapped=True,reveal='first',collision=True,count=0,reuse=False),case('same_maps_first_tag','two_source_supports_one_policy',reveal='first',count=16,reuse=False),case('same_maps_second_tag','two_source_supports_one_policy',reveal='second',count=16,reuse=False),case('same_maps_colliding_tag','two_source_supports_one_policy',reveal='first',collision=True,count=4,reuse=False),case('coarse_refined_family','correction_access_straddles',count=0,reuse=False),case('changed_financial_receipt','financial_correction_receipt6',count=0,reuse=False),case('unknown_source_access','unknown_access',count=None,reuse=False,status='unresolved_observation_map'),case('budget_family','budget_whole_domain',count=None,reuse=False,status='unresolved_timing_budget'),case('inconsistent_clocks','public_access_before_publication',count=None,reuse=False,status='inconsistent_clocks'),case('late_first_tag',reveal='first',tag_time={'kind':'point','value':'2026-01-02T00:00:00.0000001Z'},count=None,reuse=False,status='unresolved_tag_availability'),case('unknown_tag',reveal='first',tag_time={'kind':'unknown','reason':'No evidence'},count=None,reuse=False,status='unresolved_tag_availability'),case('tag_before_authorship',reveal='first',tag_time={'kind':'point','value':'2025-01-01T00:00:00Z'},count=None,reuse=False,status='unresolved_tag_availability')]
 x=case('equivalent_offset_dates');x['declaration']['first_at']='2026-01-02T08:00:00+08:00';x['declaration']['second_at']='2026-01-03T08:00:00+08:00';out.append(x)
 x=case('untrusted_tag',reveal='first',count=None,reuse=False,status='unresolved_tag_availability');x['declaration']['trusted_tag_observations']=[];out.append(x)
 return out
