from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,resource,subprocess,sys,time,traceback
import refinement as m
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120))
start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def refuse(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
 else:ck('refusal:'+n,False)
try:
 P=H.parent/'prospective-partial-policy-20261027/attempt-01';T=H.parent/'policy-domain-transport-20261027/attempt-01'
 for directory in [P,T]:
  ck('accepted_result:'+str(directory),json.loads((directory/'verification.json').read_text())['status'],'PASS')
  for n,h in json.loads((directory/'source-lock.json').read_text()).items():ck('accepted:'+n,sha(R/n),h);pins[n]=h
  for q in directory.glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'refinement.py',H/'verify.py',R/'docs/plans/accounting-policy-observation-refinement-20261027.md']:pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for n in ['refinement.py','verify.py']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');ctx=m.p.Context();saved=json.loads((P/'cases.json').read_text());plans=[]
 def select(name):
  rows=[v for v in saved if v['case']==name];return [rows[i] for i in sorted({0,len(rows)//2,len(rows)-1})]
 for item in select('two_source_supports_one_policy'):
  new=next(v['declaration'] for v in saved if v['case']=='new_low_correction_label')
  ck('same_original_split',new['input_sha256'],item['frontier']['input_sha256']);plans.append(dict(case='low_correction_split',item=item,old=item['declaration'],new=new))
 for name in ['baseline','unknown_access','conflicting_heads','inconsistent_clocks']:
  for item in select(name):
   old=cp(item['declaration']);new=cp(old)
   for row in old['maps']:
    for token in row['first']:token['token']='same'
   plans.append(dict(case='collision_to_refined:'+name,item=item,old=old,new=new))
 for item in select('baseline'):
  old=item['declaration'];new=cp(old)
  for row in new['maps']:
   for stage in ['first','second']:
    for token in row[stage]:token['token']='renamed:'+token['token']
  plans.append(dict(case='renaming_control',item=item,old=old,new=new))
 save('declarations-before-comparison.json',[dict(case=v['case'],frontier_sha256=m.identity(v['item']['frontier']),old=v['old'],new=v['new']) for v in plans])
 for row in plans:
  item=row['item'];front=item['frontier'];old=row['old'];new=row['new'];before=m.identity([front,old,new])
  result=m.evaluate(front,m.identity(front),front['input_sha256'],old,m.identity(old),new,m.identity(new),ctx,item['limit'])
  label=row['case']+':'+str(front['resolved']);ck(label+':pure',m.identity([front,old,new]),before)
  ck(label+':lifts_exact',result['lifted_candidates'],result['constant_fiber_candidates']);ck(label+':no_actual_information',result['actual_actor_information_claim'],False)
  if row['case']=='renaming_control':ck(label+':no_additional',result['additional_candidates'],[])
  if front['complete'] and row['case'].endswith('unknown_access'):ck(label+':unknown_preserved',result['new_result']['status'],'unresolved_source_family')
  if front['status']=='inconsistent_clocks':ck(label+':inconsistent_preserved',result['new_result']['status'],'inconsistent_clocks')
  cases.append(dict(case=row['case'],resolved=front['resolved'],complete=front['complete'],result=result))
 full=next(v for v in cases if v['case']=='collision_to_refined:baseline' and v['complete']);ck('coarse_no_rule',full['result']['old_result']['candidates'],[]);ck('refined_rules_present',len(full['result']['new_result']['candidates'])>0);ck('strict_reached_difference',len(full['result']['additional_reached_behaviors'])>0)
 base=plans[0];front=base['item']['frontier'];old=base['old'];new=base['new'];x=front['input'];eid=front['input_sha256']
 refuse('reverse_split_direction',lambda:m.relation(x,eid,new,m.identity(new),old,m.identity(old),ctx.evidence))
 def changed(n,mut):
  bad=cp(new);mut(bad);refuse(n,lambda:m.relation(x,eid,old,m.identity(old),bad,m.identity(bad),ctx.evidence))
 changed('actor',lambda v:v.update(actor='Bob'));changed('time',lambda v:v.update(second_at='2026-01-04T00:00:00Z'));changed('action',lambda v:v['actions'].update(first=['draw','pay']))
 changed('source',lambda v:v['maps'][0].update(source_sha256='0'*64));changed('input',lambda v:v.update(input_sha256='0'*64));changed('bound',lambda v:v.update(max_policy_keys=11))
 changed('merge_instead_of_refine',lambda v:[q.update(token='one') for row in v['maps'] for q in row['first']]);changed('drop_raw_key',lambda v:v['maps'][0]['first'].pop())
 bad=cp(front);bad['pending'].clear();refuse('drop_frontier_pending',lambda:m.evaluate(bad,m.identity(bad),eid,old,m.identity(old),new,m.identity(new),ctx))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='exact erasure/lift for same-input declared observation refinement;selected-history behavior only')
except Exception:summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,x)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact finite sets',data_version='source-lock.json',plan='docs/plans/accounting-policy-observation-refinement-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')

