"""Authored documentary fixtures and explicit expected cases; no actual company facts."""
from copy import deepcopy as cp
import hashlib,json

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def known(x):return {'status':'known','value':x}
def unknown():return {'status':'unknown','reason':'No supplied clock evidence'}
def make_record(slot,payload,text,supersedes=None,when='2026-01-01T00:00:00Z',effective='2026-01-01T00:00:00Z',access=None,event_times=None,disposition='assertion'):
 source=hashlib.sha256(text.encode()).hexdigest();r={'profile':'SyntheticScenarioSource/1','slot':slot,'information_id':slot,'source_sha256':source,'payload':payload,'effective_at':known(effective) if effective else unknown(),'disposition':disposition,'supersedes':supersedes,'access':{},'events':{}}
 comp=digest({k:r[k] for k in ['slot','information_id','source_sha256','payload','effective_at','disposition']});obs={}
 for e in ['authored','published','ingested','accepted']:
  value=(event_times or {}).get(e,when)
  if value is None:r['events'][e]=unknown();continue
  row={'profile':'SyntheticInformationObservation/1','component_sha256':comp,'event':e,'audience':'public' if e=='published' else 'internal','time':value,'precision':'utc_instant','provenance':'authored_test_clock_not_historical_evidence'};h=digest(row);obs[h]=row;r['events'][e]={'status':'observed_synthetic','observation_sha256':h}
 for actor,value in (access or {'Alice':when,'Bob':when}).items():
  if value is None:r['access'][actor]=unknown();continue
  row={'profile':'SyntheticActorAccess/1','component_sha256':comp,'actor':actor,'time':value,'provenance':'authored_test_clock_not_historical_evidence'};h=digest(row);obs[h]=row;r['access'][actor]={'status':'observed_synthetic','observation_sha256':h}
 return digest(r),r,{source:text},obs

def base():
 records={};sources={};observations={};names={}
 for slot,payload,text in [('financial_family',{'receipt':7,'family':'committed'},'Synthetic supplied receipt7 and committed family.'),('observation_scheme',{'view':'refined'},'Synthetic supplied coarse market signal plus coupon trigger.')]:
  h,r,s,o=make_record(slot,payload,text);records[h]=r;sources.update(s);observations.update(o);names[slot]=h
 req={'profile':'CertifiedSourcePolicyView/1','actor':'Alice','decision_at':'2026-01-02T00:00:00Z','system_asof':'2026-01-02T00:00:00Z','effective_at':'2026-01-02T00:00:00Z'}
 return {'request':req,'registry':records,'sources':sources,'observations':observations,'trusted':frozenset(observations),'names':names}

def add(f,slot,payload,text='Synthetic correction.',**kw):
 h,r,s,o=make_record(slot,payload,text,**kw);f['registry'][h]=r;f['sources'].update(s);f['observations'].update(o);f['trusted']=f['trusted']|frozenset(o);return h

def suite():
 out=[]
 def push(name,f,status,heads=None,scenario=None,reuse=None):
  out.append({'name':name,'fixture':f,'expected':{'status':status,'heads':heads,'scenario':scenario,'reuse':reuse}})
 def good(name,f,heads=None,scenario=None,reuse='changed_dependency_recomputed'):
  push(name,f,'complete_conditional',heads or f['names'],scenario or {'receipt':7,'family':'committed','view':'refined'},reuse)
 f=base();good('unchanged',f,reuse='same_dependency_revalidated')
 f=base();f['request']['actor']='Bob';good('different_actor_same_facts',f)
 f=base();f['request']['actor']='Carol';push('unknown_actor_access',f,'unresolved')
 f=base();f['registry']['unrelated']={'slot':'unrelated_management_note'};good('unrelated_slot',f,reuse='same_dependency_revalidated')
 f=base();h=add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],when='2026-01-03T00:00:00Z');good('future_correction_old_view',f,reuse='same_dependency_revalidated')
 f=base();h=add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],when='2026-01-02T00:00:00Z');heads={**f['names'],'observation_scheme':h};good('correction_available_at_boundary',f,heads,{'receipt':7,'family':'committed','view':'coarse'})
 f=base();h=add(f,'observation_scheme',{'view':'refined'},'Synthetic reissued same interpretation.',supersedes=f['names']['observation_scheme']);good('same_answer_new_source',f,{**f['names'],'observation_scheme':h})
 f=base();h=add(f,'financial_family',{'receipt':6,'family':'committed'},supersedes=f['names']['financial_family']);good('changed_receipt',f,{**f['names'],'financial_family':h},{'receipt':6,'family':'committed','view':'refined'})
 f=base();h=add(f,'financial_family',{'receipt':7,'family':'mixed'},supersedes=f['names']['financial_family']);good('changed_right_family',f,{**f['names'],'financial_family':h},{'receipt':7,'family':'mixed','view':'refined'})
 for event in ['published','ingested','accepted']:
  f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],event_times={event:'2026-01-03T00:00:00Z',**({'accepted':'2026-01-03T00:00:00Z'} if event=='ingested' else {})});good('future_'+event,f,reuse='same_dependency_revalidated')
 f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],access={'Alice':'2026-01-03T00:00:00Z','Bob':'2026-01-01T00:00:00Z'});good('published_but_not_accessed',f,reuse='same_dependency_revalidated')
 f=base();h=add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],access={'Alice':'2026-01-03T00:00:00Z','Bob':'2026-01-01T00:00:00Z'});f['request']['actor']='Bob';good('other_actor_accessed',f,{**f['names'],'observation_scheme':h},{'receipt':7,'family':'committed','view':'coarse'})
 f=base();h=add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],event_times={'ingested':'2026-01-03T00:00:00Z','accepted':'2026-01-04T00:00:00Z'});f['request']['system_asof']='2026-01-04T00:00:00Z';good('later_system_reconstructs_earlier_access',f,{**f['names'],'observation_scheme':h},{'receipt':7,'family':'committed','view':'coarse'})
 f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],effective='2026-01-03T00:00:00Z');good('future_economic_effect',f,reuse='same_dependency_revalidated')
 f=base();h=add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],effective='2026-01-03T00:00:00Z');f['request']['effective_at']='2026-01-03T00:00:00Z';good('effective_boundary',f,{**f['names'],'observation_scheme':h},{'receipt':7,'family':'committed','view':'coarse'})
 for event in ['authored','published','ingested','accepted']:
  f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],event_times={event:None});push('unknown_'+event,f,'unresolved')
 f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],access={'Alice':None});push('unknown_access',f,'unresolved')
 f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],effective=None);push('unknown_effective',f,'unresolved')
 f=base();add(f,'observation_scheme',None,supersedes=f['names']['observation_scheme'],disposition='retraction');push('retracted_required_scheme',f,'unresolved')
 f=base();add(f,'observation_scheme',{'view':'coarse'},supersedes=None);push('conflicting_available_heads',f,'unresolved')
 f=base();f['trusted']=frozenset();push('untrusted_clock_evidence',f,'unresolved')
 f=base();f['request']['system_asof']='2026-01-01T00:00:00Z';good('different_system_cutoff_same_heads',f)
 f=base();f['request']['decision_at']='2026-01-01T00:00:00Z';good('different_decision_cutoff_same_heads',f)
 f=base();f['request']['effective_at']='2026-01-01T00:00:00Z';good('different_effective_cutoff_same_heads',f)
 return out
