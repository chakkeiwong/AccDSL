"""Fresh bounded evidence writer; compare all saved exact predecessor families."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,os,platform,resource,subprocess,sys,time,traceback
import frontier as z
H=Path(__file__).resolve().parent;R=H.parents[2];T=H.parent/'source-time-intervals-20261027'
f=z.t.prior.load('frontier_fixture_inputs',T/'fixtures.py')
OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];records=[];snapshots=[]
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:300]+' != '+repr(b)[:300])
def reject(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError,OverflowError):controls.append(n);ck(n,True)
 else:ck(n,False)
def certificates(tree):
 result={}
 def walk(n):
  if n['kind']!='pending':result[tuple(n['path'])]=z.identity(n['proof'])
  for ch in n.get('children',[]):walk(ch)
 walk(tree);return result
lock={};method=None
try:
 method=z.Methods();lock.update(method.files)
 for p in [H/'verify.py',H/'contract.md',R/'docs/plans/accounting-temporal-frontier-20261027.md',T/'fixtures.py',T/'attempt-01/proofs.json']:
  lock[str(p.relative_to(R))]=sha(p)
 save('source-lock.json',lock)
 for p in H.glob('*.py'):(OUT/p.name).write_bytes(p.read_bytes())
 fixtures={n:x for n,x,e in f.extended_cases() if e!='invalid'}
 for a in f.oldcases.suite():
  if a['name']!='future_published':fixtures['predecessor:'+a['name']]=f.convert(a['fixture'])
 baseline=json.loads((T/'attempt-01/proofs.json').read_text());ck('complete_case_population',set(fixtures),{a['case'] for a in baseline})
 diagnostic=len(sys.argv)>2;selected=baseline[:2] if diagnostic else baseline
 for a in selected:
  name=a['case'];x=z.f.wire(fixtures[name]);expected=z.identity(x);p=z.prepare(x,expected);ck(name+':prepared',p,a['prepared'])
  observed,nodecount=z.t.verify_tree(p,a['result']['tree']);ck(name+':baseline_outcomes',observed,a['result']['outcomes']);ck(name+':baseline_nodes',nodecount,a['result']['nodes'])
  for budget in [1,2,7,4096]:
   b=z.start(x,expected,method);sequence=[cp(b)];counts=[]
   while not b['complete']:
    old=cp(b);oldid=z.identity(b);prior=certificates(b['tree']);calls=[];solve=z.t.dc.solve
    def counted(*args):calls.append(1);return solve(*args)
    z.t.dc.solve=counted
    try:b,work=z.resume(b,oldid,expected,method,budget)
    finally:z.t.dc.solve=solve
    ck(name+':pure:'+str(budget)+':'+str(b['resolved']),z.identity(old),oldid)
    ck(name+':work:'+str(budget)+':'+str(b['resolved']),len(calls),work)
    ck(name+':progress:'+str(budget)+':'+str(b['resolved']),b['resolved']-old['resolved'],work)
    ck(name+':bounded:'+str(budget)+':'+str(b['resolved']),0<work<=budget)
    now=certificates(b['tree']);ck(name+':retained_certificates:'+str(budget)+':'+str(b['resolved']),all(now[k]==v for k,v in prior.items()))
    sequence.append(cp(b));counts.append(work)
   ck(name+':full_tree:'+str(budget),z.stripped(b['tree']),a['result']['tree'])
   ck(name+':full_outcomes:'+str(budget),b['outcomes'],a['result']['outcomes'])
   ck(name+':full_supports:'+str(budget),b['supports'],z.f.supports(a['result']['tree']))
   ck(name+':total_work:'+str(budget),sum(counts),nodecount)
   done,work=z.resume(b,z.identity(b),expected,method,budget);ck(name+':complete_no_work:'+str(budget),work,0);ck(name+':complete_stable:'+str(budget),done,b)
   records.append({'case':name,'budget':budget,'work':counts,'final':b})
   # Retain every unit-step pause for independent saved-file replay.
   if budget==1:snapshots.append({'case':name,'expected_input':expected,'checkpoints':sequence})
 base=baseline[0];x=z.f.wire(fixtures[base['case']]);eid=z.identity(x);initial=z.start(x,eid,method);first,_=z.resume(initial,z.identity(initial),eid,method,1)
 ck('root_split_all_children',len(first['tree']['children']),1+len(z.prepare(x,eid)['guards'][first['tree']['record']]))
 ck('root_split_unfinished',first['complete'],False);ck('root_no_claimed_outcome',first['outcomes'],[])
 partial,_=z.resume(initial,z.identity(initial),eid,method,3)
 ck('known_outcome_not_complete',bool(partial['outcomes']) and not partial['complete'])
 cap=z.start(x,eid,method,limit=2);cap,work=z.resume(cap,z.identity(cap),eid,method,4096,limit=2);ck('cap_status',cap['status'],'capped');ck('cap_retains_pending',bool(cap['pending']));ck('cap_work',work,2)
 again,work=z.resume(cap,z.identity(cap),eid,method,7,limit=2);ck('cap_no_repeat',work,0);ck('cap_stable',again,cap)
 snapshots.append({'case':'cap2','expected_input':eid,'limit':2,'checkpoints':[cap]})
 def altered(name,src,mut):
  b=cp(src);mut(b);reject(name,lambda:z.c.verify(b,z.identity(b),eid,method))
 altered('missing_complement',first,lambda b:b['tree']['children'].pop())
 altered('duplicate_pending',first,lambda b:b['tree']['children'].__setitem__(1,cp(b['tree']['children'][0])))
 altered('extra_pending',first,lambda b:b['tree']['children'].append(cp(b['tree']['children'][0])))
 altered('pending_wrong_path',first,lambda b:b['tree']['children'][0].__setitem__('path',[99]))
 altered('bool_pending_path',first,lambda b:b['tree']['children'][0].__setitem__('path',[False]))
 altered('pending_invents_outcome',first,lambda b:b['tree']['children'][0].__setitem__('outcome',{}))
 altered('pending_invents_domain',first,lambda b:b['tree']['children'][0].__setitem__('constraints',[]))
 altered('forged_resolved_count',first,lambda b:b.__setitem__('resolved',2))
 altered('boolean_resolved_count',first,lambda b:b.__setitem__('resolved',True))
 altered('missing_pending_summary',first,lambda b:b['pending'].pop())
 altered('forged_complete',partial,lambda b:b.__setitem__('complete',True))
 altered('forged_complete_status',partial,lambda b:b.__setitem__('status','complete_family'))
 altered('dropped_support',partial,lambda b:b['supports'].clear())
 altered('duplicated_support',partial,lambda b:b['supports'].append(cp(b['supports'][0])))
 altered('wrong_outcome_summary',partial,lambda b:b['outcomes'].clear())
 altered('method_changed',first,lambda b:b.__setitem__('method_identity','0'*64))
 altered('domain_changed',first,lambda b:b.__setitem__('prepared_sha256','0'*64))
 altered('profile_changed',first,lambda b:b.__setitem__('profile','future'))
 altered('unexpected_field',first,lambda b:b.__setitem__('discarded',[]))
 altered('wrong_branch',first,lambda b:b['tree'].__setitem__('record','foreign'))
 altered('invalid_witness',first,lambda b:b['tree']['proof']['values'].__setitem__('zero','1'))
 altered('source_changed',first,lambda b:b['input']['sources'].clear())
 altered('actor_changed',first,lambda b:b['input']['request'].__setitem__('actor','Bob'))
 altered('trust_changed',first,lambda b:b['input']['trusted'].clear())
 altered('request_changed',first,lambda b:b['input'].__setitem__('max_nodes',1))
 altered('limit_changed',first,lambda b:b.__setitem__('limit',2))
 altered('input_digest_changed',first,lambda b:b.__setitem__('input_sha256','0'*64))
 for n in z.t.FLAGS:altered('admission:'+n,first,lambda b,k=n:b.__setitem__(k,True))
 reject('stale_checkpoint_digest',lambda:z.c.verify(first,z.identity(initial),eid,method))
 reject('wrong_external_request',lambda:z.c.verify(first,z.identity(first),'0'*64,method))
 for budget in [0,-1,4097,True,1.5]:reject('invalid_budget:'+str(budget),lambda k=budget:z.resume(first,z.identity(first),eid,method,k))
 for limit in [0,4097,True]:reject('invalid_cap:'+str(limit),lambda k=limit:z.start(x,eid,method,limit=k))
 # A forged proof leaf with changed outcome must fail beyond its outer digest.
 altered('changed_leaf_outcome',partial,lambda b:b['tree']['children'][0]['children'][0].__setitem__('outcome',{'status':'unknown'}))
 bad=cp(first);completed=cp(partial['tree']['children'][0]);bad['tree']['children'][1]=completed;bad['tree']['children'][1]['path']=[1]
 reject('work_after_unfinished_prefix',lambda:z.c.verify(bad,z.identity(bad),eid,method))
 for n,h in lock.items():ck('locked:'+n,sha(R/n),h)
 summary={'status':'PASS','diagnostic':diagnostic,'cases':len(selected),'budget_runs':len(records),'saved_checkpoints':sum(len(v['checkpoints']) for v in snapshots),'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'scope':'Exact selected temporal partitions, preserved pending coverage, complete predecessor trees and source supports; no scalability, durable-store, actor knowledge or accounting admission.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for name,value in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('completed.json',records),('checkpoints.json',snapshots)]:save(name,value)
 commit=subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True)
 save('run-manifest.json',{'git':commit.stdout.strip() or 'unavailable existing marker','command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT)+(' diagnostic' if len(sys.argv)>2 else ''),'environment':'existing Python '+platform.python_version()+', CPU only; GPU deliberately hidden','data_version':'source-lock.json','seeds':'N/A exact deterministic replay','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-temporal-frontier-20261027.md','result':str(OUT/'verification.json'),'artifact_paths':['checkpoints.json','completed.json','checks.json','controls.json'],'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
