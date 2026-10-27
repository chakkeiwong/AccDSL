"""Exact global message renaming; no observation-partition extension claim."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
import importlib.util
H=Path(__file__).resolve().parent;R=H.parents[2]
s=importlib.util.spec_from_file_location('transport_partial',H.parent/'prospective-partial-policy-20261027/partial.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
d=p.d;identity=d.identity;need=d.need;PROFILE='ProspectivePolicyRenaming/1'
def relation(x,input_id,old,old_id,new,new_id,e):
 one=d.derive(x,input_id,old,old_id,e);two=d.derive(x,input_id,new,new_id,e)
 need(one['status']==two['status']=='conditional_domain','bounded_domains_required')
 need(identity({k:v for k,v in old.items() if k!='maps'})==identity({k:v for k,v in new.items() if k!='maps'}),'same_declared_question_except_tokens')
 om={z['source_head']:z for z in old['maps']};nm={z['source_head']:z for z in new['maps']};tokens={}
 for stage in ['first','second']:
  mapping={};inverse={}
  for head,a in om.items():
   b=nm[head];av={d.b.wirekey(z['key']):z['token'] for z in a[stage]};bv={d.b.wirekey(z['key']):z['token'] for z in b[stage]}
   need(av.keys()==bv.keys(),'same_raw_keys')
   for raw,token in av.items():
    nt=bv[raw];need(token not in mapping or mapping[token]==nt,'no_label_split');need(nt not in inverse or inverse[nt]==token,'no_label_merge');mapping[token]=nt;inverse[nt]=token
  tokens[stage]=sorted(mapping.items())
 oldkeys=[p.tuples(k) for k in one['keys']];newkeys=[p.tuples(k) for k in two['keys']];mapping={};inverse={};rowpairs=[]
 for pair in d.pairs(x):
  a=d.map_rows(x,old,e,pair);b=d.map_rows(x,new,e,pair);need(len(a)==len(b),'same_rows')
  for ar,br in zip(a,b):
   need(all(ar[k]==br[k] for k in ['id','support','a1','a2','status']),'row_action_and_refusal_meaning')
   ak=d.b.policy.keys(ar,'never');bk=d.b.policy.keys(br,'never')
   stages=[('first',ak[0],bk[0])]+([] if ar['message2'] is None else [('second',ak[1],bk[1])])
   for stage,ok,nk in stages:
    ok=(stage,ok);nk=(stage,nk)
    need(ok not in mapping or mapping[ok]==nk,'functional_key_mapping');need(nk not in inverse or inverse[nk]==ok,'injective_key_mapping')
    mapping[ok]=nk;inverse[nk]=ok
   rowpairs.append([ar['id'],br['id']])
 need(set(mapping)==set(oldkeys) and set(inverse)==set(newkeys),'full_generated_key_bijection')
 return {'profile':PROFILE,**d.b.FLAGS,'input_sha256':input_id,'old_declaration_sha256':old_id,'new_declaration_sha256':new_id,
  'old_domain':one,'new_domain':two,'token_bijections':d.b.canonical(tokens),
  'old_to_new_positions':[newkeys.index(mapping[k]) for k in oldkeys],'row_pairs':rowpairs,'scope':'exact_global_message_renaming'}

def terms(rows,keys):
 positions={k:i for i,k in enumerate(keys)};out=set()
 for r in rows:
  one,two=d.b.policy.keys(r,'never')
  if r['status']=='refused1':term=((positions[('first',one)],int(r['a1']=='draw')),)
  elif r['status']=='refused2':term=((positions[('first',one)],int(r['a1']=='draw')),(positions[('second',two)],int(r['a2']=='draw')))
  else:continue
  out.add(tuple(sorted(term)))
 return out

def evaluate(front,front_id,input_id,old,old_id,new,new_id,old_result,old_result_id,ctx,limit=4096):
 rel=relation(front['input'],input_id,old,old_id,new,new_id,ctx.evidence);od=rel['old_domain'];nd=rel['new_domain']
 p.verify(old_result,old_result_id,front,front_id,input_id,old,old_id,od,identity(od),ctx,limit)
 current=p.evaluate(front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 p.verify(current,identity(current),front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 _,a,ak,_=p.prepare(front,front_id,input_id,old,old_id,od,identity(od),ctx,limit)
 _,b,bk,_=p.prepare(front,front_id,input_id,new,new_id,nd,identity(nd),ctx,limit)
 permutation=rel['old_to_new_positions'];ta=terms(a,ak);tb=terms(b,bk)
 need({tuple(sorted((permutation[i],bit) for i,bit in t)) for t in ta}==tb,'exact_forbidden_assignment_transport')
 moved=[]
 for rule in old_result['candidates']:
  out=[None]*len(permutation)
  for i,j in enumerate(permutation):out[j]=rule[i]
  moved.append(out)
 moved.sort();need(identity(moved)==identity(current['candidates']),'exact_candidate_permutation')
 for k in ['status','known_constraint_status','unknown_outcomes','known_supports','pending','pending_domains','complete','original_request']:
  need(identity(old_result[k])==identity(current[k]),'preserved_'+k)
 return {'profile':PROFILE,**d.b.FLAGS,'relation':rel,'relation_sha256':identity(rel),'old_result_sha256':old_result_id,
  'new_result':current,'new_result_sha256':identity(current),'transported_candidates':moved,
  'unary_constraints':sum(len(t)==1 for t in ta),'binary_constraints':sum(len(t)==2 for t in ta),
  'method_identity':identity({'transport.py':sha256(Path(__file__).read_bytes()).hexdigest(),'partial':ctx.method_identity}),
  'decision':'exact_finite_renaming_verified','extension_claim':False}

