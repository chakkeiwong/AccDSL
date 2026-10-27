"""One-shot bounded complete-state common-executor comparison."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as F
import json,sys,os,time,platform,hashlib,subprocess,traceback,importlib.util
import bridge as b
import expected
HERE=Path(__file__).resolve().parent;ROOT=b.ROOT;rt=b.rt
# Only pure earlier model definitions; never import a one-shot evidence writer.
sys.path.insert(0,str(HERE.parent/'two-date-continuous-memory-20261026'))
import model as earlier_model
spec=importlib.util.spec_from_file_location('earlier_closed_form',HERE.parent/'two-date-continuous-memory-20261026/oracle.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
CASES=[
('fixed',False,'1/50','2/25','6','pay','pay'),
('fixed',True,'1/50','2/25','7','draw','pay'),
('floating',False,'3/50','3/50','7','pay','pay'),
('floating',False,'3/50','3/50','7','draw','pay'),
('floating',True,'3/50','3/50','6','draw','pay'),
('floating',True,'3/50','3/50','7','draw','pay'),
('floating',True,'3/50','3/50','6','draw','draw'),
('floating',True,'1/50','3/50','6','pay','draw'),
('floating',True,'1/50','3/50','6','pay','pay'),
('floating',True,'11/200','3/50','6','pay','pay'),
('floating',True,'11/200','3/50','7','draw','pay'),
('floating',True,'23/400','11/200','6','draw','pay'),
('floating',True,'23/400','550001/10000000','6','draw','pay'),
('floating',True,'23/400','549999/10000000','6','draw','pay')]
checks=[];cases=[];controls=[]
def ck(name,x,y=True):
 checks.append({'name':name,'pass':x==y,'actual':x,'expected':y})
 if x!=y:raise AssertionError(name)
def control(name,ok):ck(name,ok);controls.append({'name':name,'discriminates':ok})
def reduced(book,m):
 z={k:F(book['balances'][m[k]]) for k in b.CLASSES};mem=book['memory']
 return {'cash':z['cash'],'other_assets':z['other_assets'],'old_debt':-z['old_debt'],'facility_debt':-z['facility_debt'],'interest_payable':-z['interest_payable'],'equity':-z['capital']-z['income']-z['interest_expense']-z['fee_expense']}
def at(v,r):
 if isinstance(v,earlier_model.A):return v(r)
 if isinstance(v,dict):return {k:at(x,r) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [at(x,r) for x in v]
 return v

def encode(v):
 if isinstance(v,F):return str(v)
 if isinstance(v,dict):return {k:encode(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [encode(x) for x in v]
 return v
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic()
sources={Path(__file__).resolve(),HERE/'bridge.py',HERE/'expected.py',ROOT/'docs/plans/accounting-guarded-memory-runtime-20261026.md',HERE.parent/'two-date-continuous-memory-20261026/attempt-04/verification.json'}
for mod in list(sys.modules.values()):
 p=getattr(mod,'__file__',None)
 if p and Path(p).resolve().is_relative_to(ROOT) and Path(p).suffix=='.py':sources.add(Path(p).resolve())
lock={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
for p in sources:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
try:
 for chart in ('alpha','beta'):
  for i,case in enumerate(CASES):
   body,m=b.build(*case,chart=chart);before=cp(body);wanted,trace,stop=expected.financial_oracle(body,m,case)
   actual=rt.run(body)
   ck(f'{chart}/{i}/status',actual['status'],'stopped_provisional' if stop else 'complete_provisional')
   ck('complete_input_unchanged',body,before)
   ck('complete_book',actual['current'],wanted)
   ck('trace_length',len(actual['trace']),len(trace))
   for got,want in zip(actual['trace'],trace):
    tr=got['result']['transition'];ck('full_prefix',tr['after'],want['after']);ck('journal',tr['journal'],want['journal']);ck('flows',tr['flows'],want['flows'])
    ck('before_hash',got['before_sha256'],rt.digest(want['before']))
   ck('remaining_exact',actual['remaining_commands'],body['commands'][len(trace):])
   if stop:ck('refused_key',actual['stop']['command']['method_key'],stop['key'])
   report=b.report(body,wanted);wantreport=expected.report_oracle(body,wanted);ck('complete_report',report,wantreport)
   mode,right,r1,r2,R,a1,a2=case;status=('refused1' if len(trace)==1 else 'refused2') if stop else 'accepted'
   previous=at(prior.expected(mode,right,(F(r1),F(r1)),(F(r2),F(r2)),F(R),a1,a2,status),(F(r1),F(r2)))
   ck('earlier_reduced_balance',reduced(wanted,m),previous['balances']);ck('earlier_used_flag',wanted['memory']['used'],previous['facility_used']);ck('earlier_unpaid',-F(wanted['balances'][m['interest_payable']]),previous['unpaid'])
   cases.append({'id':chart+'/'+str(i),'chart':chart,'premises':case,'body':body,'mapping':m,'execution':actual,'report':report,'oracle':{'current':wanted,'trace':trace,'stop':stop}})
  print(json.dumps({'chart':chart,'complete_cases':len(cases),'elapsed':time.monotonic()-start}),flush=True)
 # Controls operate on accepted prefix snapshots using the unchanged method engine.
 c=cases[5];body=c['body'];m=c['mapping'];accrued=cp(c['execution']['trace'][0]['result']['transition']['after']);command=body['commands'][1]
 def refuses(name,book,cmd=None,registry=None):
  before=cp(book);request=rt.call(book,registry or body['registry'],cmd or command);answer=rt.methods.propose(book,request)
  control(name,answer['status']!='proposed' and book==before)
 bad=cp(accrued);bad['memory']['used']=True;refuses('used_without_history',bad)
 bad=cp(accrued);bad['memory']['source']='later-source-v2';refuses('changed_source_scope',bad)
 bad=cp(accrued);bad['memory']['clause']='revolving-v2';refuses('changed_clause_scope',bad)
 bad=cp(accrued);bad['memory']['mode']='fixed';refuses('changed_persistent_mode',bad)
 bad=cp(accrued);bad['memory']['right']=False;refuses('unavailable_facility',bad)
 bad=cp(accrued);bad['memory']['phase']='settled1';refuses('wrong_phase',bad)
 bad=cp(accrued);bad['balances'][m['interest_payable']]='-5/1';bad['balances'][m['interest_expense']]='5/1';refuses('balanced_wrong_payable',bad)
 bad=cp(accrued);bad['balances'][m['cash']]='-1/1';bad['balances'][m['capital']]='13/2';refuses('balanced_negative_cash',bad)
 cmd=cp(command);cmd['event']['date']='2027-07-01';refuses('wrong_date',accrued,cmd)
 reg=cp(body['registry']);reg['entries']['draw1']['method_sha256']='0'*64;refuses('stale_registry_method',accrued,registry=reg)
 # Once repaid, state balance0 does not restore the used borrowing right.
 repaid=cp(c['execution']['trace'][4]['result']['transition']['after']);cmd=cp(body['commands'][-1]);cmd['method_key']='draw2';cmd['event']['id']='draw2'
 refuses('repaid_still_used',repaid,cmd)
 # Cash-sufficient first pay is legal at equality; draw is not. Different cases
 # check both sides of the later joint boundary without rounding.
 control('strict_trigger_boundary',cases[9]['execution']['status']=='complete_provisional' and cases[10]['execution']['status']=='stopped_provisional')
 control('joint_boundary_equality',cases[11]['execution']['status']=='complete_provisional')
 control('joint_boundary_above',cases[12]['execution']['status']=='stopped_provisional')
 control('joint_boundary_below',cases[13]['execution']['status']=='complete_provisional')
 control('refusal_retains_due',cases[4]['execution']['current']['balances']['interest_payable']=='-6/1')
 for p,h in lock.items():ck('source_unchanged:'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
 result={'status':'PASS','cases':len(cases),'assertions':len(checks),'controls':len(controls),'protected_files':len(lock),'scope':'Concrete common-engine conformance at declared exact points; not generic symbolic equivalence.'}
except Exception:
 result={'status':'FAIL','cases':len(cases),'assertions':len(checks),'controls':len(controls),'error':traceback.format_exc()}
finally:
 for name,obj in [('cases.json',cases),('checks.json',checks),('controls.json',controls),('source-lock.json',lock),('verification.json',result)]:
  (OUT/name).write_text(json.dumps(encode(obj),indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(ROOT))+' '+str(OUT),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':platform.python_version(),'environment':'standard-library CPU; GPU intentionally hidden; no bytecode writes','data':'explicit synthetic cases; preserved input/dependency closure','seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-guarded-memory-runtime-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)
