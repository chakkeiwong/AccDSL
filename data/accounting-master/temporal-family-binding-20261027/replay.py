"""One-shot saved-envelope audit using locked rows and independent constraint solves."""
from pathlib import Path
import hashlib,json,platform,subprocess,time
import family as m
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=H/'replay-01';OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'name':n,'pass':bool(v)});assert v,n
e=m.Evidence();saved=json.loads((H/'attempt-01/cases.json').read_text());seen={};rowschecked=0
for row in saved:
 b=row['reused'];ck(row['case']+':saved_envelope',m.verify(b,m.identity(b),b['input_sha256'],e))
 for key,v in b['numerical'].items():
  if key in seen:ck(row['case']+':same_key_same_full_payload',seen[key]==v);continue
  scenario=v['scenario'];rows=[r for r in e.rows if r['receipt']==scenario['receipt'] and (scenario['family']=='mixed' or r['right'])]
  policies,diagnostic=m.t.prior.independent.solve(rows,scenario['view'])
  ck('all_constraint_policies:'+key,policies=={m.t.prior.tuples(z) for z in v['policy_set']})
  ck('all_row_ids:'+key,[r['row_id'] for r in rows]==v['row_ids'])
  seen[key]=v;rowschecked+=len(rows)
# A zero policy count does not erase observation-domain or financial distinctions.
empty=[(key,v['scenario']) for key,v in seen.items() if v['count']==0]
ck('multiple_empty_domains_retained',len(empty)>=2 and len({m.identity(s) for k,s in empty})==len(empty))
for n,h in json.loads((H/'attempt-01/source-lock.json').read_text()).items():ck('source_preserved:'+n,sha(R/n)==h)
for n,h in e.method_files.items():ck('dependency_preserved:'+n,sha(R/n)==h)
result={'status':'PASS','saved_families':len(saved),'distinct_numerical_problems':len(seen),'distinct_empty_policy_problems':len(empty),'independent_row_population':rowschecked,'assertions':len(checks),'scope':'Saved full-family replay and independent numerical constraint formulation; no accepted writer rerun.'}
for n,x in [('verification.json',result),('checks.json',checks)]: (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
(OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R)),'environment':'Python '+platform.python_version()+'; CPU; GPU intentionally hidden','seeds':'N/A deterministic','data':'attempt-01/cases.json and protected row/method references','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-temporal-family-binding-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT)},indent=2)+'\n');print(json.dumps(result))
