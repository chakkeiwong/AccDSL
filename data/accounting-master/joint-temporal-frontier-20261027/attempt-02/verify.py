from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parents[2]
spec=importlib.util.spec_from_file_location('own_joint_frontier',H/'frontier.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120))
start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];sequences=[];policy_checks=[];pins={}
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def refuse(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
 else:ck('refusal:'+n,False)
try:
 J=H.parent/'two-decision-source-views-20261027/attempt-01';P=H.parent/'joint-stage-policy-20261027/attempt-01'
 for folder in [J,P]:
  ck('accepted_status:'+folder.parent.name,json.loads((folder/'verification.json').read_text())['status'],'PASS')
  for n,h in json.loads((folder/'source-lock.json').read_text()).items():ck('accepted:'+n,sha(R/n),h);pins[n]=h
  for q in folder.glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'frontier.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-joint-temporal-frontier-20261027.md']:pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for n in ['frontier.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');fulls=json.loads((J/'cases.json').read_text());policies=json.loads((P/'cases.json').read_text());e=m.b.b.Evidence();unit={}
 # Between-date case first is the smallest stage-order diagnostic.
 fulls.sort(key=lambda v:(v['case']!='between',v['case']))
 for ref in fulls:
  name=ref['case'];x=ref['input'];xid=m.identity(x);want=ref['result']
  for step in [1,7,4096]:
   front=m.start(x,xid);saved=[front];total=0
   while not front['complete'] and front['nodes']<4096:
    prior=m.identity(front);new,work=m.resume(front,prior,xid,step);ck(name+':'+str(step)+':immutable:'+str(front['nodes']),m.identity(front),prior);ck(name+':progress:'+str(new['nodes']),work>0);front=new;saved.append(front);total+=work
   ck(name+':'+str(step)+':complete',front['complete']);ck(name+':'+str(step)+':tree',front['tree'],want['tree']);ck(name+':'+str(step)+':outcomes',front['outcomes'],want['outcomes']);ck(name+':'+str(step)+':supports',front['supports'],want['supports']);ck(name+':'+str(step)+':work',total,want['nodes'])
   sequences.append(dict(case=name,step=step,checkpoints=saved))
   if step==1:unit[name]=saved
 # Check every unit-step prefix under each saved declaration for that request.
 for ref in policies:
  name=ref['case'];seq=unit[name.split(':')[0]];x=ref['input'];xid=m.identity(x);d=ref['declaration'];did=m.identity(d);domain=ref['domain'];uid=m.identity(domain);prior=None;curve=[]
  for front in seq:
   got=m.partial_policy(front,m.identity(front),xid,d,did,domain,uid,e);current=None if got['candidates'] is None else {tuple(v) for v in got['candidates']}
   if prior is not None and current is not None:ck(name+':monotone:'+str(front['nodes']),current<=prior)
   prior=current
   if front['nodes']==0 and current is not None:ck(name+':root_all_rules',len(current),2**domain['required_keys']);ck(name+':root_not_feasible',got['status'],'unresolved_pending')
   ck(name+':pending:'+str(front['nodes']),got['pending'],front['pending']);ck(name+':supports:'+str(front['nodes']),got['source_supports'],front['supports'])
   curve.append(dict(nodes=front['nodes'],status=got['status'],candidates=None if current is None else len(current),pending=len(got['pending']),unknown=len(got['unknown_outcomes'])))
  ck(name+':endpoint_candidates',got['candidates'],ref['result']['candidates']);ck(name+':endpoint_status',got['status'],ref['result']['status']);ck(name+':endpoint_rows',got['known_row_ids'],[r['id'] for r in ref['result']['rows']]);policy_checks.append(dict(case=name,transitions=curve,final=got))
 x=next(r['input'] for r in fulls if r['case']=='between');xid=m.identity(x);cap=m.start(x,xid,2);cap,work=m.resume(cap,m.identity(cap),xid,7,2);ck('cap_not_complete',cap['complete'],False);ck('cap_status',cap['status'],'capped');again,work=m.resume(cap,m.identity(cap),xid,7,2);ck('cap_no_more_work',work,0);ck('cap_retained',again,cap);save('cap-case.json',cap)
 base=unit['between'][4];fid=m.identity(base)
 for name,mut in [('drop_pending',lambda v:v['pending'].pop()),('drop_child',lambda v:v['tree']['children'].pop()),('wrong_stage',lambda v:v['tree'].update(stage=1)),('false_complete',lambda v:v.update(complete=True)),('wrong_nodes',lambda v:v.update(nodes=v['nodes']+1)),('wrong_method',lambda v:v.update(method_identity='0'*64))]:
  bad=cp(base);mut(bad);refuse(name,lambda q=bad:m.verify(q,m.identity(q),xid))
 full=unit['between'][-1];bad=cp(full);bad['supports'].pop();refuse('drop_support',lambda:m.verify(bad,m.identity(bad),xid))
 bad=cp(full);bad['outcomes'][0].reverse();refuse('reverse_joint_outcomes',lambda:m.verify(bad,m.identity(bad),xid))
 for flag in m.t.FLAGS:
  bad=cp(base);bad[flag]=True;refuse('admission:'+flag,lambda q=bad:m.verify(q,m.identity(q),xid))
 ref=next(r for r in policies if r['case']=='between:original');d=ref['declaration'];domain=ref['domain'];bad=cp(domain);bad['keys'].pop();refuse('changed_policy_domain',lambda:m.partial_policy(base,fid,xid,d,m.identity(d),bad,m.identity(bad),e))
 bad=cp(d);bad['mapping']['maps'][0]['first'][0]['token']='changed';refuse('changed_message_reuse',lambda:m.partial_policy(base,fid,xid,bad,m.identity(bad),domain,m.identity(domain),e))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',requests=len(fulls),complete_sequences=len(sequences),saved_checkpoints=sum(len(v['checkpoints']) for v in sequences),policy_cases=len(policy_checks),policy_prefixes=sum(len(v['transitions']) for v in policy_checks),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='exact logical joint continuation andfixed-domain partial policies;no crash durability')
except Exception:summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('sequences.json',sequences),('policy-checks.json',policy_checks)]:save(n,x)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact finite certificates',data_version='source-lock.json',plan='docs/plans/accounting-joint-temporal-frontier-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')

