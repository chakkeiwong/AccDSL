"""Read and independently recheck saved proofs; separate one-shot replay evidence."""
from pathlib import Path
import hashlib,json,sys,time
import temporal as t
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=H/'replay-01';OUT.mkdir(exist_ok=False);start=time.monotonic();saved=json.loads((H/'attempt-01/proofs.json').read_text());checks=[];nodes=0
for row in saved:
 outcomes,n=t.verify_tree(row['prepared'],row['result']['tree']);assert outcomes==row['result']['outcomes'] and n==row['result']['nodes'];nodes+=n;checks.append({'case':row['case'],'nodes':n,'pass':True})
for n,h in json.loads((H/'attempt-01/source-lock.json').read_text()).items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
# In every consistent replacement-chain leaf, a child eligible at the same cutoffs
# has its ancestor clocks no later; retain any ancestor-effective-time exception.
leaves=[]
def walk(p,node):
 if 'eligible' in node:
  for child,parent in [(c,r['supersedes']) for c,r in p['records'].items() if r['supersedes'] is not None]:
   if node['eligible'][child] and not node['eligible'][parent]:
    # It may be legitimate only when retrospective effective dates differ.
    leaves.append({'child':child,'parent':parent,'outcome':node['outcome']})
 for c in node.get('children',[]):walk(p,c)
for row in saved:walk(row['prepared'],row['result']['tree'])
result={'status':'PASS','saved_requests':len(saved),'independently_rechecked_nodes':nodes,'source_lock_verified':True,'child_eligible_ancestor_unavailable':leaves,'wall_seconds':time.monotonic()-start,'checks':checks,'scope':'Saved original-edge and exhaustive-branch certificates; no accepted writer rerun.'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','child_eligible_ancestor_unavailable']}))
