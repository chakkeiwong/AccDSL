"""Optional proportional inventory sales on the complete annual tax book."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

import annual_period_book_v1 as annual
import partial_recovered_lot_v1 as partial

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/annual-inventory-composition-20261025'
LOCK = '8a07ea950ac8ae06487126620fc6e521176c4437adcf9677ad8cde2d341accee'
PROFILE = 'AnnualInventoryProgram/1'
FLAGS = {**annual.FLAGS, 'optional_inventory_reference': True}
core = annual.core
book = annual.book
require = annual.require


def protected():
    raw = (HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, value in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == value, 'protected_source_changed:' + name)
    annual.protected(); partial.protected()


def request(root, operations):
    return {'profile': PROFILE, 'root_request': deepcopy(root),
            'root_sha256': book.digest(root), 'operations': deepcopy(operations)}


def inventory_transition(state, operation):
    annual.invariant(state); core.closed(operation, ['kind', 'event'], 'operation')
    require(operation['kind'] == 'partial_inventory_sale', 'partial_operation')
    financial = state['after']; sale = operation['event']
    annual.caller.bounded(sale)
    core.closed(sale, ['profile', 'id', 'date', 'method', 'lot_id', 'sold_units', 'proceeds', 'findings'], 'sale')
    require(sale['profile'] == partial.PROFILE, 'sale_profile')
    require(sale['method'] == partial.MODEL, 'selected_method_only', 'unsupported')
    partial.text(sale['id'], 'event_id'); partial.text(sale['lot_id'], 'lot_id')
    require(sale['id'] not in financial['seen'], 'duplicate_event')
    day = core.scalar(sale['date'], 'date')
    require(core.scalar(financial['date'], 'date') <= day < core.scalar(financial['period']['end_exclusive'], 'date'), 'event_chronology')
    endpoint = state['current_assessments'][-1]['interval']['end_exclusive'] if state['current_assessments'] else financial['period']['start']
    require(day >= core.scalar(endpoint, 'date') and day >= core.scalar(financial['tax_closed_until'], 'date'), 'event_inside_assessed_interval')
    core.closed(sale['findings'], partial.FINDINGS, 'findings')
    for key in partial.FINDINGS:
        partial.affirmative(sale['findings'][key], key)
    require(sale['lot_id'] in financial['lots'], 'unknown_lot')
    lot = financial['lots'][sale['lot_id']]
    require(not lot['disposed'], 'lot_disposed')
    units, carrying, tax_base = (partial.number(lot[k]) for k in ['units', 'carrying', 'tax_base'])
    sold, proceeds = partial.number(sale['sold_units']), partial.number(sale['proceeds'])
    require(units > 0 and 0 < sold <= units, 'sold_units_outside_remaining_lot')
    require(carrying >= 0 and tax_base == carrying, 'selected_tax_base_method', 'unsupported')
    require(proceeds >= 0, 'negative_proceeds')
    fraction = sold/units; cost = fraction*carrying; released_tax = fraction*tax_base
    journal = {k: '0/1' for k in financial['balances']}
    journal.update(cash=book.fmt(proceeds), revenue=book.fmt(-proceeds),
                   inventory=book.fmt(-cost), cogs=book.fmt(cost))
    flows = [{'entity': financial['context']['entity'], 'activity': 'operating', 'origin': 'external_sale',
              'amount': book.fmt(proceeds), 'date': sale['date'], 'event_id': sale['id']}]
    after = deepcopy(financial)
    after['balances'] = {k: book.fmt(Q(v) + Q(journal[k])) for k, v in financial['balances'].items()}
    after['lots'][sale['lot_id']].update(units=book.fmt(units-sold), carrying=book.fmt(carrying-cost),
                                      tax_base=book.fmt(tax_base-released_tax), disposed=sold == units)
    after['date'] = sale['date']; after['seen'].append(sale['id']); after['flows'].extend(flows)
    writes = {'balances', 'lots', 'date', 'seen', 'flows'}
    require(all(after[k] == v for k, v in financial.items() if k not in writes), 'financial_write_boundary')
    require(all(after['lots'][k] == v for k, v in financial['lots'].items() if k != sale['lot_id']), 'other_lot_changed')
    require(all(journal[k] == '0/1' for k in ['income_tax_payable', 'current_tax', 'deferred_tax', 'dta', 'dtl']), 'tax_footprint')
    annual.native.invariant(after)
    result = deepcopy(state); result['after'] = after
    result['unassessed_native_events'].append(sale['id'])
    if result['current_assessments']:
        result['current_period_tax'] = 'activity_after_assessment'
    result['current_period_deferred_tax'] = 'stale' if result['deferred_assessments'] else 'unassessed'
    annual.invariant(result)
    require(sum(Q(v) for v in journal.values()) == 0, 'journal_unbalanced')
    require(Q(journal['cash']) == sum(Q(f['amount']) for f in flows), 'cash_flow_mismatch')
    return {'after': result, 'journal': journal, 'flows': flows,
            'before_sha256': book.digest(state), 'operation_sha256': book.digest(operation),
            'details': {'kernel': partial.MODEL, 'partial_source_lock': partial.LOCK,
                        'lot_id': sale['lot_id'], 'opening_units': book.fmt(units), 'sold_units': book.fmt(sold),
                        'fraction_of_remaining': book.fmt(fraction), 'released_carrying': book.fmt(cost),
                        'released_tax_base': book.fmt(released_tax), 'findings': deepcopy(sale['findings'])}}


def transition(state, operation):
    if type(operation) is dict and operation.get('kind') == 'partial_inventory_sale':
        return inventory_transition(state, operation)
    return annual.transition(state, operation)


def run(body):
    base = {'profile': PROFILE, **FLAGS}
    try:
        protected(); annual.caller.bounded(body)
        core.closed(body, ['profile', 'root_request', 'root_sha256', 'operations'], 'annual_inventory_program')
        require(body['profile'] == PROFILE, 'profile')
        require(body['root_sha256'] == book.digest(body['root_request']), 'root_digest')
        require(type(body['operations']) is list, 'operations_list')
        prior = annual.root.run(body['root_request'])
        base.update(root_result=prior, request_sha256=book.digest(body), source_bundle_sha256=LOCK,
                    implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status'] == 'complete_provisional', 'root_incomplete',
                'unresolved' if prior['status'] == 'stopped_provisional' else prior['status'])
        current = annual.seed(prior); annual.invariant(current); trace = []; stop = None
        for index, operation in enumerate(body['operations']):
            try:
                result = transition(current, operation)
                trace.append({'operation': deepcopy(operation), 'result': result}); current = result['after']
            except (annual.native.Refused, annual.native.lease.Refused, annual.losses.Refused,
                    partial.book.Refused, partial.book.lease.Refused) as exc:
                stop = {'index': index, 'status': exc.status, 'reason': exc.reason}; break
            except (ValueError, TypeError, KeyError, AttributeError, AssertionError, OverflowError, RecursionError) as exc:
                stop = {'index': index, 'status': 'invalid', 'reason': str(exc)[:350]}; break
        report = annual.root.carry.statements(current['opening'], current['after'], current['account_classes'])
        report.update(scope='Finite reusable period book under selected conditional models', unresolved=deepcopy(annual.UNRESOLVED))
        return {**base, 'status': 'stopped_provisional' if stop else 'complete_provisional', 'period_book': current,
                'conditional_current_assessed': current['current_period_tax'] == 'conditionally_assessed',
                'conditional_deferred_assessed': current['current_period_deferred_tax'] == 'conditionally_assessed',
                'deferred_asset_recognized': current['current_period_deferred_tax'] == 'conditionally_assessed' and Q(current['after']['balances']['dta']) > 0,
                'trace': trace, 'stop': stop, 'remaining_operations': deepcopy(body['operations'][len(trace):]),
                'recorded_statements': report, 'unresolved': deepcopy(annual.UNRESOLVED)}
    except (annual.native.Refused, annual.native.lease.Refused, annual.losses.Refused,
            partial.book.Refused, partial.book.lease.Refused) as exc:
        return {**base, 'status': exc.status, 'reason': exc.reason}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, AssertionError, OverflowError, RecursionError) as exc:
        return {**base, 'status': 'invalid', 'reason': str(exc)[:350]}


def apply(body, result):
    expected = run(body)
    try:
        require(expected['status'] in ['complete_provisional', 'stopped_provisional'], 'no_valid_prefix')
        require(annual.caller.canonical(expected) == annual.caller.canonical(result), 'complete_result_mismatch')
        return {**deepcopy(expected), 'status': 'applied_provisional'}
    except (ValueError, TypeError, OverflowError, RecursionError):
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': 'complete_result_mismatch'}
