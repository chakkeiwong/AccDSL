"""Complete saved conditional allocations and original audit replay."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import lease_allocation_family_v1 as family
from test_lease_allocation_family_v1 import LeaseAllocationFamilyTests,request,query,domain
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def cases():
 rows=[]
 def add(name,r,status,q=None):rows.append({'case':name,'request':r,'query':q,'expected_status':status})
 add('full_partition',request(),'exact_conditional_partition')
 add('complete_open_fraction',request(Q(1,3),Q(59,2),False,True),'exact_conditional_partition')
 add('rejected_only',request(30,111,False,True),'exact_conditional_partition')
 add('unsupported_only',request(111,120,False,True),'exact_conditional_partition')
 for x in [0,30,111,120]:add('singleton_'+str(x),request(x,x),'exact_conditional_partition')
 add('partial_zero',request(cells=0),'partial_search')
 add('partial_one',request(cells=1),'partial_search')
 r=request();r['collection_complete']='unknown';add('membership_unknown',r,'unresolved')
 r=request();r['source_lock_sha256']='0'*64;add('source_mismatch',r,'unsupported')
 add('observation10',request(),'feasible_conditional_selection',query({'target':'final_rou','domain':domain(10,10)}))
 add('incompatible_joint',request(),'infeasible_conditional_selection',query({'target':'final_rou','domain':domain(30,30)},{'target':'profit','domain':domain(-69,-69)}))
 add('no_complete_cell',request(31,120),'infeasible_conditional_selection',query())
 q=query({'target':'final_rou','domain':domain(10,10)});q['max_replays']=0;add('query_budget_zero',request(),'partial_search',q)
 return rows

def conformance(saved=None):
 checks=[];outputs=[]
 def check(n,x):checks.append({'name':n,'passed':bool(x)})
 for row in cases() if saved is None else saved:
  before=deepcopy(row['request']);cond=deepcopy(row['query'])
  result=family.assess(row['request']) if cond is None else family.query(row['request'],cond)
  check(row['case']+'_status',result['status']==row['expected_status'])
  check(row['case']+'_immutable',before==row['request'] and cond==row['query'])
  check(row['case']+'_json_roundtrip',result==json.loads(json.dumps(result)))
  check(row['case']+'_flags',all(result[k] is False for k in family.FLAGS))
  if cond is None:check(row['case']+'_full_recompute',family.verify_result(row['request'],result))
  if 'result' in row:check(row['case']+'_saved_exact',row['result']==result)
  outputs.append({**{k:v for k,v in row.items() if k!='result'},'result':result})
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(LeaseAllocationFamilyTests)
 stream=io.StringIO();test=unittest.TextTestRunner(stream=stream).run(suite)
 check('16_focused_methods',test.wasSuccessful() and test.testsRun==16)
 if not test.wasSuccessful():print(stream.getvalue(),file=sys.stderr)
 source=HERE.parent/'lease-allocation-family-audit-20261024/audit.py'
 spec=importlib.util.spec_from_file_location('allocation_original_audit',source);audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
 prior,_=audit.audit()
 check('118_original_audit_replayed',prior['passed'] and len(prior['checks'])==118 and prior==json.loads((source.parent/'audit.json').read_text()))
 locks=json.loads((HERE/'source-lock.json').read_text())
 for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
 result={'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':test.testsRun,'original_audit_checks':len(prior['checks'])}
 assert result==json.loads(json.dumps(result)) and outputs==json.loads(json.dumps(outputs))
 return result,outputs,locks

def main():
 mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
 assert mode!='--record' or not (HERE/'manifest.json').exists()
 if mode=='--replay':
  m=json.loads((HERE/'manifest.json').read_text())
  for group in ['inputs','implementation','outputs']:
   for n,h in m[group].items():assert sha(ROOT/n)==h,n
  saved=json.loads((HERE/'cases.json').read_text());r,again,_=conformance(saved);assert r['passed'] and again==saved
 started=datetime.now(timezone.utc).isoformat();start=time.monotonic();r,rows,locks=conformance()
 assert r['passed'],[c['name'] for c in r['checks'] if not c['passed']]
 obs={'mode':mode,'passed':True,'checks':len(r['checks']),'unit_tests':r['unit_tests'],'original_audit_checks':r['original_audit_checks'],'cases':len(rows),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
 if mode=='--record':
  dump(HERE/'checks.json',r);dump(HERE/'cases.json',rows)
  files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]+[HERE/'source-lock.json',ROOT/'scripts/lease_allocation_family_v1.py',ROOT/'tests/test_lease_allocation_family_v1.py']
  dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':obs['wall_seconds'],
   'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
   'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record','environment':'Python '+platform.python_version(),
   'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact conditional family',
   'data_version':'original CorporateResiduals/1 and declared two-right allocation family',
   'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
   'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json']},
   'plan':'docs/plans/accounting-lease-allocation-family-reference-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
 elif mode=='--replay':assert r==json.loads((HERE/'checks.json').read_text()) and rows==json.loads((HERE/'cases.json').read_text())
 print(json.dumps(obs))
if __name__=='__main__':main()
