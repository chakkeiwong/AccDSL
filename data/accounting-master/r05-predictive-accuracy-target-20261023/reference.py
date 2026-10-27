"""Exact finite fixtures for the predictive-accuracy boundary; no model run."""
from fractions import Fraction as F


def point_crps(prediction, outcome):
    if not isinstance(prediction,F) or not isinstance(outcome,F):
        raise ValueError('point-law fixture requires exact finite values')
    return abs(prediction-outcome)


def difference(candidate, comparator, outcome, assets):
    if not isinstance(assets,F) or assets <= 0:
        raise ValueError('common as-of assets must be strictly positive')
    return point_crps(candidate,outcome)/assets - point_crps(comparator,outcome)/assets


def weighted_effect(cells):
    """cells: (issuer, origin, issuer_weight, origin_weight, difference|None)."""
    issuers = sorted({i for i,_,_,_,_ in cells})
    if issuers != [f'i{k}' for k in range(1,10)]:
        raise ValueError('fixed nine-issuer panel required')
    contribution = F(0); observed = F(0); missing=[]
    for issuer in issuers:
        rows=[x for x in cells if x[0]==issuer]
        if not rows or sum((x[3] for x in rows),F(0)) != 1:
            raise ValueError('origin weights must sum to one per issuer')
        if any(x[2] != F(1,9) for x in rows):
            raise ValueError('issuer weight must be one ninth')
        for i,o,iw,ow,d in rows:
            alpha=iw*ow
            if d is None:
                missing.append((i,o)); continue
            if not isinstance(d,F): raise ValueError('difference must be exact or unavailable')
            contribution += alpha*d; observed += alpha
    return {'contribution':contribution,'observed_weight':observed,
            'conditional_mean':contribution/observed if observed else None,
            'full_effect':None if missing else contribution,'missing':missing}


def comparator_is_locked(protocol_lock, comparator_lock, test_outcome):
    if protocol_lock is None or comparator_lock is None or test_outcome is None:
        return 'unverified'
    if comparator_lock < test_outcome and protocol_lock <= comparator_lock:
        return 'supported'
    if comparator_lock >= test_outcome:
        return 'contradicted'
    return 'unverified'


def check():
    assert difference(F(10),F(12),F(10),F(1)) == F(-2)
    assert difference(F(10),F(12),F(10),F(2)) == F(-1)
    assert difference(F(8),F(10),F(10),F(1)) == F(2)
    try:
        difference(F(10),F(12),F(10),F(0))
    except ValueError: pass
    else: raise AssertionError('zero scale accepted')
    try:
        difference(F(10),F(12),F(10),F(-1))
    except ValueError: pass
    else: raise AssertionError('negative scale accepted')
    cells=[]
    for k in range(1,10):
        issuer=f'i{k}'
        if k == 1: cells.append((issuer,'o1',F(1,9),F(1),F(-4)))
        else:
            cells.extend([(issuer,'o1',F(1,9),F(1,2),F(1)),
                          (issuer,'o2',F(1,9),F(1,2),F(1))])
    full=weighted_effect(cells)
    assert full['full_effect']==F(4,9) and full['observed_weight']==1
    equal_cells=sum((x[4] for x in cells),F(0))/len(cells)
    assert equal_cells == F(12,17) and equal_cells != full['full_effect']
    cells_missing=[x for x in cells if x[0]!='i1']+[("i1",'o1',F(1,9),F(1),None)]
    partial=weighted_effect(cells_missing)
    assert partial['full_effect'] is None and partial['observed_weight']==F(8,9)
    assert partial['conditional_mean']==F(1) and partial['contribution']==F(8,9)
    assert comparator_is_locked('2025-01-01','2025-01-02','2026-01-01')=='supported'
    assert comparator_is_locked('2025-01-01','2026-01-02','2026-01-01')=='contradicted'
    assert comparator_is_locked('2025-01-01',None,'2026-01-01')=='unverified'
    assert comparator_is_locked('2025-01-01','2025-01-01','2026-01-01')=='supported'
    refusals=[]
    try: weighted_effect(cells_missing[:-1])
    except ValueError: refusals.append('missing_issuer')
    try: weighted_effect([(i,o,F(1,9),F(1,2),d) for i,o,iw,ow,d in cells if i=='i1'] + [x for x in cells if x[0]!='i1'])
    except ValueError: refusals.append('issuer_time_sum')
    try: weighted_effect([(i,o,F(1,8),ow,d) for i,o,iw,ow,d in cells])
    except ValueError: refusals.append('wrong_issuer_weight')
    assert refusals == ['missing_issuer','issuer_time_sum','wrong_issuer_weight']
    return {'point_crps_cases':3,'scaling_cases':2,'weighted_effect_cases':4,
            'lock_cases':4,'invalid_refusals':7,'empirical_observations_used':0,
            'inference_admitted':False,'material_margin_selected':False}


if __name__=='__main__':
    import json; print(json.dumps(check()))
