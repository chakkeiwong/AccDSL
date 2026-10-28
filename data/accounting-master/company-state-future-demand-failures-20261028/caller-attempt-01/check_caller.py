"""Targeted existing bound-caller audit; leave protected code unchanged."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import importlib.util,json,sys,subprocess,time,platform
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;N=ROOT/'data/accounting-master/observation-map-binding-20261027'
sys.path.insert(0,str(N));import binding as M
start=time.monotonic();out=H/'caller-attempt-01';out.mkdir(exist_ok=False);checks=[];refusals=[]
def c(n,a,b=True):
 checks.append(dict(name=n,passed=a==b,actual=repr(a)[:300],expected=repr(b)[:300]))
 if a!=b:raise AssertionError(n)
def reject(n,fn):
 try:fn()
 except (ValueError,AssertionError,KeyError,TypeError) as x:refusals.append(dict(name=n,reason=str(x)));c(n,True)
 else:c(n,False)
E=M.Evidence();saved=json.loads((N/'attempt-01/cases.json').read_text());base=next(x for x in saved if x['case']=='baseline')['result'];b=base['family'];d=base['declaration'];before=deepcopy([b,d])
actual=M.evaluate(b,M.identity(b),d,M.identity(d),E)
c('complete baseline result',actual,base);c('unchanged inputs',[b,d],before)
expected=M.load('future_expected_rows',N/'expected.py');rr=expected.rows(b,d,E);c('independent full mapped rows',actual['rows'],rr)
policies,_=M.oracle.solve(rr,('pay','draw'),('pay','draw'),'never');c('full independent policies',actual['policies'],M.canonical(sorted(policies,key=repr)))
for field in ['rows','kernel_rows','policies']:
 broken=deepcopy(base)
 if field=='kernel_rows':broken['kernel']['rows'].pop();broken['kernel_sha256']=M.identity(broken['kernel'])
 else:broken[field].pop()
 reject(field+' original external identity',lambda x=broken:M.verify_previous(x,M.identity(base),E))
 reject(field+' self-rehashed structural rejection',lambda x=broken:M.verify_previous(x,M.identity(x),E))
broken=deepcopy(b);broken['supports'].pop();reject('missing family support',lambda:M.evaluate(broken,M.identity(b),d,M.identity(d),E))
for kind in ['map','first_key','second_key']:
 broken=deepcopy(d)
 if kind=='map':broken['maps'].pop()
 else:broken['maps'][0]['first' if kind=='first_key' else 'second'].pop()
 reject('missing declaration '+kind,lambda x=broken:M.evaluate(b,M.identity(b),x,M.identity(x),E))
for name in ['unknown_source_access','budget_family','inconsistent_clocks']:
 item=next(x['result'] for x in saved if x['case']==name);got=M.evaluate(item['family'],M.identity(item['family']),item['declaration'],M.identity(item['declaration']),E)
 c(name+' status',got['status'],item['status']);c(name+' no policies',got['policies'],None);c(name+' no selected rows',got['rows'],[])
for n,h in E.dependencies.items():c('protected '+n,sha256((ROOT/n).read_bytes()).hexdigest(),h)
paths=[N/'binding.py',N/'expected.py',N/'attempt-01/cases.json',H/'check_caller.py',ROOT/'docs/plans/company-state-policy-caller-audit-20261028.md',ROOT/'data/accounting-master/company-state-common-request-20261028/dispatcher.py']
manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only standard library',seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version='retained bound caller baseline and unresolved cases',plan_file=str(paths[-2].relative_to(ROOT)),result_file=str((H/'caller-result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})
summary=dict(status='pass',checks=len(checks),refusals=len(refusals),full_baseline_rows=len(actual['rows']),full_baseline_policies=len(actual['policies']),protected_dependencies=len(E.dependencies),scope='Existing bound caller already reconstructs complete protected rows; no integration/code change needed')
for n,x in [('checks',checks),('refusals',refusals),('verification',summary),('run-manifest',manifest)]: (out/(n+'.json')).write_text(json.dumps(x,indent=2)+chr(10))
print(json.dumps(summary))

