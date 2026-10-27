from copy import deepcopy
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as Q
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import partial_recovered_lot_v1 as m
import shared_book_statements_v1 as reports

s = importlib.util.spec_from_file_location(
    'partial_lot_shared_examples', ROOT / 'data/accounting-master/shared-book-successor-20261024/examples.py')
previous = importlib.util.module_from_spec(s)
s.loader.exec_module(previous)


@lru_cache(maxsize=1)
def settled():
    r = m.book.run_prefix(previous.opening(), previous.events()[:2])
    assert r['status'] == 'complete'
    return r['after']


def sale(units='1/1', proceeds='15/1', identity='partial-sale', day='2024-03-01', lot='recovered'):
    return m.event(identity, day, lot, units, proceeds)


def native_sale(units='2/1', proceeds='30/1', identity='sale'):
    event = deepcopy(previous.events()[2]); event['event'].update(id=identity, proceeds=proceeds)
    return event


def statement_control(opening, closing):
    """Inspected statement equations; never a claim that old dispatch ran new events."""
    reports.protected(); m.book.invariant(opening); m.book.invariant(closing)
    b0, b = opening['balances'], closing['balances']
    assert all(b[k] == b0[k] for k in reports.EQUITY)
    profit = -sum(Q(b[k]) for k in reports.INCOME)
    assets = sum(Q(b[k]) for k in reports.ASSETS)
    liabilities = -sum(Q(b[k]) for k in reports.LIABILITIES)
    initial_equity = -sum(Q(b0[k]) for k in reports.EQUITY)
    equity = -sum(Q(b[k]) for k in reports.EQUITY) + profit
    cash = Q(b['cash']) - Q(b0['cash'])
    activities = {a: sum((Q(f['amount']) for f in closing['flows'] if f['activity'] == a), Q(0))
                  for a in reports.ACTIVITIES}
    indirect = profit + Q(b['depreciation']) + Q(b['deferred_tax']) + Q(b['other_gains'])
    indirect -= sum(Q(b[k]) - Q(b0[k]) for k in reports.WORKING_CAPITAL)
    indirect -= Q(closing['opening_interest_paid'])
    checks = {'balance_sheet': assets - liabilities - equity,
              'equity': initial_equity + profit - equity,
              'direct_cash': cash - sum(activities.values()),
              'indirect_cash': indirect - activities['operating']}
    assert set(checks.values()) == {0}, checks
    return {k: m.fmt(v) for k, v in {'assets': assets, 'liabilities': liabilities,
            'equity': equity, 'profit': profit, 'cash_movement': cash,
            'operating_cash': activities['operating'], 'indirect_cash': indirect}.items()} | {
                'reconciliations': {k: m.fmt(v) for k, v in checks.items()}}


def negatives():
    rows = []
    def add(name, change, status='invalid'):
        s, e = deepcopy(settled()), sale(); change(s, e)
        rows.append({'case': name, 'before': s, 'event': e, 'expected': status})
    for name, quantity in [('zero_units', '0/1'), ('negative_units', '-1/1'),
                           ('oversale', '3/1'), ('nonreduced', '2/2'), ('float', 1.0)]:
        add(name, lambda s, e, q=quantity: e.update(sold_units=q))
    add('unknown_quantity', lambda s, e: e.update(sold_units='unknown'), 'unresolved')
    add('negative_proceeds', lambda s, e: e.update(proceeds='-1/1'))
    add('unknown_proceeds', lambda s, e: e.update(proceeds='unknown'), 'unresolved')
    add('wrong_method', lambda s, e: e.update(method='fifo'), 'unsupported')
    add('wrong_profile', lambda s, e: e.update(profile='other'))
    add('unknown_lot', lambda s, e: e.update(lot_id='absent'))
    add('duplicate_event', lambda s, e: e.update(id=s['seen'][0]))
    add('earlier_date', lambda s, e: e.update(date='2024-01-01'))
    add('end_date', lambda s, e: e.update(date='2026-01-01'))
    add('bad_date', lambda s, e: e.update(date='2024-02-30'))
    add('extra_field', lambda s, e: e.update(fraction='1/2'))
    for key in m.FINDINGS:
        add('unknown_' + key, lambda s, e, k=key: e['findings'].update({k: {'status': 'unknown', 'reason': 'Not supplied'}}), 'unresolved')
        add('false_' + key, lambda s, e, k=key: e['findings'].update({k: m.known(False)}), 'unsupported')
        add('ill_typed_' + key, lambda s, e, k=key: e['findings'][k].update(value='true'))
    add('missing_finding', lambda s, e: e['findings'].pop('homogeneous_units'))
    add('missing_provenance', lambda s, e: e['findings']['homogeneous_units'].pop('provenance'))
    add('empty_provenance', lambda s, e: e['findings']['homogeneous_units'].update(provenance=''))
    add('unknown_reason_missing', lambda s, e: e['findings'].update(homogeneous_units={'status': 'unknown'}))
    add('wrong_tax_base', lambda s, e: s['lots']['recovered'].update(tax_base='19/1'))
    add('inventory_mismatch', lambda s, e: s['lots']['recovered'].update(carrying='19/1', tax_base='19/1'))
    add('tax_close_in_future_of_sale', lambda s, e: (s.update(date='2024-04-01', tax_closed_until='2024-04-01')))
    return rows
