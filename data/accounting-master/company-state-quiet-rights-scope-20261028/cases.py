"""Finite supplied decision models, not accounting methods or admitted rights."""
from copy import deepcopy
from fixtures import model, out, state, transition


def identity_partition(m):
    return [{s['id']: s['id'] for s in d['states']} for d in m['dates']]


def quiet_rights(fee=0, known=True):
    dates = []
    for t in range(3):
        states, transitions = [], []
        for right in ['call', 'locked']:
            ident = right + str(t)
            actions = ['coupon'] if t < 2 else ['wait'] + (['refinance'] if right == 'call' else [])
            states.append(state(ident, actions, 200 - 5*t))
            if t < 2:
                transitions.append(transition(ident, 'coupon', [out(right+str(t+1), 'quiet', -5)]))
            else:
                transitions.append(transition(ident, 'wait', [out('paid', 'settled', -110)]))
                if right == 'call':
                    transitions.append(transition(ident, 'refinance', [out('refinanced', 'settled', -(102+fee))]))
        dates.append({'states': states, 'transitions': transitions})
    dates.append({'states': [state('paid', [], 80), state('refinanced', [], 88-fee)], 'transitions': []})
    m = model('relation', dates, [{'state': r+'0', 'observation': r if known else 'right_unknown'} for r in ['call', 'locked']])
    fine = identity_partition(m)
    coarse = [{r+str(t): 'same' for r in ['call', 'locked']} for t in range(3)] + [fine[-1]]
    def choose(h):
        if len(h) < 3:
            return 'coupon'
        return 'refinance' if h[0]['observation'] == 'call' and fee < 8 else 'wait'
    return m, fine, coarse, choose


def maturity(extended=False, covenant=False):
    actions = ['hold'] if covenant else ['hold', 'distribute']
    dates = [{'states': [state('start', actions, 30)], 'transitions': []},
             {'states': [state('held', ['settle'] if extended else [], 30),
                         state('distributed', ['settle'] if extended else [], 25)], 'transitions': []}]
    for a, x, payment in [('hold', 'held', 0), ('distribute', 'distributed', -5)]:
        if a in actions:
            dates[0]['transitions'].append(transition('start', a, [out(x, 'year_end', payment)]))
    if extended:
        dates[1]['transitions'] = [transition('held', 'settle', [out('held_paid', 'matured', -22)]),
                                  transition('distributed', 'settle', [out('distributed_paid', 'matured', -22)])]
        dates.append({'states': [state('held_paid', [], 8), state('distributed_paid', [], 3)], 'transitions': []})
    m = model('relation', dates, [{'state': 'start', 'observation': 'start'}])
    return m, identity_partition(m)


def choose_maturity(first='distribute'):
    return lambda h: first if len(h) == 1 else 'settle'
