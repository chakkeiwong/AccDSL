"""One-shot selected symbolic certificate; retains every failed attempt."""
from pathlib import Path
from copy import deepcopy as cp
import ast,hashlib,itertools,json,os,platform,resource,subprocess,sys,time,traceback
import certificate as c
import expected_forms as e
HERE=Path(__file__).resolve().parent;ROOT=c.ROOT
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False)
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
start=time.monotonic();checks=[];controls=[];certificates={};instances=[]
def ck(name,x,y=True):
 checks.append({'name':name,'pass':x==y})
 if x!=y:raise AssertionError(name+': '+repr(x)[:500]+' != '+repr(y)[:500])
def reject(name,mutator):
 t=c.template('alpha');mutator(t)
 try:c.check(t,e.forms())
 except (ValueError,KeyError,TypeError) as exc:
  controls.append({'name':name,'refused':True,'class':type(exc).__name__,'reason':str(exc)});ck(name,True)
 else:ck(name,False)
def meth(t,k):return t['body']['registry']['entries'][k]['method']
def pre(t,k,name):return next(r for r in meth(t,k)['preconditions']['manifest']['requirements'] if r['id']==name)
def double(t):
 rows=meth(t,'accrue1')['monetary']['definition']['postings']
 for row in rows:row['expression']={'op':'add','left':cp(row['expression']),'right':cp(row['expression'])}
def remove_guard(t):
 rows=meth(t,'pay1')['preconditions']['manifest']['requirements'];rows[:]=[r for r in rows if r['id']!='cash_to_pay']
def remove_memory(t,field):
 rows=meth(t,'draw1')['memory']['definition']['operations'];rows[:]=[r for r in rows if r['path']!=[field]]
def unsupported(t):
 row=meth(t,'accrue1')['monetary']['definition']['postings'][0]
 row['expression']={'op':'mul','left':cp(row['expression']),'right':cp(row['expression'])}
# Input snapshots, including pure predecessor definitions, never their writers.
sources={Path(__file__).resolve(),HERE/'certificate.py',HERE/'expected_forms.py',HERE/'derivation.md',ROOT/'docs/plans/accounting-symbolic-method-certificate-20261026.md',ROOT/'data/accounting-master/guarded-memory-runtime-20261026/verify.py',ROOT/'data/accounting-master/guarded-memory-runtime-20261026/attempt-01/verification.json'}
for mod in list(sys.modules.values()):
 p=getattr(mod,'__file__',None)
 if p and Path(p).resolve().is_relative_to(ROOT) and Path(p).suffix=='.py':sources.add(Path(p).resolve())
