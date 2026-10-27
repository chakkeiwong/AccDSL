"""Dated messages across explicit source/history hypotheses; no hidden world tag."""
from pathlib import Path
from copy import deepcopy as cp
from itertools import product
import importlib.util

H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('actor_world_binding',H.parent/'financial-source-world-binding-20261027/binding.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
j=w.j;d=j.d;b=d.b;identity=j.identity;need=j.need
fx=j.t.prior.load('actor_original_maps',H.parent/'prospective-policy-domain-20261027/fixtures.py')
p=j.t.prior.load('actor_rule_restrictions',H.parent/'partial-frontier-policy-20261027/partial.py')

def references(contexts):
    return [{k:identity(c[k]) for k in ('family','world','mapping')} for c in contexts]

def declaration(contexts,mode,bound=12):
    return dict(profile='RevisedSourceActorMessages/1',contexts=references(contexts),mode=mode,
                max_policy_keys=bound,provenance='supplied_synthetic_observation_assumption')

def prepare(contexts,decl,did,e):
    need(identity(decl)==did,'external_declaration')
    j.t.fields(decl,['profile','contexts','mode','max_policy_keys','provenance'],'actor_declaration_fields')
    need(decl['profile']=='RevisedSourceActorMessages/1' and decl['contexts']==references(contexts),'context_identity')
    need(decl['mode'] in ('numeric','numeric_and_reported_receipt'),'message_mode')
    need(decl['provenance']=='supplied_synthetic_observation_assumption','synthetic_observations')
    need(type(decl['max_policy_keys']) is int and 1<=decl['max_policy_keys']<=12,'bounded_keys')
    need(0<len(contexts)<=8 and len({identity(c) for c in contexts})==len(contexts),'distinct_bounded_contexts')
    summaries=[];signature=None
    for c in contexts:
        j.t.fields(c,['family','world','mapping'],'context_fields')
        f=c['family'];x=f['input'];xid=identity(x);mapping=c['mapping']
        value=w.evaluate(f,identity(f),xid,c['world'],identity(c['world']),e)
        d.derive(x['original'],identity(x['original']),mapping,identity(mapping),e)
        need(mapping==fx.declaration(x['original'],e),'protected_original_numeric_mapping')
        one=(mapping['actor'],mapping['first_at'],mapping['second_at'],identity(mapping['actions']))
        need(signature is None or signature==one,'shared_actor_dates_actions');signature=one
        need(j.t.instant(mapping['second_at'])==j.t.instant(x['second_decision_at']),'exact_second_date')
        summaries.append(dict(context_sha256=identity(c),world_binding=value))
    return summaries

def rows(context,mode,e,heads):
    f1,f2,o1,o2=heads;registry=context['family']['input']['original']['registry']
    world=context['world']['world'];maps={z['source_head']:z for z in context['mapping']['maps']}
    tables=[{b.wirekey(v['key']):v['token'] for v in maps[oh][stage]} for oh,stage in ((o1,'first'),(o2,'second'))]
    result=[];prefix=identity(context)+'/'+'/'.join(heads)+'/'
    for r in e.rows:
        if r['receipt']!=world['receipt'] or world['family']!='mixed' and not r['right']:continue
        raw1=b.observation_keys(r,registry[o1]['payload']['view'])[0]
        raw2=b.observation_keys(r,registry[o2]['payload']['view'])[1]
        one=tables[0][b.wirekey(raw1)];two=None if raw2 is None else tables[1][b.wirekey(raw2)]
        if mode=='numeric_and_reported_receipt':
            one=b.wirekey([one,registry[f1]['payload']['receipt']])
            if two is not None:two=b.wirekey([two,registry[f2]['payload']['receipt']])
        result.append(dict(id=prefix+r['row_id'],support=r['row_id'],
                           mechanism='hidden',a1=r['a1'],a2=r['a2'],message1=b.wirekey([one,None]),
                           message2=None if two is None else [two,''],status=r['status']))
    return result

def prospective(contexts,mode,e):
    allrows=[]
    for c in contexts:
        if c['world']['world'] is None:continue
        registry=c['family']['input']['original']['registry']
        fs=sorted(h for h,r in registry.items() if r['slot']=='financial_family' and r['disposition']=='assertion')
        obs=sorted(h for h,r in registry.items() if r['slot']=='observation_scheme' and r['disposition']=='assertion')
        for heads in product(fs,fs,obs,obs):allrows.extend(rows(c,mode,e,heads))
    return d.keys(allrows)

def evaluate(contexts,decl,did,e):
    summaries=prepare(contexts,decl,did,e);keys=prospective(contexts,decl['mode'],e)
    known=[];unresolved=[]
    for c,summary in zip(contexts,summaries):
        if summary['world_binding']['status']!='conditional_fixed_world':
            unresolved.append(summary['context_sha256']);continue
        for pair in c['family']['outcomes']:
            heads=tuple(v['heads']['financial_family'] for v in pair)+tuple(v['heads']['observation_scheme'] for v in pair)
            known.extend(rows(c,decl['mode'],e,heads))
    need(set(d.keys(known))<=set(keys),'prospective_domain_covers_rows')
    if not keys or len(keys)>decl['max_policy_keys']:
        status='unresolved_domain_budget';candidates=rejected=None
    elif not known:
        status='unresolved_contexts';candidates=rejected=None
    else:
        candidates,rejected=p.restrictions(known,keys)
        status='unresolved_contexts' if unresolved else 'conditionally_feasible' if candidates else 'conditionally_infeasible'
    return dict(profile='RevisedSourceActorPolicy/1',**w.FLAGS,actual_information_claim=False,
                declaration_sha256=did,contexts=summaries,keys=b.canonical(keys),required_keys=len(keys),
                status=status,rows=known,candidates=candidates,rejections=rejected,unresolved_contexts=unresolved,
                scope='resolved_context_restrictions_only' if unresolved else 'all_supplied_contexts')
