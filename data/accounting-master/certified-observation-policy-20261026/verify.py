"""One-shot complete certified information-policy comparison."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as F
from itertools import product
import gzip,hashlib,itertools,json,platform,resource,subprocess,sys,time,traceback
import observations as o
import policies as candidate
import constraint_oracle as oracle
r=o.r;g=o.g;pc=o.pc
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REG=HERE.parent/'exact-region-certificates-20261026/attempt-01'
QUEUE=HERE.parent/'exact-region-certificates-20261026/queue-attempt-01'
PATH=HERE.parent/'symbolic-path-composition-20261026/attempt-01'
OLD=HERE.parent/'two-date-continuous-memory-20261026/attempt-04'
sys.path.insert(0,str(PATH.parent));import expected_path as ep
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic()
diagnostic=len(sys.argv)>2 and sys.argv[2]=='diagnostic';checks=[];controls=[];rows=[];refinements=[];summaries=[];proof_count=0

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(name,actual,wanted=True):
 checks.append({'name':name,'pass':actual==wanted})
 if actual!=wanted:raise AssertionError(name+': '+repr(actual)[:500]+' != '+repr(wanted)[:500])
def reject(name,fn):
 try:fn()
 except (ValueError,AssertionError,KeyError,TypeError):ck(name,True);controls.append(name)
 else:ck(name,False)
def tup(v):
 if isinstance(v,list):return tuple(tup(x) for x in v)
 if isinstance(v,dict):return {k:tup(x) for k,x in v.items()}
 return v

def reference_observation(row):
 mode,right,ix,iy,a1,a2,R=row['job'];x,y=map(F,row['witness'])
 I1=F(5) if mode=='fixed' else 100*min(F(3,50),max(F(3,100),x))
 I2=F(5) if mode=='fixed' else 100*min(F(3,50),max(F(3,100),y))
 first=('low' if x<=F(1,25) else 'high',I1>F(11,2))
 if row['status']=='refused1':second=None
 else:
  cash=F(11,2)+R-I1-(F(1,4) if a1=='draw' else 0)
  second=first+(a1,I2>F(11,2),I2<=cash)
 if tup(row['obs1'])!=first or tup(row['obs2'])!=second:raise ValueError('observation_mismatch')
 return True

def refinement_check(record,steps,job):
 expected=o.coverage_guard(steps,job)
 if record['coverage_guard']!=expected or len(record['children'])!=2:raise ValueError('refinement_shape')
 for child,truth in zip(record['children'],(True,False)):
  expected_predicate=expected if truth else r.opposite(expected)
  if child['covers']!=truth or child['predicate']!=expected_predicate:raise ValueError('refinement_partition')
  pc.verify(record['constraints']+[expected_predicate],child['proof'])
 return True

source={Path(__file__).resolve(),HERE/'observations.py',HERE/'policies.py',HERE/'constraint_oracle.py',ROOT/'docs/plans/accounting-certified-observation-policy-20261026.md',REG/'jobs.jsonl.gz',REG/'scope.json',REG/'run-manifest.json',REG/'source-lock.json',REG/'verification.json',QUEUE/'registry.json',QUEUE/'verification.json',QUEUE/'source-lock.json',PATH/'cases.json',PATH/'verification.json',PATH/'source-lock.json',OLD/'verification.json',OLD/'source-lock.json',PATH.parent/'expected_path.py',REG.parent/'regions.py',REG.parent/'geometry.py',REG.parent/'proofcheck.py'}
lock={str(p.relative_to(ROOT)):sha(p) for p in source}
for p in source:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
try:
 for d in (REG,QUEUE,PATH,OLD):
  ck('predecessor_pass:'+d.parent.name,json.loads((d/'verification.json').read_text())['status'],'PASS')
  for path,h in json.loads((d/'source-lock.json').read_text()).items():ck('predecessor_source:'+path,sha(ROOT/path),h)
 ck('archive_hash',sha(REG/'jobs.jsonl.gz'),json.loads((REG/'run-manifest.json').read_text())['proof_archive_sha256'])
 registry=json.loads((QUEUE/'registry.json').read_text());scope=json.loads((REG/'scope.json').read_text());saved=json.loads((PATH/'cases.json').read_text());by={(x['mode'],x['right'],*x['actions']):x['steps'] for x in saved if x['chart']=='alpha'}
 # Certify signals on whole atoms: the opposite label region is empty.
 signal_proofs=[]
 for mode,axis,ix in product(('fixed','floating'),(0,1),range(11)):
  typ=o.sign_on_atom(mode,axis,ix);a=r.coupon(mode,axis,ix);h=r.H(-a[0],-a[1],F(11,2)-a[2],True)
  bad=r.opposite(h) if typ else h;domain=r.domain(ix,0) if axis==0 else r.domain(0,ix)
  proof=g.produce(domain+[bad]);ck('whole_atom_trigger',pc.verify(domain+[bad],proof),'empty');signal_proofs.append({'mode':mode,'axis':axis,'atom':ix,'trigger':typ,'constraints':domain+[bad],'proof':proof})
 for ix,(_,hi) in enumerate(r.atoms()):
  low=hi<=F(1,25);h=r.H(1,0,-F(1,25));bad=r.opposite(h) if low else h;domain=r.domain(ix,0);proof=g.produce(domain+[bad]);ck('whole_atom_signal',pc.verify(domain+[bad],proof),'empty');signal_proofs.append({'atom':ix,'low':low,'constraints':domain+[bad],'proof':proof})
 # Read each immutable financial proof, never invoke its one-shot writer.
 selected={0,1000,3000,3871} if diagnostic else None;jobs=0
 with gzip.open(REG/'jobs.jsonl.gz','rt') as f:
  for i,line in enumerate(f):
   if selected is not None and i not in selected:continue
   bundle=json.loads(line);job=tuple(bundle['job']);mode,right,ix,iy,a1,a2,R=job;jobs+=1
   ck('registry_binding/'+str(i),r.digest(bundle),registry[r.job_id(job)])
   ck('scope/'+str(i),bundle['scope'],scope)
   steps=by[(mode,right,a1,a2)];expected=r.instructions(ep.steps(mode,right,a1,a2),job)
   ck('instruction_binding/'+str(i),bundle['instructions'],json.loads(json.dumps(expected)))
   leaves=r.verify_tree(r.domain(ix,iy),expected,bundle['tree'])
   for li,leaf in enumerate(leaves):
    if leaf['kind']=='empty':continue
    generated,refinement=o.inspect_leaf(leaf,steps,job,li)
    if refinement:
     ck('observation_refinement/'+str(i)+'/'+str(li),refinement_check(refinement,steps,job));refinements.append(refinement);proof_count+=2
    for row in generated:ck('observed_witness/'+row['row_id'],reference_observation(row));rows.append(row)
   if jobs%1000==0:print(json.dumps({'jobs':jobs,'observation_rows':len(rows),'elapsed':time.monotonic()-start}),flush=True)
 ck('expected_job_population',jobs,4 if diagnostic else 3872)
 if not diagnostic:
  previous=json.loads((OLD/'verification.json').read_text())['policy_summary']
  for receipt,view,family in product((6,7),('coarse','refined'),('mixed','committed')):
   selected_rows=[x for x in rows if x['receipt']==receipt and (family=='mixed' or x['right'])]
   got,decisions=candidate.enumerate_policies(selected_rows,view);wanted,clauses=oracle.solve(selected_rows,view)
   ck('independent_policy_sets/'+repr((receipt,view,family)),got,wanted)
   old=next(x for x in previous if F(x['receipt'])==receipt and x['view']==view and x['family']==family);oldset=set()
   for choices in old['policy_choices']:
    first=tuple(sorted([(tup(k),v) for k,v in choices['first']],key=repr));cells=[tup(k) for k,_ in choices['second_allowed']]
    for choices2 in product(*(actions for _,actions in choices['second_allowed'])):oldset.add((first,tuple(sorted(zip(cells,choices2),key=repr))))
   ck('earlier_complete_policy_sets/'+repr((receipt,view,family)),got,oldset)
   summaries.append({'receipt':receipt,'view':view,'family':family,'world_rows':len(selected_rows),'feasible_policies':sorted(got,key=repr),'count':len(got),'candidate_decisions':decisions,'independent_constraints':clauses})
  print(json.dumps({'policy_counts':[(x['receipt'],x['view'],x['family'],x['count']) for x in summaries]}),flush=True)
 # Counterexamples identify incompatible commands inside one signal cell.
 examples=[
  {'row_id':'low_coupon_pay','obs1':('high',False),'obs2':('high',False,'pay',False,True),'a1':'pay','a2':'pay','status':'accepted'},
  {'row_id':'low_coupon_draw','obs1':('high',False),'obs2':None,'a1':'draw','a2':'pay','status':'refused1'},
  {'row_id':'high_coupon_pay','obs1':('high',True),'obs2':None,'a1':'pay','a2':'pay','status':'refused1'},
  {'row_id':'high_coupon_draw','obs1':('high',True),'obs2':('high',True,'draw',False,True),'a1':'draw','a2':'pay','status':'accepted'}]
 ck('coarse_indistinguishable_conflict',len(candidate.enumerate_policies(examples,'coarse')[0]),0)
 ck('refinement_separates_conflict',bool(candidate.enumerate_policies(examples,'refined')[0]))
 ck('dropped_world_falsely_relaxes',bool(candidate.enumerate_policies(examples[:2],'coarse')[0]));controls.append('lost_world_changes_feasibility')
 no_right=cp(examples[2:]);no_right[1].update(status='refused1',obs2=None)
 ck('unavailable_right_has_no_action',len(candidate.enumerate_policies(no_right,'refined')[0]),0);controls.append('hidden_unavailable_right')
 if refinements:
  record=refinements[-1];job=tuple(record['job']);steps=by[(job[0],job[1],job[4],job[5])]
  bad=cp(record);bad['children'].pop();reject('dropped_observation_child',lambda:refinement_check(bad,steps,job))
  bad=cp(record);bad['children'][0]['predicate']['strict']=True;reject('changed_coverage_boundary',lambda:refinement_check(bad,steps,job))
 if rows:
  bad=cp(rows[-1]);bad['obs1']=tuple(bad['obs1'])+(bad['right'],);reject('leaked_hidden_right',lambda:reference_observation(bad))
  bad=cp(rows[-1]);bad['obs1']=tuple(bad['obs1'])+(bad['job'][3],);reject('anticipative_second_rate',lambda:reference_observation(bad))
  late=next((x for x in rows if x['obs2'] is not None),None)
  if late:
   bad=cp(late);bad['obs2']=tuple(bad['obs2'][:-1])+(not bad['obs2'][-1],);reject('altered_pre_payment_coverage',lambda:reference_observation(bad))
 if not diagnostic:
  good=next(x for x in summaries if x['receipt']==7 and x['view']=='refined' and x['family']=='committed')
  ck('four_feasible_not_ranked',good['count'],4)
  six=next(x for x in summaries if x['receipt']==6 and x['view']=='refined' and x['family']=='committed');ck('repayment_exhaustion',six['count'],0);controls.append('R6_resource_veto')
  # Ignoring all refused rows is a wrong oracle even with identical state formulas.
  accepted_only=[x for x in rows if x['receipt']==7 and x['right'] and x['status']=='accepted']
  ck('ignored_refusals_falsely_relax',bool(candidate.enumerate_policies(accepted_only,'coarse')[0]));controls.append('ignored_refused_branches')
 for path,h in lock.items():ck('source_preserved:'+path,sha(ROOT/path),h)
 result={'status':'PASS','mode':'diagnostic' if diagnostic else 'full','jobs':jobs,'observation_rows':len(rows),'refinement_pairs':len(refinements),'refinement_proofs':proof_count,'whole_atom_signal_proofs':len(signal_proofs),'policy_problems':len(summaries),'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'policy_counts':[{k:x[k] for k in ('receipt','view','family','count')} for x in summaries],'scope':'Exact robust reachable policies for declared synthetic observations and selected world family; no optimality, probabilities or actual actor-source admission.'}
except Exception:result={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',result),('checks.json',checks),('controls.json',controls),('source-lock.json',lock),('policy-comparisons.json',summaries),('rows.json',rows),('observation-refinements.json',refinements),('signal-proofs.json',locals().get('signal_proofs',[]))]:(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT)+(' diagnostic' if diagnostic else ''),'python':platform.python_version(),'environment':'standard-library CPU; GPU intentionally hidden','data':'immutable exact region certificates, prior full policy reference and explicit synthetic information maps','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-certified-observation-policy-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
