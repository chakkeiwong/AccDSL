"""Pure conditional tax accrual and separate payments on a protected native prefix."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import conditional_tax_losses_v1 as losses

book = losses.book
core = losses.core
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/shared-tax-state-20261024'
LOCK = '04b51d06c9fede5503590f6abc3eddefd00cb8cfed79b41e3edf5cf614b24cdf'
ACCRUAL = 'ConditionalSharedTaxAccrual/1'
SETTLEMENT = 'ConditionalSharedTaxSettlement/1'
STATE = 'ConditionalSharedTaxBook/1'
FLAGS = {'committed': False, 'physical_durability': False, 'source_admission': False,
         'accounting_admission': False, 'annual_close_ready': False,
         'native_financial_carry': False, 'deferred_tax_computed': False,
         'complete_financial_statements': False}
require = losses.require


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                'protected_source_changed:' + name)


def accrual_request(loss_request, identity, recognition):
    return {'profile': ACCRUAL, 'id': identity, 'loss_request': deepcopy(loss_request),
            'loss_request_sha256': book.digest(loss_request), 'recognition': deepcopy(recognition)}


def settlement_request(state, identity, day, amount, authorization):
    return {'profile': SETTLEMENT, 'state': deepcopy(state), 'state_sha256': book.digest(state),
            'event': {'id': identity, 'date': day, 'amount': amount,
                      'authorization': deepcopy(authorization)}}


def _materialize(body, settlements, base):
    core.closed(body, ['profile', 'id', 'loss_request', 'loss_request_sha256', 'recognition'], 'accrual')
    require(body['profile'] == ACCRUAL, 'accrual_profile')
    core.text(body['id'], 'accrual_id')
    require(body['loss_request_sha256'] == book.digest(body['loss_request']), 'loss_request_digest')
    result = losses.propose(body['loss_request'])
    base['loss_result'] = deepcopy(result)
    require(result['status'] == 'proposed', 'loss:' + result['status'], result['status'])
    losses.affirmative(body['recognition'], 'current_tax_recognition')
    native = result['reconciliation_result']['information_result']['native_report']
    closing = native['execution']['after']
    book.invariant(closing)
    info = body['loss_request']['reconciliation_request']['information_request']
    interval = info['interval']
    require(Q(closing['balances']['current_tax']) == 0, 'existing_current_tax_unsupported', 'unsupported')
    require(closing['tax_closed_until'] == interval['start'], 'prior_native_tax_close_unsupported', 'unsupported')
    require(body['id'] not in closing['seen'], 'accrual_native_id_collision')
    tax = Q(result['proposal']['conditional_gross_current_tax'])
    require(tax >= 0, 'negative_current_tax')
    balances = deepcopy(closing['balances'])
    balances['current_tax'] = book.fmt(tax)
    balances['income_tax_payable'] = book.fmt(-tax)
    day = interval['activity_through']
    require(closing['date'] <= day < closing['period']['end_exclusive'], 'accrual_timing')
    require(type(settlements) is list, 'settlement_history')
    identities = set(closing['seen']) | {body['id']}
    for event in settlements:
        core.closed(event, ['id', 'date', 'amount', 'authorization'], 'settlement_event')
        core.text(event['id'], 'settlement_id')
        require(event['id'] not in identities, 'duplicate_financial_event')
        core.scalar(event['date'], 'date')
        require(day <= event['date'] < closing['period']['end_exclusive'], 'settlement_date')
        losses.affirmative(event['authorization'], 'cash_payment_authorization')
        paid = losses.tax.numeric(event['amount'])
        require(paid > 0, 'positive_payment_required')
        require(paid <= -Q(balances['income_tax_payable']), 'payment_exceeds_payable')
        require(paid <= Q(balances['cash']), 'cash_shortage', 'funding_failure')
        balances['income_tax_payable'] = book.fmt(Q(balances['income_tax_payable']) + paid)
        balances['cash'] = book.fmt(Q(balances['cash']) - paid)
        day = event['date']; identities.add(event['id'])
    require(sum(Q(v) for v in balances.values()) == 0, 'financial_state_unbalanced')
    state = {'profile': STATE, 'accrual_request': deepcopy(body),
             'native_closing_sha256': book.digest(closing), 'context': deepcopy(closing['context']),
             'balances': balances, 'date': day, 'assessed_until': interval['end_exclusive'],
             'native_tax_closed_until': closing['tax_closed_until'],
             'loss_state': deepcopy(result['proposal']['after']), 'settlements': deepcopy(settlements)}
    return state, native


def _validate(state, base):
    core.closed(state, ['profile', 'accrual_request', 'native_closing_sha256', 'context',
                       'balances', 'date', 'assessed_until', 'native_tax_closed_until',
                       'loss_state', 'settlements'], 'financial_tax_state')
    expected, native = _materialize(state['accrual_request'], state['settlements'], base)
    require(book.caller.canonical(state) == book.caller.canonical(expected), 'financial_state_mismatch')
    return expected, native


def _view(state, native):
    b = state['balances']; classes = deepcopy(native['account_classes'])
    classes['liabilities'].append('income_tax_payable')
    accounts = sum(classes.values(), [])
    require(len(accounts) == len(set(accounts)) and set(accounts) == set(b), 'account_classification')
    assets = sum(Q(b[k]) for k in classes['assets'])
    liabilities = -sum(Q(b[k]) for k in classes['liabilities'])
    profit = -sum(Q(b[k]) for k in classes['income'])
    equity = -sum(Q(b[k]) for k in classes['equity']) + profit
    paid = sum(Q(e['amount']) for e in state['settlements'])
    cf = deepcopy(native['cash_flows_recorded'])
    cf['activities']['operating']['payments'] = book.fmt(Q(cf['activities']['operating']['payments']) + paid)
    cf['activities']['operating']['net'] = book.fmt(Q(cf['activities']['operating']['net']) - paid)
    cf['closing_cash'] = b['cash']; cf['net_movement'] = book.fmt(Q(b['cash']) - Q(cf['opening_cash']))
    flows = [{'event_id': e['id'], 'date': e['date'], 'entity': state['context']['entity'],
              'activity': 'operating', 'origin': 'explicit_conditional_current_tax_payment',
              'amount': book.fmt(-Q(e['amount']))} for e in state['settlements']]
    cf['gross_origins'].extend(flows)
    indirect = deepcopy(native['indirect_operating_recorded']['items'])
    indirect['recorded_profit'] = book.fmt(profit)
    indirect['change_income_tax_payable'] = book.fmt(-Q(b['income_tax_payable']))
    indirect_net = sum(Q(v) for v in indirect.values())
    checks = {'balance_sheet': assets - liabilities - equity,
              'equity': Q(native['equity_recorded']['opening']) + profit - equity,
              'direct_cash': Q(cf['net_movement']) - sum(Q(x['net']) for x in cf['activities'].values()),
              'indirect_cash': indirect_net - Q(cf['activities']['operating']['net'])}
    require(all(v == 0 for v in checks.values()), 'statement_reconciliation')
    return {'scope': 'synthetic native prefix plus explicit conditional current-tax entries',
            'account_classes': classes, 'balance_sheet': {'total_assets': book.fmt(assets),
                'total_liabilities': book.fmt(liabilities), 'equity_including_profit': book.fmt(equity)},
            'recorded_profit': book.fmt(profit), 'cash_flows': cf,
            'indirect_operating': {'items': indirect, 'net': book.fmt(indirect_net)},
            'reconciliations': {k: book.fmt(v) for k, v in checks.items()},
            'unresolved': ['Actual accounting and source admission', 'Deferred-tax assessment',
                           'Later native events and financial-period carry', 'Annual completeness']}


def propose(body):
    base = {**FLAGS}
    try:
        protected(); book.caller.bounded(body)
        require(type(body) is dict, 'request_record')
        base.update(profile=body.get('profile'), request_sha256=book.digest(body),
                    source_bundle_sha256=LOCK,
                    implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if body.get('profile') == ACCRUAL:
            after, native = _materialize(body, [], base)
            before = {**native['execution']['after']['balances'], 'income_tax_payable': '0/1'}
        else:
            core.closed(body, ['profile', 'state', 'state_sha256', 'event'], 'settlement')
            require(body['profile'] == SETTLEMENT, 'profile')
            require(body['state_sha256'] == book.digest(body['state']), 'state_digest')
            state, native = _validate(body['state'], base)
            before = state['balances']
            after, native = _materialize(state['accrual_request'], state['settlements'] + [body['event']], base)
        journal = {k: book.fmt(Q(v) - Q(before[k])) for k, v in after['balances'].items()}
        require(sum(Q(v) for v in journal.values()) == 0, 'journal_unbalanced')
        return {**base, 'status': 'proposed', 'after': after, 'journal': journal,
                'native_report': deepcopy(native), 'recorded_statements': _view(after, native)}
    except losses.Refused as exc:
        return {**base, 'status': exc.status, 'reason': exc.reason}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError, OverflowError, AssertionError) as exc:
        return {**base, 'status': 'invalid', 'reason': str(exc)[:350]}


def apply(body, result):
    expected = propose(body)
    try:
        require(expected['status'] == 'proposed', 'proposal_not_available')
        require(book.caller.canonical(result) == book.caller.canonical(expected), 'proposal_mismatch')
        return {'profile': expected['profile'], **FLAGS, 'status': 'applied', 'after': deepcopy(expected['after'])}
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        return {**FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}
