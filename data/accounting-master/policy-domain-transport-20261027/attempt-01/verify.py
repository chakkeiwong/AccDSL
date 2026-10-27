from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,resource,subprocess,sys,time,traceback
import transport as m
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False)
resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def refuse(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
 else:ck('refusal:'+n,False)
try:
 P=H.parent/'prospective-partial-policy-20261027/attempt-01'
 for n,h in json.loads((P/'source-lock.json').read_text()).items():ck('accepted:'+n,sha(R/n),h);pins[n]=h
 for q in P.glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'transport.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-policy-domain-transport-20261027.md']:pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for n in ['transport.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');ctx=m.p.Context();saved=json.loads((P/'cases.json').read_text())
 plans=[]
 for name in ['baseline','unknown_access','correction_access_straddles','new_low_correction_label','retraction','conflicting_heads','inconsistent_clocks','execution_cap2']:
  rows=[r for r in saved if r['case']==name];selected=[rows[i] for i in sorted({0,len(rows)//2,len(rows)-1})]
  for item in selected:
   old=item['declaration'];new=cp(old)
   for row in new['maps']:
    for stage in ['first','second']:
     for token in row[stage]:token['token']=stage+': renamed '+token['token']
   plans.append(dict(case=name,resolved=item['frontier']['resolved'],old=old,new=new,item=item))
 save('declarations-before-comparison.json',[{k:v for k,v in r.items() if k!='item'} for r in plans])
 for row in plans:
  item=row['item'];front=item['frontier'];old=row['old'];new=row['new'];eid=front['input_sha256'];fid=m.identity(front);od=item['domain'];limit=item['limit']
  # Revalidate the saved result against the current unchanged method identities.
  oldresult=item['result'];m.p.verify(oldresult,m.identity(oldresult),front,fid,eid,old,m.identity(old),od,m.identity(od),ctx,limit)
  before=m.identity([front,old,new,oldresult]);result=m.evaluate(front,fid,eid,old,m.identity(old),new,m.identity(new),oldresult,m.identity(oldresult),ctx,limit)
  label=row['case']+':'+str(row['resolved']);ck(label+':pure',m.identity([front,old,new,oldresult]),before)
  ck(label+':new_identity',result['new_result_sha256']!=m.identity(oldresult));ck(label+':not_extension',result['extension_claim'],False)
  ck(label+':exact_population',result['transported_candidates'],result['new_result']['candidates'])
  cases.append(dict(case=row['case'],resolved=row['resolved'],result=result))
 ck('nonempty_unary_and_binary',any(r['result']['unary_constraints'] and r['result']['binary_constraints'] for r in cases))
 base=next(r for r in plans if r['case']=='baseline' and r['resolved']>0);item=base['item'];front=item['frontier'];old=base['old'];new=base['new'];eid=front['input_sha256'];fid=m.identity(front)
 def changed(n,mut):
  bad=cp(new);mut(bad);refuse(n,lambda:m.relation(front['input'],eid,old,m.identity(old),bad,m.identity(bad),ctx.evidence))
 changed('actor',lambda x:x.update(actor='Bob'));changed('time',lambda x:x.update(second_at='2026-01-04T00:00:00Z'))
 changed('action',lambda x:x['actions'].update(first=['draw','pay']));changed('source',lambda x:x['maps'][0].update(source_sha256='0'*64))
 changed('bound',lambda x:x.update(max_policy_keys=11));changed('input',lambda x:x.update(input_sha256='0'*64))
 changed('tag',lambda x:x['maps'][0].update(tag={'reveal':'first'}))
 changed('merge',lambda x:[t.update(token='one') for row in x['maps'] for t in row['first']])
 # A split is tested on the original shared-token two-head declaration.
 split=next(r for r in saved if r['case']=='two_source_supports_one_policy');so=split['declaration'];sn=cp(so);sn['maps'][0]['first'][0]['token']='split'
 refuse('split_shared_message',lambda:m.relation(split['frontier']['input'],split['frontier']['input_sha256'],so,m.identity(so),sn,m.identity(sn),ctx.evidence))
 big=next(r for r in saved if r['case']=='new_correction_label');bo=big['declaration']
 refuse('over_budget_relation',lambda:m.relation(big['frontier']['input'],big['frontier']['input_sha256'],bo,m.identity(bo),bo,m.identity(bo),ctx.evidence))
 bad=cp(item['result']);bad['candidates'].pop();refuse('altered_old_population',lambda:m.evaluate(front,fid,eid,old,m.identity(old),new,m.identity(new),bad,m.identity(bad),ctx,item['limit']))
 bad=cp(front);bad['pending'].clear();refuse('altered_frontier',lambda:m.evaluate(bad,m.identity(bad),eid,old,m.identity(old),new,m.identity(new),item['result'],m.identity(item['result']),ctx,item['limit']))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='exact global bijective message renaming;no domain extension or observation refinement')
except Exception:summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,x)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact finite sets',data_version='source-lock.json',plan='docs/plans/accounting-policy-domain-transport-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')

