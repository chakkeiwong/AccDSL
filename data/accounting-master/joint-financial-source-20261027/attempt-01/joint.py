"""Two source decisions share clock variables and chronology; no policy result."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from fractions import Fraction as Q
import sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'prospective-policy-domain-20261027'))
import domain as d
f=d.b.f;t=f.t;identity=t.identity;need=t.need;PROFILE='JointRevisableFinancialSourceViews/1'
check=t.prior.load('joint_independent_head_selector',H.parent/'temporal-frontier-20261027/check.py')
def request(x,second,second_effective):return dict(profile='JointTwoDecisionSourceRequest/1',original=cp(x),second_decision_at=second,second_effective_at=second_effective)
def prepare(x,expected):
 need(identity(x)==expected,'external_joint_request');t.fields(x,['profile','original','second_decision_at','second_effective_at'],'joint_request_fields')
 need(x['profile']=='JointTwoDecisionSourceRequest/1','joint_request_profile')
 old=x['original'];first=f.prepared(old,identity(old));new=cp(old)
 need(t.instant(x['second_decision_at'])>t.instant(old['request']['decision_at']),'ordered_decisions')
 need(t.instant(x['second_effective_at'])>=t.instant(old['request']['effective_at']),'ordered_effective_cutoffs')
 new['request']['decision_at']=x['second_decision_at'];new['request']['effective_at']=x['second_effective_at'];second=f.prepared(new,identity(new))
 for k in ['variables','constraints','records','ancestry','clocks']:need(identity(first[k])==identity(second[k]),'shared_'+k)
 return [first,second],new

def evaluate(x,expected,max_nodes=4096):
 ps,second=prepare(x,expected);need(type(max_nodes) is int and 1<=max_nodes<=4096,'execution_budget');p=ps[0]
 order=[(stage,h) for stage in range(2) for h in sorted(p['records'])];nodes=0;pairs={};supports=[]
 def walk(edges,i,eligible,path):
  nonlocal nodes
  nodes+=1
  if nodes>max_nodes:raise t.Budget('joint_budget')
  proof=t.dc.solve(p['variables'],edges);t.pc.verify(p['variables'],edges,proof)
  if proof['kind']=='empty':return dict(kind='empty',proof=proof)
  if i==len(order):
   outcomes=[t.outcome(ps[k],eligible[k]) for k in range(2)];oid=identity(outcomes);pairs[oid]=outcomes;supports.append(dict(path=path,joint_outcome_sha256=oid))
   return dict(kind='leaf',proof=proof,eligible=cp(eligible),outcomes=outcomes)
  stage,h=order[i];guards=ps[stage]['guards'][h];children=[]
  for k in range(len(guards)+1):
   es=edges+guards if k==0 else edges+guards[:k-1]+[t.dc.opposite(guards[k-1])]
   updated=cp(eligible);updated[stage][h]=k==0;children.append(walk(es,i+1,updated,path+[k]))
  return dict(kind='expanded',proof=proof,stage=stage,record=h,children=children)
 base=dict(profile=PROFILE,**t.FLAGS,input=cp(x),input_sha256=expected,prepared_sha256=identity(ps),max_nodes=max_nodes,
  method_identity=identity({'joint.py':sha256(Path(__file__).read_bytes()).hexdigest(),'temporal.py':sha256(Path(t.__file__).read_bytes()).hexdigest()}),scope='joint_revisable_financial_source_views_no_policy_binding',financial_policy_binding='not_assessed_source_selection_only')
 try:
  tree=walk(p['constraints'],0,[{},{}],[])
  out=dict(base,status='complete_family' if pairs else 'inconsistent_clocks',complete=True,tree=tree,nodes=nodes,outcomes=[pairs[k] for k in sorted(pairs)],supports=supports,remainder=None)
 except t.Budget:
  out=dict(base,status='unresolved_budget',complete=False,tree=None,nodes=max_nodes,outcomes=[],supports=[],remainder=dict(kind='entire_original_clock_domain',request=cp(x),prepared_sha256=identity(ps)))
 return out

def verify(result,expected_result,expected_input):
 need(identity(result)==expected_result,'external_joint_result');ps,_=prepare(result['input'],expected_input);p=ps[0]
 fields=['profile',*t.FLAGS,'input','input_sha256','prepared_sha256','max_nodes','method_identity','scope','financial_policy_binding','status','complete','tree','nodes','outcomes','supports','remainder']
 t.fields(result,fields,'joint_result_fields');need(result['profile']==PROFILE and all(result[k] is False for k in t.FLAGS),'joint_profile_nonadmission')
 need(result['input_sha256']==expected_input and result['prepared_sha256']==identity(ps),'joint_bindings')
 need(result['method_identity']==identity({'joint.py':sha256(Path(__file__).read_bytes()).hexdigest(),'temporal.py':sha256(Path(t.__file__).read_bytes()).hexdigest()}),'joint_methods')
 need(result['scope']=='joint_revisable_financial_source_views_no_policy_binding','joint_scope');need(result['financial_policy_binding']=='not_assessed_source_selection_only','no_policy_binding');limit=result['max_nodes'];need(type(limit) is int and 1<=limit<=4096,'node_limit')
 if result['status']=='unresolved_budget':
  need(result['complete'] is False and result['tree'] is None and result['outcomes']==[] and result['supports']==[],'no_partial_answer')
  need(result['nodes']==limit and result['remainder']==dict(kind='entire_original_clock_domain',request=result['input'],prepared_sha256=identity(ps)),'complete_original_remainder')
  return True
 order=[(stage,h) for stage in range(2) for h in sorted(p['records'])];nodes=0;pairs={};supports=[]
 def visit(node,edges,i,eligible,path):
  nonlocal nodes
  nodes+=1;need(nodes<=limit,'joint_node_cap');kind=t.pc.verify(p['variables'],edges,node['proof'])
  if kind=='empty':t.fields(node,['kind','proof'],'empty_fields');need(node['kind']=='empty','empty_kind');return
  if i==len(order):
   t.fields(node,['kind','proof','eligible','outcomes'],'leaf_fields');need(node['kind']=='leaf' and node['eligible']==eligible,'leaf_eligibility')
   expected=[check.selected(ps[k],eligible[k]) for k in range(2)];need(node['outcomes']==expected,'independent_joint_outcomes');oid=identity(expected);pairs[oid]=expected;supports.append(dict(path=path,joint_outcome_sha256=oid));return
  stage,h=order[i];gs=ps[stage]['guards'][h];t.fields(node,['kind','proof','stage','record','children'],'expanded_fields')
  need(node['kind']=='expanded' and node['stage']==stage and node['record']==h and len(node['children'])==len(gs)+1,'full_joint_partition')
  for k,child in enumerate(node['children']):
   if k==0:es=edges+gs
   else:g=gs[k-1];es=edges+gs[:k-1]+[t.edge(g['v'],g['u'],-Q(g['bound']),not g['strict'])]
   new=cp(eligible);new[stage][h]=k==0;visit(child,es,i+1,new,path+[k])
 visit(result['tree'],p['constraints'],0,[{},{}],[])
 need(result['complete'] is True and result['remainder'] is None,'joint_completeness')
 need(result['nodes']==nodes and result['outcomes']==[pairs[k] for k in sorted(pairs)] and result['supports']==supports,'exact_joint_population')
 need(result['status']==('complete_family' if pairs else 'inconsistent_clocks'),'joint_status');return True

