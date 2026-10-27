"""Bounded one-shot evidence writer. Never import predecessor verification writers."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,os,platform,resource,subprocess,sys,time,traceback
import views as v
import cases
H=Path(__file__).resolve().parent;R=H.parents[2];P=H.parent/'certified-observation-policy-20261026/attempt-01';OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];results=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(name,x,y=True):
 checks.append({'name':name,'pass':x==y})
 if x!=y:raise AssertionError(name+': '+repr(x)[:200]+' != '+repr(y)[:200])
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
paths=[H/'views.py',H/'cases.py',H/'verify.py',H/'interface-audit.md',R/'docs/plans/accounting-certified-source-views-20261026.md',P/'rows.json',P/'policy-comparisons.json',P/'verification.json',P/'source-lock.json',R/'data/accounting-master/policy-control-integration-20261026/source-preservation.json']
# Record actual locally imported source modules as well as explicit saved inputs.
paths+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(R)) and Path(m.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in paths};dump('source-lock.json',lock)
for n in ['views.py','cases.py','verify.py','interface-audit.md']:(OUT/n).write_bytes((H/n).read_bytes())
rows=json.loads((P/'rows.json').read_text());comparisons=json.loads((P/'policy-comparisons.json').read_text());ids={'rows':sha(P/'rows.json'),'comparisons':sha(P/'policy-comparisons.json'),'observations':sha(P.parent/'observations.py'),'policy':sha(P.parent/'policies.py'),'constraint':sha(P.parent/'constraint_oracle.py')}
def run(f,previous=None):return v.assess(**{k:f[k] for k in ['request','registry','sources','observations','trusted']},rows=rows,comparisons=comparisons,evidence_identity=ids,previous=previous)
try:
 ck('certified_predecessor',json.loads((P/'verification.json').read_text())['status'],'PASS')
 priorlock=json.loads((R/'data/accounting-master/policy-control-integration-20261026/source-preservation.json').read_text())['evidence']
 for name in ['rows.json','policy-comparisons.json','verification.json','source-lock.json']:ck('integration_binding:'+name,sha(P/name),priorlock[str((P/name).relative_to(R))])
 for n,h in json.loads((P/'source-lock.json').read_text()).items():ck('predecessor_source:'+n,sha(R/n),h)
 base=cases.base();before=cp(base);good=run(base);ck('baseline_status',good['status'],'complete_conditional');ck('baseline_four',good['count'],4);ck('pure_baseline',base,before)
 selected=cases.suite()[:5] if len(sys.argv)>2 and sys.argv[2]=='diagnostic' else cases.suite()
 for case in selected:
  f=case['fixture'];before=cp(f);out=run(f,good);e=case['expected'];ck(case['name']+':status',out['status'],e['status']);ck(case['name']+':pure',f,before)
  ck(case['name']+':no_admission',all(out[k] is False for k in v.FLAGS))
  if e['status']=='complete_conditional':
   ck(case['name']+':heads',out['binding']['heads'],e['heads']);ck(case['name']+':scenario',out['scenario'],e['scenario']);ck(case['name']+':reuse',out['reuse'],e['reuse'])
   expected=next(x for x in comparisons if all(x[k]==e['scenario'][k] for k in ['receipt','family','view']));ck(case['name']+':whole_policy',out['policy_set'],expected['feasible_policies']);ck(case['name']+':whole_population',len(out['row_ids']),expected['world_rows'])
  results.append({'case':case['name'],'expected':e,'result':out})
 # All eight scenario mappings independently bind exactly their saved world family.
 for old in comparisons:
  f=cases.base();hf=cases.add(f,'financial_family',{k:old[k] for k in ['receipt','family']},'Synthetic scenario variation.',supersedes=f['names']['financial_family']);ho=cases.add(f,'observation_scheme',{'view':old['view']},'Synthetic observation variation.',supersedes=f['names']['observation_scheme']);out=run(f)
  ck('eight_scenario_status',out['status'],'complete_conditional');ck('eight_complete_sets',out['policy_set'],old['feasible_policies']);ck('eight_rows',len(out['row_ids']),old['world_rows'])
 # Each corruption addresses a distinct dependency/temporal failure.
 def reject(name,modify,want='invalid'):
  f=cases.base();modify(f);out=run(f,good);ck('control:'+name,out['status'],want);controls.append({'name':name,'result':out})
 reject('altered_source_bytes',lambda f:f['sources'].__setitem__(next(iter(f['sources'])),'changed bytes'))
 reject('altered_record_under_old_hash',lambda f:f['registry'][f['names']['financial_family']]['payload'].__setitem__('receipt',6))
 reject('missing_observation_bytes',lambda f:f['observations'].pop(next(iter(f['observations']))))
 reject('self_trust_absent',lambda f:f.update(trusted=frozenset()),'unresolved')
 reject('missing_ancestry',lambda f:cases.add(f,'observation_scheme',{'view':'coarse'},supersedes='0'*64))
 reject('cross_slot_ancestry',lambda f:cases.add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['financial_family']))
 reject('unsupported_receipt',lambda f:cases.add(f,'financial_family',{'receipt':8,'family':'committed'},supersedes=f['names']['financial_family']))
 reject('leaked_hidden_right_observation',lambda f:cases.add(f,'observation_scheme',{'view':'refined','right':True},supersedes=f['names']['observation_scheme']))
 reject('unknown_actor_not_publication',lambda f:f['request'].__setitem__('actor','Unknown'),'unresolved')
 reject('subsecond_not_silently_rounded',lambda f:f['request'].__setitem__('decision_at','2026-01-02T00:00:00.0000001Z'))
 reject('date_only_not_midnight',lambda f:f['request'].__setitem__('decision_at','2026-01-02'))
 reject('invalid_calendar',lambda f:f['request'].__setitem__('decision_at','2026-02-30T00:00:00Z'))
 reject('replacement_clock_reversal',lambda f:cases.add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],when='2025-12-31T00:00:00Z'))
 reject('ingestion_after_acceptance',lambda f:cases.add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],event_times={'ingested':'2026-01-02T00:00:00Z'}))
 reject('access_before_authorship',lambda f:cases.add(f,'observation_scheme',{'view':'coarse'},supersedes=f['names']['observation_scheme'],access={'Alice':'2025-12-31T00:00:00Z'}))
 # A source revision with unchanged policies still invalidates the view binding.
 same=next(r for r in results if r['case']=='same_answer_new_source') if len(selected)>5 else None
 if same:ck('equal_policies_not_equal_dependencies',same['result']['policy_set']==good['policy_set'] and same['result']['dependency_sha256']!=good['dependency_sha256'])
 for n,h in lock.items():ck('preserved:'+n,sha(R/n),h)
 summary={'status':'PASS','cases':len(selected),'scenario_mappings':8,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'scope':'Conditional two-slot immutable source/actor view over the eight certified synthetic policy problems; no actual source admission or probability.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 dump('verification.json',summary);dump('checks.json',checks);dump('controls.json',controls);dump('cases.json',results)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT)+(' diagnostic' if len(sys.argv)>2 else ''),'environment':'existing Python '+platform.python_version()+', standard library and existing jsonschema; CPU; GPU intentionally hidden','data':'locked certified policy rows, complete policy sets and explicitly synthetic revision/access clocks','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-certified-source-views-20261026.md','result':str(OUT/'verification.json'),'artifacts':str(OUT),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
