"""Exact supplied structural laws and joint scenarios; no fitted causal model."""
from collections import defaultdict
from fractions import Fraction as Q

def exact(x):
    if isinstance(x,(bool,float)) or not isinstance(x,(str,int,Q)):raise ValueError('exact_quantity_required')
    return Q(x)

def structural(model,intervention=None):
    if model not in ['confounded_demand','rate_driven_demand']:raise ValueError('model_required')
    if intervention is not None and (type(intervention) is not int or intervention not in [1,2]):raise ValueError('supported_intervention')
    rows=[]
    for u in [0,1]:
        rate=1+u if intervention is None else intervention
        demand=100-40*u if model=='confounded_demand' else 140-40*rate
        rows.append(dict(u=u,rate=rate,demand=demand,cash=demand-10*rate,mass='1/2'))
    return rows

def condition(rows,rate):
    kept=[r for r in rows if r['rate']==rate];mass=sum((Q(r['mass']) for r in kept),Q(0))
    if not mass:return dict(status='unresolved_zero_condition',rows=[])
    return dict(status='conditional',rows=[{**r,'mass':str(Q(r['mass'])/mass)} for r in kept])

def law(rows):
    result=defaultdict(Q)
    for r in rows:result[(r['rate'],r['demand'],r['cash'])]+=Q(r['mass'])
    return dict(result)

def mean(rows):return sum(Q(r['cash'])*Q(r['mass']) for r in rows)

def joint(scenarios,weights=None):
    if type(scenarios) is not list or not scenarios:return dict(status='invalid',reason='scenario_list')
    if any(type(r) is not dict or set(r)!={'id','fx','demand'} for r in scenarios):return dict(status='invalid',reason='scenario_fields')
    ids=[r['id'] for r in scenarios]
    if any(type(x) is not str or not x for x in ids) or len(ids)!=len(set(ids)):return dict(status='invalid',reason='scenario_identity')
    if any(r[k] is None for r in scenarios for k in ['fx','demand']):return dict(status='unresolved',reason='unknown_joint_quantity',scenarios=scenarios)
    try:
        rows=[]
        for r in scenarios:
            fx,demand=exact(r['fx']),exact(r['demand'])
            if fx<=0 or demand<0:raise ValueError('fx_demand_domain')
            rows.append({**r,'cash':str(fx*demand-50)})
        result=dict(status='conditional_family',scenarios=rows,mean=None,negative_cash_probability=None,
                    cash_bounds=[str(min(Q(r['cash']) for r in rows)),str(max(Q(r['cash']) for r in rows))],
                    source_admission=False,joint_dependence_verified=False)
        if weights is not None:
            if type(weights) is not dict or set(weights)!=set(ids):raise ValueError('explicit_mass_coverage')
            w={k:exact(v) for k,v in weights.items()}
            if any(x<0 for x in w.values()) or sum(w.values())!=1:raise ValueError('probability_mass')
            result.update(status='conditional_supplied_law',mean=str(sum(w[r['id']]*Q(r['cash']) for r in rows)),
                          negative_cash_probability=str(sum(w[r['id']] for r in rows if Q(r['cash'])<0)),weights={k:str(v) for k,v in w.items()})
        return result
    except (ValueError,TypeError,ZeroDivisionError) as exc:return dict(status='invalid',reason=str(exc))

def supported(scenarios,fx,demand):
    checked=joint(scenarios)
    if checked['status']!='conditional_family':return checked
    if fx is None or demand is None:return dict(status='unresolved',reason='joint_request_unknown')
    try:pair=(exact(fx),exact(demand))
    except (ValueError,TypeError,ZeroDivisionError) as exc:return dict(status='invalid',reason=str(exc))
    matches=[r['id'] for r in scenarios if (exact(r['fx']),exact(r['demand']))==pair]
    return dict(status='supported' if matches else 'outside_declared_joint_support',matching_scenarios=matches)
