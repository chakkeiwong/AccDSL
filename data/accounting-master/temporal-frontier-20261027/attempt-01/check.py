"""Independent reconstruction of the full frontier partition, with no solver calls."""
from fractions import Fraction as Q
from copy import deepcopy as cp
import family as f
t=f.t;need=t.need;identity=t.identity

def selected(p,eligible):
 live={h for h in eligible if eligible[h]};heads=[]
 for h in sorted(live):
  if not any(h in p['ancestry'][j] for j in live):heads.append(h)
 chosen={};issues=[]
 for slot in t.SLOTS:
  matches=[h for h in heads if p['records'][h]['slot']==slot]
  if len(matches)!=1:issues.append({'slot':slot,'reason':'missing_or_conflicting_head','heads':matches});continue
  h=matches[0]
  if p['records'][h]['disposition']=='retraction':issues.append({'slot':slot,'reason':'retracted','head':h});continue
  if not all(a in live for a in p['ancestry'][h]):issues.append({'slot':slot,'reason':'ancestor_unavailable','head':h});continue
  chosen[slot]=h
 if issues:return {'status':'unresolved','issues':issues}
 return {'status':'selected_conditional','heads':chosen,'scenario':{**p['records'][chosen['financial_family']]['payload'],**p['records'][chosen['observation_scheme']]['payload']}}

def verify(b,expected_checkpoint,expected_input,m,expected_limit=4096):
 need(isinstance(expected_checkpoint,str) and identity(b)==expected_checkpoint,'external_checkpoint_identity')
 t.fields(b,['profile',*t.FLAGS,'input','input_sha256','prepared_sha256','method_identity','limit','tree','resolved','pending','outcomes','supports','complete','status'],'checkpoint_fields')
 need(b['profile']=='ResumableTemporalFrontier/1' and all(b[k] is False for k in t.FLAGS),'profile_and_nonadmission')
 need(type(expected_limit) is int and 1<=expected_limit<=4096 and type(b['limit']) is int and b['limit']==expected_limit,'external_execution_cap')
 need(b['method_identity']==m.identity,'methods')
 p=f.prepared(b['input'],expected_input);need(b['input']['max_nodes']==4096,'original_scope_cap')
 need(b['input_sha256']==expected_input and b['prepared_sha256']==identity(p),'request_and_domain')
 order=sorted(p['records']);resolved=0;pending=[];domains=[];out={};supports=[];seen_pending=False
 def visit(n,edges,i,eligible,path):
  nonlocal resolved,seen_pending
  need(type(n) is dict and type(n.get('path')) is list and all(type(k) is int for k in n['path']) and n['path']==path,'unique_reconstructed_path')
  k=n.get('kind')
  if k=='pending':
   t.fields(n,['kind','path'],'pending_fields');seen_pending=True;pending.append(path);domains.append({'path':path,'domain_sha256':identity(edges)});return
  need(not seen_pending,'dfs_prefix_order');resolved+=1;need(resolved<=expected_limit,'resolved_cap')
  proof_kind=t.pc.verify(p['variables'],edges,n['proof'])
  if proof_kind=='empty':t.fields(n,['kind','path','proof'],'empty_fields');need(k=='empty','empty_kind');return
  if i==len(order):
   t.fields(n,['kind','path','proof','eligible','outcome'],'leaf_fields');need(k=='leaf' and identity(n['eligible'])==identity(eligible),'leaf_eligibility')
   want=selected(p,eligible);need(identity(n['outcome'])==identity(want),'independent_leaf_outcome');key=identity(want);out[key]=want;supports.append({'path':path,'outcome_sha256':key});return
  t.fields(n,['kind','path','proof','record','children'],'expanded_fields');h=order[i];gs=p['guards'][h]
  need(k=='expanded' and n['record']==h and type(n['children']) is list and len(n['children'])==len(gs)+1,'complete_partition_children')
  visit(n['children'][0],edges+gs,i+1,{**eligible,h:True},path+[0])
  for j,g in enumerate(gs):
   opposite={'u':g['v'],'v':g['u'],'bound':str(-Q(g['bound'])),'strict':not g['strict']}
   visit(n['children'][j+1],edges+gs[:j]+[opposite],i+1,{**eligible,h:False},path+[j+1])
 visit(b['tree'],p['constraints'],0,{},[])
 need(type(b['resolved']) is int and b['resolved']==resolved,'exact_resolved_count')
 for name,want in [('pending',pending),('supports',supports),('outcomes',[out[k] for k in sorted(out)])]:need(identity(b[name])==identity(want),'exact_'+name)
 need(type(b['complete']) is bool and b['complete']==(not pending),'completeness')
 status=('capped' if resolved==expected_limit else 'paused') if pending else ('complete_family' if out else 'inconsistent_clocks')
 need(b['status']==status,'exact_status')
 return {'resolved':resolved,'pending_domains':domains,'supports':cp(supports),'outcomes':cp(b['outcomes'])}
