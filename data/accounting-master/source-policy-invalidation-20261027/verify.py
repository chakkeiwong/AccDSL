"""One-shot exact dependency and cold/reused-result comparison."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,os,platform,resource,subprocess,sys,time,traceback
import reuse as r
import expected
import cases
H=Path(__file__).resolve().parent;R=H.parents[2];P=H.parent/'certified-observation-policy-20261026/attempt-01';V=H.parent/'certified-source-views-20261026';OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];results=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n+': '+repr(x)[:200]+' != '+repr(y)[:200])
paths={'rows':P/'rows.json','comparisons':P/'policy-comparisons.json','observations':P.parent/'observations.py','policy':P.parent/'policies.py','constraint':P.parent/'constraint_oracle.py'}
files=[H/'reuse.py',H/'expected.py',H/'verify.py',R/'docs/plans/accounting-source-policy-invalidation-20261027.md',V/'attempt-01/source-lock.json',V/'attempt-01/verification.json',V/'result.md']+list(paths.values())
files+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(R)) and Path(m.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in files};dump('source-lock.json',lock)
for n in ['reuse.py','expected.py','verify.py']:(OUT/n).write_bytes((H/n).read_bytes())
try:
 ck('predecessor_pass',json.loads((V/'attempt-01/verification.json').read_text())['status'],'PASS')
 for n,h in json.loads((V/'attempt-01/source-lock.json').read_text()).items():ck('predecessor_preserved:'+n,sha(R/n),h)
 raw={k:p.read_bytes() for k,p in paths.items()};external={k:sha(p) for k,p in paths.items()};e=r.Evidence(raw,external)
 baseline=r.evaluate(cases.base(),e);ck('baseline',baseline['status'],'complete_conditional');ck('baseline_count',baseline['numerical']['count'],4);trusted=r.v.identity(baseline)
 for case in cases.suite():
  f=case['fixture'];cold=r.evaluate(f,e);reuse=r.evaluate(f,e,baseline,trusted);wanted=case['expected'];ck(case['name']+':status',reuse['status'],wanted['status'])
  if cold['status']=='complete_conditional':
   ck(case['name']+':complete_outcome',reuse['numerical'],cold['numerical']);ck(case['name']+':graph',reuse['node_specs'],cold['node_specs']);ck(case['name']+':binding',reuse['binding'],cold['binding']);ck(case['name']+':change_mask',reuse['changed_nodes'],expected.CHANGES[case['name']]);ck(case['name']+':actual_reuse',reuse['cache_reused'],'policy' not in expected.CHANGES[case['name']])
  else:ck(case['name']+':no_cache_on_unresolved',reuse['cache_reused'],False)
  results.append({'case':case['name'],'cold':cold,'reused':reuse})
 # Tampering is rejected against expected identities held outside the transport.
 def reject(name,fn):
  try:fn()
  except (ValueError,KeyError,TypeError,AssertionError):controls.append(name);ck(name,True)
  else:ck(name,False)
 for name,edit in [('deleted_row',lambda x:x.pop()),('duplicate_row',lambda x:x.append(cp(x[0]))),('changed_hidden_right',lambda x:x[0].__setitem__('right',True)),('changed_signal',lambda x:x[0].__setitem__('obs1',['high',True]))]:
  b=dict(raw);rows=json.loads(raw['rows']);edit(rows);b['rows']=json.dumps(rows).encode();reject(name,lambda b=b:r.Evidence(b,external))
 b=dict(raw);x=json.loads(raw['comparisons']);x[-1]['feasible_policies']=[];b['comparisons']=json.dumps(x).encode();reject('altered_saved_policy',lambda:r.Evidence(b,external))
 b=dict(raw);b['policy']=b['policy']+b'\n#changed';reject('altered_policy_source',lambda:r.Evidence(b,external))
 reject('missing_expected_component',lambda:r.Evidence(raw,{k:v for k,v in external.items() if k!='rows'}))
 for name,edit in [('prior_policy',lambda x:x['numerical']['policy_set'].pop()),('prior_world',lambda x:x['numerical']['row_ids'].pop()),('prior_binding',lambda x:x['binding']['request'].__setitem__('actor','Mallory')),('prior_graph',lambda x:x['node_ids'].__setitem__('policy','0'*64))]:
  bad=cp(baseline);edit(bad);bad['policy_payload_sha256']=r.v.identity(bad['numerical']);reject(name,lambda bad=bad:r.evaluate(cases.base(),e,bad,trusted))
 reject('no_external_prior_lock',lambda:r.evaluate(cases.base(),e,baseline,None))
 # A source change with identical numerical policies must not reuse its source node.
 same=next(x for x in results if x['case']=='same_answer_new_source')['reused'];ck('semantic_reuse_source_rebind',same['cache_reused'] and 'observation_source' in same['changed_nodes'] and same['numerical']==baseline['numerical'])
 for n,h in lock.items():ck('preserved:'+n,sha(R/n),h)
 summary={'status':'PASS','cases':len(results),'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'reused_cases':sum(x['reused'].get('cache_reused',False) for x in results),'scope':'Exact selected dependency graph and trusted prior/content locks; no authenticated transport or durable cache.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',results)]:dump(n,x)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'existing Python '+platform.python_version()+'; CPU, GPU intentionally hidden; existing jsonschema','data':'externally locked certified observation rows and complete policy references; synthetic source-view scenarios','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-source-policy-invalidation-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
