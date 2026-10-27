"""One-shot bounded deterministic source-clock evidence writer."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from itertools import product
import hashlib,json,platform,resource,subprocess,sys,time,traceback
import temporal as t
f=t.prior.load('exact_temporal_fixture_cases',Path(__file__).resolve().parent/'fixtures.py')
import order_oracle as oracle
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];saved=[];proofs=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:250]+' != '+repr(b)[:250])
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def labels(result):return {o['scenario']['view'] if o['status']=='selected_conditional' else 'missing' for o in result['outcomes']}
files=[H/n for n in ['temporal.py','difference.py','proofcheck.py','fixtures.py','order_oracle.py','verify.py','contract.md']]+[R/'docs/plans/accounting-source-time-intervals-20261027.md',H.parent/'certified-source-views-20261026/attempt-01/source-lock.json',H.parent/'source-policy-invalidation-20261027/attempt-01/source-lock.json']
P=H.parent/'certified-observation-policy-20261026/attempt-01'
PIN=H.parent/'policy-control-integration-20261026/source-preservation.json'
files += [P/'rows.json',P/'policy-comparisons.json',PIN]
files+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(R)) and Path(m.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in files};dump('source-lock.json',lock)
for p in H.glob('*.py'):(OUT/p.name).write_bytes(p.read_bytes())
try:
 for folder in ['certified-source-views-20261026','source-policy-invalidation-20261027']:
  for n,h in json.loads((H.parent/folder/'attempt-01/source-lock.json').read_text()).items():ck('predecessor:'+n,sha(R/n),h)
 pins=json.loads(PIN.read_text())['evidence']
 for name in ['rows.json','policy-comparisons.json']:ck('externally_bound_policy:'+name,sha(P/name),pins[str((P/name).relative_to(R))])
 # Exact finite-order comparator on all selected bound/strict/order combinations.
 engine=0
 for lx,hx,ly,hy,strictx,stricty,relation in product([0,1],[1,2],[0,1],[1,2],[False,True],[False,True],['none','xy','yx','cycle']):
  es=[t.edge('x','zero',-lx),t.edge('zero','x',hx,strictx),t.edge('y','zero',-ly),t.edge('zero','y',hy,stricty)]
  if relation in ['xy','cycle']:es.append(t.edge('y','x',0,relation=='cycle'))
  if relation in ['yx','cycle']:es.append(t.edge('x','y',0))
  p=t.dc.solve(['x','y'],es);kind=t.pc.verify(['x','y'],es,p);ck('finite_order:'+str(engine),kind=='nonempty',oracle.exists(['x','y'],es));engine+=1
 # Full-domain proof partitions, checked after JSON serialization.
 diagnostic=len(sys.argv)>2;extended=f.extended_cases()[:8] if diagnostic else f.extended_cases()
 for name,fixture,expected in extended:
  before=cp(fixture);p,result=t.assess(fixture);ck(name+':pure',fixture,before);ck(name+':no_admission',all(result[k] is False for k in t.FLAGS))
  if expected=='invalid':ck(name+':invalid',result['status'],'invalid')
  else:
   ck(name+':complete',result['status'],'complete_family' if expected else 'inconsistent_clocks');ck(name+':views',labels(result),expected)
   outcomes,nodes=t.verify_tree(p,json.loads(json.dumps(result['tree'])));ck(name+':saved_tree',outcomes,result['outcomes']);ck(name+':node_population',nodes,result['nodes']);proofs.append({'case':name,'prepared':p,'result':result})
  saved.append({'case':name,'expected':sorted(expected) if isinstance(expected,set) else expected,'result':result})
 compat=0;disagreements=[]
 if not diagnostic:
  for old in f.oldcases.suite():
   fixture=f.convert(old['fixture']);p,result=t.assess(fixture);oldstatus=old['expected']['status']
   if old['name']=='future_published':
    ck('new_public_route_contradiction',result['status'],'inconsistent_clocks');disagreements.append({'case':old['name'],'old_status':oldstatus,'new_status':result['status'],'reason':'new explicit public-retrieval route requires publication<=actor access'});continue
   if oldstatus=='complete_conditional':
    ck(old['name']+':one_view',len(result['outcomes']),1);out=result['outcomes'][0];ck(old['name']+':selected',out['status'],'selected_conditional');ck(old['name']+':scenario',out['scenario'],old['expected']['scenario']);ck(old['name']+':heads',out['heads'],{k:fixture['mapping'][h] for k,h in old['expected']['heads'].items()});compat+=1
   else:
    # Missing clocks remain explicitly unknown even when chronology entails eligibility.
    ck(old['name']+':complete_partial_views',result['status'],'complete_family')
    ck(old['name']+':unknown_or_unresolved_retained',bool(result['unknown_clocks']) or any(o['status']=='unresolved' for o in result['outcomes']))
   outcomes,nodes=t.verify_tree(p,result['tree']);ck(old['name']+':proof_tree',outcomes,result['outcomes']);saved.append({'case':'predecessor:'+old['name'],'result':result});proofs.append({'case':'predecessor:'+old['name'],'prepared':p,'result':result})
 # The exact parser must preserve submicroseconds and offset equality.
 ck('submicrosecond_difference',t.instant('2026-01-02T00:00:00.0000001Z')-t.instant('2026-01-02T00:00:00Z'),Q(1,10000000))
 ck('offset_equality',t.instant('2026-01-02T08:00:00+08:00'),t.instant('2026-01-02T00:00:00Z'))
 # Strict certificates and complete partitions reject alteration.
 def reject(name,fn):
  try:fn()
  except (ValueError,KeyError,TypeError,AssertionError):controls.append(name);ck(name,True)
  else:ck(name,False)
 p,result=t.assess(f.convert(f.oldcases.base()));bad=cp(result['tree']);bad['children'].pop();reject('missing_complement_child',lambda:t.verify_tree(p,bad))
 bad=cp(result['tree']);bad['record']='foreign';reject('changed_record_order',lambda:t.verify_tree(p,bad))
 bad=cp(result['tree']);bad['proof']['values'][p['variables'][0]]='-1';reject('altered_witness',lambda:t.verify_tree(p,bad))
 es=[t.edge('zero','x',0,True),t.edge('x','zero',0)];proof=t.dc.solve(['x'],es);ck('strict_zero_cycle',t.pc.verify(['x'],es,proof),'empty');bad=cp(proof);bad['cycle']=bad['cycle'][:1];reject('broken_contradiction_cycle',lambda:t.pc.verify(['x'],es,bad))
 _,limited=t.assess(f.convert(f.oldcases.base()),1);ck('budget_keeps_incomplete',limited['status'],'unresolved_budget');ck('budget_no_complete_views',limited['outcomes'],[]);controls.append('budget_not_completeness')
 for name,clock in [('empty_half_open',f.interval('2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')),('unknown_timezone',f.point('2026-01-01T00:00:00-00:00')),('leap_second',f.point('2026-01-01T00:00:60Z')),('unlabelled_date',f.point('2026-01-01')),('noncanonical_day',{'kind':'day_utc','date':'20260101'})]:reject(name,lambda c=clock:t.bounds(c))
 # Compare possible policies with the immutable eight-problem evidence; preserve each view label.
 P=H.parent/'certified-observation-policy-20261026/attempt-01';rows=json.loads((P/'rows.json').read_text());comp=json.loads((P/'policy-comparisons.json').read_text());policy_views=[]
 for name,fixture,expected in f.extended_cases():
  if name!='correction_access_straddles':continue
  p,res=t.assess(fixture)
  for o in res['outcomes']:
   if o['status']!='selected_conditional':continue
   s=o['scenario'];selected=[r for r in rows if r['receipt']==s['receipt'] and (s['family']=='mixed' or r['right'])];got,_=t.prior.policy.enumerate_policies(selected,s['view']);wanted,_=t.prior.independent.solve(selected,s['view']);old=next(x for x in comp if all(x[k]==s[k] for k in ['receipt','family','view']));ck('possible_policy_full_set',got,wanted);ck('saved_policy_full_set',got,{t.prior.tuples(x) for x in old['feasible_policies']});ck('policy_world_population',len(selected),old['world_rows']);policy_views.append({'heads':o['heads'],'scenario':s,'policies':json.loads(json.dumps(sorted(got,key=repr))),'count':len(got),'rows':len(selected)})
 ck('different_possible_policy_counts',sorted(x['count'] for x in policy_views),[0,4])
 for n,h in lock.items():ck('source_preserved:'+n,sha(R/n),h)
 summary={'status':'PASS','diagnostic':diagnostic,'engine_comparisons':engine,'interval_cases':len(extended),'predecessor_complete_compatibility_cases':compat,'explicit_profile_disagreements':disagreements,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'possible_policy_counts':[x['count'] for x in policy_views],'scope':'Exact conditional clock-view families under supplied chronology/access premises; no actual availability or probability.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',saved),('proofs.json',proofs),('policy-views.json',locals().get('policy_views',[]))]:dump(n,x)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT)+(' diagnostic' if len(sys.argv)>2 else ''),'environment':'existing Python '+platform.python_version()+'; CPU, GPU intentionally hidden; standard library and existing jsonschema','seeds':'N/A deterministic','data':'locked selected policy rows and synthetic source/clock families','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-source-time-intervals-20261027.md','result':str(OUT/'verification.json'),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
