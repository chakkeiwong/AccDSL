"""Exact, deliberately finite two-date decision reference; no import-time I/O."""
from datetime import date
from fractions import Fraction as F
from itertools import product


class InvalidModel(ValueError):
    pass


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, F)):
        raise InvalidModel('exact_rational_required')
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise InvalidModel('invalid_rational') from exc


def validate(model):
    if model['schema'] != 'TwoDateFinancingFixture/1':
        raise InvalidModel('schema')
    dates = model['dates']
    if len(dates) != 3 or any(date.fromisoformat(x).isoformat() != x for x in dates) or not dates[0] < dates[1] < dates[2]:
        raise InvalidModel('date_order')
    if model['signal_known_date'] != dates[1] or model['terminal_known_date'] != dates[2]:
        raise InvalidModel('information_timing')
    if model['terminal_cash_date'] != dates[2]:
        raise InvalidModel('cash_timing')
    factors = model['discount_factors']
    if len(factors) != 2 or any(rational(x) <= 0 for x in factors):
        raise InvalidModel('discount_intervals')
    for key in ('senior_face', 'new_face', 'investment', 'old_shares', 'conversion_shares'):
        if rational(model[key]) <= 0:
            raise InvalidModel('positive_' + key)
    if rational(model['conversion_risky_private_benefit']) < 0:
        raise InvalidModel('private_benefit')
    rational(model['outside_utility_date0'])
    governance = model['governance']
    if governance['rule'] != 'strict_majority' or governance['tie_controller'] not in (None, 'old', 'new'):
        raise InvalidModel('governance')
    if set(model['branches']) != {'debt', 'conversion'}:
        raise InvalidModel('branches')
    probs = []
    for name, branch in model['branches'].items():
        if branch['converts'] is not (name == 'conversion'):
            raise InvalidModel('conversion_event')
        probs.append(rational(branch['probability']))
        if set(branch['policies']) != {'safe', 'risky'}:
            raise InvalidModel('policy_domain')
        for outcomes in branch['policies'].values():
            if not outcomes or any(len(row) != 2 for row in outcomes):
                raise InvalidModel('outcomes')
            weights = [rational(row[0]) for row in outcomes]
            if any(x <= 0 for x in weights) or sum(weights) != 1:
                raise InvalidModel('conditional_mass')
            if any(rational(row[1]) < 0 for row in outcomes):
                raise InvalidModel('negative_estate')
    if any(x <= 0 for x in probs) or sum(probs) != 1:
        raise InvalidModel('signal_mass')


def rights(model, branch):
    converts = model['branches'][branch]['converts']
    old = rational(model['old_shares'])
    new = rational(model['conversion_shares']) if converts else F(0)
    old_fraction, new_fraction = old / (old + new), new / (old + new)
    controller = 'old' if old_fraction > F(1, 2) else 'new' if new_fraction > F(1, 2) else model['governance']['tie_controller']
    return dict(date=model['dates'][1], senior_face=rational(model['senior_face']),
                new_debt=F(0) if converts else rational(model['new_face']),
                old_shares=old, new_shares=new, old_cash_fraction=old_fraction,
                new_cash_fraction=new_fraction, old_vote_fraction=old_fraction,
                new_vote_fraction=new_fraction, controller=controller,
                conversion=dict(date=model['dates'][1], debt_extinguished=rational(model['new_face']), shares_issued=new) if converts else None)


def branch_payoffs(model, name, state):
    policies = {}
    for policy, outcomes in model['branches'][name]['policies'].items():
        leaves, cash, private = [], dict(senior=F(0), new=F(0), old=F(0)), F(0)
        for probability, estate in outcomes:
            pr, estate = rational(probability), rational(estate)
            senior = min(estate, state['senior_face'])
            debt = min(estate - senior, state['new_debt'])
            equity = estate - senior - debt
            allocation = dict(senior=senior, new=debt + equity * state['new_cash_fraction'], old=equity * state['old_cash_fraction'])
            benefit = rational(model['conversion_risky_private_benefit']) if name == 'conversion' and policy == 'risky' else F(0)
            leaves.append(dict(date=model['dates'][2], probability=pr, estate=estate, cash=allocation, old_private_utility=benefit))
            for actor in cash:
                cash[actor] += pr * allocation[actor]
            private += pr * benefit
        policies[policy] = dict(leaves=leaves, expected_cash=cash, expected_private_utility=private,
                                terminal_utility=dict(new=cash['new'], old=cash['old'] + private))
    return policies


