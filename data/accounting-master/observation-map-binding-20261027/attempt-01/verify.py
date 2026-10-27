"""One-shot finite observation binding and complete cold/reused comparison."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,resource,subprocess,sys,time,traceback
import binding as m
H=Path(__file__).resolve().parent;R=H.parents[2]
fx=m.load('observation_binding_full_fixtures',H/'fixtures.py');expect=m.load('observation_binding_independent_rows',H/'expected.py')
OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];saved=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:200]+' != '+repr(b)[:200])
def reject(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck(n,True)
 else:ck(n,False)
files=[H/n for n in ['binding.py','fixtures.py','expected.py','verify.py','contract.md']]+[R/'docs/plans/accounting-observation-map-binding-20261027.md',fx.SAVED]
files+=sorted({Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and str(Path(x.__file__).resolve()).startswith(str(R)) and Path(x.__file__).suffix=='.py'})
lock={str(p.relative_to(R)):sha(p) for p in files};dump('source-lock.json',lock)
for n in ['binding.py','fixtures.py','expected.py','verify.py','contract.md']:(OUT/n).write_bytes((H/n).read_bytes())
try:
 e=m.Evidence();suite=fx.suite(e);base=suite[0];b,d=base['family'],base['declaration'];baseline=m.evaluate(b,m.identity(b),d,m.identity(d),e);prior=m.identity(baseline);results={}
 for c in suite:
  name=c['name'];b,d=c['family'],c['declaration'];before=cp([b,d]);cold=m.evaluate(b,m.identity(b),d,m.identity(d),e);got=m.evaluate(b,m.identity(b),d,m.identity(d),e,baseline,prior)
  ck(name+':status',got['status'],c['expected_status']);ck(name+':count',got['count'],c['expected_count']);ck(name+':expected_reuse',got['reused'],c['expected_reuse'])
  ck(name+':full_cold_semantics',{k:v for k,v in cold.items() if k not in ('reused','binding_changed')},{k:v for k,v in got.items() if k not in ('reused','binding_changed')});ck(name+':immutable_inputs',[b,d],before)
  ck(name+':all_source_outcomes',got['binding']['source_outcomes'],b['outcomes']);ck(name+':all_temporal_supports',got['binding']['temporal_supports'],b['supports']);ck(name+':no_admission',all(got[k] is False for k in m.FLAGS))
  if got['status']=='complete_conditional':
   independent_rows=expect.rows(b,d,e);ck(name+':independent_row_mapping',got['rows'],independent_rows)
   independent,diag=m.oracle.solve(independent_rows,('pay','draw'),('pay','draw'),'never');ck(name+':full_independent_policies',got['policies'],m.canonical(sorted(independent,key=repr)))
   ck(name+':kernel_hidden_identity',all(r['mechanism']=='hidden' for r in got['kernel']['rows']))
   ck(name+':saved_transport',json.loads(json.dumps(got)),got)
  else:ck(name+':no_favorable_subset',got['policies'] is None and got['count'] is None and got['rows']==[])
  results[name]=got;saved.append({'case':name,'expected_status':c['expected_status'],'expected_count':c['expected_count'],'expected_reuse':c['expected_reuse'],'result':got})
 ck('same_count_changed_labels_recomputes',results['changed_message_labels']['count']==baseline['count'] and results['changed_message_labels']['kernel_sha256']!=baseline['kernel_sha256'] and results['changed_message_labels']['policies']!=baseline['policies'])
 ck('source_correction_rebinds',results['same_meaning_correction']['reused'] and results['same_meaning_correction']['binding_changed'])
 ck('distinct_zero_policy_kernels',results['swapped_hidden']['count']==results['changed_financial_receipt']['count']==0 and results['swapped_hidden']['kernel_sha256']!=results['changed_financial_receipt']['kernel_sha256'])
 ck('colliding_tag_does_not_identify',results['swapped_first_tag']['count']==16 and results['swapped_colliding_first_tag']['count']==0)
 b=base['family'];original=base['declaration']
 def bad_decl(n,edit,rehash=True):
  d=cp(original);edit(d);reject(n,lambda:m.evaluate(b,m.identity(b),d,m.identity(d) if rehash else m.identity(original),e))
 bad_decl('external_decl_identity',lambda d:d.__setitem__('actor','Bob'),False)
 bad_decl('actor_mismatch',lambda d:d.__setitem__('actor','Bob'))
 bad_decl('family_mismatch',lambda d:d.__setitem__('family_sha256','0'*64))
 bad_decl('future_first_cutoff',lambda d:d.__setitem__('first_at','2026-01-02T00:00:00.0000001Z'))
 bad_decl('second_not_after_first',lambda d:d.__setitem__('second_at',d['first_at']))
 bad_decl('unknown_offset',lambda d:d.__setitem__('first_at','2026-01-02T00:00:00-00:00'))
 bad_decl('wrong_actions',lambda d:d['actions']['first'].append('borrow'))
 bad_decl('missing_map',lambda d:d['maps'].pop())
 bad_decl('duplicate_map',lambda d:d['maps'].append(cp(d['maps'][0])))
 bad_decl('wrong_source_head',lambda d:d['maps'][0].__setitem__('source_head','0'*64))
 bad_decl('wrong_source_bytes',lambda d:d['maps'][0].__setitem__('source_sha256','0'*64))
 bad_decl('missing_first_key',lambda d:d['maps'][0]['first'].pop())
 bad_decl('duplicate_first_key',lambda d:d['maps'][0]['first'].append(cp(d['maps'][0]['first'][0])))
 bad_decl('hidden_right_in_first_key',lambda d:d['maps'][0]['first'][0]['key'].append(True))
 bad_decl('future_signal_in_first_key',lambda d:d['maps'][0]['first'][0]['key'].extend([False,True]))
 bad_decl('row_specific_first_key',lambda d:d['maps'][0]['first'][0].__setitem__('key',['floating|secret']))
 bad_decl('missing_second_key',lambda d:d['maps'][0]['second'].pop())
 bad_decl('internal_id_extra_field',lambda d:d['maps'][0].__setitem__('expose_source_hash',True))
 bad_decl('hidden_tag_has_token',lambda d:d['maps'][0]['tag'].__setitem__('token','secret'))
 visible=next(x for x in suite if x['name']=='same_maps_first_tag')
 def bad_tag(n,edit,rekey=True):
  b,d=cp(visible['family']),cp(visible['declaration']);digest=d['maps'][0]['tag']['observation_sha256'];o=d['tag_observations'].pop(digest);edit(o);key=m.identity(o) if rekey else digest;d['tag_observations'][key]=o;d['maps'][0]['tag']['observation_sha256']=key;d['trusted_tag_observations']=sorted(key if k==digest else k for k in d['trusted_tag_observations']);reject(n,lambda:m.evaluate(b,m.identity(b),d,m.identity(d),e))
 bad_tag('tag_wrong_actor',lambda o:o.__setitem__('actor','Bob'))
 bad_tag('tag_wrong_source',lambda o:o.__setitem__('source_head','0'*64))
 bad_tag('tag_mutated_bytes',lambda o:o.__setitem__('token','altered'),False)
 bad_tag('tag_claimed_actual_evidence',lambda o:o.__setitem__('provenance','actual_knowledge'))
 bad_tag('unsupported_tag_interval',lambda o:o.__setitem__('at',{'kind':'interval','start':'2026-01-01T00:00:00Z','end':'2026-01-02T00:00:00Z'}))
 corrupted=cp(baseline);corrupted['policies'].pop();reject('forged_prior_external',lambda:m.evaluate(base['family'],m.identity(base['family']),original,m.identity(original),e,corrupted,prior));reject('forged_prior_structural',lambda:m.evaluate(base['family'],m.identity(base['family']),original,m.identity(original),e,corrupted,m.identity(corrupted)))
 corrupted=cp(baseline);corrupted['rows'].pop();reject('missing_prior_support',lambda:m.verify_previous(corrupted,m.identity(corrupted),e))
 corrupted=cp(baseline);corrupted['kernel']['rows'].pop();corrupted['kernel_sha256']=m.identity(corrupted['kernel']);reject('missing_prior_numeric_world',lambda:m.verify_previous(corrupted,m.identity(corrupted),e))
 reject('missing_prior_expected_hash',lambda:m.verify_previous(baseline,None,e))
 corrupted=cp(base['family']);corrupted['supports'].pop();reject('missing_original_family_support',lambda:m.evaluate(corrupted,m.identity(base['family']),original,m.identity(original),e))
 for n,h in lock.items():ck('source_preserved:'+n,sha(R/n),h)
 for n,h in e.dependencies.items():ck('accepted_dependency:'+n,sha(R/n),h)
 summary={'status':'PASS','cases':len(saved),'assertions':len(checks),'controls':len(controls),'reused_cases':sum(z['result']['reused'] for z in saved),'protected_direct_files':len(lock),'protected_dependency_files':len(e.dependencies),'source_support_rows':sum(len(z['result']['rows']) for z in saved),'scope':'Finite conditional actor observation maps and exact kernel reuse; no actual knowledge or source authentication.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',saved)]:dump(n,x)
 dump('run-manifest.json',{'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'Python '+platform.python_version()+'; CPU; GPU intentionally hidden; existing dependencies only','data':'protected temporal families, certified financial rows and explicit synthetic observation/tag declarations','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-observation-map-binding-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT),'local_date':'2026-10-27'})
 print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':sys.exit(1)
