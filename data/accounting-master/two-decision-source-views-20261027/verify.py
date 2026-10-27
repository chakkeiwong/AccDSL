from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
from itertools import product
import json,os,platform,resource,subprocess,sys,time,traceback
import joint as m
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120))
start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
f=m.t.prior.load('joint_original_fixtures',H.parent/'source-time-intervals-20261027/fixtures.py')
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n

def fixtures():
 for name,clock,want in [
  ('before_both',f.point('2026-01-01T12:00:00Z'),{('coarse','coarse')}),
  ('between',f.point('2026-01-02T12:00:00Z'),{('refined','coarse')}),
  ('after_both',f.point('2026-01-03T12:00:00Z'),{('refined','refined')}),
  ('at_first',f.point('2026-01-02T00:00:00Z'),{('coarse','coarse')}),
  ('just_after_first',f.point('2026-01-02T00:00:00.0000001Z'),{('refined','coarse')}),
  ('at_second',f.point('2026-01-03T00:00:00Z'),{('refined','coarse')}),
  ('interval_both',f.interval('2026-01-01T12:00:00Z','2026-01-03T12:00:00Z'),{('coarse','coarse'),('refined','coarse'),('refined','refined')}),
  ('unknown_access',f.unknown(),{('coarse','coarse'),('refined','coarse'),('refined','refined')})]:
  b=f.oldcases.base();h=f.oldcases.add(b,'observation_scheme',{'view':'coarse'},supersedes=b['names']['observation_scheme'],when='2026-01-01T01:00:00Z')
  v=f.convert(b,{h:{'access:Alice':clock}},cutoffs={'system_asof':'2026-01-04T00:00:00Z'});x=m.f.wire(v)
  yield name,m.request(x,'2026-01-03T00:00:00Z','2026-01-03T00:00:00Z'),want
 for name,retract in [('late_retraction',True),('late_conflict',False)]:
  b=f.oldcases.base();h=f.oldcases.add(b,'observation_scheme',None if retract else {'view':'coarse'},supersedes=b['names']['observation_scheme'] if retract else None,when='2026-01-01T01:00:00Z',disposition='retraction' if retract else 'assertion')
  v=f.convert(b,{h:{'access:Alice':f.point('2026-01-02T12:00:00Z')}},cutoffs={'system_asof':'2026-01-04T00:00:00Z'})
  yield name,m.request(m.f.wire(v),'2026-01-03T00:00:00Z','2026-01-03T00:00:00Z'),{('refined','unresolved')}
 b=f.oldcases.base();h=b['names']['observation_scheme'];v=f.convert(b,{h:{'published':f.point('2026-01-03T00:00:00Z')}},cutoffs={'system_asof':'2026-01-04T00:00:00Z'})
 yield 'inconsistent',m.request(m.f.wire(v),'2026-01-03T00:00:00Z','2026-01-03T00:00:00Z'),set()
def label(o):return o['scenario']['view'] if o['status']=='selected_conditional' else 'unresolved'
try:
 e=m.d.b.Evidence();pins.update(e.dependencies);pins.update(e.method_files)
 for q in [H/'joint.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-two-decision-source-views-20261027.md',H.parent/'temporal-frontier-20261027/check.py']:pins[str(q.relative_to(R))]=sha(q)
 for n,h in pins.items():ck('predecessor:'+n,sha(R/n),h)
 save('source-lock.json',pins)
 for n in ['joint.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');inputs=list(fixtures());save('inputs-and-expectations.json',[dict(case=n,input=x,expected=sorted(w)) for n,x,w in inputs])
 for name,x,want in inputs:
  xid=m.identity(x);before=m.identity(x);result=m.evaluate(x,xid);ck(name+':independent_check',m.verify(result,m.identity(result),xid));ck(name+':pure',m.identity(x),before)
  actual={tuple(label(o) for o in pair) for pair in result['outcomes']};ck(name+':authored_joint_pairs',actual,want)
  ps,new=m.prepare(x,xid);marginals=[]
  for stage,p in enumerate(ps):
   marginal=m.t.enumerate_views(p);out,n=m.t.verify_tree(p,marginal['tree']);ck(name+':marginal_certificate:'+str(stage),n,marginal['nodes'])
   ck(name+':marginal_projection:'+str(stage),{m.identity(pair[stage]) for pair in result['outcomes']},{m.identity(o) for o in out});marginals.append(out)
  cart={tuple(label(o) for o in pair) for pair in product(*marginals)}
  if name=='interval_both':ck('marginal_cartesian_adds_impossible_pair',cart-actual,{('coarse','refined')})
  cases.append(dict(case=name,input=x,result=result,expected=sorted(want),marginals=marginals,cartesian_extra=sorted(cart-actual)))
 name,x,w=inputs[6];small=m.evaluate(x,m.identity(x),2);ck('budget_unresolved',small['status'],'unresolved_budget');ck('budget_checked',m.verify(small,m.identity(small),m.identity(x)));ck('budget_retains_request',small['remainder']['request'],x);save('budget-case.json',small)
 def refuse(n,fn):
  try:fn()
  except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
  else:ck('refusal:'+n,False)
 base=next(v for v in cases if v['case']=='between');res=base['result'];x=base['input']
 for name,mut in [('drop_support',lambda v:v['supports'].pop()),('drop_outcome',lambda v:v['outcomes'].pop()),('false_status',lambda v:v.update(status='conditionally_feasible')),('changed_scope',lambda v:v.update(scope='policy_solution')),('fake_complete',lambda v:v.update(complete=False))]:
  bad=cp(res);mut(bad);refuse(name,lambda q=bad:m.verify(q,m.identity(q),m.identity(x)))
 for flag in m.t.FLAGS:
  bad=cp(res);bad[flag]=True;refuse('admission:'+flag,lambda q=bad:m.verify(q,m.identity(q),m.identity(x)))
 bad=cp(res)
 def leaf(n):
  if n['kind']=='leaf':return n
  for c in n.get('children',[]):
   got=leaf(c)
   if got is not None:return got
 node=leaf(bad['tree']);node['outcomes'].reverse();refuse('rewrite_earlier_view',lambda:m.verify(bad,m.identity(bad),m.identity(x)))
 badx=cp(x);badx['second_decision_at']=x['original']['request']['decision_at'];refuse('unordered_decisions',lambda:m.evaluate(badx,m.identity(badx)))
 badx=cp(x);badx['second_effective_at']='2025-12-31T00:00:00Z';refuse('backward_effective_cutoff',lambda:m.evaluate(badx,m.identity(badx)))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='joint source sequences over shared clocks;no policy binding or resumable joint frontier')
except Exception:summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,x)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact rational certificates',data_version='source-lock.json',plan='docs/plans/accounting-two-decision-source-views-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')

