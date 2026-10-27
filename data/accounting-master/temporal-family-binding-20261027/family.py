"""Exact conditional family transport; every temporal proof support is retained."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];T=H.parent/'source-time-intervals-20261027'
sys.path.insert(0,str(T));import temporal as t
r=t.prior.load('temporal_family_numeric_reuse',H.parent/'source-policy-invalidation-20261027/reuse.py')
identity=t.identity;need=t.need;fields=t.fields
PROFILE='BoundTemporalPolicyFamily/1'
INPUT_KEYS=['profile','request','registry','sources','observations','trusted','max_nodes']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wire(f,max_nodes=4096):
 return {'profile':'TemporalFamilyRequest/1',**{k:cp(f[k]) for k in ['request','registry','sources','observations']},'trusted':sorted(f['trusted']),'max_nodes':max_nodes}

def prepared(x,expected):
 need(isinstance(expected,str) and identity(x)==expected,'external_request_identity');fields(x,INPUT_KEYS,'family_request_fields')
 need(x['profile']=='TemporalFamilyRequest/1','family_request_profile');need(type(x['trusted']) is list and x['trusted']==sorted(set(x['trusted'])),'canonical_trust_set')
 need(type(x['max_nodes']) is int and 1<=x['max_nodes']<=4096,'node_budget')
 return t.prepare(**{k:x[k] for k in ['request','registry','sources','observations']},trusted=frozenset(x['trusted']))

class Evidence(r.Evidence):
 def __init__(self):
  pin=json.loads((T/'attempt-01/source-lock.json').read_text())
  old=json.loads((H.parent/'source-policy-invalidation-20261027/attempt-01/source-lock.json').read_text())
  self.method_files={**old,**pin}
  for n,h in self.method_files.items():need(sha(R/n)==h,'protected_method_or_evidence:'+n)
  P=H.parent/'certified-observation-policy-20261026'
  paths={'rows':P/'attempt-01/rows.json','comparisons':P/'attempt-01/policy-comparisons.json','observations':P/'observations.py','policy':P/'policies.py','constraint':P/'constraint_oracle.py'}
  expected={k:self.method_files[str(p.relative_to(R))] for k,p in paths.items()}
  super().__init__({k:p.read_bytes() for k,p in paths.items()},expected)
  self.method_identity=identity({'family.py':sha(Path(__file__)),'protected_files':self.method_files})

 def numerical(self,s,cold=False):
  chosen=[x for x in self.rows if x['receipt']==s['receipt'] and (s['family']=='mixed' or x['right'])]
  ref=next(z for z in self.comparisons if all(z[k]==s[k] for k in ['receipt','family','view']))
  policy_set=sorted({t.prior.tuples(z) for z in ref['feasible_policies']},key=repr)
  need(len(chosen)==ref['world_rows'] and len(policy_set)==ref['count'],'complete_numerical_reference')
  if cold:
   actual,_=t.prior.policy.enumerate_policies(chosen,s['view']);independent,_=t.prior.independent.solve(chosen,s['view'])
   need(actual==independent==set(policy_set),'full_cold_policy_comparison')
  return {'scenario':cp(s),'policy_set':json.loads(json.dumps(policy_set)),'count':len(policy_set),'row_ids':[z['row_id'] for z in chosen],'policy_meaning':'complete reachable robust policies; no probabilities or optimality'}

 def key(self,s):return identity({'scenario':s,'evidence_identity':self.audit_identity})

def supports(tree):
 """Each nonempty leaf appears exactly once, even when outcomes coincide."""
 out=[]
 def visit(n,path):
  if 'outcome' in n:out.append({'path':path,'outcome_sha256':identity(n['outcome'])})
  for i,c in enumerate(n.get('children',[])):visit(c,path+[i])
 visit(tree,[]);return out

def outcome_entries(result,support,e):
 return [{'outcome':cp(o),'outcome_sha256':identity(o),'supports':[s['path'] for s in support if s['outcome_sha256']==identity(o)],'numerical_key':e.key(o['scenario']) if o['status']=='selected_conditional' else None} for o in result['outcomes']]

def verify(bundle,expected_bundle,expected_input,e):
 need(isinstance(expected_bundle,str) and identity(bundle)==expected_bundle,'external_family_identity')
 fields(bundle,['profile','input','input_sha256','prepared','temporal','supports','outcomes','numerical','reused_keys','cold_keys','evidence_identity','method_identity','temporal_complete','remainder',*t.FLAGS],'family_fields')
 need(bundle['profile']==PROFILE,'family_profile');need(all(bundle[k] is False for k in t.FLAGS),'no_admission')
 need(bundle['evidence_identity']==e.audit_identity and bundle['method_identity']==e.method_identity,'evidence_and_method_binding')
 p=prepared(bundle['input'],expected_input);need(bundle['input_sha256']==expected_input and bundle['prepared']==p,'prepared_original_domain')
 res=bundle['temporal'];need(all(res[k] is False for k in t.FLAGS),'temporal_no_admission')
 if res['status']=='unresolved_budget':
  # The predecessor has no saved partial tree. Recheck the bounded stop; keep all original scope.
  need(res==t.enumerate_views(p,bundle['input']['max_nodes']),'budget_result')
  need(bundle['temporal_complete'] is False and bundle['supports']==[] and bundle['outcomes']==[] and bundle['numerical']=={} and bundle['reused_keys']==[] and bundle['cold_keys']==[],'no_budget_prefix_promotion')
  need(bundle['remainder']=={'kind':'entire_original_clock_domain','prepared_sha256':identity(p),'resumable_frontier':False},'budget_original_domain_remainder')
  return True
 fields(res,[*t.FLAGS,'status','tree','outcomes','nodes','unknown_clocks','certainty'],'temporal_fields')
 out,count=t.verify_tree(p,res['tree']);need(res['outcomes']==out and res['nodes']==count and count<=bundle['input']['max_nodes'],'full_temporal_population')
 need(res['status']==('complete_family' if out else 'inconsistent_clocks'),'temporal_status')
 need(res['unknown_clocks']==sorted(k for k,v in p['clocks'].items() if v['unknown']),'unknown_clocks_retained')
 need(res['certainty']==('one_view' if len(out)==1 else 'multiple_views' if out else 'no_admissible_clock_assignment'),'temporal_certainty')
 expected_supports=supports(res['tree']);need(bundle['supports']==expected_supports,'exact_leaf_supports')
 want=outcome_entries(res,expected_supports,e);need(bundle['outcomes']==want,'full_outcome_support_binding')
 need(bundle['temporal_complete'] is True and bundle['remainder'] is None,'complete_family_scope')
 scenarios={e.key(o['scenario']):o['scenario'] for o in out if o['status']=='selected_conditional'}
 need(set(bundle['numerical'])==set(scenarios),'exact_numerical_population')
 for key,s in scenarios.items():need(bundle['numerical'][key]==e.numerical(s),'complete_policy_and_rows')
 reuse,cold=bundle['reused_keys'],bundle['cold_keys']
 need(reuse==sorted(set(reuse)) and cold==sorted(set(cold)) and not set(reuse)&set(cold) and set(reuse)|set(cold)==set(scenarios),'exact_computation_partition')
 return True

def evaluate(x,expected_input,e,previous=None,expected_prior=None):
 p=prepared(x,expected_input)
 if previous is not None:verify(previous,expected_prior,previous['input_sha256'],e)
 res=t.enumerate_views(p,x['max_nodes']);complete=res['status']!='unresolved_budget'
 support=supports(res['tree']) if complete else []
 out=outcome_entries(res,support,e) if complete else []
 numerical={};reused=[];cold=[]
 for item in out:
  key=item['numerical_key']
  if key is None or key in numerical:continue
  s=item['outcome']['scenario']
  if previous is not None and key in previous['numerical']:
   numerical[key]=cp(previous['numerical'][key]);reused.append(key)
  else:numerical[key]=e.numerical(s,cold=True);cold.append(key)
 result={'profile':PROFILE,**t.FLAGS,'input':cp(x),'input_sha256':expected_input,'prepared':p,'temporal':res,'supports':support,'outcomes':out,'numerical':numerical,'reused_keys':sorted(reused),'cold_keys':sorted(cold),'evidence_identity':e.audit_identity,'method_identity':e.method_identity,'temporal_complete':complete,'remainder':None if complete else {'kind':'entire_original_clock_domain','prepared_sha256':identity(p),'resumable_frontier':False}}
 verify(result,identity(result),expected_input,e);return result

def semantic(bundle):return {k:v for k,v in bundle.items() if k not in ('reused_keys','cold_keys')}
