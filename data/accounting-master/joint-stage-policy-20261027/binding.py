"""Policy messages bind each stage's source head without leaking head identities."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util,itertools
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('joint_stage_source',H.parent/'two-decision-source-views-20261027/joint.py');j=importlib.util.module_from_spec(s);s.loader.exec_module(j)
d=j.d;b=d.b;identity=d.identity;need=d.need
p=j.t.prior.load('joint_stage_partial',H.parent/'partial-frontier-policy-20261027/partial.py')
def rows(x,decl,e,heads):
 fh,h1,h2=heads;records=x['original']['registry'];fin=records[fh]['payload'];maps={v['source_head']:v for v in decl['mapping']['maps']}
 a={b.wirekey(z['key']):z['token'] for z in maps[h1]['first']};c={b.wirekey(z['key']):z['token'] for z in maps[h2]['second']};out=[]
 for r in e.rows:
  if r['receipt']!=fin['receipt'] or fin['family']!='mixed' and not r['right']:continue
  one=b.observation_keys(r,records[h1]['payload']['view'])[0];two=b.observation_keys(r,records[h2]['payload']['view'])[1]
  out.append(dict(id='/'.join(heads)+'/'+r['row_id'],support=r['row_id'],mechanism='hidden',a1=r['a1'],a2=r['a2'],message1=b.wirekey([a[b.wirekey(one)],None]),message2=None if two is None else [c[b.wirekey(two)],''],status=r['status']))
 return out

def derive(x,input_id,decl,decl_id,e):
 j.prepare(x,input_id);need(identity(decl)==decl_id,'external_declaration');d.fields(decl,['profile','joint_request_sha256','mapping'],'joint_map_fields')
 need(decl['profile']=='JointStageObservationMap/1' and decl['joint_request_sha256']==input_id,'joint_map_binding')
 mapping=decl['mapping'];need(j.t.instant(mapping['second_at'])==j.t.instant(x['second_decision_at']),'exact_second_date')
 d.derive(x['original'],identity(x['original']),mapping,identity(mapping),e)
 registry=x['original']['registry'];financial=[h for h,r in registry.items() if r.get('slot')=='financial_family' and r['disposition']=='assertion'];obs=[h for h,r in registry.items() if r.get('slot')=='observation_scheme' and r['disposition']=='assertion']
 triples=sorted(itertools.product(financial,obs,obs));allrows=[]
 for triple in triples:allrows+=rows(x,decl,e,triple)
 keys=d.keys(allrows);base=dict(profile='JointStageMessageDomain/1',**b.FLAGS,input_sha256=input_id,declaration_sha256=decl_id,source_head_triples=b.canonical(triples),required_keys=len(keys),candidate_feasibility='not_assessed')
 if not keys or len(keys)>mapping['max_policy_keys']:return dict(base,status='unresolved_domain_budget',keys=None,request=cp(x))
 return dict(base,status='conditional_domain',keys=b.canonical(keys),total_rules=2**len(keys))

def evaluate(x,input_id,decl,decl_id,domain,domain_id,family,family_id,e):
 expected=derive(x,input_id,decl,decl_id,e);need(identity(domain)==domain_id==identity(expected),'exact_joint_domain')
 j.verify(family,family_id,input_id);need(family['input']==x,'same_joint_input');known=[];unknown=[]
 for pair in family['outcomes']:
  if any(o['status']!='selected_conditional' for o in pair):unknown.append(cp(pair));continue
  need(pair[0]['heads']['financial_family']==pair[1]['heads']['financial_family'],'fixed_financial_view')
  known+=rows(x,decl,e,(pair[0]['heads']['financial_family'],pair[0]['heads']['observation_scheme'],pair[1]['heads']['observation_scheme']))
 keys=None if domain['keys'] is None else [j.t.prior.tuples(v) for v in domain['keys']]
 if keys is None:candidates=rejected=None;status='unresolved_domain_budget'
 elif family['status']=='unresolved_budget':candidates=rejected=None;status='unresolved_timing_budget'
 elif family['status']=='inconsistent_clocks':candidates=rejected=None;status='inconsistent_clocks'
 else:
  need(set(d.keys(known))<=set(keys),'selected_joint_keys_covered');candidates,rejected=p.restrictions(known,keys)
  need({tuple(v) for v in candidates}==p.oracle(known,keys),'independent_joint_policies')
  status='unresolved_source_family' if unknown else 'conditionally_feasible' if candidates else 'conditionally_infeasible'
 return dict(profile='JointStagePolicy/1',**b.FLAGS,input_sha256=input_id,declaration_sha256=decl_id,domain_sha256=domain_id,family_sha256=family_id,
  status=status,rows=known,candidates=candidates,rejections=rejected,unknown_outcomes=unknown,source_supports=cp(family['supports']),temporal_remainder=cp(family['remainder']),
  original_request=cp(x),scope='complete_joint_source_family_stage_specific_messages')

