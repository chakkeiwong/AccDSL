"""Exact finite-law summary retaining unresolved branch mass."""
from fractions import Fraction as Q
def summarize(rows,threshold,unknown_cash_bounds=None):
    if not rows:raise ValueError('empty_law')
    ids=set();total=Q(0);known_mass=Q(0);contribution=Q(0);breach=Q(0);unresolved=Q(0)
    for row in rows:
        if set(row)!={'id','mass','status','cash'}:raise ValueError('row_fields')
        if row['id'] in ids:raise ValueError('duplicate_branch')
        ids.add(row['id']);mass=Q(row['mass'])
        if mass<=0:raise ValueError('nonpositive_mass')
        total+=mass
        if row['status']=='unresolved':
            if row['cash'] is not None:raise ValueError('unknown_has_value')
            unresolved+=mass
        elif row['status']=='complete':
            if row['cash'] is None:raise ValueError('complete_missing_value')
            cash=Q(row['cash']);known_mass+=mass;contribution+=mass*cash
            if cash<Q(threshold):breach+=mass
        else:raise ValueError('unknown_status')
    if total!=1:raise ValueError('mass_not_one')
    bounds=None
    if unknown_cash_bounds is not None:
        lower,upper=map(Q,unknown_cash_bounds)
        if lower>upper:raise ValueError('invalid_cash_bounds')
        bounds=[str(contribution+unresolved*lower),str(contribution+unresolved*upper)]
    return dict(status='complete' if unresolved==0 else 'partial',known_mass=str(known_mass),unresolved_mass=str(unresolved),known_weighted_contribution=str(contribution),unconditional_mean=str(contribution) if unresolved==0 else None,conditional_on_success_mean=str(contribution/known_mass) if known_mass else None,conditioning_event='status complete',breach_probability_bounds=[str(breach),str(breach+unresolved)],mean_bounds=bounds,bound_assumption=list(map(str,unknown_cash_bounds)) if unknown_cash_bounds is not None else None)
