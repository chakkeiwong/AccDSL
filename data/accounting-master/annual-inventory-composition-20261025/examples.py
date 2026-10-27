from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts'))
import annual_inventory_program_v1 as m

s = importlib.util.spec_from_file_location(
    'annual_inventory_prior_examples', ROOT/'data/accounting-master/reusable-annual-interface-20261025/examples.py')
previous = importlib.util.module_from_spec(s); s.loader.exec_module(previous)


@lru_cache(maxsize=1)
def root():
    q = previous.previous.retained_lot_scenario()
    q['operations'] = []
    return q


def sale(identity='inventory-partial', units='1/1', proceeds='15/1', day='2027-01-02'):
    return {'kind': 'partial_inventory_sale',
            'event': m.partial.event(identity, day, 'recovered', units, proceeds)}


def start():
    result = m.run(m.request(root(), []))
    assert result['status'] == 'complete_provisional', result
    return result['period_book']


def append(q, state, operation):
    result = m.transition(state, operation)
    q['operations'].append(deepcopy(operation))
    return result['after']


def residual_carry():
    q = m.request(root(), []); state = start()
    for operation in [sale()]:
        state = append(q, state, operation)
    state = append(q, state, previous.assessment(state, '8/1', 'inventory-year-end', end='2028-01-01'))
    state = append(q, state, previous.deferred(state, 'inventory-deferred'))
    state = append(q, state, previous.carry(state, 'inventory-carry'))
    state = append(q, state, sale('inventory-next-year', day='2028-01-02'))
    return q


def after_assessment():
    q = m.request(root(), []); state = start()
    state = append(q, state, previous.assessment(state, '8/1', 'inventory-midyear'))
    state = append(q, state, previous.deferred(state, 'inventory-mid-deferred'))
    state = append(q, state, sale(day='2027-07-01'))
    return q


def refreshed_carry():
    q = after_assessment(); state = m.run(q)['period_book']
    state = append(q, state, previous.assessment(state, '12/1', 'inventory-reassessed', 'replace', '2028-01-01'))
    state = append(q, state, previous.deferred(state, 'inventory-fresh-deferred'))
    state = append(q, state, previous.carry(state, 'inventory-refreshed-carry'))
    return q


def native_full_sale():
    q = previous.previous.retained_lot_scenario()
    operation = deepcopy(q['operations'][0])
    operation['event']['event'].update(id='full-inventory-sale', date='2027-01-02')
    return m.annual.request(root(), [operation])


def cases():
    rows = []
    def add(name, q, status='complete_provisional', stop=None):
        rows.append({'case': name, 'request': q, 'expected_status': status, 'expected_stop': stop})
    add('empty', m.request(root(), []))
    add('partial', m.request(root(), [sale()]))
    add('full', m.request(root(), [sale('full-inventory-sale', '2/1', '30/1')]))
    add('residual_carry_and_sale', residual_carry())
    add('after_assessment', after_assessment())
    add('refreshed_carry', refreshed_carry())
    q = after_assessment(); state = m.run(q)['period_book']; q['operations'].append(previous.carry(state, 'stale-carry'))
    add('stale_carry', q, 'stopped_provisional', 'unresolved')
    q = after_assessment(); stale = deepcopy(q['operations'][1]); stale['event']['id'] = 'reused-measurement'; q['operations'].append(stale)
    add('measurement_without_reassessment', q, 'stopped_provisional', 'unresolved')
    q = after_assessment(); state = m.run(q)['period_book']; stale = deepcopy(q['operations'][1])
    state = append(q, state, previous.assessment(state, '12/1', 'inventory-current-again', 'replace', '2027-07-02'))
    stale['event']['id'] = 'stale-after-reassessment'; stale['event']['measurement']['at'] = state['after']['date']
    q['operations'].append(stale)
    add('stale_measurement', q, 'stopped_provisional', 'invalid')
    q = after_assessment(); q['operations'][2]['event']['date'] = '2027-06-30'
    add('inside_assessment', q, 'stopped_provisional', 'invalid')
    for name, change, status in [
        ('unknown_findings', lambda e: e['findings'].update(homogeneous_units={'status': 'unknown', 'reason': 'Not supplied'}), 'unresolved'),
        ('false_findings', lambda e: e['findings'].update(divisible_units=m.partial.known(False)), 'unsupported'),
        ('oversale', lambda e: e.update(sold_units='3/1'), 'invalid'),
        ('wrong_profile', lambda e: e.update(profile='SyntheticReturnLeaseBook/1'), 'invalid'),
        ('wrong_date', lambda e: e.update(date='2028-01-01'), 'invalid'),
        ('wrong_method', lambda e: e.update(method='arbitrary'), 'unsupported')]:
        op = sale(); change(op['event']); add(name, m.request(root(), [op]), 'stopped_provisional', status)
    add('retained_prefix', m.request(root(), [sale(), sale('over', '2/1', '30/1'), sale('later')]), 'stopped_provisional', 'invalid')
    return rows
