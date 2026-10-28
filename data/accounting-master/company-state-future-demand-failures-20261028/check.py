"""Original future-demand discriminator against unchanged native/oracle policy code."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from itertools import product
import importlib.util,json,sys,time,subprocess,platform
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;N=ROOT/'data/accounting-master/cross-mechanism-policy-20261027'
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
P=load('future_native',N/'policy.py');O=load('future_oracle',N/'oracle.py')
A=('order0','order1');B=('settle',)
def rows(target='exact',labels=('future0','future1'),early_message=False,late_message=True):
 out=[]
 for demand,mechanism in enumerate(labels):
  for quantity,action in enumerate(A):
   ok=quantity==demand if target=='exact' else quantity>=demand if target=='allow_overstock' else True
   out.append(dict(id=mechanism+'/'+action,support='demand'+str(demand)+'/'+action,mechanism=mechanism,a1=action,a2='settle',
    message1='cash1:demand'+str(demand) if early_message else 'cash1',message2=['demand'+str(demand)] if late_message else ['terminal'],status='accepted' if ok else 'refused2'))
 return out
# Independent hand construction uses semantic admissible orders, not candidate outcomes.
def hand(target,reveal,labels=('future0','future1'),early_message=False,late_message=True):
 result=set()
 if reveal=='first' or early_message:
  assignments=[(0,1)] if target=='exact' else [(0,1),(1,1)] if target=='allow_overstock' else list(product((0,1),repeat=2))
 else:assignments=[] if target=='exact' else [(1,1)] if target=='allow_overstock' else [(0,0),(1,1)]
 for orders in assignments:
  first={};second={}
  for demand,label in enumerate(labels):
   msg='cash1:demand'+str(demand) if early_message else 'cash1'
   key=('known',label,msg) if reveal=='first' else ('unknown',msg)
   action=A[orders[demand]];first[key]=action
   second[(key,action,label if reveal in ('first','second') else None,('demand'+str(demand),) if late_message else ('terminal',))]='settle'
  result.add((tuple(sorted(first.items(),key=repr)),tuple(sorted(second.items(),key=repr))))
 return result
start=time.monotonic();out=H/'attempt-01';out.mkdir(parents=True,exist_ok=False);checks=[];cases=[];controls=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=repr(a),expected=repr(b)))
for target,reveal,late in product(('exact','allow_overstock','independent'),('never','second','first'),(False,True)):
 rr=rows(target,late_message=late);native=P.solve(rr,A,B,reveal);oracle,meta=O.solve(rr,A,B,reveal);expected=hand(target,reveal,late_message=late);name=target+'/'+reveal+'/'+str(late)
 c(name+' full oracle',native,oracle);c(name+' independent hand',native,expected)
 c(name+' row order',P.solve(list(reversed(rr)),A,B,reveal),expected)
 for pi in native:
  first=dict(pi[0]);actions=[first[P.keys(rr[i],reveal)[0]] for i in [0,2]]
  if reveal!='first':c(name+' same current information',actions[0],actions[1])
 cases.append(dict(name=name,rows=rr,reveal=reveal,policies=sorted(native,key=repr),oracle=meta))
for target in ['exact','allow_overstock','independent']:
 labels=('renamed-low','renamed-high');rr=rows(target,labels=labels);expected=hand(target,'never',labels=labels)
 c(target+' hidden label invariant',P.solve(rr,A,B,'never'),expected)
 rr2=deepcopy(rr)
 for i,r in enumerate(rr2):r['id']='opaque'+str(i);r['support']='audit-only'+str(i)
 c(target+' audit identity invariant',P.solve(rr2,A,B,'never'),expected)
# Intentionally changed information problem exposes the future before ordering.
rr=rows('exact',early_message=True);native=P.solve(rr,A,B,'never');expected=hand('exact','never',early_message=True)
c('clairvoyant control full set',native,expected);c('clairvoyant admits one policy',len(native),1)
c('hidden exact has no robust policy',P.solve(rows(),A,B,'never'),set())
controls.append(dict(name='future demand leaked into first message',rows=rr,policies=sorted(native,key=repr),scope='deliberately different information contract'))
# A fixed viable policy cannot depend on changed future-demand label at the first action.
viable=P.solve(rows('allow_overstock'),A,B,'never')
for pi in viable:
 first=dict(pi[0]);c('paired changed future demand same first order',first[P.keys(rows('allow_overstock')[0],'never')[0]],first[P.keys(rows('allow_overstock')[2],'never')[0]])
# Guard checks on independent deep copies. Missing actions across the common cell must refuse.
for name,rr,expected in [('undeclared future field',rows(),'row_fields'),('missing common action',[r for r in rows() if r['a1']=='order0'],'first_action_coverage'),('duplicate audit id',rows(),'unique_support_rows')]:
 if name=='undeclared future field':rr[0]['future_demand']=0
 if name=='duplicate audit id':rr[1]['id']=rr[0]['id']
 try:P.solve(rr,A,B,'never');error='no_refusal'
 except ValueError as e:error=str(e)
 c(name,error,expected);controls.append(dict(name=name,expected=expected,actual=error))
failed=[x['name'] for x in checks if not x['passed']]
summary=dict(status='pass' if not failed else 'fail',checks=len(checks),cases=len(cases),controls=len(controls),failed=failed,original_targets=['SIM-F012','LIT-F004'],scope='Exact two-world/two-date finite profile; no actual actor admission or engine-wide enforcement')
paths=[N/'policy.py',N/'oracle.py',Path(__file__),ROOT/'docs/plans/company-state-future-demand-failures-20261028.md',ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only standard library; no GPU imports',seeds='N/A exact enumeration',wall_seconds=time.monotonic()-start,data_version='explicit synthetic finite rows in cases.json',plan_file=str(paths[3].relative_to(ROOT)),result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})
for n,d in [('checks',checks),('cases',cases),('controls',controls),('verification',summary),('run-manifest',manifest)]: (out/(n+'.json')).write_text(json.dumps(d,indent=2)+chr(10))
print(json.dumps(summary));raise SystemExit(bool(failed))

