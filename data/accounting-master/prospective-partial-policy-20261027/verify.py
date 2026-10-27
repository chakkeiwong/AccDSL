"""Exact frontier-by-frontier comparisons; versioned evidence only."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parents[2]
s=importlib.util.spec_from_file_location('own_prospective_partial',H/'partial.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120))
start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];results=[];transitions=[];pins={}
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def refuse(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
 else:ck('refusal:'+n,False)
try:
 ctx=m.Context();pins.update(ctx.methods.files);pins.update(ctx.evidence.dependencies);pins.update(ctx.evidence.method_files)
 P=H.parent/'prospective-policy-domain-20261027/attempt-03';T=H.parent/'temporal-frontier-20261027/attempt-01'
 for base in [P,T]:
  lock=json.loads((base/'source-lock.json').read_text())
  for n,h in lock.items():ck('predecessor:'+n,sha(R/n),h);pins[n]=h
  for q in base.glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'partial.py',H/'verify.py',R/'docs/plans/accounting-prospective-partial-policy-20261027.md']:
  pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for n in ['partial.py','verify.py']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1')
 declarations=json.loads((P/'declared-before-evaluation.json').read_text())
 for row in declarations:
  got=m.d.derive(row['input'],m.identity(row['input']),row['declaration'],m.identity(row['declaration']),ctx.evidence)
  ck(row['case']+':prospective_domain',got,row['domain'])
 save('domains-before-frontiers.json',declarations)
 saved=json.loads((T/'checkpoints.json').read_text());cache={};endpoints={}
 def sequence(x,eid):
  if eid in cache:return cache[eid]
  matches=[v for v in saved if v['expected_input']==eid and v.get('limit',4096)==4096]
  ck('at_most_one_saved:'+eid,len(matches)<=1)
  if matches:seq=matches[0]['checkpoints'];origin='saved_all_checkpoints'
  else:
   front=m.z.start(x,eid,ctx.methods);seq=[front];origin='new_16_node_increments'
   while not front['complete'] and front['resolved']<4096:
    front,work=m.z.resume(front,m.identity(front),eid,ctx.methods,16);ck('resume_progress:'+eid+':'+str(front['resolved']),work>0);seq.append(front)
  cache[eid]=(seq,origin);return seq,origin
 def run(name,x,decl,domain,seq,limit=4096,origin='saved'):
  eid=m.identity(x);did=m.identity(decl);uid=m.identity(domain);prior=None;curve=[]
  for front in seq:
   fid=m.identity(front);before=m.identity([front,decl,domain]);label=name+':'+str(front['resolved'])
   # Candidate and independent checker must never request complete temporal evaluation.
   old=m.d.b.f.evaluate;old_enum=m.d.b.f.t.enumerate_views
   def forbidden(*args,**kwargs):raise AssertionError('hindsight_complete_evaluation')
   m.d.b.f.evaluate=forbidden;m.d.b.f.t.enumerate_views=forbidden
   try:
    got=m.evaluate(front,fid,eid,decl,did,domain,uid,ctx,limit)
    ck(label+':independent_verification',m.verify(got,m.identity(got),front,fid,eid,decl,did,domain,uid,ctx,limit))
   finally:m.d.b.f.evaluate=old;m.d.b.f.t.enumerate_views=old_enum
   ck(label+':pure',m.identity([front,decl,domain]),before)
   candidates=None if got['candidates'] is None else {tuple(v) for v in got['candidates']}
   if prior is not None:ck(label+':monotone',candidates<=prior)
   prior=candidates
   if front['resolved']==0 and candidates is not None:
    ck(label+':root_all_rules',len(candidates),2**domain['required_keys']);ck(label+':root_pending',got['status'],'unresolved_pending')
   curve.append(dict(resolved=front['resolved'],pending=len(front['pending']),known_outcomes=len(front['outcomes']),
    unknown_outcomes=len(got['unknown_outcomes']),candidates=None if candidates is None else len(candidates),status=got['status']))
   results.append(dict(case=name,frontier=front,result=got,limit=limit,declaration=decl,domain=domain))
  transitions.append(dict(case=name,origin=origin,sequence=curve));endpoints[name]=results[-1]
 for row in declarations:
  seq,origin=sequence(row['input'],m.identity(row['input']))
  run(row['case'],row['input'],row['declaration'],row['domain'],seq,origin=origin)
 # Contradictory clocks are valid input with no possible temporal assignment.
 badseq=next(v for v in saved if v['case']=='public_access_before_publication')
 x=badseq['checkpoints'][0]['input']
 fs=importlib.util.spec_from_file_location('own_prospective_fixture',P.parent/'fixtures.py');f=importlib.util.module_from_spec(fs);fs.loader.exec_module(f)
 decl=f.declaration(x,ctx.evidence);domain=m.d.derive(x,m.identity(x),decl,m.identity(decl),ctx.evidence)
 save('inconsistent-domain-before-comparison.json',dict(input=x,declaration=decl,domain=domain))
 run('inconsistent_clocks',x,decl,domain,badseq['checkpoints']);ck('inconsistent_is_not_feasible',endpoints['inconsistent_clocks']['result']['status'],'inconsistent_clocks')
 base=declarations[0];front=m.z.start(base['input'],m.identity(base['input']),ctx.methods,2);capped,work=m.z.resume(front,m.identity(front),m.identity(base['input']),ctx.methods,2,2)
 run('execution_cap2',base['input'],base['declaration'],base['domain'],[front,capped],limit=2,origin='new_explicit_cap')
 ck('cap_stays_pending',endpoints['execution_cap2']['result']['status'],'unresolved_pending')
 # Complete references are loaded only after all candidate frontier evaluations.
 fulls=json.loads((P/'cases.json').read_text())
 for ref in fulls:
  got=endpoints[ref['case']]['result'];ck(ref['case']+':complete_candidates',got['candidates'],ref['candidates']);ck(ref['case']+':complete_status',got['status'],ref['status'])
  if 'family' in ref:
   ck(ref['case']+':complete_supports',got['known_supports'],ref['family']['supports'])
   ck(ref['case']+':complete_unknowns',got['unknown_outcomes'],[o['outcome'] for o in ref['unknown_outcomes']])
 target=next(v for v in results if v['case']=='baseline' and v['frontier']['pending'] and v['result']['rejections'])
 def altered(name,change,item=target):
  r=cp(item['result']);change(r);front=item['frontier'];decl=item['declaration'];domain=item['domain']
  refuse(name,lambda:m.verify(r,m.identity(r),front,m.identity(front),front['input_sha256'],decl,m.identity(decl),domain,m.identity(domain),ctx,item['limit']))
 for name,mut in [
  ('false_feasible',lambda r:r.update(status='conditionally_feasible')),('drop_pending',lambda r:r['pending'].clear()),
  ('drop_pending_domain',lambda r:r['pending_domains'].clear()),('drop_support',lambda r:r['known_supports'].clear()),
  ('false_complete',lambda r:r.update(complete=True)),('duplicate_candidate',lambda r:r['candidates'].append(cp(r['candidates'][0]))),
  ('remove_candidate',lambda r:r['candidates'].pop()),('bool_bit',lambda r:r['candidates'][0].__setitem__(0,False)),
  ('drop_rejection',lambda r:r['rejections'].pop()),('wrong_witness',lambda r:r['rejections'][0].update(row='unknown')),
  ('wrong_domain',lambda r:r.update(domain_sha256='0'*64)),('wrong_frontier',lambda r:r.update(frontier_sha256='0'*64)),
  ('wrong_declaration',lambda r:r.update(declaration_sha256='0'*64)),('wrong_method',lambda r:r.update(method_identity='0'*64)),
  ('wrong_known_status',lambda r:r.update(known_constraint_status='empty')),('invent_probability',lambda r:r.update(probability=1))]:altered(name,mut)
 for flag in m.d.b.FLAGS:altered('admission:'+flag,lambda r,k=flag:r.__setitem__(k,True))
 altered('discard_unknown',lambda r:r['unknown_outcomes'].clear(),endpoints['unknown_access'])
 altered('unknown_as_feasible',lambda r:r.update(status='conditionally_feasible'),endpoints['unknown_access'])
 altered('inconsistent_as_feasible',lambda r:r.update(status='conditionally_feasible'),endpoints['inconsistent_clocks'])
 altered('budget_as_empty',lambda r:r.update(candidates=[]),endpoints['new_correction_label'])
 front=target['frontier'];decl=target['declaration'];domain=target['domain'];fid=m.identity(front);eid=front['input_sha256']
 for name,mut in [('shrink_domain',lambda v:v['keys'].pop()),('reorder_domain',lambda v:v['keys'].reverse())]:
  bad=cp(domain);mut(bad);refuse(name,lambda q=bad:m.evaluate(front,fid,eid,decl,m.identity(decl),q,m.identity(q),ctx))
 for name,mut in [('changed_actor',lambda v:v.update(actor='Bob')),('changed_source',lambda v:v['maps'][0].update(source_sha256='0'*64)),
  ('changed_message',lambda v:v['maps'][0]['first'][0].update(token='new'))]:
  bad=cp(decl);mut(bad);refuse(name,lambda q=bad:m.evaluate(front,fid,eid,q,m.identity(q),domain,m.identity(domain),ctx))
 bad=cp(front);bad['pending'].clear();refuse('tampered_frontier',lambda:m.evaluate(bad,m.identity(bad),eid,decl,m.identity(decl),domain,m.identity(domain),ctx))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',cases=len(transitions),checkpoints=len(results),assertions=len(checks),controls=len(controls),protected_files=len(pins),
  scope='fixed prospective original-registry domains over verified partial temporal frontiers; finite synthetic evidence only')
except Exception:
 summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,obj in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',results),('transitions.json',transitions)]:save(n,obj)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],
  git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU deliberately hidden',
  started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A deterministic exhaustive sets',data_version='source-lock.json',
  plan='docs/plans/accounting-prospective-partial-policy-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')
