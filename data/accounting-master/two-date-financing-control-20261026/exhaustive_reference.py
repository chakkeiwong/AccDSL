"""Independent literal-table oracle; does not import the candidate or its model."""
from fractions import Fraction
from itertools import product


def exact(value):
    if isinstance(value, dict):
        return {key: exact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [exact(item) for item in value]
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError):
            pass
    return value


def enumerate_strategies(table, investment=Fraction(60)):
    table = exact(table)
    cash_keys = ('senior', 'new', 'old')
    branches = {}
    for branch in ('debt', 'conversion'):
        policies = {}
        for policy in ('safe', 'risky'):
            outcomes = table['branches'][branch][policy]
            expected = {actor: sum(row['probability'] * row['cash'][i] for row in outcomes) for i, actor in enumerate(cash_keys)}
            benefit = sum(row['probability'] * row['private_benefit'] for row in outcomes)
            policies[policy] = dict(
                leaves=[dict(date='2029-01-01', probability=row['probability'], estate=row['estate'],
                             cash=dict(zip(cash_keys, row['cash'])), old_private_utility=row['private_benefit']) for row in outcomes],
                expected_cash=expected, expected_private_utility=benefit,
                terminal_utility=dict(new=expected['new'], old=expected['old'] + benefit))
        branches[branch] = dict(probability=table['branch_weights'][branch], rights=table['rights'][branch], policies=policies)
    strategies = []
    for debt_policy, conversion_policy in product(('safe', 'risky'), repeat=2):
        strategy = dict(debt=debt_policy, conversion=conversion_policy)
        deviations = []
        terminal_cash = dict.fromkeys(cash_keys, Fraction(0))
        private = Fraction(0)
        for branch, chosen in strategy.items():
            record = branches[branch]
            actor = table['controller'][branch]
            selected = record['policies'][chosen]
            for alternative in ('safe', 'risky'):
                gain = record['policies'][alternative]['terminal_utility'][actor] - selected['terminal_utility'][actor]
                deviations.append(dict(branch=branch, controller=actor, selected=chosen, alternative=alternative, terminal_gain=gain))
            for actor in cash_keys:
                terminal_cash[actor] += table['branch_weights'][branch] * selected['expected_cash'][actor]
            private += table['branch_weights'][branch] * selected['expected_private_utility']
        pv = {actor: amount * table['date0_terminal_factor'] for actor, amount in terminal_cash.items()}
        contribution = investment - pv['new']
        strategies.append(dict(
            strategy=strategy, stable=all(row['terminal_gain'] <= 0 for row in deviations), deviations=deviations,
            pricing=dict(strategy=strategy, expected_terminal_cash=terminal_cash, expected_terminal_private_utility=private,
                         discounted_cash=pv, discounted_private_utility=private * table['date0_terminal_factor'],
                         quote=pv['new'], required_owner_cash=contribution,
                         owner_net_utility=pv['old'] + private * table['date0_terminal_factor'] - contribution)))
    for branch, record in branches.items():
        controller = table['controller'][branch]
        record['best_responses'] = [policy for policy in ('safe', 'risky') if all(
            alternative['terminal_utility'][controller] <= record['policies'][policy]['terminal_utility'][controller]
            for alternative in record['policies'].values())]
    return dict(branches=branches, all_strategies=strategies, strategies=[x['strategy'] for x in strategies if x['stable']])
