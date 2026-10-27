"""Exact conditional current-tax arithmetic; no journal, refund or annual close."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_readiness_v1 as information

book = information.book
core = information.core
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/shared-tax-reconciliation-20261024'
LOCK = '3ce68d2496a0802a4ce4986d16caa38f4bebe0545728ad8d957b72bbc499d0cd'
PROFILE = 'ConditionalSharedCurrentTax/1'
MODEL = 'uniform_rate_no_credits_v1'
FLAGS = {'posted': False, 'committed': False, 'source_admission': False,
         'accounting_admission': False, 'annual_close_ready': False,
         'cash_settled': False, 'deferred_tax_computed': False}


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    core.need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        core.need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                  'protected_source_changed:' + name)


def request(body, model, allocations):
    return {'profile': PROFILE, 'information_request': deepcopy(body),
            'information_sha256': book.digest(body), 'model': deepcopy(model),
            'allocations': deepcopy(allocations)}


def numeric(value): return core.scalar(value, 'rational')


def selected(model):
    core.closed(model, ['profile', 'selected'], 'model')
    core.need(model['profile'] == MODEL, 'unsupported_model')
    value = model['selected']; core.need(type(value) is dict, 'model_selection')
    if value.get('status') == 'unknown':
        core.closed(value, ['status', 'reason'], 'unknown_selection')
        core.text(value['reason'], 'selection_unknown_reason')
        return 'unresolved'
    core.closed(value, ['status', 'value', 'provenance'], 'known_selection')
    core.need(value['status'] == 'known', 'selection_status')
    core.scalar(value['value'], 'boolean')
    origin = value['provenance']; core.closed(origin, ['kind', 'reference'], 'selection_provenance')
    core.need(origin['kind'] in ['assumption', 'source_reference'], 'selection_provenance_kind')
    core.text(origin['reference'], 'selection_reference')
    return 'selected' if value['value'] else 'unsupported'


def calculate(body):
    base = None
    try:
        protected(); information.author.lexical.bounded(body)
        core.closed(body, ['profile', 'information_request', 'information_sha256', 'model', 'allocations'], 'request')
        core.need(body['profile'] == PROFILE, 'profile')
        core.need(body['information_sha256'] == book.digest(body['information_request']), 'information_digest')
        selection = selected(body['model'])
        core.need(type(body['allocations']) is list, 'allocation_list')
        ready = information.assess(body['information_request'])
        base = {'profile': PROFILE, **FLAGS, 'request': deepcopy(body),
                'request_sha256': book.digest(body), 'information_result': ready,
                'source_bundle_sha256': LOCK,
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'tax_cash_settlement': 'unresolved', 'deferred_tax_assessment': 'unresolved',
                'annual_completion': 'unresolved'}
        if ready['status'] != 'information_supplied':
            return {**base, 'status': ready['status'], 'reason': 'information:' + ready['status']}
        if selection != 'selected':
            return {**base, 'status': selection, 'reason': 'explicit_model_selection_required'}
        native = ready['native_report']; inputs = body['information_request']['information']
        closing = native['execution']['after']; accounts = ready['population']['pretax_accounts']
        totals = {key: Q(0) for key in accounts}
        interval = body['information_request']['interval']
        native_adjustments = {a['event_id']: a for a in closing['tax_adjustments']
                              if interval['start'] <= a['date'] < interval['end_exclusive']}
        ids, allocated = set(), set()
        for item in body['allocations']:
            core.closed(item, ['id', 'account', 'amount', 'origin'], 'allocation')
            core.text(item['id'], 'allocation_id')
            core.need(item['id'] not in ids, 'duplicate_allocation_id'); ids.add(item['id'])
            core.need(type(item['account']) is str and item['account'] in totals, 'allocation_account')
            amount = numeric(item['amount']); origin = item['origin']
            core.need(type(origin) is dict, 'allocation_origin')
            if origin.get('kind') == 'native_return':
                core.closed(origin, ['kind', 'event_id'], 'native_origin')
                core.text(origin['event_id'], 'native_event_id'); event_id = origin['event_id']
                core.need(event_id in native_adjustments, 'unknown_native_adjustment')
                core.need(event_id not in allocated, 'duplicate_native_adjustment')
                core.need(amount == numeric(native_adjustments[event_id]['amount']), 'native_adjustment_amount')
                allocated.add(event_id)
            else:
                core.closed(origin, ['kind', 'reference'], 'assumption_origin')
                core.need(origin['kind'] == 'assumption', 'allocation_origin_kind')
                core.text(origin['reference'], 'allocation_assumption')
            totals[item['account']] += amount
        core.need(allocated == set(native_adjustments), 'incomplete_native_adjustments')
        for account in accounts:
            declared = numeric(inputs['income/' + information.pointer(account) + '/current_adjustment']['value'])
            core.need(totals[account] == declared, 'adjustment_allocation_mismatch:' + account)
        basis_checks = {}
        for when in ['opening', 'closing']:
            for side, account in [('asset', 'rou'), ('liability', 'lease_liability')]:
                total = Q(0)
                for right in ready['population']['lease_rights']:
                    key = 'lease/' + information.pointer(right['lease_id']) + '/' + information.pointer(right['right_id'])
                    total += numeric(inputs[key + '/' + when + '_' + side + '_tax_base']['value'])
                aggregate = numeric(inputs['basis/' + account + '/' + when]['value'])
                core.need(total == aggregate, 'lease_basis_mismatch:' + when + ':' + side)
                basis_checks[when + '_' + side] = {'rights_total': book.fmt(total), 'account_basis': book.fmt(aggregate)}
        pretax = -sum(numeric(closing['balances'][key]) for key in accounts)
        adjustment = sum(totals.values()); taxable = pretax + adjustment; rate = numeric(inputs['rate']['value'])
        core.need(rate >= 0, 'negative_rate')
        calculation = {'pretax_income': book.fmt(pretax), 'signed_adjustments': book.fmt(adjustment),
            'taxable_profit': book.fmt(taxable), 'rate': book.fmt(rate),
            'adjustment_totals': {k: book.fmt(v) for k, v in totals.items()},
            'native_adjustment_ids': sorted(allocated), 'basis_reconciliations': basis_checks,
            'interpretation': 'Conditional uniform-rate arithmetic before credits; no tax-law admission or settlement'}
        if taxable < 0:
            return {**base, 'status': 'loss_route_required', 'calculation': calculation,
                    'reason': 'Negative taxable profit requires a separate loss method; no refund is computed'}
        calculation['gross_current_tax'] = book.fmt(taxable * rate)
        return {**base, 'status': 'conditional_gross_current_tax', 'calculation': calculation}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError, OverflowError, AssertionError) as exc:
        return {**(base if base is not None else {'profile': PROFILE, **FLAGS}),
                'status': 'invalid', 'reason': str(exc)[:350]}


def verify_result(body, result):
    try: return book.caller.canonical(result) == book.caller.canonical(calculate(body))
    except (ValueError, TypeError, RecursionError, OverflowError): return False
