"""One-shot exact path-composition checks; no earlier writers imported."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as F
import hashlib,importlib.util,itertools,json,os,platform,resource,subprocess,sys,time,traceback
import compose as c
import expected_path as e
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRE=HERE.parent/'symbolic-method-certificate-20261026/attempt-01'
sys.path.insert(0,str(HERE.parent/'two-date-continuous-memory-20261026'))
import model as types
spec=importlib.util.spec_from_file_location('prior_closed_form',HERE.parent/'two-date-continuous-memory-20261026/oracle.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic()
checks=[];controls=[];cases=[]
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n+': '+repr(x)[:800]+' != '+repr(y)[:800])
def tuples(x):
 if isinstance(x,list):return tuple(tuples(v) for v in x)
 if isinstance(x,dict):return {k:tuples(v) for k,v in x.items()}
 return x
source={Path(__file__).resolve(),HERE/'compose.py',HERE/'expected_path.py',ROOT/'docs/plans/accounting-symbolic-path-composition-20261026.md',PRE/'verification.json',PRE/'certificates.json',PRE/'source-lock.json',HERE.parent/'two-date-continuous-memory-20261026/model.py',HERE.parent/'two-date-continuous-memory-20261026/oracle.py'}
lock={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}
for p in source:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
def prior_form(form,mode,R):
 out=types.aff(F(form[2]));vars={'I1':types.aff(5) if mode=='fixed' else types.A(x=100),'I2':types.aff(5) if mode=='fixed' else types.A(y=100),'R':types.aff(R)}
 for key,co in form[1]:
  a=vars[key];out=out+types.A(a.x*F(co),a.y*F(co),a.c*F(co))
 return out
try:
 ck('predecessor_pass',json.loads((PRE/'verification.json').read_text())['status'],'PASS')
 for p,h in json.loads((PRE/'source-lock.json').read_text()).items():ck('predecessor_source:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 saved=tuples(json.loads((PRE/'certificates.json').read_text()))
 for chart,mode,right,a1,a2 in itertools.product(('alpha','beta'),('fixed','floating'),(False,True),('pay','draw'),('pay','draw')):
  label='/'.join(map(str,(chart,mode,right,a1,a2)));forms=saved[chart]['actual'];got=c.sequence(forms,mode,right,a1,a2);want=e.steps(mode,right,a1,a2)
  for i,(x,y) in enumerate(zip(got,want)):
   for key in ('key','before','pre','after','post'):ck(label+'/'+str(i)+'/'+key,x[key],y[key])
  branches=[]
  for stop in (1,5,None):
   branch=c.branch(got,stop);n=6 if stop is None else stop;wanted_state=e.state(n,mode,right,a1,a2)
   ck(label+'/branch/'+str(stop)+'/state',branch['current'],wanted_state)
   ck(label+'/branch/'+str(stop)+'/accepted',len(branch['accepted_conditions']),n)
   ck(label+'/branch/'+str(stop)+'/remaining',branch['remaining'],[s['key'] for s in want[n:]])
   ck(label+'/branch/'+str(stop)+'/refusal',branch['refusal'],None if stop is None else {'key':want[n]['key'],'not_all':{'pre':want[n]['pre'],'post':want[n]['post']}})
   for R in (6,7):
    b=branch['current']['book'];p=prior.expected(mode,right,(F(3,100),F(3,50)),(F(3,100),F(3,50)),F(R),a1,a2,branch['status'])
    reduced={k:prior_form(b[k],mode,R) for k in ('cash','other_assets')}
    reduced.update({k:-prior_form(b[k],mode,R) for k in ('old_debt','facility_debt','interest_payable')})
    reduced['equity']=sum((-prior_form(b[k],mode,R) for k in ('capital','income','interest_expense','fee_expense')),types.aff(0))
    ck(label+'/prior/'+str(stop)+'/'+str(R),reduced,p['balances'])
    ck(label+'/used/'+str(stop)+'/'+str(R),branch['current']['memory']['used'][2],p['facility_used'])
   branches.append(branch)
  cases.append({'chart':chart,'mode':mode,'right':right,'actions':[a1,a2],'steps':got,'branches':branches,'feasibility':'not_decided'})
 print(json.dumps({'complete_symbolic_variants':len(cases),'checks':len(checks)}),flush=True)
 def reject(name,mutate):
  forms=cp(saved['alpha']['actual']);mutate(forms)
  try:ok=c.sequence(forms,'floating',True,'draw','pay')!=e.steps('floating',True,'draw','pay')
  except (ValueError,KeyError,TypeError):ok=True
  ck(name,ok);controls.append({'name':name,'discriminates':ok})
 reject('repayment_wrong_cash',lambda f:f['repay2']['postings'].update(cash=c.lin({'account/facility_debt':-1})))
 reject('lost_paid_history',lambda f:f['draw1']['memory'].pop('paid1'))
 reject('right_restored_after_repay',lambda f:f['repay2']['memory'].update(used=('literal','boolean',False)))
 reject('weak_trigger',lambda f:f['draw1']['pre'].update(strict_trigger=('le',f['draw1']['pre']['strict_trigger'][1])))
 reject('gross_flow_origin',lambda f:f['draw1']['flows'].update(facility_draw=('financing','net',c.lin(c=1))))
 reject('due_from_wrong_coupon',lambda f:f['accrue2']['memory'].update(due2=c.lin({'parameter/I1':1})))
 reject('removed_postcondition',lambda f:f['pay2']['post'].pop('payable_matches_history'))
 reject('unbound_reference',lambda f:f['pay2']['postings'].update(cash=c.lin({'missing':1})))
 reject('wrong_fee_expense',lambda f:f['draw1']['postings'].update(fee_expense=c.lin(c='1/2')))
 reject('lost_facility_balance',lambda f:f['draw1']['postings'].pop('facility_debt'))
 # Explicit substitution unit: simultaneous postings both read one unchanged pre-state.
 form=c.lin({'account/cash':1,'memory/due1':-1},'1/4')
 ck('simultaneous_substitution',c.value(form,{'account/cash':c.lin({'I1':-1},'11/2'),'memory/due1':c.lin({'I1':1})}),c.lin({'I1':-2},'23/4'))
 for p,h in lock.items():ck('source_preserved:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 result={'status':'PASS','variants':len(cases),'conditional_branches':len(cases)*3,'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'region_obligations_discharged':0,'region_obligations_remaining':3872,'scope':'Complete known-valued symbolic account/memory/flow and guard substitution for the selected sequence, with conditional refusal prefixes; reachability and policy mapping unproved.'}
except Exception:result={'status':'FAIL','assertions':len(checks),'controls':len(controls),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',result),('checks.json',checks),('controls.json',controls),('cases.json',cases),('source-lock.json',lock)]: (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'environment':'standard-library CPU; GPU intentionally hidden','python':platform.python_version(),'data':'exact immutable predecessor certificates and independent selected path formulas','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'cpu_limit_seconds':120,'plan':'docs/plans/accounting-symbolic-path-composition-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
