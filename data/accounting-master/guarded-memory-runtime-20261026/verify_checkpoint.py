"""One-shot scope/queue and complete-prefix resume checks, separate from bridge."""
from pathlib import Path
from copy import deepcopy as cp
import json,sys,os,time,platform,subprocess,hashlib,traceback
import checkpoint as c
rt=c.rt;HERE=Path(__file__).resolve().parent;ROOT=c.b.ROOT
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic()
saved=json.loads((HERE/'attempt-01/cases.json').read_text());checks=[];controls=[];cases=[]
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n)
def reject(n,fn):
 try:fn();ok=False
 except (ValueError,KeyError,IndexError):ok=True
 ck(n,ok);controls.append({'name':n,'discriminates':ok})
def compare(record,baseline):
 ck('whole_book',record['current'],baseline['current']);ck('cursor',record['cursor'],len(baseline['trace']))
 ck('remaining',record['remaining'],[rt.identity(x) for x in baseline['remaining_commands']])
 ck('status',record['status'],'refused_concrete' if baseline['stop'] else 'complete_concrete')
 for a,b in zip(record['accepted'],baseline['trace']):
  for key in ('command','request','result','before_sha256'):ck('accepted_'+key,a[key],b[key])
 if baseline['stop']:
  for key in ('command','request','result','before_sha256'):ck('stop_'+key,record['stop'][key],baseline['stop'][key])
 else:ck('no_stop',record['stop'],None)
sources={HERE/'checkpoint.py',HERE/'verify_checkpoint.py',HERE/'attempt-01/verification.json',HERE/'attempt-01/cases.json',ROOT/'docs/plans/accounting-guarded-memory-checkpoint-20261026.md'}
for mod in list(sys.modules.values()):
 p=getattr(mod,'__file__',None)
 if p and Path(p).resolve().is_relative_to(ROOT) and Path(p).suffix=='.py':sources.add(Path(p).resolve())
