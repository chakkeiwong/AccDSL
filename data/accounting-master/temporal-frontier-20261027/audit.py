"""Read accepted checkpoints without rerunning the accepted evidence writer."""
from pathlib import Path
from copy import deepcopy as cp
import json,hashlib,platform,subprocess,sys,time,traceback,resource
import frontier as z
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[]
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def reject(n,b,e,m):
 try:z.c.verify(b,z.identity(b),e,m)
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck(n,True)
 else:ck(n,False)
def nodes(n):
 yield n
 for child in n.get('children',[]):yield from nodes(child)
try:
 pin=json.loads((H/'attempt-01/source-lock.json').read_text());m=z.Methods()
 accepted={str(p.relative_to(R)):sha(p) for p in (H/'attempt-01').iterdir() if p.is_file()}
 save('accepted-lock.json',accepted)
 for n,h in pin.items():ck('source:'+n,sha(R/n)==h)
 saved=json.loads((H/'attempt-01/checkpoints.json').read_text());total=0;pending_empty=None
 for case in saved:
  last=None;limit=case.get('limit',4096)
  for b in case['checkpoints']:
   result=z.c.verify(b,z.identity(b),case['expected_input'],m,limit);total+=1
   ck(case['case']+':saved:'+str(total),result['resolved']==b['resolved'])
   if last is not None:
    ck(case['case']+':unit_progress:'+str(total),b['resolved']==last['resolved']+1)
    old={tuple(n['path']):z.identity(n['proof']) for n in nodes(last['tree']) if n['kind']!='pending'}
    now={tuple(n['path']):z.identity(n['proof']) for n in nodes(b['tree']) if n['kind']!='pending'}
    ck(case['case']+':old_certificates:'+str(total),all(now[k]==v for k,v in old.items()))
   last=b
  if case['case']!='cap2':ck(case['case']+':exhaustive',last['complete'] and not last['pending'])
 a=saved[0];e=a['expected_input'];full=a['checkpoints'][-1];initial=a['checkpoints'][0]
 b=cp(full);leaf=next(n for n in nodes(b['tree']) if n['kind']=='empty');leaf['proof']['cycle']=[];reject('corrupt_saved_empty_certificate',b,e,m)
 b=cp(full);leaf=next(n for n in nodes(b['tree']) if n['kind']=='leaf');key=next(iter(leaf['eligible']));leaf['eligible'][key]=int(leaf['eligible'][key]);reject('eligibility_bool_as_integer',b,e,m)
 b=cp(full);next(n for n in nodes(b['tree']) if n['kind']=='leaf')['kind']='pending';reject('leaf_concealed_as_pending',b,e,m)
 b=cp(full);b['pending']=[[]];reject('fabricated_pending_root',b,e,m)
 # Caller-supplied digest may change; structural proofs and trusted request remain binding.
 b=cp(full);b['input']['trusted'].clear();b['input_sha256']=z.identity(b['input']);reject('changed_trust_with_internal_digest',b,e,m)
 # A checkpoint makes no feasibility assertion for its pending cells.
 p=z.prepare(initial['input'],e);root,_=z.resume(initial,z.identity(initial),e,m,1)
 h=root['tree']['record'];gs=p['guards'][h]
 proven_empty=0
 for k,n in enumerate(root['tree']['children']):
  edges=p['constraints']+gs if k==0 else p['constraints']+gs[:k-1]+[z.t.dc.opposite(gs[k-1])]
  proof=z.t.dc.solve(p['variables'],edges)
  if z.t.pc.verify(p['variables'],edges,proof)=='empty':proven_empty+=1
 ck('pending_can_be_empty_without_being_discarded',proven_empty>0 and len(root['pending'])==len(gs)+1)
 for n,h in accepted.items():ck('accepted_unchanged:'+n,sha(R/n)==h)
 summary={'status':'PASS','saved_checkpoints':total,'saved_case_sequences':len(saved),'assertions':len(checks),'additional_controls':len(controls),'pending_empty_cells':proven_empty,'scope':'Independent structural checker rereads every saved pause and preserves prior proofs; no durability or scalability claim.'}
except Exception:summary={'status':'FAIL','error':traceback.format_exc(),'assertions':len(checks)}
finally:
 save('verification.json',summary);save('checks.json',checks);save('controls.json',controls)
 save('run-manifest.json',{'git':subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True).stdout.strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'environment':'existing Python '+platform.python_version()+'; CPU only; GPU deliberately hidden','seeds':'N/A deterministic exact audit','data_version':'accepted-lock.json','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-temporal-frontier-20261027.md','result':str(OUT/'verification.json')})
 print(json.dumps(summary));sys.exit(summary['status']!='PASS')
