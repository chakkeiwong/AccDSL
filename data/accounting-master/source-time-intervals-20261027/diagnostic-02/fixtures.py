"""Synthetic clocks. Expected boundary cases are authored independently."""
from copy import deepcopy as cp
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'certified-source-views-20261026'))
import cases as oldcases
from temporal import identity,component,PROFILE

def point(s):return {'kind':'point','value':s}
def unknown():return {'kind':'unknown','reason':'No admitted clock observation'}
def interval(a,b):return {'kind':'interval','start':a,'end':b}

def convert(f,changes=None,cutoffs=None):
 changes=changes or {};out={'request':{**f['request'],'profile':PROFILE},'registry':{},'sources':cp(f['sources']),'observations':{},'trusted':frozenset(),'names':{}};mapping={}
 if cutoffs:out['request'].update(cutoffs)
 def build(h):
  if h in mapping:return mapping[h]
  r=f['registry'][h]
  if r.get('slot') not in ('financial_family','observation_scheme'):out['registry'][h]=cp(r);return h
  ch=changes.get(h,{});new={k:cp(r[k]) for k in ['slot','information_id','source_sha256','payload','disposition']};new.update(profile='SyntheticScenarioSource/2',supersedes=build(r['supersedes']) if r['supersedes'] else None,access={},events={})
  new['effective_at']=cp(ch.get('effective',point(r['effective_at']['value']) if r['effective_at']['status']=='known' else unknown()))
  comp=component(new)
  def obs(event,ref,actor=None,route=None):
   key='access:'+actor if event=='accessed' else event
   if key in ch:clock=cp(ch[key]);trusted=True
   elif ref.get('status')=='unknown':return cp(ref)
   else:original=f['observations'][ref['observation_sha256']];clock=point(original['time']);trusted=ref['observation_sha256'] in f['trusted']
   audience=route if event=='accessed' else ch.get('publication_channel','public') if event=='published' else 'internal'
   o={'profile':'SyntheticExactClock/1','component_sha256':comp,'event':event,'subject':actor if actor else 'source_system','channel':audience,'clock':clock,'provenance':'authored_test_clock_not_historical_evidence'};key=identity(o);out['observations'][key]=o
   if trusted:out['trusted']=out['trusted']|frozenset([key])
   return {'status':'observed_synthetic','observation_sha256':key}
  for event,ref in r['events'].items():new['events'][event]=obs(event,ref)
  actors=set(r['access'])|{f['request']['actor']}
  for actor in actors:
   route=ch.get('route:'+actor,'public_document');new['access'][actor]={'route':route,'observation':obs('accessed',r['access'].get(actor,{'status':'unknown','reason':'Actor access absent'}),actor,route)}
  nh=identity(new);mapping[h]=nh;out['registry'][nh]=new;return nh
 for h in f['registry']:build(h)
 out['names']={k:mapping[h] for k,h in f['names'].items()};out['mapping']=mapping
 return out

def extended_cases():
 out=[]
 def push(name,f,changes,wanted,cutoffs=None):out.append((name,convert(f,changes,cutoffs),wanted))
 base=oldcases.base();h=base['names']['observation_scheme']
 d='2026-01-02T00:00:00Z';later='2026-01-02T00:00:00.0000001Z';before='2026-01-01T23:59:59.9999999Z'
 # Labels in expected sets describe selected observation schemes; "missing" is a retained unresolved view.
 push('exact_at_cutoff',base,{h:{'access:Alice':point(d)}},{'refined'})
 push('submicrosecond_after_cutoff',base,{h:{'access:Alice':point(later)}},{'missing'})
 push('equivalent_fixed_offset',base,{h:{'access:Alice':point('2026-01-02T08:00:00+08:00')}},{'refined'})
 push('exclusive_end_at_cutoff',base,{h:{'access:Alice':interval(before,d)}},{'refined'})
 push('interval_begins_at_cutoff',base,{h:{'access:Alice':interval(d,later)}},{'refined','missing'})
 push('day_begins_at_cutoff',base,{h:{'access:Alice':{'kind':'day_utc','date':'2026-01-02'}}},{'refined','missing'})
 push('day_ends_at_cutoff',base,{h:{'access:Alice':{'kind':'day_utc','date':'2026-01-01'}}},{'refined'})
 push('unknown_access',base,{h:{'access:Alice':unknown()}},{'refined','missing'})
 push('unknown_effective',base,{h:{'effective':unknown()}},{'refined','missing'})
 push('private_delivery_without_publication',base,{h:{'route:Alice':'private_delivery','published':unknown()}},{'refined'})
 push('private_delivery_before_publication',base,{h:{'route:Alice':'private_delivery','published':point('2026-01-03T00:00:00Z')}},{'refined'})
 push('public_access_before_publication',base,{h:{'published':point('2026-01-03T00:00:00Z')}},set())
 push('public_route_private_release',base,{h:{'publication_channel':'internal'}},'invalid')
 push('chronology_interval_overlap',base,{h:{'authored':interval('2026-01-01T00:00:00Z','2026-01-01T02:00:00Z'),'ingested':interval('2026-01-01T01:00:00Z','2026-01-01T03:00:00Z'),'accepted':point('2026-01-01T04:00:00Z'),'published':point('2026-01-01T03:00:00Z'),'access:Alice':point('2026-01-01T03:00:00Z')}},{'refined'})
 push('exclusive_chronology_boundary',base,{h:{'authored':point('2026-01-01T02:00:00Z'),'published':interval('2026-01-01T01:00:00Z','2026-01-01T02:00:00Z')}},set())
 push('unknown_access_forced_future_by_authorship',base,{h:{'authored':point('2026-01-03T00:00:00Z'),'ingested':point('2026-01-03T00:00:00Z'),'accepted':point('2026-01-03T00:00:00Z'),'published':point('2026-01-03T00:00:00Z'),'access:Alice':unknown()}},{'missing'})
 f=oldcases.base();new=oldcases.add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],when='2026-01-01T01:00:00Z')
 push('correction_access_straddles',f,{new:{'access:Alice':interval(before,later)}},{'refined','coarse'})
 push('correction_effect_straddles',f,{new:{'effective':interval(before,later)}},{'refined','coarse'})
 push('correction_public_and_access_correlated',f,{new:{'published':interval(before,later),'access:Alice':interval(before,later)}},{'refined','coarse'})
 push('private_unknown_access_not_public_fallback',base,{h:{'route:Alice':'private_delivery','access:Alice':unknown(),'published':point('2026-01-01T00:00:00Z')}},{'refined','missing'})
 return out
