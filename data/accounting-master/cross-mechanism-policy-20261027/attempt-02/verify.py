"""One-shot complete cross-mechanism policy comparison and source-boundary checks."""
from pathlib import Path
from itertools import product
from copy import deepcopy as cp
import hashlib,importlib.util,json,platform,resource,subprocess,sys,time,traceback
import policy,oracle
H=Path(__file__).resolve().parent;R=H.parents[2]
spec=importlib.util.spec_from_file_location('cross_mechanism_full_fixtures',H/'fixtures.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];saved=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:250]+' != '+repr(b)[:250])
def serial(x):return json.loads(json.dumps(sorted(x,key=repr)))
def reject(n,fn):
 try:fn()
 except (ValueError,AssertionError,KeyError,TypeError):controls.append(n);ck(n,True)
 else:ck(n,False)
files=[H/n for n in ['policy.py','oracle.py','fixtures.py','verify.py','contract.md']]+[R/'docs/plans/accounting-cross-mechanism-policy-20261027.md',H.parent/'temporal-family-binding-20261027/attempt-01/source-lock.json',H.parent/'temporal-family-binding-20261027/attempt-01/cases.json']
files+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(R)) and Path(m.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in files};dump('source-lock.json',lock)
for n in ['policy.py','oracle.py','fixtures.py','verify.py','contract.md']:(OUT/n).write_bytes((H/n).read_bytes())
try:
 e=f.f.Evidence()
 for n,h in json.loads((H.parent/'temporal-family-binding-20261027/attempt-01/source-lock.json').read_text()).items():ck('prior_family_source:'+n,sha(R/n),h)
 base=next(x for x in e.comparisons if x['receipt']==7 and x['family']=='committed' and x['view']=='refined')
 # Independent relabeling of the known four policies; does not call the new key builder.
 def mapped(p,mechanism,reveal):
  first=[];second=[]
  for observation,action in p[0]:
   token=f.MAPPING[mechanism][tuple(observation)];hist=('known',mechanism,token) if reveal=='first' else ('unknown',token);first.append((hist,action))
  for observation,action in p[1]:
   token=f.MAPPING[mechanism][tuple(observation[:2])];hist=('known',mechanism,token) if reveal=='first' else ('unknown',token)
   second.append(((hist,observation[2],None if reveal=='never' else mechanism,tuple(observation[-2:])),action))
  return tuple(sorted(first,key=repr)),tuple(sorted(second,key=repr))
 def run(name,rows,a1,a2,reveal,expected,wanted=None):
  before=cp(rows);actual=policy.solve(rows,a1,a2,reveal);ind,diag=oracle.solve(rows,a1,a2,reveal)
  ck(name+':complete_sets',actual,ind);ck(name+':hand_count',len(actual),expected);ck(name+':immutable_rows',rows,before)
  if wanted is not None:ck(name+':independent_relabelled_set',actual,wanted)
  for first,second in actual:
   first=dict(first)
   ck(name+':own_action_memory',all(key[1]==first[key[0]] for key,action in second))
   ck(name+':hidden_tag_absent',reveal!='never' or all(key[0]=='unknown' for key in first) and all(key[2] is None for key,action in second))
  saved.append({'case':name,'reveal':reveal,'expected_count':expected,'rows':rows,'actions1':a1,'actions2':a2,'policies':serial(actual),'independent_constraints':diag})
  return actual
 for mechanism in ('A','B'):
  for reveal in ('never','first','second'):
   wanted={mapped(p,mechanism,reveal) for p in base['feasible_policies']};run('separate_'+mechanism+'_'+reveal,f.financial(e,(mechanism,)),('pay','draw'),('pay','draw'),reveal,4,wanted)
 wanted=set()
 for a,b in product(base['feasible_policies'],repeat=2):
  pa,pb=mapped(a,'A','first'),mapped(b,'B','first');wanted.add((tuple(sorted(pa[0]+pb[0],key=repr)),tuple(sorted(pa[1]+pb[1],key=repr))))
 joint=f.financial(e)
 for reveal,count in [('first',16),('second',0),('never',0)]:run('joint_swapped_'+reveal,joint,('pay','draw'),('pay','draw'),reveal,count,wanted if reveal=='first' else set())
 # Direct first-date conflict: same H message demands opposite instructions.
 for mechanism,required in [('A','pay'),('B','draw')]:
  cells=[r for r in joint if r['mechanism']==mechanism and r['message1']=='H'];allowed={a for a in ('pay','draw') if not any(r['a1']==a and r['status']=='refused1' for r in cells)}
  ck('hand_H_required_'+mechanism,allowed,{required})
 for transparent in (False,True):
  rows,a1,a2=f.cash_late(transparent)
  for reveal,count in [('first',1),('second',1),('never',1 if transparent else 0)]:run('cash_'+str(transparent)+'_'+reveal,rows,a1,a2,reveal,count)
 # Preserve selected, unresolved, inconsistent and incomplete temporal-family distinctions.
 families=json.loads((H.parent/'temporal-family-binding-20261027/attempt-01/cases.json').read_text());lookup={x['case']:x['reused'] for x in families}
 for name in ['correction_access_straddles','two_source_supports_one_policy']:
  b=lookup[name];mapped_family=f.family_rows(b,f.f.identity(b),e);ck(name+':supports',mapped_family['supports'],b['supports']);ck(name+':two_full_row_populations',len(mapped_family['rows']),1936)
  for reveal in ('first','second','never'):
   expected=0 if name=='correction_access_straddles' else 4 if reveal=='never' else 16
   explicit=set()
   if name=='two_source_supports_one_policy':
    ids=[o['outcome_sha256'] for o in b['outcomes']]
    def relabel_same(p,mechanism):
     first=[];second=[]
     for obs,action in p[0]:
      token=obs[0]+':'+str(int(obs[1]));hist=('known',mechanism,token) if reveal=='first' else ('unknown',token);first.append((hist,action))
     for obs,action in p[1]:
      token=obs[0]+':'+str(int(obs[1]));hist=('known',mechanism,token) if reveal=='first' else ('unknown',token);second.append(((hist,obs[2],None if reveal=='never' else mechanism,tuple(obs[-2:])),action))
     return first,second
    for pa,pb in product(base['feasible_policies'],repeat=2):
     aa,bb=relabel_same(pa,ids[0]),relabel_same(pb,ids[1]);pairs=aa[0]+bb[0];later=aa[1]+bb[1]
     if any(dict(pairs)[k]!=v for k,v in pairs) or any(dict(later)[k]!=v for k,v in later):continue
     explicit.add((tuple(sorted(dict(pairs).items(),key=repr)),tuple(sorted(dict(later).items(),key=repr))))
   run('temporal_'+name+'_'+reveal,mapped_family['rows'],('pay','draw'),('pay','draw'),reveal,expected,explicit)
 for name,status in [('unknown_access','unresolved_observation_map'),('budget_whole_domain','unresolved_timing_budget'),('public_access_before_publication','inconsistent_clocks')]:
  b=lookup[name];r=f.family_rows(b,f.f.identity(b),e);ck(name+':policy_question',r['status'],status);ck(name+':no_selected_subset',r['rows'],[])
 rows,a1,a2=f.cash_late()
 bad=cp(rows);bad.append(cp(bad[0]));reject('duplicate_support',lambda:policy.solve(bad,a1,a2,'never'))
 reject('unknown_revelation',lambda:policy.solve(rows,a1,a2,'sometimes'))
 bad=cp(rows);bad[0]['message2']=None;reject('missing_reachable_message',lambda:policy.solve(bad,a1,a2,'first'))
 bad=[r for r in rows if r['a2']!='draw'];reject('missing_action_support',lambda:policy.solve(bad,a1,a2,'first'))
 bad=cp(rows);bad[0]['a1']='pay';reject('wrong_action_domain',lambda:policy.solve(bad,a1,a2,'never'))
 bad=cp(rows);bad[0]['source_hash_as_observation']='leak';reject('unregistered_observation_field',lambda:policy.solve(bad,a1,a2,'never'))
 b=cp(lookup['correction_access_straddles']);b['outcomes'].pop();reject('dropped_temporal_mechanism',lambda:f.family_rows(b,f.f.identity(lookup['correction_access_straddles']),e))
 # A hidden-tag leak reverses the main verdict, so it is an explicit discriminator.
 ck('mechanism_leak_changes_answer',len(policy.solve(joint,('pay','draw'),('pay','draw'),'first'))==16 and len(policy.solve(joint,('pay','draw'),('pay','draw'),'never'))==0);controls.append('hidden_mechanism_leak_discriminator')
 for n,h in lock.items():ck('source_preserved:'+n,sha(R/n),h)
 for n,h in e.method_files.items():ck('accepted_dependency:'+n,sha(R/n),h)
 summary={'status':'PASS','policy_cases':len(saved),'assertions':len(checks),'controls':len(controls),'protected_direct_files':len(lock),'financial_row_population_per_mechanism':968,'joint_policies_observed_first':16,'joint_policies_observed_second':0,'joint_policies_unobserved':0,'late_cash_resolution_policies':1,'scope':'Finite exact common-history policies under explicit synthetic message mechanisms; no actual actor information or optimality.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',saved)]:dump(n,x)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'Python '+platform.python_version()+'; CPU; GPU intentionally hidden; existing dependencies only','data':'protected refined financial rows, complete temporal families and labeled synthetic cash/message tables','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-cross-mechanism-policy-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
