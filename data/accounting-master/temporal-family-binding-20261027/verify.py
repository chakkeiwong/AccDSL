"""One-shot complete-family comparison and adversarial transport verification."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,resource,subprocess,sys,time,traceback
import family as m
H=Path(__file__).resolve().parent;R=H.parents[2]
c=m.t.prior.load('family_binding_complete_cases',H/'cases.py')
OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];saved=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:240]+' != '+repr(b)[:240])
def labels(bundle):return {o['outcome']['scenario']['view'] if o['outcome']['status']=='selected_conditional' else 'missing' for o in bundle['outcomes']}
def reject(name,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(name);ck(name,True)
 else:ck(name,False)
files=[H/n for n in ['family.py','cases.py','verify.py','contract.md']]+[R/'docs/plans/accounting-temporal-family-binding-20261027.md',m.T/'attempt-01/source-lock.json',m.T/'attempt-01/verification.json',m.T/'result.md']
files+=sorted({Path(v.__file__).resolve() for v in list(sys.modules.values()) if getattr(v,'__file__',None) and str(Path(v.__file__).resolve()).startswith(str(R)) and Path(v.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in files};dump('source-lock.json',lock)
for n in ['family.py','cases.py','verify.py','contract.md']:(OUT/n).write_bytes((H/n).read_bytes())
try:
 e=m.Evidence();basef=c.f.convert(c.f.oldcases.base());x=m.wire(basef);baseline=m.evaluate(x,m.identity(x),e);trusted=m.identity(baseline);results={}
 for name,f,budget,wanted,reuse_count in c.suite():
  x=m.wire(f,budget);input_hash=m.identity(x);cold=m.evaluate(x,input_hash,e);got=m.evaluate(x,input_hash,e,baseline,trusted)
  ck(name+':complete_semantics',m.semantic(cold),m.semantic(got));ck(name+':expected_views',labels(got),wanted);ck(name+':reused_numerical_count',len(got['reused_keys']),reuse_count)
  ck(name+':json_transport',m.verify(json.loads(json.dumps(got)),m.identity(got),input_hash,e));ck(name+':input_immutable',m.identity(x),input_hash)
  ck(name+':no_admission',all(got[k] is False for k in m.t.FLAGS))
  # Independent path/leaf population walk; no implementation support collector used.
  leaves=[]
  def visit(node,path):
   if 'eligible' in node:leaves.append((path,m.identity(node['outcome'])))
   for i,child in enumerate(node.get('children',[])):visit(child,path+[i])
  if got['temporal_complete']:
   visit(got['temporal']['tree'],[]);ck(name+':full_leaf_paths',[(r['path'],r['outcome_sha256']) for r in got['supports']],leaves)
   ck(name+':full_support_union',sorted((path,o['outcome_sha256']) for o in got['outcomes'] for path in o['supports']),sorted(leaves))
  else:ck(name+':remainder_scope',got['remainder'],{'kind':'entire_original_clock_domain','prepared_sha256':m.identity(got['prepared']),'resumable_frontier':False})
  results[name]=got;saved.append({'case':name,'expected_views':sorted(wanted),'expected_reused':reuse_count,'cold':cold,'reused':got})
 dual=results['correction_access_straddles'];ck('two_different_policy_sets',sorted(p['count'] for p in dual['numerical'].values()),[0,4])
 shared=results['two_source_supports_one_policy'];ck('same_scenario_two_source_outcomes',len(shared['outcomes']),2);ck('same_scenario_single_numeric',len(shared['numerical']),1);ck('same_scenario_source_heads_distinct',len({m.identity(o['outcome']['heads']) for o in shared['outcomes']}),2)
 same=results['same_meaning_new_source'];ck('same_meaning_numerical_reuse',same['numerical'],baseline['numerical']);ck('same_meaning_input_rebind',same['input_sha256']!=baseline['input_sha256']);ck('same_meaning_support_rebind',same['outcomes']!=baseline['outcomes'])
 # The caller can reuse both complete numerical problems from a prior multi-view family.
 x=cp(dual['input']);samefamily=m.evaluate(x,m.identity(x),e,dual,m.identity(dual));ck('multi_view_reuses_both',len(samefamily['reused_keys']),2);ck('multi_view_cold_equality',m.semantic(samefamily),m.semantic(dual))
 limited=results['budget_whole_domain'];resumed=m.evaluate(baseline['input'],baseline['input_sha256'],e,limited,m.identity(limited));ck('budget_never_supplies_policy_cache',resumed['reused_keys'],[]);ck('budget_followed_by_complete',m.semantic(resumed),m.semantic(baseline))
 # Outer expected identity must be held outside the transported family.
 altered=cp(dual);altered['outcomes'].pop();reject('external_lock_detects_dropped_view',lambda:m.verify(altered,m.identity(dual),dual['input_sha256'],e))
 # Recomputing the inner/outer digest cannot repair structurally incomplete evidence.
 def structural(name,b,edit):
  bad=cp(b);edit(bad);reject(name,lambda:m.verify(bad,m.identity(bad),b['input_sha256'],e))
 structural('deleted_proof_branch',dual,lambda b:b['temporal']['tree']['children'].pop())
 structural('duplicated_proof_branch',dual,lambda b:b['temporal']['tree']['children'].append(cp(b['temporal']['tree']['children'][0])))
 structural('deleted_leaf_support',dual,lambda b:b['supports'].pop())
 structural('duplicated_leaf_support',dual,lambda b:b['supports'].append(cp(b['supports'][0])))
 structural('deleted_selected_outcome',dual,lambda b:b['outcomes'].pop())
 structural('missing_outcome_support',dual,lambda b:b['outcomes'][0]['supports'].pop())
 unresolved=results['unknown_access'];idx=next(i for i,o in enumerate(unresolved['outcomes']) if o['outcome']['status']=='unresolved')
 structural('deleted_unresolved_outcome',unresolved,lambda b:b['outcomes'].pop(idx))
 structural('relabelled_unresolved_outcome',unresolved,lambda b:b['outcomes'][idx]['outcome'].__setitem__('status','selected_conditional'))
 structural('unknown_clock_erased',unresolved,lambda b:b['temporal'].__setitem__('unknown_clocks',[]))
 structural('budget_promoted',limited,lambda b:b.__setitem__('temporal_complete',True))
 structural('budget_remainder_dropped',limited,lambda b:b.__setitem__('remainder',None))
 structural('budget_invents_policy',limited,lambda b:b.__setitem__('numerical',cp(baseline['numerical'])))
 structural('changed_prepared_domain',dual,lambda b:b['prepared']['constraints'].pop())
 structural('changed_method_identity',dual,lambda b:b.__setitem__('method_identity','0'*64))
 structural('admission_flag_promoted',dual,lambda b:b.__setitem__('accounting_admission',True))
 structural('deleted_world_row',baseline,lambda b:next(iter(b['numerical'].values()))['row_ids'].pop())
 structural('duplicated_world_row',baseline,lambda b:next(iter(b['numerical'].values()))['row_ids'].append(next(iter(b['numerical'].values()))['row_ids'][0]))
 structural('dropped_policy',baseline,lambda b:next(iter(b['numerical'].values()))['policy_set'].pop())
 structural('changed_observation_domain',baseline,lambda b:next(iter(b['numerical'].values()))['scenario'].__setitem__('view','coarse'))
 for name,edit in [('actor',lambda x:x['request'].__setitem__('actor','Bob')),('trust',lambda x:x.__setitem__('trusted',[])),('budget',lambda x:x.__setitem__('max_nodes',1)),('source',lambda x:x['sources'].__setitem__(next(iter(x['sources'])),'altered'))]:
  x=cp(baseline['input']);edit(x);reject('external_input_'+name,lambda x=x:m.evaluate(x,baseline['input_sha256'],e))
 forged=cp(baseline);next(iter(forged['numerical'].values()))['policy_set'].pop()
 reject('forged_prior_family',lambda:m.evaluate(baseline['input'],baseline['input_sha256'],e,forged,trusted))
 reject('missing_external_prior_lock',lambda:m.evaluate(baseline['input'],baseline['input_sha256'],e,baseline,None))
 for n,h in lock.items():ck('preserved:'+n,sha(R/n),h)
 for n,h in e.method_files.items():ck('accepted_dependency:'+n,sha(R/n),h)
 summary={'status':'PASS','cases':len(saved),'assertions':len(checks),'controls':len(controls),'protected_direct_files':len(lock),'protected_dependency_files':len(e.method_files),'temporal_proof_supports':sum(len(s['reused']['supports']) for s in saved),'numerical_reuse_instances':sum(len(s['reused']['reused_keys']) for s in saved),'scope':'Complete conditional temporal-family binding and selected numerical reuse; no common cross-view policy, authentication or resumable budget frontier.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',saved)]:dump(n,v)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'existing Python '+platform.python_version()+'; standard library/existing jsonschema; CPU; GPU intentionally hidden','data':'protected exact temporal fixtures, policy rows/comparisons and caller input/trust identities','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-temporal-family-binding-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
