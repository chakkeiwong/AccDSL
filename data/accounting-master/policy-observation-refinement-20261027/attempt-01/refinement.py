"""Finite message refinement with exact erasure/lift and reached-row comparison."""
from pathlib import Path
from hashlib import sha256
import importlib.util
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('refinement_transport',H.parent/'policy-domain-transport-20261027/transport.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
p=r.p;d=r.d;identity=d.identity;need=d.need;PROFILE='ProspectiveObservationRefinement/1'
def relation(x,input_id,old,old_id,new,new_id,e):
 od=d.derive(x,input_id,old,old_id,e);nd=d.derive(x,input_id,new,new_id,e)
 need(od['status']==nd['status']=='conditional_domain','bounded_domains_required')
 need(identity({k:v for k,v in old.items() if k!='maps'})==identity({k:v for k,v in new.items() if k!='maps'}),'same_question_except_tokens')
 om={z['source_head']:z for z in old['maps']};nm={z['source_head']:z for z in new['maps']};erasures={}
 for stage in ['first','second']:
  erase={};oldtokens=set()
  for head,a in om.items():
   av={d.b.wirekey(v['key']):v['token'] for v in a[stage]};bv={d.b.wirekey(v['key']):v['token'] for v in nm[head][stage]}
   need(av.keys()==bv.keys(),'same_raw_observations')
   for raw,ot in av.items():
    nt=bv[raw];need(nt not in erase or erase[nt]==ot,'functional_message_erasure');erase[nt]=ot;oldtokens.add(ot)
  need(set(erase.values())==oldtokens,'surjective_message_erasure');erasures[stage]=sorted(erase.items())
 ok=[p.tuples(k) for k in od['keys']];nk=[p.tuples(k) for k in nd['keys']];keyerase={}
 for pair in d.pairs(x):
  aa=d.map_rows(x,old,e,pair);bb=d.map_rows(x,new,e,pair);need(len(aa)==len(bb),'same_action_rows')
  for a,b in zip(aa,bb):
   need(all(a[k]==b[k] for k in ['id','support','a1','a2','status']),'same_refusal_meaning')
   ka=d.b.policy.keys(a,'never');kb=d.b.policy.keys(b,'never')
   stages=[('first',ka[0],kb[0])]+([] if a['message2'] is None else [('second',ka[1],kb[1])])
   for stage,ak,bk in stages:
    ak=(stage,ak);bk=(stage,bk);need(bk not in keyerase or keyerase[bk]==ak,'functional_policy_key_erasure');keyerase[bk]=ak
 need(set(keyerase)==set(nk) and set(keyerase.values())==set(ok),'full_surjective_policy_key_erasure')
 return {'profile':PROFILE,**d.b.FLAGS,'input_sha256':input_id,'old_declaration_sha256':old_id,'new_declaration_sha256':new_id,
  'old_domain':od,'new_domain':nd,'message_erasures':d.b.canonical(erasures),'new_to_old_positions':[ok.index(keyerase[k]) for k in nk],
  'scope':'same_original_input_declared_message_refinement'}

def reached(rule,keys,rows):
 assigned=dict(zip(keys,rule));out=set()
 for row in rows:
  one,two=d.b.policy.keys(row,'never')
  if assigned[('first',one)]!=int(row['a1']=='draw'):continue
  if row['message2'] is not None and assigned[('second',two)]!=int(row['a2']=='draw'):continue
  out.add(row['id'])
 return tuple(sorted(out))

def evaluate(front,front_id,input_id,old,old_id,new,new_id,ctx,limit=4096):
 rel=relation(front['input'],input_id,old,old_id,new,new_id,ctx.evidence);od=rel['old_domain'];nd=rel['new_domain']
 a=p.evaluate(front,front_id,input_id,old,old_id,od,identity(od),ctx,limit);b=p.evaluate(front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 p.verify(a,identity(a),front,front_id,input_id,old,old_id,od,identity(od),ctx,limit);p.verify(b,identity(b),front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 _,ar,ak,_=p.prepare(front,front_id,input_id,old,old_id,od,identity(od),ctx,limit);_,br,bk,_=p.prepare(front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 er=rel['new_to_old_positions'];oldterms=r.terms(ar,ak);newterms=r.terms(br,bk)
 erased={tuple(sorted(set((er[i],bit) for i,bit in term))) for term in newterms};need(erased==oldterms,'exact_erased_forbidden_constraints')
 lifts={tuple(rule[i] for i in er) for rule in a['candidates']};newrules={tuple(rule) for rule in b['candidates']}
 constant=set()
 for rule in newrules:
  fibers={};valid=True
  for i,oldpos in enumerate(er):
   if oldpos in fibers and fibers[oldpos]!=rule[i]:valid=False;break
   fibers[oldpos]=rule[i]
  if valid:constant.add(rule)
 need(lifts==constant,'constant_fiber_candidates_equal_lifts');need(lifts<=newrules,'old_feasible_rules_preserved')
 oldtraces={reached(rule,ak,ar) for rule in a['candidates']};lifttraces={reached(rule,bk,br) for rule in lifts};newtraces={reached(rule,bk,br) for rule in newrules}
 need(oldtraces==lifttraces,'lift_preserves_selected_row_behavior');need(lifttraces<=newtraces,'known_reached_behaviors_preserved')
 for k in ['unknown_outcomes','known_supports','pending','pending_domains','complete','original_request']:need(identity(a[k])==identity(b[k]),'retained_'+k)
 return {'profile':PROFILE,**d.b.FLAGS,'relation':rel,'relation_sha256':identity(rel),'old_result':a,'new_result':b,
  'lifted_candidates':[list(v) for v in sorted(lifts)],'constant_fiber_candidates':[list(v) for v in sorted(constant)],
  'additional_candidates':[list(v) for v in sorted(newrules-lifts)],'old_reached_behaviors':[list(v) for v in sorted(oldtraces)],
  'new_reached_behaviors':[list(v) for v in sorted(newtraces)],'additional_reached_behaviors':[list(v) for v in sorted(newtraces-lifttraces)],
  'behavior_scope':'selected_completed_histories_only' if front['pending'] or b['unknown_outcomes'] else 'complete_selected_family' if front['status']!='inconsistent_clocks' else 'no_admissible_clock_assignment',
  'method_identity':identity({'refinement':sha256(Path(__file__).read_bytes()).hexdigest(),'partial':ctx.method_identity}),
  'decision':'exact_finite_refinement_relation_verified','actual_actor_information_claim':False}

