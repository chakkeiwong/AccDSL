"""Retrospective fixed-domain policy restrictions with externally bound source frontiers."""
from pathlib import Path
from copy import deepcopy as cp
from itertools import product
import hashlib,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'temporal-frontier-20261027'));import frontier as z
b=z.t.prior.load('partial_observation_binding',H.parent/'observation-map-binding-20261027/binding.py')
identity=z.identity;need=z.need
PROFILE='FixedDomainPartialPolicy/1'
class Context:
 def __init__(self):self.methods=z.Methods();self.evidence=b.Evidence();self.memo={}
 def bind(self,full,expected):
  need(identity(full)==expected,'external_full_comparison_identity')
  if expected not in self.memo:
   b.verify_previous(full,expected,self.evidence);self.memo[expected]=cp(full)
  need(self.memo[expected]==full,'comparison_payload')

def schema(rows):
 k1=sorted({b.policy.keys(r,'never')[0] for r in rows},key=repr)
 k2=sorted({b.policy.keys(r,'never')[1] for r in rows if r['message2'] is not None},key=repr)
 keys=[('first',k) for k in k1]+[('second',k) for k in k2]
 need(0<len(keys)<=12,'bounded_total_policy_domain');return keys

def prepare(front,expected_front,expected_request,full,expected_full,domain,expected_domain,ctx,limit=4096):
 ctx.bind(full,expected_full);z.c.verify(front,expected_front,expected_request,ctx.methods,limit)
 need(front['input']==full['family']['input'],'same_original_question')
 want={'profile':'DeclaredTotalPayDrawDomain/1','full_comparison_sha256':expected_full,'keys':b.canonical(schema(full['rows'])),'actions':['pay','draw']}
 need(identity(domain)==expected_domain and identity(domain)==identity(want),'externally_declared_fixed_domain')
 known={identity(o) for o in front['outcomes']};available={r['mechanism'] for r in full['rows']}
 need(known<=available,'complete_maps_for_known_outcomes')
 full_supports=full['binding']['temporal_supports']
 need(all(s in full_supports for s in front['supports']),'retained_full_support_relation')
 rows=[r for r in full['rows'] if r['mechanism'] in known]
 return rows,schema(full['rows'])

def restrictions(rows,keys):
 """Direct full-assignment evaluation of finite forbidden decisions."""
 positions={k:i for i,k in enumerate(keys)};forbidden={}
 for r in rows:
  first,second=b.policy.keys(r,'never');i=positions[('first',first)];a=int(r['a1']=='draw')
  if r['status']=='refused1':term=((i,a),)
  elif r['status']=='refused2':term=((i,a),(positions[('second',second)],int(r['a2']=='draw')))
  else:continue
  forbidden.setdefault(term,r['id'])
 survivors=[];rejected=[]
 for choices in product((0,1),repeat=len(keys)):
  witness=next((rid for term,rid in forbidden.items() if all(choices[i]==a for i,a in term)),None)
  if witness is None:survivors.append(list(choices))
  else:rejected.append({'policy':list(choices),'row':witness})
 return survivors,rejected

def extension_set(reachable,keys):
 """Independent total extensions of the prior reachable-policy oracle."""
 result=set()
 for p,q in reachable:
  supplied={('first',k):int(a=='draw') for k,a in p};supplied.update({('second',k):int(a=='draw') for k,a in q})
  missing=[i for i,k in enumerate(keys) if k not in supplied]
  for values in product((0,1),repeat=len(missing)):
   row=[supplied.get(k) for k in keys]
   for i,a in zip(missing,values):row[i]=a
   result.add(tuple(row))
 return result

def oracle(rows,keys):
 if not rows:return set(product((0,1),repeat=len(keys)))
 reachable,_=b.oracle.solve(rows,('pay','draw'),('pay','draw'),'never')
 return extension_set(reachable,keys)

def status(front,candidates):
 if not candidates:return 'conditionally_infeasible'
 if not front['complete']:return 'unresolved_pending'
 if front['status']=='inconsistent_clocks':return 'inconsistent_clocks'
 return 'conditionally_feasible'

def evaluate(front,expected_front,expected_request,full,expected_full,domain,expected_domain,ctx,limit=4096):
 rows,keys=prepare(front,expected_front,expected_request,full,expected_full,domain,expected_domain,ctx,limit)
 candidates,rejected=restrictions(rows,keys)
 need({tuple(p) for p in candidates}==oracle(rows,keys),'full_independent_candidate_sets')
 return {'profile':PROFILE,**b.FLAGS,'frontier_sha256':expected_front,'request_sha256':expected_request,'full_comparison_sha256':expected_full,'domain_sha256':expected_domain,'status':status(front,candidates),'candidates':candidates,'rejections':rejected,'known_supports':cp(front['supports']),'pending':cp(front['pending']),'pending_domains':z.c.verify(front,expected_front,expected_request,ctx.methods,limit)['pending_domains'],'complete':front['complete'],'known_row_ids':[r['id'] for r in rows],'total_policy_keys':len(keys),'scope':'retrospective_declared_domain_conditional_comparison'}

def verify(result,expected_result,front,expected_front,expected_request,full,expected_full,domain,expected_domain,ctx,limit=4096):
 need(identity(result)==expected_result,'external_result_identity')
 rows,keys=prepare(front,expected_front,expected_request,full,expected_full,domain,expected_domain,ctx,limit)
 z.t.fields(result,['profile',*b.FLAGS,'frontier_sha256','request_sha256','full_comparison_sha256','domain_sha256','status','candidates','rejections','known_supports','pending','pending_domains','complete','known_row_ids','total_policy_keys','scope'],'result_fields')
 need(result['profile']==PROFILE and all(result[k] is False for k in b.FLAGS),'profile_noadmission')
 need(result['frontier_sha256']==expected_front and result['request_sha256']==expected_request and result['full_comparison_sha256']==expected_full and result['domain_sha256']==expected_domain,'external_bindings')
 expected=oracle(rows,keys);need(identity(result['candidates'])==identity([list(v) for v in sorted(expected)]),'full_candidate_population')
 rejected=result['rejections'];need(type(rejected) is list,'rejection_list');byid={r['id']:r for r in rows};seen=set()
 for item in rejected:
  z.t.fields(item,['policy','row'],'rejection_fields');p=item['policy'];need(type(p) is list and len(p)==len(keys) and all(type(v) is int and v in [0,1] for v in p),'total_policy_type');p=tuple(p);need(p not in seen and p not in expected,'unique_rejection');seen.add(p)
  r=byid[item['row']];first,second=b.policy.keys(r,'never');assigned=dict(zip(keys,p));need(assigned[('first',first)]==int(r['a1']=='draw'),'first_witness')
  need(r['status']=='refused1' or r['status']=='refused2' and assigned[('second',second)]==int(r['a2']=='draw'),'refused_row_witness')
 need(len(seen)+len(expected)==2**len(keys),'full_universe_coverage')
 for k,want in [('known_supports',front['supports']),('pending',front['pending']),('complete',front['complete']),('known_row_ids',[r['id'] for r in rows]),('total_policy_keys',len(keys)),('pending_domains',z.c.verify(front,expected_front,expected_request,ctx.methods,limit)['pending_domains'])]:need(identity(result[k])==identity(want),'retained_'+k)
 want='conditionally_infeasible' if not expected else 'unresolved_pending' if front['pending'] else 'inconsistent_clocks' if front['status']=='inconsistent_clocks' else 'conditionally_feasible'
 need(result['status']==want and result['scope']=='retrospective_declared_domain_conditional_comparison','exact_conclusion_scope')
 return True
