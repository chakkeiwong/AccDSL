"""Reread every saved partial-policy payload under the independent checker."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,subprocess,resource,sys,time,traceback
import partial as p
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[]
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,x):
 checks.append({'name':n,'pass':bool(x)})
 if not x:raise AssertionError(n)
try:
 lock={str(q.relative_to(R)):sha(q) for q in (H/'attempt-01').iterdir() if q.is_file()};save('accepted-lock.json',lock)
 for n,h in json.loads((H/'attempt-01/source-lock.json').read_text()).items():ck('source:'+n,sha(R/n)==h)
 ctx=p.Context();refs={x['case']:x for x in json.loads((H/'attempt-01/full-references.json').read_text())};cases=json.loads((H/'attempt-01/cases.json').read_text());checked=0
 def verify(case,out):
  r=refs[case['case']];b=case['frontier'];return p.verify(out,p.identity(out),b,p.identity(b),b['input_sha256'],r['full'],r['full_sha256'],r['domain'],r['domain_sha256'],ctx)
 for x in cases:ck('saved:'+x['case']+':'+str(x['frontier']['resolved']),verify(x,x['result']));checked+=1
 mid=next(x for x in cases if x['case']=='baseline' and x['frontier']['resolved']==3)
 for n,mutation in [('integer_complete_flag',lambda b:b.__setitem__('complete',0)),('wrong_pending_domain',lambda b:b['pending_domains'][0].__setitem__('domain_sha256','0'*64)),('duplicated_source_support',lambda b:b['known_supports'].append(cp(b['known_supports'][0]))),('missing_known_action_row',lambda b:b['known_row_ids'].pop()),('candidate_as_infeasible',lambda b:b.__setitem__('status','conditionally_infeasible')),('numeric_count_as_policy_set',lambda b:b.__setitem__('candidates',4))]:
  bad=cp(mid['result']);mutation(bad)
  try:verify(mid,bad)
  except (ValueError,TypeError,KeyError,AssertionError):controls.append(n);ck(n,True)
  else:ck(n,False)
 # Negative source-declaration status cannot be smuggled into the complete comparison.
 r=refs['baseline'];bad=cp(r['full']);bad['status']='unresolved_observation_map'
 try:ctx.bind(bad,p.identity(bad))
 except (ValueError,KeyError,TypeError,AssertionError):controls.append('unresolved_full_comparison');ck('unresolved_full_comparison',True)
 else:ck('unresolved_full_comparison',False)
 for n,h in lock.items():ck('accepted_unchanged:'+n,sha(R/n)==h)
 summary={'status':'PASS','saved_checkpoints':checked,'assertions':len(checks),'additional_controls':len(controls),'scope':'All saved full candidate sets and refused-row witnesses rechecked; retrospective declared domains only.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 save('verification.json',summary);save('checks.json',checks);save('controls.json',controls)
 save('run-manifest.json',{'git':subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True).stdout.strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'existing Python '+platform.python_version()+'; CPU, GPU deliberately hidden','seeds':'N/A deterministic exact audit','data_version':'accepted-lock.json','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-partial-frontier-policy-20261027.md','result':str(OUT/'verification.json')})
 print(json.dumps(summary));sys.exit(summary['status']!='PASS')
