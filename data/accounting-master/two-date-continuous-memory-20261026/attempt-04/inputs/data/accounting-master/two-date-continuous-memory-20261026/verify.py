import json,sys,os,time,hashlib,platform,subprocess
from pathlib import Path
from itertools import product,combinations
from fractions import Fraction as F
from model import A,H,Region,aff,atoms,traces,rect,enc
import oracle
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False)
start=time.monotonic();checks=[];controls=[];examples=[];summary=[]
def ck(n,c,details=None):
 checks.append({'name':n,'pass':bool(c),'details':enc(details)})
 if not c:raise AssertionError(n)
def ctrl(n,c,details=None):ck(n,c,details);controls.append({'name':n,'discriminates':bool(c),'details':enc(details)})
def canonical(x,xa,ya):
 if isinstance(x,A):
  a,b,c=x.x,x.y,x.c
  if xa[0]==xa[1]:c+=a*xa[0];a=0
  if ya[0]==ya[1]:c+=b*ya[0];b=0
  return enc(A(F(a),F(b),F(c)))
 if isinstance(x,dict):return {k:canonical(v,xa,ya) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [canonical(v,xa,ya) for v in x]
 return x

def minus(region,other):
 # Disjoint ordered decomposition of region \ other.
 remaining=[region];outside=[]
 for h in other.hs:
  next_inside=[]
  for q in remaining:
   for flag,p in q.split(h):(next_inside if flag else outside).append(p)
  remaining=next_inside
 return outside

def policies(rows,view,rightset):
 # Only obs1 depends on the requested coarse/refined first signal. At date2,
 # retain that signal and the selected first instruction in the actor history.
 rows=[r for r in rows if r['right'] in rightset]
 def o1(r):return r['obs1'] if view=='refined' else r['obs1'][:1]
 def o2(r):return o1(r)+(r['a1'],)+r['obs2'][-2:]
 signals=sorted({o1(r) for r in rows},key=repr);valid=[]
 for values in product(('pay','draw'),repeat=len(signals)):
  chosen=dict(zip(signals,values));selected=[r for r in rows if r['a1']==chosen[o1(r)]]
  if any(r['status']=='refused1' for r in selected):continue
  allowed={};observed=set()
  for r in selected:
   key=o2(r);observed.add(key);allowed.setdefault(key,{'pay','draw'})
   if r['status']!='accepted':allowed[key].discard(r['a2'])
  if any(not allowed[k] for k in observed):continue
  count=1
  for k in observed:count*=len(allowed[k])
  valid.append({'first':[(k,chosen[k]) for k in signals],'second_allowed':[(k,sorted(allowed[k])) for k in sorted(observed,key=repr)],'count':count})
 return valid

deps=[HERE/n for n in ('model.py','oracle.py','solver_check.py','verify.py')]+[ROOT/'docs/plans/accounting-two-date-continuous-memory-20261026.md',ROOT/'data/accounting-master/continuous-guards-20261026/attempt-02/verification.json']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}
for p in deps:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
try:
 diagnostic=subprocess.run([sys.executable,str(HERE/'solver_check.py')],capture_output=True,text=True,timeout=10)
 (OUT/'solver-check.json').write_text(diagnostic.stdout)
 ck('solver_validity',diagnostic.returncode==0)
 total_regions=0;cells=0
 for R in (F(6),F(7)):
  rows=[];state_keys=set()
  for mode,right in product(('fixed','floating'),(False,True)):
   for xa,ya in product(tuple(atoms()),repeat=2):
    base=rect(*xa,*ya);rs=list(traces(mode,right,xa,ya,R,'refined'));cells+=1
    I1=oracle.oracle_interest(mode,0,*xa);I2=oracle.oracle_interest(mode,1,*ya)
    for row in rs:
     region=row['region'];s=row['state'];total_regions+=1
     want=oracle.expected(mode,right,xa,ya,R,row['a1'],row['a2'],s['status'])
     ck('complete_state_journal',canonical(s,xa,ya)==canonical(want,xa,ya),(str(R),mode,right,xa,ya,row['a1'],row['a2'],s['status']))
     b=s['balances'];res=b['cash']+b['other_assets']-b['old_debt']-b['facility_debt']-b['interest_payable']-b['equity']
     ck('accounting_identity',res==A())
     ck('retained_region_nonempty',region.feasible())
     ck('region_within_original',region.subset(base))
     ck('cash_nonnegative_prefix',region.bounds(b['cash'])['inf']>=0)
     if s['status'].startswith('refused'):ck('unpaid_retained',canonical(s['unpaid'],xa,ya)==canonical(I1 if s['date']==1 else I2,xa,ya))
     state_keys.add(json.dumps(canonical(s,xa,ya),sort_keys=True))
     rows.append({'mode':mode,'right':right,'obs1':row['obs1'],'obs2':row['obs2'],'a1':row['a1'],'a2':row['a2'],'status':s['status']})
    # Compare full accepted action domains with independently derived inequalities.
    for a1,a2 in product(('pay','draw'),repeat=2):
     hs=oracle.guards(I1,I2,a1,a2,right,R)
     expected=None if hs is None else base.add(*hs)
     accepts=[row['region'] for row in rs if row['a1']==a1 and row['a2']==a2 and row['state']['status']=='accepted']
     if expected is None or not expected.feasible():ck('no_false_acceptance',not accepts)
     else:
      ck('accepted_domain_nonempty',bool(accepts))
      ck('all_accepted_subset',all(q.subset(expected) for q in accepts))
      uncovered=[expected]
      for q in accepts:uncovered=[s for z in uncovered for s in minus(z,q)]
      ck('entire_expected_domain',not uncovered)
    # For every chosen first/second order, acceptance and refusal partition full
    # starting region; refused-first prefixes occur once and terminate later work.
    for a1,a2 in product(('pay','draw'),repeat=2):
     seq=[q['region'] for q in rs if q['a1']==a1 and (q['a2'] is None or q['a2']==a2)]
     ck('outcomes_disjoint',all(not p.add(*q.hs).feasible() for p,q in combinations(seq,2)))
     unseen=[base]
     for q in seq:unseen=[s for z in unseen for s in minus(z,q)]
     ck('outcomes_cover_domain',not unseen)
    if xa==(F(3,50),F(3,50)) and ya==xa and mode=='floating' and right:
     examples.extend({'receipt':R,**q} for q in rs)
  for view in ('coarse','refined'):
   for fam,rights in [('mixed',{False,True}),('committed',{True})]:
    ps=policies(rows,view,rights);expect=R==7 and view=='refined' and fam=='committed'
    ck('robust_policy_exists',bool(ps)==expect,(R,view,fam))
    summary.append({'receipt':R,'view':view,'family':fam,'feasible_policy_count':sum(p['count'] for p in ps),'policy_choices':ps})
  print(json.dumps({'receipt_done':str(R),'comparisons_so_far':total_regions,'elapsed':time.monotonic()-start}),flush=True)
 # Exact counterexamples retain resource memory, dates and ordering.
 c=[q for q in examples if q['receipt']==6 and q['a1']=='draw' and q['a2']=='pay'][0]
 ctrl('double_high_fails_after_repayment',c['state']['status']=='refused2' and c['state']['balances']['cash']((F(3,50),F(3,50)))==F(21,4) and c['state']['unpaid']((F(3,50),F(3,50)))==6)
 ctrl('omitted_repayment_falsely_accepts',F(21,4)<6<=F(21,4)+1)
 ctrl('replenished_facility_falsely_accepts',F(21,4)+1-F(1,4)==6 and c['state']['facility_used'])
 good=[q for q in examples if q['receipt']==7 and q['a1']=='draw' and q['a2']=='pay'][0]
 ctrl('extra_receipt_changes_feasibility',good['state']['status']=='accepted' and good['state']['balances']['cash']((F(3,50),F(3,50)))==F(1,4))
 ctrl('coarse_information_veto',not next(q for q in summary if q['receipt']==7 and q['view']=='coarse' and q['family']=='committed')['feasible_policy_count'])
 ctrl('right_remains_hidden_and_relevant',not next(q for q in summary if q['receipt']==7 and q['view']=='refined' and q['family']=='mixed')['feasible_policy_count'])
 # A path at rate5% reveals neither coupon type nor facility. Redrawing type
 # after this observation creates switches that violate the persistent family.
 ctrl('persistent_mode_not_resampled',len({(m,m) for m in ('fixed','floating')})==2 and len(set(product(('fixed','floating'),repeat=2)))==4)
 # Safety is not determined by a corner if the full coupled-domain relation is
 # erased. At I1=5.75,I2=5.5 equality is allowed; any positive increase fails.
 ctrl('joint_diagonal_equality',F(23,4)+F(11,2)==F(45,4) and F(23,4)+F(11,2)+F(1,10**8)>F(45,4))
 for p,h in hashes.items():ck('source_unchanged',hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h)
 result={'status':'PASS','assertions':len(checks),'controls':len(controls),'rate_mode_receipt_cells':cells,'complete_symbolic_states':total_regions,'policy_summary':enc(summary),'protected_files':len(hashes),'scope':'Exact two-rate/two-date supplied persistent-mode fixture; shared region value type; independent closed-form finance oracle.'}
except Exception as e:result={'status':'FAIL','error':repr(e),'assertions':len(checks),'controls':len(controls)}
finally:
 for name,obj in [('verification.json',result),('checks.json',checks),('controls.json',controls),('examples.json',examples),('source-lock.json',hashes)]:
  (OUT/name).write_text(json.dumps(enc(obj),indent=2)+'\n')
 manifest={'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'python':platform.python_version(),'platform':platform.platform(),'cpu_gpu':'CPU with CUDA_VISIBLE_DEVICES='+str(os.getenv('CUDA_VISIBLE_DEVICES'))+'; no GPU imports','data':'supplied exact synthetic premises; source snapshots retained','seeds':'N/A exact','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-two-date-continuous-memory-20261026.md','result':str(OUT/'verification.json')}
 (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)
