"""Bind complete finite requests and preserve the post-run missing-row witness."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json,importlib.util,sys,subprocess,time,platform
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bound_request',H/'bound_request.py');B=importlib.util.module_from_spec(s);s.loader.exec_module(B)
s=importlib.util.spec_from_file_location('native_debug',B.NATIVE);P=importlib.util.module_from_spec(s);s.loader.exec_module(P)
start=time.monotonic();out=H/'admission-attempt-01';out.mkdir(exist_ok=False);checks=[];records=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=repr(a),expected=repr(b)))
def canonical(policies):return json.dumps(sorted(policies,key=repr),sort_keys=True)
cases=json.loads((H/'attempt-01/cases.json').read_text())
for case in cases:
 request=dict(schema=B.SCHEMA,rows=case['rows'],actions1=['order0','order1'],actions2=['settle'],reveal=case['reveal'])
 expected=B.identity(request);r=B.solve(request,expected)
 c(case['name']+' accepted',r['status'],'complete_conditional');c(case['name']+' full policy preservation',canonical(r['policies']),canonical(case['policies']))
 records.append(dict(name=case['name'],expected_identity=expected,result=r))
base=next(x for x in cases if x['name']=='exact/never/False');request=dict(schema=B.SCHEMA,rows=base['rows'],actions1=['order0','order1'],actions2=['settle'],reveal='never');expected=B.identity(request)
mutations=[]
for i in range(4):
 m=deepcopy(request);m['rows'].pop(i);mutations.append(('missing row'+str(i),m))
m=deepcopy(request);m['rows']=m['rows'][:2];mutations.append(('missing whole future world',m))
m=deepcopy(request);m['rows'][1]['status']='accepted';mutations.append(('changed refusal',m))
m=deepcopy(request);m['rows'][0]['message1']='future0';mutations.append(('future label leak',m))
m=deepcopy(request);m['reveal']='first';mutations.append(('unadmitted revelation',m))
m=deepcopy(request);m['actions1']=['order0'];mutations.append(('changed action domain',m))
m=deepcopy(request);m['rows'].append(deepcopy(m['rows'][0]));mutations.append(('duplicate row',m))
m=deepcopy(request);m['rows'][0]['support']='another-world';mutations.append(('changed world support',m))
m=deepcopy(request);m['rows'][0]['message2']=['changed'];mutations.append(('changed later message',m))
for name,m in mutations:
 r=B.solve(m,expected);c(name+' rejected',r['status'],'refused');c(name+' before native',r['native_executed'],False);records.append(dict(name=name,result=r))
# Preserve original missing-refusal witness; the complete table has no policy.
broken=deepcopy(request);broken['rows'].pop(1)
full=P.solve(request['rows'],request['actions1'],request['actions2'],'never');wrong=P.solve(broken['rows'],broken['actions1'],broken['actions2'],'never')
c('complete native exact set',full,set());c('bare native lost-refusal false feasibility',len(wrong),1)
c('binding rejects lost refusal',B.solve(broken,expected)['reason'],'request_identity')
# Explicit external admission changes the question; a payload cannot authorize itself.
changed=deepcopy(request);changed['reveal']='first';new=B.solve(changed,B.identity(changed));c('explicit newly admitted information',len(new['policies']),1)
selfsigned=deepcopy(broken);selfsigned['expected_request_sha256']=B.identity(broken);c('self-signed field rejected',B.solve(selfsigned,expected)['reason'],'request_shape')
for bad in [None,'',expected[:-1]+'x']:
 c('wrong expected identity '+repr(bad),B.solve(request,bad)['reason'],'request_identity')
# Even a trusted identity does not erase native structural guards.
invalid=deepcopy(request);invalid['rows'][0]['future_demand']=0;c('native guard remains',B.solve(invalid,B.identity(invalid))['reason'],'native_validation:row_fields')
failed=[x['name'] for x in checks if not x['passed']]
summary=dict(status='pass' if not failed else 'fail',checks=len(checks),complete_cases=len(cases),mutations=len(mutations),failed=failed,native_complete_table_unchanged=True,external_identity_assumption=True)
paths=[B.NATIVE,H/'bound_request.py',Path(__file__),H/'attempt-01/cases.json',ROOT/'docs/plans/company-state-future-demand-admission-repair-20261028.md']
manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact standard library',seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version='attempt01 complete synthetic tables',plan_file=str(paths[-1].relative_to(ROOT)),result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})
for n,d in [('checks',checks),('results',records),('verification',summary),('missing-refusal-witness',dict(full_request=request,altered_request=broken,full_policies=sorted(full,key=repr),false_policies=sorted(wrong,key=repr),bound_result=B.solve(broken,expected))),('run-manifest',manifest)]: (out/(n+'.json')).write_text(json.dumps(d,indent=2)+chr(10))
print(json.dumps(summary));raise SystemExit(bool(failed))

