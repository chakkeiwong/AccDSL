from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy as cp
import gzip,hashlib,importlib.util,json,platform,resource,subprocess,sys,time,traceback
import regions as r
import queue as frontier
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PRE=HERE/'attempt-01';OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic()
sys.path.insert(0,str(HERE.parent/'symbolic-path-composition-20261026'));import expected_path as ep
sys.path.insert(0,str(HERE.parent/'two-date-continuous-memory-20261026'));import model as m
spec=importlib.util.spec_from_file_location('independent_prior',HERE.parent/'two-date-continuous-memory-20261026/oracle.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
checks=[];controls=[];registry={};counts={'accepted':0,'refused':0,'empty':0}
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n)
def reject(n,q,scope,reg):
 try:frontier.validate(scope,reg,q)
 except (ValueError,KeyError,TypeError):controls.append(n);ck(n,True)
 else:ck(n,False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source={Path(__file__).resolve(),HERE/'queue.py',HERE/'regions.py',HERE/'proofcheck.py',HERE/'geometry.py',PRE/'verification.json',PRE/'source-lock.json',PRE/'jobs.jsonl.gz',PRE/'scope.json',PRE/'run-manifest.json',ROOT/'docs/plans/accounting-region-certificate-queue-20261026.md',HERE.parent/'symbolic-path-composition-20261026/expected_path.py',HERE.parent/'two-date-continuous-memory-20261026/oracle.py',HERE.parent/'two-date-continuous-memory-20261026/model.py'}
lock={str(p.relative_to(ROOT)):sha(p) for p in source}
for p in source:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
try:
 ck('predecessor_PASS',json.loads((PRE/'verification.json').read_text())['status'],'PASS')
 ck('archive_hash',sha(PRE/'jobs.jsonl.gz'),json.loads((PRE/'run-manifest.json').read_text())['proof_archive_sha256'])
 for p,h in json.loads((PRE/'source-lock.json').read_text()).items():ck('protected_predecessor:'+p,sha(ROOT/p),h)
 scope=json.loads((PRE/'scope.json').read_text());roster=r.roster()
 with gzip.open(PRE/'jobs.jsonl.gz','rt') as f:
  for i,line in enumerate(f):
   row=json.loads(line);job=roster[i];mode,right,ix,iy,a1,a2,R=job
   ck('scope/'+str(i),row['scope'],scope);ck('job/'+str(i),row['job'],list(job))
   expected=r.instructions(ep.steps(mode,right,a1,a2),job)
   ck('instructions/'+str(i),row['instructions'],json.loads(json.dumps(expected)))
   leaves=r.verify_tree(r.domain(ix,iy),expected,row['tree'])
   for leaf in leaves:
    counts[leaf['kind']]+=1
    if leaf['kind']=='empty':continue
    n=6 if leaf['kind']=='accepted' else leaf['event_index'];ck('refusal_position/'+str(i),n in (1,5,6))
    state=ep.state(n,mode,right,a1,a2);v={'I1':r.coupon(mode,0,ix),'I2':r.coupon(mode,1,iy),'R':[0,0,R]}
    book={k:m.A(*map(F,r.affine(x,v))) for k,x in state['book'].items()}
    b={k:book[k] for k in ('cash','other_assets')};b.update({k:-book[k] for k in ('old_debt','facility_debt','interest_payable')});b['equity']=sum((-book[k] for k in ('capital','income','interest_expense','fee_expense')),m.aff(0))
    want=prior.expected(mode,right,r.atoms()[ix],r.atoms()[iy],F(R),a1,a2,'accepted' if n==6 else 'refused1' if n==1 else 'refused2')
    ck('financial_relation/'+str(i),b,want['balances'])
   registry[r.job_id(job)]=r.digest(row)
 ck('complete_archive',len(registry),3872)
 q=frontier.seed(scope,registry);ck('zero_budget',frontier.advance(scope,registry,q,0),q)
 all_at_once=frontier.advance(scope,registry,q,3872)
 for budget in (1,17,997,0,2500,357):
  q=frontier.advance(scope,registry,json.loads(json.dumps(q)),budget);frontier.validate(scope,registry,q)
 ck('pause_resume_equivalence',q,all_at_once);ck('no_pending_after_proofs',q['pending'],[])
 bad=cp(q);bad['scope']['source_revision']='v2';reject('changed_source',bad,scope,registry)
 bad=cp(q);bad['scope']['method_certificate']='0'*64;reject('changed_method',bad,scope,registry)
 bad=cp(q);bad['roster'].pop();reject('dropped_roster',bad,scope,registry)
 bad=cp(q);bad['certified'].pop(next(iter(registry)));reject('lost_certificate',bad,scope,registry)
 bad=cp(q);bad['certified'][next(iter(registry))]='0'*64;reject('false_completion',bad,scope,registry)
 bad=frontier.seed(scope,registry);bad['pending'].pop();reject('dropped_pending',bad,scope,registry)
 bad=frontier.seed(scope,registry);bad['pending'].append(bad['pending'][0]);reject('duplicate_pending',bad,scope,registry)
 bad=cp(q);bad['certified']['foreign']='0'*64;reject('foreign_job',bad,scope,registry)
 for p,h in lock.items():ck('protected:'+p,sha(ROOT/p),h)
 result={'status':'PASS','archive_jobs':len(registry),'leaf_counts':counts,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'certified_jobs':len(q['certified']),'pending_jobs':len(q['pending']),'scope':'Verified saved region archive and finite JSON frontier; not authenticated or crash-durable storage.'}
 (OUT/'registry.json').write_text(json.dumps(registry,indent=2)+'\n');(OUT/'final-queue.json').write_text(json.dumps(q,indent=2)+'\n')
except Exception:result={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for name,x in [('verification.json',result),('checks.json',checks),('controls.json',controls),('source-lock.json',lock)]: (OUT/name).write_text(json.dumps(x,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'environment':'standard-library CPU; GPU intentionally hidden','python':platform.python_version(),'data':'saved exact-region archive with source scope and independent financial formulas','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-region-certificate-queue-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
