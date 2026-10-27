"""Pure conditional loss-lot proposals; no refunds, DTA or financial-book carry."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_reconciliation_v1 as tax

core = tax.core
book = tax.book
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/conditional-tax-losses-20261024'
LOCK = '75ccb716fa43f63e2f545a39877802d8143b86feadebe667c3c83d94ecbdea33'
PROFILE = 'ConditionalTaxLossStep/1'
STATE = 'ConditionalTaxLossLedger/1'
MODEL = 'close_day_explicit_use_v1'
FLAGS = {'posted': False, 'committed': False, 'cash_refund': False,
         'deferred_asset_recognized': False, 'source_admission': False,
         'accounting_admission': False, 'native_financial_carry': False,
         'annual_close_ready': False}


class Refused(ValueError):
    def __init__(self, status, reason):
        super().__init__(reason); self.status = status; self.reason = reason


def require(ok, reason, status='invalid'):
    if not ok: raise Refused(status, reason)


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                'protected_source_changed:' + name)


def provenance(value):
    core.closed(value, ['kind', 'reference'], 'provenance')
    require(value['kind'] in ['assumption', 'source_reference'], 'provenance_kind')
    core.text(value['reference'], 'provenance_reference')


def declaration(value, kind):
    require(type(value) is dict, 'declaration_record')
    if value.get('status') == 'unknown':
        core.closed(value, ['status', 'reason'], 'unknown_declaration')
        core.text(value['reason'], 'unknown_reason'); return None
    core.closed(value, ['status', 'value', 'provenance'], 'known_declaration')
    require(value['status'] == 'known', 'declaration_status')
    provenance(value['provenance'])
    return core.scalar(value['value'], kind)


def affirmative(value, reason):
    found = declaration(value, 'boolean')
    require(found is not None, reason + ':unknown', 'unresolved')
    require(found is True, reason + ':false', 'unsupported')


def expiry(value):
    require(type(value) is dict, 'expiry_record')
    if value.get('kind') == 'unknown':
        core.closed(value, ['kind', 'reason'], 'unknown_expiry')
        core.text(value['reason'], 'expiry_reason'); return 'unknown'
    if value.get('kind') == 'none':
        core.closed(value, ['kind', 'provenance'], 'no_expiry')
        provenance(value['provenance']); return None
    core.closed(value, ['kind', 'end_exclusive', 'provenance'], 'dated_expiry')
    require(value['kind'] == 'date', 'expiry_kind'); provenance(value['provenance'])
    return core.scalar(value['end_exclusive'], 'date')


def amount(value):
    parsed = tax.numeric(value); require(parsed >= 0, 'negative_loss_quantity'); return parsed


def validate_state(state):
    tax.information.author.lexical.bounded(state)
    core.closed(state, ['profile', 'context', 'jurisdiction', 'regime', 'cursor',
                        'lots', 'seen', 'history', 'opening_inventory'], 'loss_state')
    require(state['profile'] == STATE, 'state_profile')
    core.closed(state['context'], ['entity', 'book_role', 'currency', 'case_id'], 'context')
    for value in state['context'].values(): core.text(value, 'context_value')
    for key in ['jurisdiction', 'regime']: core.text(state[key], key)
    cursor = core.scalar(state['cursor'], 'date')
    declaration(state['opening_inventory'], 'boolean')
    require(type(state['lots']) is list and type(state['history']) is list, 'state_collections')
    core.identifiers(state['seen'], 'seen')
    ids = set()
    for lot in state['lots']:
        core.closed(lot, ['id', 'origin_reference', 'available_from', 'expiry',
                         'original', 'remaining', 'used', 'expired', 'eligible'], 'loss_lot')
        core.text(lot['id'], 'lot_id'); require(lot['id'] not in ids, 'duplicate_lot'); ids.add(lot['id'])
        core.text(lot['origin_reference'], 'lot_origin')
        available = core.scalar(lot['available_from'], 'date')
        require(available <= cursor, 'future_opening_lot')
        limit = expiry(lot['expiry'])
        if isinstance(limit, date): require(limit > available, 'expiry_before_availability')
        declaration(lot['eligible'], 'boolean')
        quantities = {key: amount(lot[key]) for key in ['original', 'remaining', 'used', 'expired']}
        require(quantities['original'] == sum(quantities[key] for key in ['remaining', 'used', 'expired']),
                'lot_conservation:' + lot['id'])
    history_ids = []
    previous = None
    previous_closing = None
    for row in state['history']:
        core.closed(row, ['step_id', 'start', 'end_exclusive', 'reconciliation_sha256',
                         'opening', 'generated', 'used', 'expired', 'closing'], 'loss_history')
        core.text(row['step_id'], 'history_id'); history_ids.append(row['step_id'])
        start = core.scalar(row['start'], 'date'); end = core.scalar(row['end_exclusive'], 'date')
        require(start < end <= cursor, 'history_interval')
        if previous is not None: require(start == previous, 'history_gap')
        previous = end
        core.need(type(row['reconciliation_sha256']) is str and len(row['reconciliation_sha256']) == 64
                  and all(c in '0123456789abcdef' for c in row['reconciliation_sha256']), 'history_digest')
        q = {key: amount(row[key]) for key in ['opening', 'generated', 'used', 'expired', 'closing']}
        require(q['opening'] + q['generated'] == q['used'] + q['expired'] + q['closing'], 'history_conservation')
        if previous_closing is not None:
            require(q['opening'] == previous_closing, 'history_balance_discontinuity')
        previous_closing = q['closing']
    require(history_ids == state['seen'], 'history_seen_identity')
    if state['history']:
        require(previous == cursor, 'history_cursor')
        require(amount(state['history'][-1]['closing']) == sum(amount(lot['remaining']) for lot in state['lots']),
                'history_closing_balance')
    return state


def request(state, reconciliation_request, step_id, model, utilization_cap, uses, generation):
    return {'profile': PROFILE, 'state': deepcopy(state), 'state_sha256': book.digest(state),
        'reconciliation_request': deepcopy(reconciliation_request),
        'reconciliation_sha256': book.digest(reconciliation_request), 'step_id': step_id,
        'model': deepcopy(model), 'utilization_cap': deepcopy(utilization_cap),
        'uses': deepcopy(uses), 'generation': deepcopy(generation)}


def propose(body):
    base = {'profile': PROFILE, **FLAGS}
    try:
        protected(); tax.information.author.lexical.bounded(body)
        core.closed(body, ['profile', 'state', 'state_sha256', 'reconciliation_request',
                          'reconciliation_sha256', 'step_id', 'model', 'utilization_cap',
                          'uses', 'generation'], 'loss_request')
        require(body['profile'] == PROFILE, 'profile')
        require(body['state_sha256'] == book.digest(body['state']), 'state_digest')
        require(body['reconciliation_sha256'] == book.digest(body['reconciliation_request']), 'reconciliation_digest')
        validate_state(body['state']); core.text(body['step_id'], 'step_id')
        require(body['step_id'] not in body['state']['seen'], 'duplicate_step')
        core.closed(body['model'], ['profile', 'selected'], 'loss_model')
        require(body['model']['profile'] == MODEL, 'unsupported_loss_model')
        declaration(body['model']['selected'], 'boolean')
        cap = declaration(body['utilization_cap'], 'rational')
        if cap is not None: require(cap >= 0, 'negative_utilization_cap')
        require(type(body['uses']) is list, 'usage_list')
        calc = tax.calculate(body['reconciliation_request'])
        base.update(request=deepcopy(body), request_sha256=book.digest(body), reconciliation_result=calc,
            source_bundle_sha256=LOCK, implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if calc['status'] not in ['loss_route_required', 'conditional_gross_current_tax']:
            return {**base, 'status': calc['status'], 'reason': 'reconciliation:' + calc['status']}
        affirmative(body['model']['selected'], 'loss_model_selected')
        affirmative(body['state']['opening_inventory'], 'complete_opening_loss_inventory')
        require(cap is not None, 'utilization_cap_unknown', 'unresolved')
        info = body['reconciliation_request']['information_request']
        native = calc['information_result']['native_report']
        state = body['state']; interval = info['interval']
        require(state['context'] == native['context'], 'loss_context_mismatch')
        for key in ['jurisdiction', 'regime']:
            require(state[key] == info['information'][key]['value'], 'loss_scope_mismatch:' + key)
        require(state['cursor'] == interval['start'], 'noncontiguous_loss_interval')
        end = core.scalar(interval['end_exclusive'], 'date')
        usage_day = core.scalar(interval['activity_through'], 'date')
        taxable = Q(calc['calculation']['taxable_profit']); rate = Q(calc['calculation']['rate'])
        after = deepcopy(state); lots = {lot['id']: lot for lot in after['lots']}
        movements = {lot['id']: {'opening': amount(lot['remaining']), 'generated': Q(0),
                               'used': Q(0), 'expired': Q(0)} for lot in after['lots']}
        expiries = {}
        for lot in after['lots']:
            if amount(lot['remaining']) == 0: continue
            affirmative(lot['eligible'], 'lot_eligibility:' + lot['id'])
            limit = expiry(lot['expiry']); require(limit != 'unknown', 'lot_expiry_unknown:' + lot['id'], 'unresolved')
            expiries[lot['id']] = limit
        used_ids = set(); total_used = Q(0)
        for usage in body['uses']:
            core.closed(usage, ['lot_id', 'amount'], 'loss_use'); core.text(usage['lot_id'], 'use_lot_id')
            key = usage['lot_id']; require(key in lots, 'unknown_used_lot')
            require(key not in used_ids, 'duplicate_used_lot'); used_ids.add(key)
            used = amount(usage['amount']); require(used > 0, 'zero_use_must_be_omitted')
            lot = lots[key]; limit = expiries.get(key)
            require(amount(lot['remaining']) >= used, 'lot_overuse')
            require(limit is None or limit > usage_day, 'expired_lot_use')
            lot['remaining'] = book.fmt(amount(lot['remaining']) - used)
            lot['used'] = book.fmt(amount(lot['used']) + used)
            movements[key]['used'] = used; total_used += used
        require(total_used <= cap and total_used <= max(Q(0), taxable), 'usage_exceeds_cap_or_profit')
        for lot in after['lots']:
            limit = expiries.get(lot['id'])
            if limit is not None and limit <= end:
                remaining = amount(lot['remaining']); lot['remaining'] = '0/1'
                lot['expired'] = book.fmt(amount(lot['expired']) + remaining)
                movements[lot['id']]['expired'] = remaining
        generated = Q(0)
        if taxable < 0:
            require(not body['uses'], 'negative_profit_cannot_use_losses')
            generation = body['generation']
            core.closed(generation, ['id', 'eligible', 'expiry'], 'loss_generation')
            core.text(generation['id'], 'generation_id'); require(generation['id'] not in lots, 'reused_loss_id')
            affirmative(generation['eligible'], 'generated_loss_eligibility')
            limit = expiry(generation['expiry']); require(limit != 'unknown', 'generated_expiry_unknown', 'unresolved')
            require(limit is None or limit > end, 'generated_expiry_before_availability')
            generated = -taxable; key = generation['id']
            after['lots'].append({'id': key, 'origin_reference': 'sha256:' + book.digest(calc) + '#/calculation/taxable_profit',
                'available_from': interval['end_exclusive'], 'expiry': deepcopy(generation['expiry']),
                'original': book.fmt(generated), 'remaining': book.fmt(generated), 'used': '0/1', 'expired': '0/1',
                'eligible': deepcopy(generation['eligible'])})
            movements[key] = {'opening': Q(0), 'generated': generated, 'used': Q(0), 'expired': Q(0)}
        else: require(body['generation'] is None, 'generation_requires_negative_profit')
        for lot in after['lots']: movements[lot['id']]['closing'] = amount(lot['remaining'])
        totals = {key: sum(row[key] for row in movements.values()) for key in ['opening', 'generated', 'used', 'expired', 'closing']}
        require(totals['opening'] + totals['generated'] == totals['used'] + totals['expired'] + totals['closing'], 'step_conservation')
        after['cursor'] = interval['end_exclusive']; after['seen'].append(body['step_id'])
        after['history'].append({'step_id': body['step_id'], 'start': interval['start'],
            'end_exclusive': interval['end_exclusive'], 'reconciliation_sha256': body['reconciliation_sha256'],
            **{key: book.fmt(value) for key, value in totals.items()}})
        validate_state(after)
        profit_after = max(Q(0), taxable - total_used)
        proposal = {'before_sha256': body['state_sha256'], 'after': after,
            'movements': {key: {k: book.fmt(v) for k, v in row.items()} for key, row in movements.items()},
            'totals': {key: book.fmt(value) for key, value in totals.items()},
            'taxable_profit_before_losses': book.fmt(taxable), 'taxable_profit_after_losses': book.fmt(profit_after),
            'conditional_gross_current_tax': book.fmt(profit_after * rate),
            'expiry_rule': MODEL, 'usage_day': interval['activity_through'],
            'continuity_scope': 'loss ledger only; native financial carry unestablished'}
        return {**base, 'status': 'proposed', 'proposal': proposal}
    except Refused as exc:
        return {**base, 'status': exc.status, 'reason': exc.reason}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError, OverflowError, AssertionError) as exc:
        return {**base, 'status': 'invalid', 'reason': str(exc)[:350]}


def apply(body, result):
    expected = propose(body)
    try:
        require(expected['status'] == 'proposed', 'proposal_not_available')
        require(book.caller.canonical(result) == book.caller.canonical(expected), 'proposal_mismatch')
        return {'profile': PROFILE, **FLAGS, 'status': 'applied', 'after': deepcopy(expected['proposal']['after'])}
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}