def analyze(model):
    validate(model)
    branches, choices = {}, []
    for name in ('debt', 'conversion'):
        state = rights(model, name)
        policies = branch_payoffs(model, name, state)
        controller = state['controller']
        if controller is None:
            best = []
        else:
            maximum = max(x['terminal_utility'][controller] for x in policies.values())
            best = [k for k, v in policies.items() if v['terminal_utility'][controller] == maximum]
        branches[name] = dict(probability=rational(model['branches'][name]['probability']), rights=state, policies=policies, best_responses=best)
        choices.append(best)
    strategies = [dict(zip(('debt', 'conversion'), pair)) for pair in product(*choices)]
    return dict(status='resolved' if strategies else 'unsupported_governance', branches=branches, strategies=strategies)


def validate_strategy(model, strategy):
    if set(strategy) != set(model['branches']) or any(not isinstance(v, str) or v not in model['branches'][k]['policies'] for k, v in strategy.items()):
        raise InvalidModel('nonanticipating_strategy_required')


def price_strategy(model, strategy, analysis=None):
    analysis = analysis or analyze(model)
    validate_strategy(model, strategy)
    cash, private = dict(senior=F(0), new=F(0), old=F(0)), F(0)
    for name, policy in strategy.items():
        branch = analysis['branches'][name]
        payoff = branch['policies'][policy]
        for actor in cash:
            cash[actor] += branch['probability'] * payoff['expected_cash'][actor]
        private += branch['probability'] * payoff['expected_private_utility']
    discount = rational(model['discount_factors'][0]) * rational(model['discount_factors'][1])
    pv = {actor: amount / discount for actor, amount in cash.items()}
    contribution = rational(model['investment']) - pv['new']
    return dict(strategy=dict(strategy), expected_terminal_cash=cash, expected_terminal_private_utility=private,
                discounted_cash=pv, discounted_private_utility=private / discount, quote=pv['new'],
                required_owner_cash=contribution, owner_net_utility=pv['old'] + private / discount - contribution)


def offer(model, strategy, quote, available_cash):
    analysis = analyze(model)
    priced = price_strategy(model, strategy, analysis)
    quote, available = rational(quote), rational(available_cash)
    if quote < 0 or available < 0:
        raise InvalidModel('negative_offer_cash')
    contribution = rational(model['investment']) - quote
    net = priced['discounted_cash']['old'] + priced['discounted_private_utility'] - contribution
    outside = rational(model['outside_utility_date0'])
    reasons = []
    if analysis['status'] != 'resolved':
        reasons.append('unsupported_governance')
    elif strategy not in analysis['strategies']:
        reasons.append('continuation_deviation')
    if quote != priced['quote']:
        reasons.append('quote_payoff_mismatch')
    if contribution < 0:
        reasons.append('unsupported_owner_distribution')
    if contribution > available:
        reasons.append('insufficient_owner_cash')
    if net < outside:
        reasons.append('owner_participation')
    return dict(status='accepted' if not reasons else 'rejected', reasons=reasons, strategy=dict(strategy),
                quote=quote, required_owner_cash=contribution, available_owner_cash=available, owner_net_utility=net,
                outside_utility=outside, participation='strict' if net > outside else 'indifferent' if net == outside else 'fails',
                cash_legs=[dict(date=model['dates'][0], actor='new', amount=quote),
                           dict(date=model['dates'][0], actor='old', amount=contribution),
                           dict(date=model['dates'][0], actor='investment', amount=-rational(model['investment']))],
                execution='funded' if not reasons else 'no_funding_executed')
