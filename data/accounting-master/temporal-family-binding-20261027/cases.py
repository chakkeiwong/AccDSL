"""Independently named expected family changes; reused fixtures retain original semantics."""
from copy import deepcopy as cp
import family as m
f=m.t.prior.load('family_binding_exact_fixture_cases',m.T/'fixtures.py')

def suite():
 base=f.oldcases.base();converted=f.convert(base);yield 'baseline',converted,4096,{'refined'},1
 for name,fixture,expected in f.extended_cases():
  if expected=='invalid':continue
  yield name,fixture,4096,expected,1 if 'refined' in expected else 0
 financial=f.oldcases.base();f.oldcases.add(financial,'financial_family',{'receipt':6,'family':'committed'},supersedes=financial['names']['financial_family'],when='2026-01-01T01:00:00Z')
 yield 'financial_correction_receipt6',f.convert(financial),4096,{'refined'},0
 source=f.oldcases.base();f.oldcases.add(source,'observation_scheme',{'view':'refined'},supersedes=source['names']['observation_scheme'],when='2026-01-01T01:00:00Z')
 yield 'same_meaning_new_source',f.convert(source),4096,{'refined'},1
 actor=cp(converted);actor['request']['actor']='Bob';yield 'changed_actor_same_semantics',actor,4096,{'refined'},1
 trust=cp(converted);trust['trusted']=frozenset();yield 'withdraw_all_clock_trust',trust,4096,{'refined','missing'},1
 yield 'budget_whole_domain',converted,1,set(),0
 # Two distinct source heads with equal financial meaning share one numerical set.
 c=f.oldcases.base();new=f.oldcases.add(c,'observation_scheme',{'view':'refined'},supersedes=c['names']['observation_scheme'],when='2026-01-01T01:00:00Z')
 changed=f.convert(c,{new:{'access:Alice':f.interval('2026-01-01T23:59:59.9999999Z','2026-01-02T00:00:00.0000001Z')}})
 yield 'two_source_supports_one_policy',changed,4096,{'refined'},1
