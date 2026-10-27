"""Declare a bounded total-message domain without completed temporal outcomes."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util,json,sys
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'observation-map-binding-20261027'))
import binding as b
identity=b.identity;need=b.need;fields=b.fields
PROFILE='ProspectiveActorPolicyDomain/1'
def pairs(x):
    records=x['registry']
    fs=sorted(k for k,r in records.items() if r.get('slot')=='financial_family' and r['disposition']=='assertion')
    obs=sorted(k for k,r in records.items() if r.get('slot')=='observation_scheme' and r['disposition']=='assertion')
    return [(a,z) for a in fs for z in obs]
def raw_population(x,head,e):
    view=x['registry'][head]['payload']['view'];rows=[]
    for fh,oh in pairs(x):
        if oh!=head:continue
        s=x['registry'][fh]['payload']
        rows += [r for r in e.rows if r['receipt']==s['receipt'] and (s['family']=='mixed' or r['right'])]
    first={b.wirekey(b.observation_keys(r,view)[0]) for r in rows}
    second={b.wirekey(b.observation_keys(r,view)[1]) for r in rows if r['obs2'] is not None}
    return first,second
def map_rows(x,d,e,heads):
    fh,oh=heads;s={**x['registry'][fh]['payload'],**x['registry'][oh]['payload']}
    m=next(m for m in d['maps'] if m['source_head']==oh)
    first={b.wirekey(z['key']):z['token'] for z in m['first']};second={b.wirekey(z['key']):z['token'] for z in m['second']}
    rows=[]
    for r in e.rows:
        if r['receipt']!=s['receipt'] or s['family']!='mixed' and not r['right']:continue
        a,z=b.observation_keys(r,s['view'])
        rows.append(dict(id=fh+'/'+oh+'/'+r['row_id'],support=r['row_id'],mechanism='hidden',a1=r['a1'],a2=r['a2'],
          message1=b.wirekey([first[b.wirekey(a)],None]),message2=None if z is None else [second[b.wirekey(z)],''],status=r['status']))
    return rows
def keys(rows):
    first={b.policy.keys(r,'never')[0] for r in rows};second={b.policy.keys(r,'never')[1] for r in rows if r['message2'] is not None}
    return [('first',k) for k in sorted(first,key=repr)]+[('second',k) for k in sorted(second,key=repr)]
def derive(x,expected_input,d,expected_declaration,e):
    # Preparation checks raw registry/clocks only; no enumerate_views call here.
    b.f.prepared(x,expected_input)
    need(identity(d)==expected_declaration,'external_declaration_identity')
    fields(d,['profile','input_sha256','actor','first_at','second_at','actions','maps','max_policy_keys'],'declaration_fields')
    need(d['profile']=='ProspectiveActorObservationMap/1' and d['input_sha256']==expected_input,'input_binding')
    need(d['actor']==x['request']['actor'],'actor_binding')
    need(b.f.t.instant(d['first_at'])==b.f.t.instant(x['request']['decision_at']) and b.f.t.instant(d['first_at'])<b.f.t.instant(d['second_at']),'decision_dates')
    need(d['actions']==b.ACTIONS,'action_meanings');need(type(d['max_policy_keys']) is int and 1<=d['max_policy_keys']<=12,'key_bound')
    heads={k for k,r in x['registry'].items() if r.get('slot')=='observation_scheme' and r['disposition']=='assertion'}
    need(type(d['maps']) is list,'maps_list');seen=set()
    for m in d['maps']:
        fields(m,['source_head','source_sha256','first','second','tag'],'map_fields');head=m['source_head']
        need(head in heads and head not in seen,'unique_original_observation_head');seen.add(head)
        need(m['source_sha256']==x['registry'][head]['source_sha256'],'source_binding')
        need(m['tag']=={'reveal':'never'},'no_tag_profile')
        one,two=raw_population(x,head,e);b.table(m['first'],one,'first');b.table(m['second'],two,'second')
    need(seen==heads,'all_original_observation_heads')
    rows=[];supports=[]
    for pair in pairs(x):
        rows+=map_rows(x,d,e,pair);supports.append(list(pair))
    policy_keys=keys(rows)
    out=dict(profile=PROFILE,**b.FLAGS,input_sha256=expected_input,declaration_sha256=expected_declaration,
      declaration=cp(d),source_head_pairs=supports,evidence_identity=e.audit_identity,
      question_scope='conservative_original_registry_no_completed_outcomes',candidate_feasibility='not_assessed')
    if not policy_keys:return dict(out,status='unresolved_no_assertion_domain',keys=None,required_keys=0,request=cp(x))
    if len(policy_keys)>d['max_policy_keys']:return dict(out,status='unresolved_domain_budget',keys=None,required_keys=len(policy_keys),request=cp(x))
    return dict(out,status='conditional_domain',keys=b.canonical(policy_keys),required_keys=len(policy_keys),total_rules=2**len(policy_keys))
