"""Declarations authored from original registry/action vocabulary only."""
from copy import deepcopy as cp
import json
import domain as m
c=m.b.f.t.prior.load('prospective_original_cases',m.H.parent/'temporal-family-binding-20261027/cases.py')
def declaration(x,e,rename=False,collision=False,bound=12):
    d=dict(profile='ProspectiveActorObservationMap/1',input_sha256=m.identity(x),actor=x['request']['actor'],
      first_at=x['request']['decision_at'],second_at='2026-01-03T00:00:00Z',actions=cp(m.b.ACTIONS),maps=[],max_policy_keys=bound)
    for head,r in sorted(x['registry'].items()):
        if r.get('slot')!='observation_scheme' or r['disposition']!='assertion':continue
        # Independent vocabulary enumeration: all original financial payloads,
        # never a completed temporal family or selected outcome.
        raw=[]
        for f in x['registry'].values():
            if f.get('slot')!='financial_family' or f['disposition']!='assertion':continue
            s=f['payload'];raw += [z for z in e.rows if z['receipt']==s['receipt'] and (s['family']=='mixed' or z['right'])]
        first={tuple(z['obs1']) if r['payload']['view']=='refined' else (z['obs1'][0],) for z in raw}
        second={tuple(z['obs2'][-2:]) for z in raw if z['obs2'] is not None}
        def token(key):
            t='L' if key[0]=='low' else ('X' if len(key)>1 and key[1] else 'H')
            if collision:t='same'
            if r['supersedes'] is not None and (rename is True or rename=='low' and t=='L'):t='corrected_'+t
            return t
        d['maps'].append(dict(source_head=head,source_sha256=r['source_sha256'],
          first=[dict(key=list(k),token=token(k)) for k in sorted(first,key=repr)],
          second=[dict(key=list(k),token='trigger='+str(k[0])+';covers='+str(k[1])) for k in sorted(second,key=repr)],tag={'reveal':'never'}))
    return d
def inputs():
    selected={'baseline','correction_access_straddles','financial_correction_receipt6','unknown_access','two_source_supports_one_policy'}
    for name,f,budget,want,reuse in c.suite():
        if name in selected:yield name,m.b.f.wire(f),{}
        if name=='two_source_supports_one_policy':
            yield 'new_correction_label',m.b.f.wire(f),{'rename':True}
            yield 'new_low_correction_label',m.b.f.wire(f),{'rename':'low'}
            yield 'message_collision',m.b.f.wire(f),{'collision':True}
    base=c.f.oldcases.base();c.f.oldcases.add(base,'observation_scheme',None,supersedes=base['names']['observation_scheme'],when='2026-01-01T01:00:00Z',disposition='retraction')
    yield 'retraction',m.b.f.wire(c.f.convert(base)),{}
    base=c.f.oldcases.base();c.f.oldcases.add(base,'observation_scheme',{'view':'coarse'},supersedes=None)
    yield 'conflicting_heads',m.b.f.wire(c.f.convert(base)),{}
