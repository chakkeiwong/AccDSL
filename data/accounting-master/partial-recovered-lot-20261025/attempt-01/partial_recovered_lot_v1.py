"""Conditional proportional sale of a divisible homogeneous recovered lot."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

import shared_book_successor_v1 as book

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/partial-recovered-lot-20261025'
LOCK = '37d1bbcb4b1709b3da4bffc0bd6306365fee9a354ba77c98e9ff4a2b1f47e442'
PROFILE = 'RecoveredLotSale/1'
MODEL = 'proportional_remaining_homogeneous_lot_v1'
FINDINGS = ['proportional_allocation_selected', 'homogeneous_units', 'divisible_units',
            'measurement_basis_unchanged', 'performance_complete', 'tax_base_equals_carrying']
FLAGS = {**book.FLAGS, 'annual_ready': False, 'general_inventory_method': False}
need = book.need
fmt = book.fmt
digest = book.digest


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed', 'unsupported')
    for name, expected in json.loads(raw).items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             'protected_source_changed:' + name, 'unsupported')
    book.protected()


def text(value, name):
    need(type(value) is str and 0 < len(value) <= 4096 and bool(value.strip()), name)
    value.encode('utf-8', errors='strict')


def known(value=True, provenance='Explicit hypothetical caller premise'):
    return {'status': 'known', 'value': value, 'provenance': provenance}


def affirmative(value, name):
    need(type(value) is dict, 'finding_record:' + name)
    if value.get('status') == 'unknown':
        book.caller.closed(value, ['status', 'reason'])
        text(value['reason'], 'unknown_reason')
        need(False, name + ':unknown', 'unresolved')
    book.caller.closed(value, ['status', 'value', 'provenance'])
    need(value['status'] == 'known' and type(value['value']) is bool, 'boolean_finding:' + name)
    text(value['provenance'], 'finding_provenance:' + name)
    need(value['value'], name + ':false', 'unsupported')


def number(value):
    need(type(value) is str and len(value) <= 256, 'bounded_rational_string')
    return book.amount(value)


def event(identity, date, lot_id, sold_units, proceeds, provenance='Explicit hypothetical caller premise'):
    return {'profile': PROFILE, 'id': identity, 'date': date, 'method': MODEL,
            'lot_id': lot_id, 'sold_units': sold_units, 'proceeds': proceeds,
            'findings': {name: known(provenance=provenance) for name in FINDINGS}}


def propose(state, sale):
    try:
        protected(); book.invariant(state); book.caller.bounded(sale)
        book.caller.closed(sale, ['profile', 'id', 'date', 'method', 'lot_id',
                                 'sold_units', 'proceeds', 'findings'])
        need(sale['profile'] == PROFILE, 'event_profile')
        need(sale['method'] == MODEL, 'selected_method_only', 'unsupported')
        text(sale['id'], 'event_id'); text(sale['lot_id'], 'lot_id')
        need(sale['id'] not in state['seen'], 'duplicate_event')
        day = book.lease.day(sale['date'])
        need(book.lease.day(state['date']) <= day < book.lease.day(state['period']['end_exclusive'])
             and book.lease.day(state['tax_closed_until']) <= day, 'event_chronology')
        findings = sale['findings']; book.caller.closed(findings, FINDINGS)
        for name in FINDINGS:
            affirmative(findings[name], name)
        need(sale['lot_id'] in state['lots'], 'unknown_lot')
        lot = state['lots'][sale['lot_id']]
        need(not lot['disposed'], 'lot_disposed')
        units, carrying, tax_base = (number(lot[k]) for k in ['units', 'carrying', 'tax_base'])
        sold, proceeds = number(sale['sold_units']), number(sale['proceeds'])
        need(units > 0 and 0 < sold <= units, 'sold_units_outside_remaining_lot')
        need(carrying >= 0 and tax_base == carrying, 'selected_tax_base_method', 'unsupported')
        need(proceeds >= 0, 'negative_proceeds')
        fraction = sold / units
        released_cost, released_tax = fraction * carrying, fraction * tax_base
        journal = {key: '0/1' for key in book.ACCOUNTS}
        journal.update(cash=fmt(proceeds), revenue=fmt(-proceeds),
                       inventory=fmt(-released_cost), cogs=fmt(released_cost))
        # Preserve the original sale's gross-flow convention, including a zero receipt.
        flows = [{'entity': state['context']['entity'], 'activity': 'operating',
                  'origin': 'external_sale', 'amount': fmt(proceeds),
                  'date': sale['date'], 'event_id': sale['id']}]
        after = deepcopy(state)
        after['balances'] = {key: fmt(book.amount(value) + Q(journal[key]))
                             for key, value in state['balances'].items()}
        after['lots'][sale['lot_id']].update(units=fmt(units - sold),
            carrying=fmt(carrying - released_cost), tax_base=fmt(tax_base - released_tax),
            disposed=sold == units)
        after['date'] = sale['date']; after['seen'].append(sale['id']); after['flows'].extend(flows)
        writes = {'balances', 'lots', 'date', 'seen', 'flows'}
        need(all(after[key] == value for key, value in state.items() if key not in writes),
             'unrelated_state_changed')
        need(all(after['lots'][key] == value for key, value in state['lots'].items()
                 if key != sale['lot_id']), 'other_lot_changed')
        need(sum(Q(v) for v in journal.values()) == 0, 'journal_balance')
        need(Q(journal['cash']) == sum(Q(f['amount']) for f in flows), 'cash_flow_identity')
        book.invariant(after)
        proposal = {'profile': PROFILE, **FLAGS, 'before_sha256': digest(state),
            'event_sha256': digest(sale), 'source_lock_sha256': LOCK,
            'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'journal': journal, 'flows': flows, 'after': after,
            'allocation': {'lot_id': sale['lot_id'], 'opening_units': fmt(units),
                'sold_units': fmt(sold), 'fraction_of_remaining': fmt(fraction),
                'released_carrying': fmt(released_cost), 'released_tax_base': fmt(released_tax)},
            'findings': deepcopy(findings), 'write_fields': sorted(writes)}
        return {'status': 'proposed', 'proposal': proposal, **FLAGS}
    except (book.Refused, book.lease.Refused) as exc:
        return {'status': exc.status, 'reason': exc.reason, 'proposal': None, **FLAGS}
    except (ValueError, TypeError, KeyError, AttributeError, OSError,
            AssertionError, RecursionError, OverflowError) as exc:
        return {'status': 'invalid', 'reason': str(exc)[:350], 'proposal': None, **FLAGS}


def apply(state, sale, proposal):
    expected = propose(state, sale)
    if expected['status'] != 'proposed':
        return expected
    try:
        book.caller.bounded(proposal)
        need(book.caller.canonical(proposal) == book.caller.canonical(expected['proposal']),
             'complete_proposal_mismatch')
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError):
        return {'status': 'invalid', 'reason': 'complete_proposal_mismatch', 'proposal': None, **FLAGS}
    return {'status': 'applied_diagnostic', 'after': deepcopy(expected['proposal']['after']), **FLAGS}


def run_prefix(state, sales):
    current = deepcopy(state); trace = []
    try:
        protected(); book.invariant(current); book.caller.bounded(sales)
        need(type(sales) is list, 'sale_list')
    except (ValueError, TypeError, KeyError, AttributeError, OSError,
            AssertionError, RecursionError, OverflowError) as exc:
        return {'status': 'invalid', 'reason': str(exc)[:350], 'after': current, 'trace': [], **FLAGS}
    for index, sale in enumerate(sales):
        result = propose(current, sale)
        if result['status'] != 'proposed':
            return {'status': 'stopped', 'after': current, 'trace': trace,
                    'stop': {'index': index, 'result': result},
                    'remaining_sales': deepcopy(sales[index:]), **FLAGS}
        trace.append({'event': deepcopy(sale), 'proposal': result['proposal']})
        current = deepcopy(result['proposal']['after'])
    return {'status': 'complete', 'after': current, 'trace': trace,
            'stop': None, 'remaining_sales': [], **FLAGS}
