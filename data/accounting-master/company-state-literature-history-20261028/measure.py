"""Separately authored weights for finite histories, with explicit provenance."""
from fractions import Fraction
from hashlib import sha256
import json


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def evaluate(support,measure=None):
    if not isinstance(support,list) or not support:
        raise ValueError('nonempty_support_required')
    if any(set(row)!={'id','history'} for row in support):
        raise ValueError('support_fields')
    ids=[row['id'] for row in support]
    if any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids):
        raise ValueError('support_identity')
    binding=digest(support)
    if measure is None:
        return dict(status='unweighted',support_sha256=binding,probability_law=None)
    if set(measure)!={'profile','support_sha256','weights','provenance'} or measure['profile']!='AuthoredHistoryMeasure/1':
        raise ValueError('measure_fields')
    if measure['support_sha256']!=binding:raise ValueError('stale_support')
    provenance=measure['provenance']
    if not isinstance(provenance,dict) or set(provenance)!={'origin','meaning','source'} or any(not isinstance(v,str) or not v.strip() for v in provenance.values()):
        raise ValueError('explicit_provenance_required')
    weights=measure['weights']
    if not isinstance(weights,dict) or set(weights)!=set(ids):raise ValueError('weight_support_mismatch')
    mass={}
    for ident,value in weights.items():
        if not isinstance(value,str):raise ValueError('exact_rational_required')
        try:mass[ident]=Fraction(value)
        except (ValueError,ZeroDivisionError):raise ValueError('exact_rational_required')
        if mass[ident]<0:raise ValueError('negative_mass')
    if sum(mass.values())!=1:raise ValueError('mass_not_one')
    law={};histories={}
    for row in support:
        key=json.dumps(row['history'],sort_keys=True,separators=(',',':'))
        law[key]=law.get(key,Fraction())+mass[row['id']];histories[key]=row['history']
    return dict(status='conditional_authored_measure',support_sha256=binding,measure_sha256=digest(measure),
                provenance=dict(provenance),probability_law=[dict(history=histories[k],probability=str(law[k])) for k in sorted(law)],
                source_admission=False,issuer_prior_justified=False)
