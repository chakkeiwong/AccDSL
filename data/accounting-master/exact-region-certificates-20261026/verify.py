"""Bounded exact-region certification. Full partitions, never point promotion."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy as cp
import gzip,hashlib,importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
import regions as r
import geometry as g
import proofcheck as pc
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=HERE.parent/'symbolic-path-composition-20261026/attempt-01';M=HERE.parent/'symbolic-method-certificate-20261026/attempt-01'
sys.path.insert(0,str(HERE.parent/'two-date-continuous-memory-20261026'))
import model as types
spec=importlib.util.spec_from_file_location('prior_closed_form',HERE.parent/'two-date-continuous-memory-20261026/oracle.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sys.path.insert(0,str(HERE.parent/'symbolic-path-composition-20261026'));import expected_path as ep
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic()
limit=4 if len(sys.argv)>2 and sys.argv[2]=='diagnostic' else 3872
checks=[];controls=[];counts={'jobs':0,'nonempty_leaves':0,'accepted_leaves':0,'refused_leaves':0,'empty_certificates':0};sample=[]
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n+': '+repr(x)[:300]+' != '+repr(y)[:300])
def reject(name,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(name);ck(name,True)
 else:ck(name,False)
def tuples(x):
 if isinstance(x,list):return tuple(tuples(z) for z in x)
 if isinstance(x,dict):return {k:tuples(v) for k,v in x.items()}
 return x
source={Path(__file__).resolve(),HERE/'regions.py',HERE/'geometry.py',HERE/'proofcheck.py',ROOT/'docs/plans/accounting-exact-region-certificates-20261026.md',P/'verification.json',P/'source-lock.json',P/'cases.json',M/'verification.json',M/'source-lock.json',M/'certificates.json',HERE.parent/'symbolic-path-composition-20261026/expected_path.py',HERE.parent/'two-date-continuous-memory-20261026/model.py',HERE.parent/'two-date-continuous-memory-20261026/oracle.py'}
lock={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}
for p in source:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
scope={'profile':'SelectedExactRegionJob/1','source_revision':'synthetic-source-v1','clause':'once-only-v1','horizon':'two-2027-dates','query':'complete-account-memory-flows-and-refusal-prefix','valuation':'known-exact-rational','chart':'alpha','method_certificate':hashlib.sha256((M/'certificates.json').read_bytes()).hexdigest(),'composition_certificate':hashlib.sha256((P/'cases.json').read_bytes()).hexdigest(),'source_lock':r.digest(lock),'observation_policy':'not_certified'}
def physical(a):return types.A(*map(F,a))
def state_check(leaf,job,steps):
 mode,right,ix,iy,a1,a2,R=job
 n=6 if leaf['kind']=='accepted' else leaf['event_index']
 if n not in (1,5,6):raise ValueError('unexpected_reachable_refusal')
 state=steps[n-1]['after'];status='accepted' if n==6 else 'refused1' if n==1 else 'refused2'
 v={'I1':r.coupon(mode,0,ix),'I2':r.coupon(mode,1,iy),'R':[0,0,R]}
 b={k:physical(r.affine(x,v)) for k,x in state['book'].items()}
 reduced={k:b[k] for k in ('cash','other_assets')};reduced.update({k:-b[k] for k in ('old_debt','facility_debt','interest_payable')})
 reduced['equity']=sum((-b[k] for k in ('capital','income','interest_expense','fee_expense')),types.aff(0))
 expected=prior.expected(mode,right,r.atoms()[ix],r.atoms()[iy],F(R),a1,a2,status)
 if reduced!=expected['balances']:raise ValueError('independent_financial_formula')
 if state['memory']['used'][2]!=expected['facility_used']:raise ValueError('used_history')
 # Independent full-state formulas also protect signed profit/expense and flows.
 if state!=tuples(ep.state(n,mode,right,a1,a2)):raise ValueError('complete_state_formula')
 return {'status':status,'prefix_events':n,'complete_symbolic_state_sha256':r.digest(state)}
def check_job(bundle,steps,job):
 if set(bundle)!={'scope','job','instructions','tree'} or bundle['scope']!=scope or tuple(bundle['job'])!=tuple(job):raise ValueError('job_scope')
 expected=r.instructions(ep.steps(job[0],job[1],job[4],job[5]),job)
 if bundle['instructions']!=expected:raise ValueError('independent_instruction_sequence')
 leaves=r.verify_tree(r.domain(job[2],job[3]),expected,bundle['tree'])
 for leaf in leaves:
  if leaf['kind']!='empty':state_check(leaf,job,steps)
 return leaves
try:
 for path in (P,M):
  ck('predecessor_pass:'+path.parent.name,json.loads((path/'verification.json').read_text())['status'],'PASS')
  for p,h in json.loads((path/'source-lock.json').read_text()).items():ck('protected_predecessor:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 pathcases=tuples(json.loads((P/'cases.json').read_text()));by={(x['mode'],x['right'],*x['actions']):x['steps'] for x in pathcases if x['chart']=='alpha'}
 atoms=r.atoms();ck('atom_count',len(atoms),11);ck('atom_endpoints',(atoms[0][0],atoms[-1][1]),(F(1,50),F(2,25)))
 for i in range(10):ck('atom_adjacency/'+str(i),atoms[i][1],atoms[i+1][0])
 for mode in ('fixed','floating'):
  for axis in (0,1):
   for i,atom in enumerate(atoms):ck('coupon_piece/'+mode+'/'+str(axis)+'/'+str(i),physical(r.coupon(mode,axis,i)),prior.oracle_interest(mode,axis,*atom))
 # A zero constant contradicts only if some positive-weight inequality is strict.
 strict=[r.H(1,0,0,True),r.H(-1,0,0)]
 proof=g.produce(strict);ck('strict_contradiction',pc.verify(strict,proof),'empty')
 weak=cp(strict);weak[0]['strict']=False;reject('strictness_removed',lambda:pc.verify(weak,proof))
 bad=cp(proof);bad['weights'][next(iter(bad['weights']))]='0';reject('zero_multiplier',lambda:pc.verify(strict,bad))
 bad=cp(proof);bad['weights'][next(iter(bad['weights']))]='2';reject('unbalanced_multiplier',lambda:pc.verify(strict,bad))
 reject('invalid_witness',lambda:pc.verify([r.H(1,0,0)],{'kind':'witness','point':['1','0']}))
 roster=r.roster();jobs=roster if limit==3872 else [roster[i] for i in (0,1000,3000,3871)]
 with gzip.open(OUT/'jobs.jsonl.gz','wt',compresslevel=1) as out:
  for job in jobs:
   mode,right,ix,iy,a1,a2,R=job;steps=by[(mode,right,a1,a2)]
   ins=r.instructions(steps,job);bundle={'scope':scope,'job':job,'instructions':ins,'tree':r.build(r.domain(ix,iy),ins)}
   leaves=check_job(bundle,steps,job)
   if len(sample)<2 and any(x['kind']=='refused' for x in leaves):sample.append(cp(bundle))
   counts['jobs']+=1
   for x in leaves:
    if x['kind']=='empty':counts['empty_certificates']+=1
    else:counts['nonempty_leaves']+=1;counts[x['kind']+'_leaves']+=1
   out.write(json.dumps(bundle,separators=(',',':'))+'\n')
   if counts['jobs']%500==0:print(json.dumps({**counts,'elapsed':time.monotonic()-start}),flush=True)
 ck('requested_jobs_complete',counts['jobs'],limit)
 # Actual bound proof mutations; no conclusion from merely changing a checksum.
 good=sample[-1] if sample else bundle;j=tuple(good['job']);s=by[(j[0],j[1],j[4],j[5])]
 bad=cp(good);bad['scope']['source_revision']='v2';reject('changed_source_scope',lambda:check_job(bad,s,j))
 bad=cp(good);bad['instructions'][0]['predicate']=False;reject('changed_coupon_instruction',lambda:check_job(bad,s,j))
 bad=cp(good)
 node=bad['tree']
 while node.get('kind')=='constant_true':node=node['child']
 if node.get('kind')=='split':node.pop('no')
 else:node['kind']='accepted'
 reject('missing_partition_child',lambda:check_job(bad,s,j))
 changed=cp(s);changed[0]['after']['memory']['due1']=('linear',(), '0')
 reject('erased_unpaid_memory',lambda:state_check({'kind':'refused','event_index':1},j,changed))
 for p,h in lock.items():ck('protected:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 result={'status':'PASS','mode':'diagnostic' if limit==4 else 'full_selected_roster',**counts,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'selected_roster':3872,'closed_jobs':counts['jobs'],'pending_jobs':3872-counts['jobs'],'scope':'Exact selected known-valued two-rate job partitions and financial relations; no policy/observation or general-runtime proof.'}
except Exception:result={'status':'FAIL',**counts,'assertions':len(checks),'error':traceback.format_exc()}
finally:
 for name,x in [('verification.json',result),('checks.json',checks),('controls.json',controls),('scope.json',scope),('source-lock.json',lock)]: (OUT/name).write_text(json.dumps(x,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT)+(' diagnostic' if limit==4 else ''),'environment':'standard-library CPU; GPU intentionally hidden','python':platform.python_version(),'seeds':'N/A exact deterministic','data':'selected3872 obligations with pinned affine composition and independent oracle','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-exact-region-certificates-20261026.md','result':str(OUT/'verification.json'),'proof_archive_sha256':hashlib.sha256((OUT/'jobs.jsonl.gz').read_bytes()).hexdigest() if (OUT/'jobs.jsonl.gz').exists() else None},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
