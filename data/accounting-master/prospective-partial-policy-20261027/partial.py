"""Prospective finite policies from original declarations and verified frontiers."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
import importlib.util,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'prospective-policy-domain-20261027'))
import domain as d
p=d.b.f.t.prior.load('prospective_partial_predecessor',H.parent/'partial-frontier-policy-20261027/partial.py')
z=p.z;identity=d.identity;need=d.need;PROFILE='ProspectivePartialPolicy/1'
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x
class Context:
 def __init__(self):
  self.methods=z.Methods();self.evidence=d.b.Evidence()
  self.method_identity=identity({'partial':sha256(Path(__file__).read_bytes()).hexdigest(),
   'domain':sha256((d.H/'domain.py').read_bytes()).hexdigest(),'frontier':self.methods.identity,
   'observation':self.evidence.binding_method_identity,'restrictions':sha256(Path(p.__file__).read_bytes()).hexdigest()})

def prepare(front,front_id,input_id,declaration,declaration_id,domain,domain_id,ctx,limit):
 proof=z.c.verify(front,front_id,input_id,ctx.methods,limit)
 need(identity(domain)==domain_id,'external_domain_identity')
 expected=d.derive(front['input'],input_id,declaration,declaration_id,ctx.evidence)
 need(identity(domain)==identity(expected),'exact_prospective_domain')
 rows=[];unknown=[]
 for outcome in proof['outcomes']:
  if outcome['status']!='selected_conditional':unknown.append(cp(outcome));continue
  heads=outcome['heads'];rows+=d.map_rows(front['input'],declaration,ctx.evidence,(heads['financial_family'],heads['observation_scheme']))
 keys=None if domain['keys'] is None else [tuples(k) for k in domain['keys']]
 if keys is not None:need(set(d.keys(rows))<=set(keys),'all_known_keys_covered')
 return proof,rows,keys,unknown

def conclusion(front,domain,candidates,unknown):
 if front['status']=='inconsistent_clocks':return 'inconsistent_clocks'
 if domain['status']!='conditional_domain':return domain['status']
 if unknown:return 'unresolved_source_family'
 if not candidates:return 'conditionally_infeasible'
 if not front['complete']:return 'unresolved_pending'
 return 'conditionally_feasible'

def evaluate(front,front_id,input_id,declaration,declaration_id,domain,domain_id,ctx,limit=4096):
 proof,rows,keys,unknown=prepare(front,front_id,input_id,declaration,declaration_id,domain,domain_id,ctx,limit)
 candidates,rejected=(None,None) if keys is None else p.restrictions(rows,keys)
 return {'profile':PROFILE,**d.b.FLAGS,'method_identity':ctx.method_identity,
  'frontier_sha256':front_id,'input_sha256':input_id,'declaration_sha256':declaration_id,'domain_sha256':domain_id,
  'status':conclusion(front,domain,candidates,unknown),'candidates':candidates,'rejections':rejected,
  'known_constraint_status':'not_assessed' if candidates is None else 'empty' if not candidates else 'nonempty',
  'unknown_outcomes':unknown,'known_supports':cp(proof['supports']),'pending':cp(front['pending']),
  'pending_domains':cp(proof['pending_domains']),'complete':front['complete'],'known_row_ids':[r['id'] for r in rows],
  'total_policy_keys':domain['required_keys'],'original_request':cp(front['input']),
  'scope':'prospective_original_registry_partial_constraints'}

def verify(result,result_id,front,front_id,input_id,declaration,declaration_id,domain,domain_id,ctx,limit=4096):
 need(identity(result)==result_id,'external_result_identity')
 expected_fields=['profile',*d.b.FLAGS,'method_identity','frontier_sha256','input_sha256','declaration_sha256','domain_sha256',
  'status','candidates','rejections','known_constraint_status','unknown_outcomes','known_supports','pending',
  'pending_domains','complete','known_row_ids','total_policy_keys','original_request','scope']
 d.fields(result,expected_fields,'result_fields')
 proof,rows,keys,unknown=prepare(front,front_id,input_id,declaration,declaration_id,domain,domain_id,ctx,limit)
 need(result['profile']==PROFILE and all(result[k] is False for k in d.b.FLAGS),'profile_no_admission')
 need(result['method_identity']==ctx.method_identity,'method_identity')
 for name,want in [('frontier_sha256',front_id),('input_sha256',input_id),('declaration_sha256',declaration_id),('domain_sha256',domain_id),
  ('unknown_outcomes',unknown),('known_supports',proof['supports']),('pending',front['pending']),('pending_domains',proof['pending_domains']),
  ('complete',front['complete']),('known_row_ids',[r['id'] for r in rows]),('total_policy_keys',domain['required_keys']),
  ('original_request',front['input']),('scope','prospective_original_registry_partial_constraints')]:
  need(identity(result[name])==identity(want),'retained_'+name)
 if keys is None:
  want=None;need(result['candidates'] is None and result['rejections'] is None,'no_budget_population')
 else:
  want=p.oracle(rows,keys);candidates=result['candidates'];rejected=result['rejections']
  need(type(candidates) is list and all(type(c) is list and len(c)==len(keys) and all(type(v) is int and v in [0,1] for v in c) for c in candidates),'candidate_types')
  need(identity(candidates)==identity([list(c) for c in sorted(want)]),'independent_complete_candidate_set')
  need(type(rejected) is list,'rejections_list');seen=set();byid={r['id']:r for r in rows}
  for item in rejected:
   d.fields(item,['policy','row'],'rejection_fields');bits=item['policy']
   need(type(bits) is list and len(bits)==len(keys) and all(type(v) is int and v in [0,1] for v in bits),'rejection_types')
   rule=tuple(bits);need(rule not in seen and rule not in want,'unique_rejected_rule');seen.add(rule)
   row=byid[item['row']];one,two=d.b.policy.keys(row,'never');assigned=dict(zip(keys,bits))
   need(assigned[('first',one)]==int(row['a1']=='draw'),'first_refusal_witness')
   need(row['status']=='refused1' or row['status']=='refused2' and assigned[('second',two)]==int(row['a2']=='draw'),'refusal_witness')
  need(len(seen)+len(want)==2**len(keys),'full_rule_partition')
 known='not_assessed' if want is None else 'empty' if not want else 'nonempty'
 need(result['known_constraint_status']==known,'known_constraint_status')
 status='inconsistent_clocks' if front['status']=='inconsistent_clocks' else domain['status'] if keys is None else 'unresolved_source_family' if unknown else 'conditionally_infeasible' if not want else 'unresolved_pending' if front['pending'] else 'conditionally_feasible'
 need(result['status']==status,'independent_status')
 return True