lock={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
for p in sources:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
try:
 terminal={};prefixes={};bodies={};S=c.scope()
 for ix in (5,4):
  entry=saved[ix];body=entry['body'];bodies[ix]=body
  r=c.seed(body,S);pres=[cp(r)]
  for _ in range(6):
   if r['stop'] is None and r['cursor']<6:c.step(body,r)
   pres.append(cp(r))
  terminal[ix]=cp(r);prefixes[ix]=pres
  compare(r,entry['execution'])
  for pause,prefix in enumerate(pres):
   serialized=json.loads(json.dumps(prefix));before=cp(serialized)
   resumed,attempts=c.advance(body,S,serialized,6)
   ck('resume_does_not_mutate',serialized,before);compare(resumed,entry['execution'])
   cases.append({'saved_case':entry['id'],'pause':pause,'new_events':attempts,'status':resumed['status'],'checkpoint_sha256':rt.digest(serialized),'resumed_sha256':rt.digest(resumed)})
  print(json.dumps({'case':ix,'resume_boundaries':len(pres),'elapsed':time.monotonic()-start}),flush=True)
 # Zero budget and a real 2/1/3 event split, plus a second chart and first refusal.
 body=bodies[5];r=prefixes[5][2];r0,n=c.advance(body,S,r,0);ck('zero_budget_identity',r0,r);ck('zero_budget_attempts',n,0)
 r1,n=c.advance(body,S,r,1);ck('one_event_budget',n,1)
 r2,n=c.advance(body,S,r1,3);compare(r2,saved[5]['execution'])
 for ix in (19,3):
  body=saved[ix]['body'];r=c.seed(body,S);r,_=c.advance(body,S,r,6);compare(r,saved[ix]['execution']);cases.append({'saved_case':saved[ix]['id'],'status':r['status']})
 # Refused terminal remains replayable without attempting later commands.
 rr,n=c.advance(bodies[4],S,terminal[4],6);ck('refusal_no_later_events',n,0);ck('refusal_identity',rr,terminal[4])
 body=bodies[5];record=prefixes[5][2]
 for key,new in [('source_revision','revision2'),('clause','revolving'),('actor','lender'),('observation','coarse'),('actions',['pay']),('query','terminal_cash'),('horizon','three-dates'),('precision','cents'),('method','new-engine')]:
  changed=cp(S);changed[key]=new;reject('scope_'+key,lambda changed=changed:c.validate(body,changed,record))
 ck('old_actor_scope_still_valid',c.validate(body,S,record))
 # Mutations may remain balanced or carry a recomputed plain JSON checksum;
 # full prefix replay is the required criterion, not checksum equality alone.
 bad=cp(record);bad['current']['balances']['cash']='1/2';bad['current']['balances']['capital']='-1/4'
 reject('balanced_cash_change',lambda:c.validate(body,S,bad))
 bad2=cp(record);bad2['current']['memory']['used']=False
 reject('used_flag_change',lambda:c.validate(body,S,bad2))
 bad3=cp(record);bad3['current']['memory']['paid1']='5/1'
 reject('paid_history_change',lambda:c.validate(body,S,bad3))
 bad4=cp(record);bad4['cursor']=1
 reject('cursor_change',lambda:c.validate(body,S,bad4))
 bad5=cp(record);bad5['accepted'].pop()
 reject('missing_transition',lambda:c.validate(body,S,bad5))
 bad6=cp(record);bad6['remaining']=[]
 reject('dropped_pending_commands',lambda:c.validate(body,S,bad6))
 bad7=cp(record);bad7['status']='complete_concrete'
 reject('premature_complete',lambda:c.validate(body,S,bad7))
 bad8=cp(terminal[4]);bad8['stop']['result']['reason']='invented'
 reject('changed_stop',lambda:c.validate(bodies[4],S,bad8))
 changedbody=cp(body);changedbody['commands'][-1]['event']['date']='2027-12-30'
 reject('program_change',lambda:c.validate(changedbody,S,record))
 bad9=cp(record);bad9['registry']='0'*64
 reject('registry_change',lambda:c.validate(body,S,bad9))
 # No later source registry is consulted; an old query selects its old explicit
 # scope. Caller authentication/actual availability remain outside this layer.
 jobs={'accepted':rt.digest(bodies[5]),'refused':rt.digest(bodies[4]),'not_started':rt.digest(saved[0]['body'])}
 q=c.queue(jobs);ck('continuous_roster_size',len(q['region_roster']),3872)
 q=c.finish(q,'accepted',terminal[5]);q=c.finish(q,'refused',terminal[4]);ck('queue_valid',c.validate_queue(jobs,q));ck('pending_retained',q['pending'],['not_started']);ck('regions_not_certified',q['completed_regions'],[])
 mutated=cp(q);mutated['pending']=[];reject('dropped_job',lambda:c.validate_queue(jobs,mutated))
 mutated=cp(q);mutated['pending'].append('accepted');reject('duplicate_job',lambda:c.validate_queue(jobs,mutated))
 mutated=cp(q);mutated['pending'].append('foreign');reject('foreign_job',lambda:c.validate_queue(jobs,mutated))
 mutated=cp(q);mutated['completed_regions']=[q['region_roster'][0]];reject('witness_cannot_close_region',lambda:c.validate_queue(jobs,mutated))
 mutated=cp(q);mutated['records']['accepted']['program']=rt.digest(saved[0]['body']);reject('record_wrong_program',lambda:c.validate_queue(jobs,mutated))
 mutated=cp(q);mutated['region_roster'].pop();reject('dropped_continuous_region',lambda:c.validate_queue(jobs,mutated))
 reject('negative_budget',lambda:c.advance(body,S,record,-1))
 for p,h in lock.items():ck('source_unchanged:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 result={'status':'PASS','assertions':len(checks),'controls':len(controls),'resume_cases':len(cases),'unresolved_regions':len(q['region_roster']),'protected_files':len(lock),'scope':'Replay-validated concrete checkpoints and structural queue preservation; no continuous certification or durable storage.'}
except Exception:result={'status':'FAIL','assertions':len(checks),'controls':len(controls),'resume_cases':len(cases),'error':traceback.format_exc()}
finally:
 for name,obj in [('verification.json',result),('cases.json',cases),('checks.json',checks),('controls.json',controls),('source-lock.json',lock)]:
  (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':platform.python_version(),'environment':'CPU standard library; GPU intentionally hidden; bytecode disabled','data':'accepted bridge attempt-01; exact scope and job roster','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-guarded-memory-checkpoint-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)