lock={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
for p in sources:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
try:
 # Deliberate failures precede positive promotion; both preserve bookkeeping balance.
 reject('balanced_double_accrual',double)
 reject('strict_becomes_weak',lambda t:pre(t,'draw1','strict_trigger')['predicate'].update(op='le'))
 wanted=e.forms()
 for chart in ('alpha','beta'):
  t=c.template(chart);before=cp(t);got=c.check(t,wanted)
  ck(chart+'/input_preserved',t,before)
  for key in wanted:
   for part in ('pre','post','postings','flows','memory'):ck(chart+'/'+key+'/'+part,got[key][part],wanted[key][part])
  certificates[chart]={'template':t,'actual':got,'expected':wanted}
  print(json.dumps({'chart':chart,'symbolic_methods':len(got)}),flush=True)
 # Safely extract data without importing the old one-shot verifier.
 tree=ast.parse((ROOT/'data/accounting-master/guarded-memory-runtime-20261026/verify.py').read_text())
 cases=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CASES' for x in n.targets))
 for chart in ('alpha','beta'):
  t=c.template(chart)
  for i,case in enumerate(cases):
   actual=c.literalize(t,*case);original,_=c.b.build(*case,chart=chart)
   ck(chart+'/literalization/'+str(i),actual,original)
   instances.append({'chart':chart,'premises':case,'program_sha256':c.rt.digest(actual),'comparison':'exact_builder_equality'})
  for mode,right,a1,a2 in itertools.product(('fixed','floating'),(False,True),('pay','draw'),('pay','draw')):
   body=c.literalize(t,mode,right,'1/50','2/25','6',a1,a2)
   c.rt.validate(body);ck(chart+'/typed/'+repr((mode,right,a1,a2)),True)
  print(json.dumps({'chart':chart,'literalizations':len(cases),'typed_variants':16,'elapsed':time.monotonic()-start}),flush=True)
 reject('missing_cash_guard',remove_guard)
 reject('wrong_binding',lambda t:meth(t,'pay1')['monetary']['bindings']['coupon'].update(pointer='/due2'))
 reject('wrong_units',lambda t:meth(t,'draw1')['monetary']['definition']['inputs']['coupon']['type'].update(scale='100/1'))
 reject('noninjective_chart',lambda t:t['mapping'].update(cash=t['mapping']['old_debt']))
 reject('removed_paid_memory',lambda t:remove_memory(t,'paid1'))
 reject('removed_used_memory',lambda t:remove_memory(t,'used'))
 reject('unsupported_multiplication',unsupported)
 reject('omitted_method',lambda t:t['body']['registry']['entries'].pop('draw2'))
 reject('extra_parameter',lambda t:t['parameters'].update(unused=c.b.BOOL))
 reject('parameter_substitution',lambda t:pre(t,'accrue1','selected_coupon')['predicate']['right'].update(id='I2'))
 reject('literalized_parameter_loss',lambda t:pre(t,'accrue1','selected_coupon')['predicate'].update(right={'op':'const','type':t['parameters']['I1'],'value':'6/1'}))
 reject('opening_right_overridden',lambda t:t['body']['opening']['memory'].update(right=True))
 reject('source_revision',lambda t:t['body']['opening']['memory'].update(source='synthetic-source-v2'))
 reject('wrong_event_amount_parameter',lambda t:t['body']['commands'][0]['event']['inputs']['amount']['value'].update(value={'parameter_value':'I2'}))
 reject('unused_input_metadata',lambda t:meth(t,'accrue1')['preconditions']['manifest']['inputs'].update(unused=cp(meth(t,'accrue1')['preconditions']['manifest']['inputs']['amount'])))
 reject('unknown_becomes_pass',lambda t:pre(t,'draw1','right').update(on_unknown='satisfied'))
 reject('flow_origin_erased',lambda t:meth(t,'draw1')['monetary']['definition']['flows'][0].update(origin='net_cash'))
 reject('postcondition_removed',lambda t:meth(t,'draw1')['postconditions']['manifest']['requirements'].pop())
 reject('unknown_chart',lambda t:t.update(chart='gamma'))
 for label,args in [('right_integer',('floating',1,'3/50','3/50','7','pay','pay')),('receipt_outside',('floating',True,'3/50','3/50','8','pay','pay')),('rate_outside',('floating',True,'0','3/50','7','pay','pay')),('mode_outside',('unknown',True,'3/50','3/50','7','pay','pay')),('order_outside',('floating',True,'3/50','3/50','7','hold','pay'))]:
  try:c.literalize(c.template('alpha'),*args)
  except ValueError:ck(label,True);controls.append({'name':label,'refused':True})
  else:ck(label,False)
 for p,h in lock.items():ck('protected:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 result={'status':'PASS','symbolic_methods':16,'charts':2,'literalization_cases':len(instances),'typed_finite_variants':32,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'continuous_region_obligations_discharged':0,'continuous_region_obligations_remaining':3872,'scope':'Selected affine effects, known-valued Boolean guards, memory semantics and pinned metadata; no general compiler or region-composition proof.'}
except Exception:
 result={'status':'FAIL','assertions':len(checks),'controls':len(controls),'error':traceback.format_exc()}
finally:
 for name,obj in [('verification.json',result),('checks.json',checks),('controls.json',controls),('certificates.json',certificates),('literalizations.json',instances),('source-lock.json',lock)]:
  (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'python':platform.python_version(),'environment':'standard-library CPU; GPU intentionally hidden','data':'explicit exact synthetic template and28 predecessor premises','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'cpu_limit_seconds':120,'plan':'docs/plans/accounting-symbolic-method-certificate-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
