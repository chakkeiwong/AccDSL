"""Complete shared-book proposals and saved original-comparator replay."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import lease_shared_book_v1 as lease
from test_lease_shared_book_v1 import LeaseBookTests,fixture,two_leases,cash
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def cases():
 rows=[]
 def add(name,s,e,status):rows.append({'case':name,'opening':s,'events':e,'expected_status':status})
 s,e=fixture();add('original_lifecycle',s,e,'hypothetical_sequence_complete')
 s,e=two_leases();cash(s,Q(400));add('shared_book_unrelated_lease',s,e,'hypothetical_sequence_complete')
 s,e=two_leases();cash(s,Q(300));joined=[]
 for event in e:
  joined.append(event);other=deepcopy(event);other['id']='other-'+event['id'];other['lease_id']='lease2';joined.append(other)
 add('two_interleaved_leases',s,joined,'hypothetical_sequence_complete')
 s,e=fixture();cash(s,Q(50));add('funding_failure_prefix',s,e,'funding_failure')
 s,e=fixture();e[2]['parameters']['amount']='unknown';add('unknown_payment_prefix',s,e,'unresolved')
 s,e=fixture();s['collection_complete']='unknown';add('unknown_membership',s,e,'unresolved')
 s,e=fixture();e[0]['original_scope_sha256']='0'*64;add('wrong_source_scope',s,e,'unsupported')
 return rows
def conformance(retained=None):
 checks=[];outputs=[]
 def check(n,x):checks.append({'name':n,'passed':bool(x)})
 for row in cases() if retained is None else retained:
  before=deepcopy(row['opening']);r=lease.run_prefix(row['opening'],row['events'])
  check(row['case']+'_status',r['status']==row['expected_status'])
  check(row['case']+'_immutable',before==row['opening'])
  check(row['case']+'_json_stable',json.loads(json.dumps(r))==r)
  check(row['case']+'_boundary',all(r[k] is False for k in lease.FLAGS))
  state=deepcopy(before)
  for index,p in enumerate(r['proposals']):
   state=lease.apply(state,row['events'][index],json.loads(json.dumps(p)))
   check(row['case']+'_original_replay_'+str(index),state==p['after'])
  check(row['case']+'_complete_prefix',state==r['state'])
  if 'result' in row:check(row['case']+'_saved_result',r==row['result'])
  outputs.append({**{k:v for k,v in row.items() if k!='result'},'result':r})
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(LeaseBookTests)
 stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream).run(suite)
 check('15_focused_shared_lease_methods',tests.wasSuccessful() and tests.testsRun==15)
 if not tests.wasSuccessful():print(stream.getvalue(),file=sys.stderr)
 source=HERE.parent/'lease-module-composition-audit-20261024-r2/audit.py'
 spec=importlib.util.spec_from_file_location('shared_lease_original_audit',source)
 original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
 audit,_=original.conformance()
 check('70_original_lease_audit_checks',audit['passed'] and len(audit['checks'])==70 and audit==json.loads((source.parent/'audit.json').read_text()))
 locks=json.loads((HERE/'source-lock.json').read_text())
 for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
 result={'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':tests.testsRun,'original_audit_checks':len(audit['checks'])}
 assert result==json.loads(json.dumps(result)) and outputs==json.loads(json.dumps(outputs))
 return result,outputs,locks
def main():
 mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
 assert mode!='--record' or not (HERE/'manifest.json').exists()
 if mode=='--replay':
  m=json.loads((HERE/'manifest.json').read_text())
  for group in ['inputs','implementation','outputs']:
   for name,h in m[group].items():assert sha(ROOT/name)==h,name
  saved=json.loads((HERE/'cases.json').read_text());r,again,_=conformance(saved)
  assert r['passed'] and again==saved
 started=datetime.now(timezone.utc).isoformat();start=time.monotonic();r,rows,locks=conformance()
 assert r['passed'],[c for c in r['checks'] if not c['passed']]
 obs={'mode':mode,'passed':True,'checks':len(r['checks']),'unit_tests':r['unit_tests'],'original_audit_checks':r['original_audit_checks'],'cases':len(rows),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
 if mode=='--record':
  dump(HERE/'checks.json',r);dump(HERE/'cases.json',rows)
  files=[p for p in HERE.iterdir() if p.suffix in ['.py','.md']]+[HERE/'source-lock.json',HERE/'original-scope.json',ROOT/'scripts/lease_shared_book_v1.py',ROOT/'tests/test_lease_shared_book_v1.py']
  dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':obs['wall_seconds'],
   'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
   'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record','environment':'Python '+platform.python_version(),
   'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact finite lease replay',
   'data_version':'original CorporateResiduals/1 lease inputs and explicit synthetic shared-book premises',
   'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
   'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json']},
   'plan':'docs/plans/accounting-lease-shared-book-contract-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
 elif mode=='--replay':
  assert r==json.loads((HERE/'checks.json').read_text()) and rows==json.loads((HERE/'cases.json').read_text())
 print(json.dumps(obs))
if __name__=='__main__':main()
