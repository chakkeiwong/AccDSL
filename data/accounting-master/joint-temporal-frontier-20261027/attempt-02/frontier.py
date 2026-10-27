"""Resumable joint clock partition, independently reconstructed at each read."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('joint_front_binding',H.parent/'joint-stage-policy-20261027/binding.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
j=b.j;t=j.t;identity=j.identity;need=j.need;PROFILE='ResumableJointSourceFrontier/1'
def method():return identity({'frontier.py':sha256(Path(__file__).read_bytes()).hexdigest(),'joint.py':sha256(Path(j.__file__).read_bytes()).hexdigest()})
def summary(tree,limit):
 nodes=0;pending=[];out={};supports=[]
 def walk(n,path):
  nonlocal nodes
  if n['kind']=='pending':pending.append(path);return
  nodes+=1
  if n['kind']=='leaf':oid=identity(n['outcomes']);out[oid]=n['outcomes'];supports.append(dict(path=path,joint_outcome_sha256=oid))
  for i,ch in enumerate(n.get('children',[])):walk(ch,path+[i])
 walk(tree,[])
 return dict(nodes=nodes,pending=pending,outcomes=[out[k] for k in sorted(out)],supports=supports,complete=not pending,status=('capped' if nodes==limit else 'paused') if pending else 'complete_family' if out else 'inconsistent_clocks')
def start(x,xid,limit=4096):
 ps,_=j.prepare(x,xid);need(type(limit) is int and 1<=limit<=4096,'total_cap');tree=dict(kind='pending')
 out=dict(profile=PROFILE,**t.FLAGS,input=cp(x),input_sha256=xid,prepared_sha256=identity(ps),method_identity=method(),limit=limit,tree=tree,**summary(tree,limit));verify(out,identity(out),xid,limit);return out

def verify(front,fid,xid,limit=4096):
 need(identity(front)==fid,'external_frontier');t.fields(front,['profile',*t.FLAGS,'input','input_sha256','prepared_sha256','method_identity','limit','tree','nodes','pending','outcomes','supports','complete','status'],'frontier_fields')
 need(front['profile']==PROFILE and all(front[k] is False for k in t.FLAGS),'profile_nonadmission');need(front['limit']==limit and type(limit) is int and 1<=limit<=4096,'external_cap');need(front['method_identity']==method(),'method_identity')
 ps,_=j.prepare(front['input'],xid);need(front['input_sha256']==xid and front['prepared_sha256']==identity(ps),'input_bindings');p=ps[0];order=[(s,h) for s in range(2) for h in sorted(p['records'])];nodes=0;pending=[];domains=[];pairs={};supports=[];seen=False
 def visit(n,edges,i,eligible,path):
  nonlocal nodes,seen
  if n['kind']=='pending':t.fields(n,['kind'],'pending_fields');seen=True;pending.append(path);domains.append(dict(path=path,constraints_sha256=identity(edges)));return
  need(not seen,'dfs_prefix_order');nodes+=1;need(nodes<=limit,'node_cap');kind=t.pc.verify(p['variables'],edges,n['proof'])
  if kind=='empty':t.fields(n,['kind','proof'],'empty_fields');need(n['kind']=='empty','empty_kind');return
  if i==len(order):
   t.fields(n,['kind','proof','eligible','outcomes'],'leaf_fields');need(n['kind']=='leaf' and n['eligible']==eligible,'leaf_eligibility');expected=[j.check.selected(ps[s],eligible[s]) for s in range(2)];need(n['outcomes']==expected,'joint_leaf_outcomes');oid=identity(expected);pairs[oid]=expected;supports.append(dict(path=path,joint_outcome_sha256=oid));return
  stage,h=order[i];gs=ps[stage]['guards'][h];t.fields(n,['kind','proof','stage','record','children'],'expanded_fields');need(n['kind']=='expanded' and n['stage']==stage and n['record']==h and len(n['children'])==len(gs)+1,'joint_partition_children')
  for k,ch in enumerate(n['children']):
   if k==0:es=edges+gs
   else:g=gs[k-1];es=edges+gs[:k-1]+[t.edge(g['v'],g['u'],-Q(g['bound']),not g['strict'])]
   new=cp(eligible);new[stage][h]=k==0;visit(ch,es,i+1,new,path+[k])
 visit(front['tree'],p['constraints'],0,[{},{}],[])
 want=dict(nodes=nodes,pending=pending,outcomes=[pairs[k] for k in sorted(pairs)],supports=supports,complete=not pending,status=('capped' if nodes==limit else 'paused') if pending else 'complete_family' if pairs else 'inconsistent_clocks')
 for k,v in want.items():need(identity(front[k])==identity(v),'exact_'+k)
 return dict(pending_domains=domains)

def resume(front,fid,xid,budget,limit=4096):
 verify(front,fid,xid,limit);need(type(budget) is int and 1<=budget<=4096,'step_budget');out=cp(front);ps,_=j.prepare(out['input'],xid);p=ps[0];order=[(s,h) for s in range(2) for h in sorted(p['records'])]
 def locate(n,edges,i,eligible):
  if n['kind']=='pending':return n,edges,i,eligible
  if n['kind']!='expanded':return None
  stage,h=order[i];gs=ps[stage]['guards'][h]
  for k,ch in enumerate(n['children']):
   es=edges+gs if k==0 else edges+gs[:k-1]+[t.dc.opposite(gs[k-1])];new=cp(eligible);new[stage][h]=k==0;got=locate(ch,es,i+1,new)
   if got is not None:return got
  return None
 work=0
 while work<budget and out['nodes']<limit:
  got=locate(out['tree'],p['constraints'],0,[{},{}])
  if got is None:break
  n,edges,i,eligible=got;proof=t.dc.solve(p['variables'],edges);kind=t.pc.verify(p['variables'],edges,proof)
  if kind=='empty':replacement=dict(kind='empty',proof=proof)
  elif i==len(order):replacement=dict(kind='leaf',proof=proof,eligible=cp(eligible),outcomes=[t.outcome(ps[s],eligible[s]) for s in range(2)])
  else:stage,h=order[i];replacement=dict(kind='expanded',proof=proof,stage=stage,record=h,children=[dict(kind='pending') for _ in range(len(ps[stage]['guards'][h])+1)])
  n.clear();n.update(replacement);work+=1;out['nodes']+=1
 out.update(summary(out['tree'],limit));verify(out,identity(out),xid,limit);return out,work

def partial_policy(front,fid,xid,decl,did,domain,uid,e,limit=4096):
 audit=verify(front,fid,xid,limit);expected=b.derive(front['input'],xid,decl,did,e);need(identity(domain)==uid==identity(expected),'fixed_prospective_domain');rows=[];unknown=[]
 for pair in front['outcomes']:
  if any(o['status']!='selected_conditional' for o in pair):unknown.append(cp(pair));continue
  rows+=b.rows(front['input'],decl,e,(pair[0]['heads']['financial_family'],pair[0]['heads']['observation_scheme'],pair[1]['heads']['observation_scheme']))
 keys=None if domain['keys'] is None else [t.prior.tuples(k) for k in domain['keys']]
 if keys is None:candidates=rejected=None;status='unresolved_domain_budget'
 elif front['status']=='inconsistent_clocks':candidates=rejected=None;status='inconsistent_clocks'
 else:
  need(set(b.d.keys(rows))<=set(keys),'known_joint_key_coverage');candidates,rejected=b.p.restrictions(rows,keys);need({tuple(v) for v in candidates}==b.p.oracle(rows,keys),'independent_partial_policy')
  status='unresolved_source_family' if unknown else 'conditionally_infeasible' if not candidates else 'unresolved_pending' if front['pending'] else 'conditionally_feasible'
 return dict(profile='PartialJointStagePolicy/1',**b.b.FLAGS,frontier_sha256=fid,input_sha256=xid,declaration_sha256=did,domain_sha256=uid,status=status,candidates=candidates,rejections=rejected,unknown_outcomes=unknown,source_supports=cp(front['supports']),pending=cp(front['pending']),pending_domains=audit['pending_domains'],complete=front['complete'],known_row_ids=[r['id'] for r in rows])

