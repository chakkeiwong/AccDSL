"""Resumable exact temporal partition; pending cells are not feasible-world claims."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'temporal-family-binding-20261027'))
import family as f
import check as c
t=f.t;identity=t.identity;need=t.need;PROFILE='ResumableTemporalFrontier/1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Methods:
 def __init__(self):
  locks=[H.parent/'source-time-intervals-20261027/attempt-01/source-lock.json',H.parent/'temporal-family-binding-20261027/attempt-01/source-lock.json']
  self.files={}
  for lock in locks:
   for n,h in json.loads(lock.read_text()).items():need(sha(R/n)==h,'predecessor_changed:'+n);self.files[n]=h
   self.files[str(lock.relative_to(R))]=sha(lock)
  for p in [H/'frontier.py',H/'check.py',H.parent/'temporal-family-binding-20261027/family.py']:
   self.files[str(p.relative_to(R))]=sha(p)
  self.identity=identity(self.files)
def prepare(x,expected):
 p=f.prepared(x,expected);need(x['max_nodes']==4096,'original_scope_cap');return p
def pending(path):return {'kind':'pending','path':path}
def summary(p,tree,limit):
 resolved=0;pending_paths=[];out={};supports=[]
 def walk(n):
  nonlocal resolved
  if n['kind']=='pending':pending_paths.append(n['path']);return
  resolved+=1
  if n['kind']=='leaf':
   o=n['outcome'];k=identity(o);out[k]=o;supports.append({'path':n['path'],'outcome_sha256':k})
  for ch in n.get('children',[]):walk(ch)
 walk(tree)
 return {'resolved':resolved,'pending':pending_paths,'outcomes':[out[k] for k in sorted(out)],'supports':supports,'complete':not pending_paths,'status':('capped' if resolved==limit else 'paused') if pending_paths else ('complete_family' if out else 'inconsistent_clocks')}
def start(x,expected,m,limit=4096):
 need(type(limit) is int and 1<=limit<=4096,'execution_cap');p=prepare(x,expected);tree=pending([])
 b={'profile':PROFILE,**t.FLAGS,'input':cp(x),'input_sha256':expected,'prepared_sha256':identity(p),'method_identity':m.identity,'limit':limit,'tree':tree,**summary(p,tree,limit)}
 c.verify(b,identity(b),expected,m,limit);return b
def locate(n,p,edges,i,eligible):
 if n['kind']=='pending':return n,edges,i,eligible
 if n['kind']=='expanded':
  h=sorted(p['records'])[i];gs=p['guards'][h]
  for k,ch in enumerate(n['children']):
   es=edges+gs if k==0 else edges+gs[:k-1]+[t.dc.opposite(gs[k-1])]
   got=locate(ch,p,es,i+1,{**eligible,h:k==0})
   if got is not None:return got
 return None
def resume(previous,expected_checkpoint,expected_input,m,budget,limit=4096):
 need(type(budget) is int and 1<=budget<=4096,'step_budget')
 c.verify(previous,expected_checkpoint,expected_input,m,limit)
 b=cp(previous);p=prepare(b['input'],expected_input);order=sorted(p['records']);work=0
 while work<budget and b['resolved']<limit:
  found=locate(b['tree'],p,p['constraints'],0,{})
  if found is None:break
  n,edges,i,eligible=found;path=n['path'];proof=t.dc.solve(p['variables'],edges);kind=t.pc.verify(p['variables'],edges,proof)
  replacement={'path':path,'proof':proof}
  if kind=='empty':replacement['kind']='empty'
  elif i==len(order):replacement.update(kind='leaf',eligible=eligible,outcome=t.outcome(p,eligible))
  else:
   h=order[i];replacement.update(kind='expanded',record=h,children=[pending(path+[k]) for k in range(1+len(p['guards'][h]))])
  n.clear();n.update(replacement);work+=1;b['resolved']+=1
 b.update(summary(p,b['tree'],limit));c.verify(b,identity(b),expected_input,m,limit);return b,work

def stripped(n):
 need(n['kind']!='pending','unfinished_tree')
 a={'proof':cp(n['proof'])}
 if n['kind']=='expanded':a.update(record=n['record'],children=[stripped(ch) for ch in n['children']])
 if n['kind']=='leaf':a.update(eligible=cp(n['eligible']),outcome=cp(n['outcome']))
 return a
