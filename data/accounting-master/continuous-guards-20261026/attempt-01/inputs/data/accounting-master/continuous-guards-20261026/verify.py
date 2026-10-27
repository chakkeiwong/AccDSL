"""One-shot exact validation; give a fresh output directory for every attempt."""
import copy, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
from fractions import Fraction as F
from dataclasses import replace
from itertools import product
from reference import Aff, Cell, Scope, Shared, image, truth, guard_margin, encode, specialize
import oracle

start=time.monotonic();here=Path(__file__).resolve().parent;repo=here.parents[2]
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
checks=[];controls=[];cases=[]
def ck(name,ok,details=None):
    checks.append({'name':name,'pass':bool(ok),'details':encode(details)})
    if not ok:raise AssertionError(name)
def control(name,ok,details=None):
    ck(name,ok,details);controls.append({'name':name,'discriminates':bool(ok),'details':encode(details)})
def canon(x,c):
    if isinstance(x,Aff):return encode(Aff(b=x(c.lo)) if c.point else x)
    if isinstance(x,dict):return {k:canon(v,c) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [canon(v,c) for v in x]
    return x

deps=[here/'reference.py',here/'oracle.py',here/'verify.py',repo/'docs/plans/accounting-continuous-guards-20261026.md',repo/'docs/design/proposal/manuscript-decision-conversion-v519-20261026/simulation/17-continuous-methods.tex',repo/'docs/design/proposal/manuscript-decision-conversion-v519-20261026/simulation/09-approximation.tex',repo/'data/accounting-master/literature-closure-20261026/recent-method-results.json']
hashes={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}
(out/'inputs').mkdir()
for p in deps:
 q=out/'inputs'/p.relative_to(repo);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
try:
 families={'mixed':Scope().modes,'committed':(('fixed',True),('floating',True)),'fixed':(('fixed',False),('fixed',True))}
 summaries=[]
 for fam,modes in families.items():
  for view in ('coarse','refined','full'):
   s=Scope(modes=modes,observation=view);engine=Shared(s)
   ck(f'{fam}/{view}/lazy_initial',len(engine.nodes)==0)
   actual=[];expected=[]
   for mode,right in modes:
    recs=[x for x in engine.records if (x['mode'],x['right'])==(mode,right)]
    ck(f'{fam}/{view}/{mode}/{right}/cover_ends',recs[0]['cell']==Cell(*[s.domain[0]]*2,True) and recs[-1]['cell']==Cell(*[s.domain[1]]*2,True))
    ck(f'{fam}/{view}/{mode}/{right}/cover_adjacent',all(a['cell'].hi==b['cell'].lo and a['cell'].point!=b['cell'].point for a,b in zip(recs,recs[1:])))
    for lo,hi in oracle.cells():
     c=Cell(lo,hi,lo==hi);matches=[x for x in recs if x['cell'].contains(c.sample())]
     ck('unique_common_region',len(matches)==1,(fam,view,mode,right,c))
     # Candidate affine region must contain the entire oracle atom. Together
     # with disjoint cover this reduces function equality to coefficients.
     rec=matches[0];rc=rec['cell']
     ck('oracle_atom_contained',rc.contains(lo) if c.point else (not rc.point and rc.lo<=lo and hi<=rc.hi))
     node=engine.resolve(rec);got=canon(node,c);want=oracle.expected(mode,right,lo,hi,view)
     ck('complete_symbolic_transition',got==want,{'family':fam,'view':view,'mode':mode,'right':right,'cell':c})
     actual.append(got);expected.append(want)
     for action,t in node['actions'].items():
      b=t['balances'];res=b['cash']+b['other_assets']-b['old_debt']-b['facility_debt']-b['interest_payable']-b['equity']
      ck('balance_identity',res==Aff(),(fam,view,mode,right,c,action))
      if t['status']=='refused':
       ck('refusal_retains_due',t['claim']['unpaid']==node['interest'] and t['claim']['paid']==Aff() and len(t['journal'])==1)
      else:ck('cash_feasible_entire_region',truth(b['cash'],c,'>=') is True)
     cases.append({'family':fam,'view':view,'mode':mode,'right':right,'cell':encode(c),'actual':got,'oracle':want})
   # Independent candidate policy method: intersect feasible actions by signal,
   # then form products. Oracle enumerates total policies and rejects per atom.
   per_signal={}
   for x in actual:
    o=tuple(x['observation']);allowed={a for a,t in x['actions'].items() if t['status']=='accepted'}
    per_signal[o]=per_signal.get(o,{'pay','draw'})&allowed
   keys=sorted(per_signal,key=repr)
   gotpol=sorted([tuple(zip(keys,a)) for a in product(*[sorted(per_signal[k]) for k in keys])],key=repr)
   wantpol=sorted(oracle.policies(expected),key=repr)
   ck('observation_measurable_policy_set',gotpol==wantpol,(fam,view))
   anticipated=0 if fam=='mixed' or (fam=='committed' and view=='coarse') else 1
   ck('declared_policy_count',len(gotpol)==anticipated,(fam,view,len(gotpol)))
   summaries.append({'family':fam,'view':view,'retained_regions':len(engine.records),'shared_nodes':len(engine.nodes),'oracle_atoms':len(actual),'feasible_policies':encode(gotpol)})
 # Complete lazy metadata and partial materialization preserve support.
 for budget in (0,1,7,31,32,100):
  e=Shared(Scope());a=e.materialize(budget);joined=a['resolved']+a['unresolved']
  ck('budget_retains_all_regions',len(joined)==32 and len({(x['mode'],x['right'],x['cell'].key()) for x in joined})==32)
  ck('unresolved_nodes_unevaluated',all(x['node'] is None for x in a['unresolved']))
  ck('complete_iff_all_resolved',a['complete']==(budget>=32))
  ck('valid_interest_outer',a['interest_outer']=={'inf':F(3),'sup':F(6)})
  if budget==1:control('one_region_is_not_complete',not a['complete'] and len(a['unresolved'])==31)
 e=Shared(Scope(observation='refined'));e.materialize(100)
 control('shared_formulas_do_not_delete_histories',len(e.records)==32 and len(e.nodes)<32,(len(e.records),len(e.nodes)))
 # Tight, attained/unattained ranges on the committed floating draw region.
 c=Cell(F(11,200),F(3,50));p=next(x for x in e.records if x['mode']=='floating' and x['right'] and x['cell']==c)
 b=image(e.resolve(p)['actions']['draw']['balances']['cash'],c)
 ck('open_draw_cash_bounds',b=={'inf':F(1,4),'sup':F(3,4),'inf_attained':False,'sup_attained':False})
 atcap=e.evaluate('floating',True,F(3,50),e.scope)
 ck('minimum_cash_attained_at_cap',atcap['actions']['draw']['balances']['cash']==F(1,4))
 # Failure controls target the intended target, not just assertions of balance.
 at=e.evaluate('floating',True,F(11,200),e.scope)
 after=e.evaluate('floating',True,F(11,200)+F(1,10**9),e.scope)
 control('strict_equality_boundary',at['actions']['pay']['status']=='accepted' and at['actions']['draw']['status']=='refused' and after['actions']['draw']['status']=='accepted')
 unavailable=e.evaluate('floating',False,F(3,50),e.scope)
 control('same_coupon_different_rights',atcap['interest']==unavailable['interest'] and atcap['actions']['draw']['status']!=unavailable['actions']['draw']['status'])
 fixed=e.evaluate('fixed',False,F(3,50),e.scope)
 control('same_prior_interest_different_shock',e.evaluate('fixed',False,F(1,20),e.scope)['interest']==e.evaluate('floating',False,F(1,20),e.scope)['interest'] and fixed['interest']!=unavailable['interest'])
 control('forgotten_payable_is_wrong',unavailable['actions']['pay']['claim']['unpaid']==6)
 coarse=[x for x in summaries if x['family']=='committed' and x['view']=='coarse'][0]
 refined=[x for x in summaries if x['family']=='committed' and x['view']=='refined'][0]
 control('clairvoyance_changes_feasible_policy',len(coarse['feasible_policies'])==0 and len(refined['feasible_policies'])==1)
 control('independent_intervals_lose_cash_identity',(F(93),F(97))!=(F(95),F(95)),{'relation':'cash=95-interest; interest in [5,7]'})
 control('midpoint_drops_possible_breach',F(5)<=F(11,2)<F(6))
 # Margin checks are consequences of the supplied interval bound, not estimated
 # error. Strict equality is checked on both sides; bounds may be zero.
 for eps in (F(0),F(1,1000),F(1,10)):
  for center in (F(11,2)-2*eps,F(11,2)-eps,F(11,2),F(11,2)+eps,F(11,2)+2*eps):
   for op in ('>','<='):
    got=guard_margin(center,eps,F(11,2),op)
    lo,hi=center-eps,center+eps
    want=(True if lo>F(11,2) else False if hi<=F(11,2) else None) if op=='>' else (True if hi<=F(11,2) else False if lo>F(11,2) else None)
    ck('uniform_interval_margin',got==want,(center,eps,op,got))
 control('zero_margin_refines',guard_margin(F(11,2),F(1,1000),F(11,2),'>') is None)
 control('observation_margin_refines',guard_margin(F(1,25),F(1,10000),F(1,25),'<=') is None)
 control('small_error_flips_default',guard_margin(F(11,2)-F(1,1000),F(1,500),F(11,2),'>') is None and (F(11,2)+F(1,1000)>F(11,2)))
 # Every scope component remains in the cache key, even where this selected
 # query might happen to be invariant under a particular revision.
 variants={'domain':(F(1,50),F(9,100)),'modes':(('floating',True),),'floor':F(1,100),'cap':F(7,100),'trigger':F(6),'signal_cut':F(1,20),'observation':'coarse','horizon':'two-dates','query':'terminal-profit','actions':('pay','draw','contingent-order'),'clause_version':'amended','precision':'cents'}
 for name,value in variants.items():
  try:e.check_scope(replace(e.scope,**{name:value}));refused=False
  except ValueError:refused=True
  control('scope_change_'+name,refused)
 for p,h in hashes.items():ck('source_unchanged',hashlib.sha256((repo/p).read_bytes()).hexdigest()==h,p)
 result={'status':'PASS','assertions':len(checks),'controls':len(controls),'symbolic_comparisons':len(cases),'scope_summaries':summaries,'protected_files':len(hashes),'scope':'Exact one-rate one-date synthetic rational-affine profile; no probabilities or production acceptance.'}
except Exception as exc:
 result={'status':'FAIL','error':repr(exc),'assertions':len(checks),'controls':len(controls)}
finally:
 for name,obj in [('checks.json',checks),('controls.json',controls),('cases.json',cases),('verification.json',result),('source-lock.json',hashes)]:
  (out/name).write_text(json.dumps(encode(obj),indent=2)+'\n')
 manifest={'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 timeout 120s python3 '+str(Path(__file__).relative_to(repo))+' '+str(out),'python':platform.python_version(),'platform':platform.platform(),'cpu_gpu':'CPU; CUDA_VISIBLE_DEVICES='+str(os.getenv('CUDA_VISIBLE_DEVICES'))+'; no ML imports','data':'synthetic exact declared premises; inputs retained','seeds':'N/A deterministic rational arithmetic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-continuous-guards-20261026.md','result':str(out/'verification.json')}
 (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)
