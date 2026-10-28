"""Finite supplied-policy checks; no inferred probabilities or general solver."""
from fractions import Fraction as Q
from itertools import product


def exact(x):
    if isinstance(x,(bool,float)):raise ValueError('exact_rational_required')
    try:return Q(x)
    except (ValueError,TypeError,ZeroDivisionError):raise ValueError('exact_rational_required')


def issue(action):
    a=exact(action)
    if a not in {0,1}:raise ValueError('indivisible_action')
    cash=100*a;paid=min(cash,50);unpaid=50-paid
    return dict(action=str(a),proceeds=str(cash),payment=str(paid),closing_cash=str(cash-paid),
                unpaid=str(unpaid),default=unpaid>0,cost=str(a+2*int(unpaid>0)))


def lift(histories):
    """A caller supplies original feasible actions for reduced observations."""
    actions={}
    for row in histories:
        observation=row['observation'];action=exact(row['lifted_action'])
        issue(action)
        if observation in actions and actions[observation]!=action:
            raise ValueError('lift_uses_hidden_history')
        actions[observation]=action
    return {o:issue(a) for o,a in actions.items()}


def boundary(rows,threshold,delta,context):
    if context.get('x_currency')!=context.get('y_currency') or context.get('x_date')!=context.get('y_date'):
        raise ValueError('cash_basis_mismatch')
    if not context.get('x_currency') or not context.get('x_date'):
        raise ValueError('cash_basis_required')
    c,d=exact(threshold),exact(delta)
    if d<=0:raise ValueError('positive_delta_required')
    if not rows:raise ValueError('coupling_required')
    ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('coupling_identity')
    if all('mass' not in r for r in rows):
        uncertain=[r['id'] for r in rows if abs(exact(r['x'])-c)<=d or abs(exact(r['x'])-exact(r['y']))>=d]
        return dict(status='unweighted_boundary_set',uncertain_ids=uncertain,probability_bound=None)
    if any('mass' not in r for r in rows):raise ValueError('partial_measure')
    triples=[(exact(r['x']),exact(r['y']),exact(r['mass'])) for r in rows]
    if any(w<0 for x,y,w in triples):raise ValueError('negative_mass')
    if sum(w for x,y,w in triples)!=1:raise ValueError('mass_not_one')
    px=sum(w for x,y,w in triples if x<c);py=sum(w for x,y,w in triples if y<c)
    mass=sum(w for x,y,w in triples if abs(x-c)<=d);error=sum(w*abs(x-y) for x,y,w in triples)
    raw=mass+error/d
    return dict(status='conditional_exact_coupling',exact_default=str(px),approx_default=str(py),
                probability_error=str(abs(px-py)),boundary_mass=str(mass),mean_absolute_error=str(error),
                raw_bound=str(raw),probability_bound=str(min(Q(1),raw)),premises_validated_externally=False)


def regret(exact_cost,approx_cost,selected,epsilon,eta):
    if not exact_cost or set(exact_cost)!=set(approx_cost):raise ValueError('common_policy_class_required')
    if selected not in exact_cost:raise ValueError('selected_policy_missing')
    e,h=exact(epsilon),exact(eta)
    if e<0 or h<0:raise ValueError('nonnegative_error_required')
    x={k:exact(v) for k,v in exact_cost.items()};y={k:exact(v) for k,v in approx_cost.items()}
    uniform=max(abs(x[k]-y[k]) for k in x)
    if uniform>e:raise ValueError('uniform_bound_violated')
    if y[selected]>min(y.values())+h:raise ValueError('eta_optimality_violated')
    value=x[selected]-min(x.values())
    return dict(status='finite_common_class',uniform_error=str(uniform),optimized_value_gap=str(abs(min(x.values())-min(y.values()))),
                selected_regret=str(value),bound=str(2*e+h),policy_feasibility_source='Explicit common identities; caller must establish real feasibility')


def stopping(rows,observations):
    """Enumerate stop at0, or stop/continue at1 by supplied observation."""
    if set(observations)!={r['id'] for r in rows}:raise ValueError('observation_coverage')
    if sum(exact(r['mass']) for r in rows)!=1:raise ValueError('mass_not_one')
    if any(exact(r['mass'])<0 for r in rows):raise ValueError('negative_mass')
    signals=sorted(set(observations.values()));results=[]
    for values in product(['stop','continue'],repeat=len(signals)):
        policy=dict(zip(signals,values));paths=[];cost=Q()
        for row in rows:
            action=policy[observations[row['id']]];t=1 if action=='stop' else 2
            cash=exact(row['x1'] if t==1 else row['x2']);cost+=exact(row['mass'])*cash
            paths.append(dict(id=row['id'],observation=observations[row['id']],action=action,stopping_time=t,cost=str(cash),mass=str(exact(row['mass']))))
        results.append(dict(policy=policy,cost=str(cost),paths=paths))
    results.append(dict(policy={'time0':'stop'},cost='0',paths=[dict(id=r['id'],stopping_time=0,cost='0',mass=str(exact(r['mass']))) for r in rows]))
    return dict(status='exact_supplied_information',policies=results,optimal_cost=str(min(Q(r['cost']) for r in results)))


def validate_path_actions(rows,observations,actions):
    seen={}
    for r in rows:
        ident=r['id'];signal=observations[ident];action=actions[ident]
        if action not in ['stop','continue']:raise ValueError('unsupported_action')
        if signal in seen and seen[signal]!=action:raise ValueError('future_information_leak')
        seen[signal]=action
    return seen
