"""Bounded documentary semantics; no forecast-journal import or durable writes."""
from copy import deepcopy
from datetime import date, datetime
from fractions import Fraction as Q
import hashlib
import json
from jsonschema import Draft202012Validator, FormatChecker
from authoring import q, schema

KINDS = ['purchase', 'delivery', 'facility_draw', 'supplier_payment', 'collection',
         'facility_interest', 'facility_repayment', 'payroll', 'plant_addition',
         'depreciation', 'interest', 'tax', 'dividend', 'close']
TEMPORARY = ['revenue', 'cost_of_sales', 'payroll', 'depreciation', 'interest', 'tax']
ASSETS = ['cash', 'receivables', 'inventory', 'plant_cost', 'accum_depreciation', 'tax_prepaid']
ACCOUNTS = ASSETS + ['payables', 'debt', 'capital', 'retained'] + TEMPORARY


def record_digest(entry):
    canonical = json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(('accdsl.portable.v1/' + entry['schema']).encode() + b'\0' + canonical).hexdigest()


def result(status, **fields):
    return {'status': status, 'committed': False, 'conditional_state': True, **fields}


def validate(body, source_bytes):
    errors = sorted(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(body),
                    key=lambda e: str(list(e.path)))
    if errors:
        return result('invalid', reason='schema', path=list(errors[0].path))
    if hashlib.sha256(source_bytes).hexdigest() != body['source']['sha256']:
        return result('invalid', reason='source_digest')
    source = json.loads(source_bytes)
    entry = source.get('record_registry', {}).get(body['opening_digest'])
    if entry is None or entry.get('kind') != 'CompanyState':
        return result('invalid', reason='opening_reference')
    if record_digest(entry) != body['opening_digest']:
        return result('invalid', reason='opening_record_digest')
    opening = entry['body']
    context_entry = source['record_registry'].get(opening['context_ref']['digest'])
    if not context_entry or context_entry.get('kind') != 'Context':
        return result('invalid', reason='opening_context_reference')
    if record_digest(context_entry) != opening['context_ref']['digest']:
        return result('invalid', reason='opening_context_digest')
    context = context_entry['body']
    if any(body['context'][k] != context[k] for k in ['entity', 'book', 'currency']):
        return result('invalid', reason='context_mismatch')
    start = date.fromisoformat(body['period']['start'])
    end = date.fromisoformat(body['period']['end_exclusive'])
    if start.month != 1 or start.day != 1 or end != date(start.year + 1, 1, 1):
        return result('unsupported', reason='full_calendar_year_required')
    if context['period_end_exclusive'] != body['period']['start']:
        return result('invalid', reason='opening_period_mismatch')
    methods = [(body['inventory']['method'], 'homogeneous_cost'),
               (body['inventory']['purchase_policy'], 'demand_plus_target_less_opening'),
               (body['depreciation_method'], 'straight_line_full_year'),
               (body['loan']['day_count'], 'ACT365_calendar'),
               (body['loan']['interest_cash_class'], 'operating'),
               (body['tax']['method'], 'immediate_deductible')]
    if any(got != expected for got, expected in methods):
        return result('unsupported', reason='method', methods=methods)
    unknown = []
    def inspect(value, rule, path=''):
        if isinstance(value, dict):
            for key, child in value.items():
                inspect(child, rule['properties'][key], path + '/' + key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                inspect(child, rule['items'], path + '/' + str(i))
        elif value == 'unknown':
            if rule.get('pattern', '').startswith('^(unknown|') or 'oneOf' in rule or 'unknown' in rule.get('enum', []):
                unknown.append(path)
        elif rule.get('pattern', '').startswith('^(unknown|'):
            if q(value) < 0:
                raise ValueError('negative input ' + path)
    try:
        inspect(body, schema())
    except (ValueError, ZeroDivisionError) as exc:
        return result('invalid', reason='rational', detail=str(exc))
    if unknown:
        return result('unresolved', obligations=['supply:' + p for p in unknown])
    amounts = {a: Q(v['n']) / Q(v['d']) for a, v in opening['balances'].items()}
    if set(amounts) != set(ACCOUNTS) or sum(amounts.values(), Q(0)) or any(amounts[a] for a in TEMPORARY):
        return result('invalid', reason='opening_accounts')
    units = Q(opening['inventory_units']['n']) / Q(opening['inventory_units']['d'])
    inv, trade, cash, debt, facility, loan = [body[k] for k in ['inventory', 'trade', 'cash', 'debt', 'facility', 'loan']]
    if units < 0 or units * q(inv['unit_cost']) != amounts['inventory']:
        return result('invalid', reason='inventory_control')
    if q(inv['unit_cost']) <= 0 or q(cash['capex_life']) <= 0 or any(q(a['life']) <= 0 for a in body['assets']):
        return result('invalid', reason='positive_cost_or_life')
    if not all(q(v) <= 1 for v in [trade['collection_fraction'], debt['floating_share'], body['tax']['rate']]):
        return result('invalid', reason='fraction_domain')
    if q(debt['coupon_years']) != 1:
        return result('unsupported', reason='legacy_coupon_period')
    if q(debt['principal']) + q(facility['drawn']) != -amounts['debt']:
        return result('invalid', reason='debt_control')
    if q(facility['drawn']) != 0:
        return result('unsupported', reason='opening_facility_accrual_unspecified')
    if loan['facility_id'] != facility['id'] or q(facility['drawn']) + q(facility['reserved']) > q(facility['limit']):
        return result('invalid', reason='facility_identity_or_capacity')
    if q(loan['fee']) != 0:
        return result('unsupported', reason='loan_fee')
    ids = [c['id'] for c in body['opening_claims']] + [trade['sales_claim_id'], trade['purchase_claim_id']]
    if len(set(ids)) != len(ids):
        return result('invalid', reason='duplicate_claim')
    for ledger, account, sign in [('receivable', 'receivables', 1), ('payable', 'payables', -1)]:
        total = sum((q(c['amount']) for c in body['opening_claims'] if c['ledger'] == ledger), Q(0))
        if total != sign * amounts[account]:
            return result('invalid', reason='opening_claim_control')
    if any(q(c['settlement']) > q(c['amount']) for c in body['opening_claims']):
        return result('invalid', reason='opening_over_settlement')
    asset_ids = [a['id'] for a in body['assets']] + [cash['capex_id']]
    if len(set(asset_ids)) != len(asset_ids):
        return result('invalid', reason='duplicate_asset')
    if sum((q(a['cost']) for a in body['assets']), Q(0)) != amounts['plant_cost'] or sum((q(a['accumulated']) for a in body['assets']), Q(0)) != -amounts['accum_depreciation']:
        return result('invalid', reason='asset_control')
    if any(q(a['accumulated']) > q(a['cost']) for a in body['assets']):
        return result('invalid', reason='asset_carrying')
    service_dates = [date.fromisoformat(a['in_service']) for a in body['assets']] + [date.fromisoformat(cash['capex_service'])]
    if any(start < d < end for d in service_dates):
        return result('unsupported', reason='midyear_service_fraction')
    events = body['events']
    if len(events) != len(KINDS) or set(e['kind'] for e in events) != set(KINDS):
        return result('invalid', reason='event_set')
    times = [datetime.fromisoformat(e['at'].replace('Z', '+00:00')) for e in events]
    if any(t.date() < start or t.date() >= end for t in times) or times != sorted(times):
        return result('invalid', reason='event_chronology')
    pos = {e['kind']: i for i, e in enumerate(events)}
    pairs = [('purchase', 'delivery'), ('delivery', 'collection'), ('purchase', 'supplier_payment'),
             ('facility_draw', 'facility_interest'), ('facility_interest', 'facility_repayment'),
             ('plant_addition', 'depreciation')]
    pairs += [(k, 'tax') for k in ['delivery', 'payroll', 'depreciation', 'interest', 'facility_interest']]
    pairs += [(k, 'close') for k in KINDS if k != 'close']
    if any(pos[a] >= pos[b] for a, b in pairs):
        return result('invalid', reason='event_dependency')
    last_date = date(end.year - 1, 12, 31)
    if any(times[pos[k]].date() != last_date for k in ['depreciation', 'interest', 'tax', 'close']):
        return result('unsupported', reason='annual_accrual_at_fiscal_end')
    if times[pos['facility_interest']].date() != times[pos['facility_repayment']].date():
        return result('unsupported', reason='bridge_interest_settles_on_repayment_date')
    capex_at = times[pos['plant_addition']].date()
    if date.fromisoformat(cash['capex_service']) < capex_at:
        return result('invalid', reason='service_before_acquisition')
    if any(d > start and q(a['accumulated']) for a, d in zip(body['assets'], service_dates)):
        return result('invalid', reason='unserved_asset_accumulation')
    if q(inv['demand_units']) + q(inv['target_units']) - units < 0:
        return result('unsupported', reason='negative_target_purchase')
    purchase = (q(inv['demand_units']) + q(inv['target_units']) - units) * q(inv['unit_cost'])
    if q(trade['supplier_payment']) > purchase:
        return result('invalid', reason='purchase_over_settlement')
    return result('validated', opening=amounts, units=units)


def _execute(body, source_bytes):
    admitted = validate(body, source_bytes)
    if admitted['status'] != 'validated':
        return admitted
    balances = admitted['opening'].copy()
    initial = balances.copy()
    units = admitted['units']
    inv, trade, cash, debt, facility, loan = [body[k] for k in ['inventory', 'trade', 'cash', 'debt', 'facility', 'loan']]
    assets = deepcopy(body['assets'])
    claims = {c['id']: {'ledger': c['ledger'], 'recognised': q(c['amount']), 'settled': Q(0), 'outstanding': q(c['amount'])} for c in body['opening_claims']}
    purchase_units = q(inv['demand_units']) + q(inv['target_units']) - units
    purchase = purchase_units * q(inv['unit_cost'])
    sales = q(inv['demand_units']) * q(inv['price'])
    schedule, flows = [], {c: Q(0) for c in ['operating', 'investing', 'financing']}
    dates = {e['kind']: date.fromisoformat(e['at'][:10]) for e in body['events']}
    principal = q(loan['principal'])
    facility_interest = principal * q(loan['annual_rate']) * Q((dates['facility_repayment'] - dates['facility_draw']).days, 365)
    facility_drawn = q(facility['drawn'])
    minimum = balances['cash']
    def halted(status, reason, event, **extra):
        return result(status, reason=reason, event=event, balances=balances.copy(), claims=deepcopy(claims),
                      assets=deepcopy(assets), inventory_units=units, facility_drawn=facility_drawn,
                      flows=flows.copy(), applied=deepcopy(schedule), **extra)
    for event in body['events']:
        kind = event['kind']
        nc, na, nu, nd = deepcopy(claims), deepcopy(assets), units, facility_drawn
        cash_class = None
        paths = []
        if kind == 'purchase':
            lines = {'inventory': purchase, 'payables': -purchase}
            nu += purchase_units
            nc[trade['purchase_claim_id']] = {'ledger': 'payable', 'recognised': purchase, 'settled': Q(0), 'outstanding': purchase}
            paths = ['/inventory', '/trade/purchase_claim_id', '/opening_digest']
        elif kind == 'delivery':
            if not inv['control_transferred']:
                return halted('unsupported', 'control_not_transferred_method', kind)
            if units < q(inv['demand_units']):
                return halted('economic_failure', 'inventory_shortfall', kind)
            cost = q(inv['demand_units']) * q(inv['unit_cost'])
            lines = {'receivables': sales, 'revenue': -sales, 'cost_of_sales': cost, 'inventory': -cost}
            nu -= q(inv['demand_units'])
            nc[trade['sales_claim_id']] = {'ledger': 'receivable', 'recognised': sales, 'settled': Q(0), 'outstanding': sales}
            paths = ['/inventory', '/trade/sales_claim_id']
        elif kind in ['collection', 'supplier_payment']:
            ledger = 'receivable' if kind == 'collection' else 'payable'
            allocations = {c['id']: q(c['settlement']) for c in body['opening_claims'] if c['ledger'] == ledger}
            allocations[trade['sales_claim_id'] if kind == 'collection' else trade['purchase_claim_id']] = sales * q(trade['collection_fraction']) if kind == 'collection' else q(trade['supplier_payment'])
            for key, amount in allocations.items():
                if key not in nc or amount > nc[key]['outstanding']:
                    return halted('invalid', 'claim_settlement', kind)
                nc[key]['settled'] += amount
                nc[key]['outstanding'] -= amount
            amount = sum(allocations.values(), Q(0))
            lines = {'cash': amount, 'receivables': -amount} if kind == 'collection' else {'payables': amount, 'cash': -amount}
            cash_class, paths = 'operating', ['/opening_claims', '/trade']
        elif kind == 'facility_draw':
            if not facility['eligible']:
                return halted('funding_failure', 'known_ineligible_facility', kind)
            headroom = q(facility['limit']) - nd - q(facility['reserved'])
            if principal > headroom:
                return halted('funding_failure', 'facility_headroom', kind, shortfall=principal - headroom)
            lines = {'cash': principal, 'debt': -principal}
            nd += principal
            cash_class, paths = 'financing', ['/facility', '/loan/principal']
        elif kind == 'facility_interest':
            lines = {'interest': facility_interest, 'cash': -facility_interest}
            cash_class, paths = loan['interest_cash_class'], ['/loan', '/events']
        elif kind == 'facility_repayment':
            if nd < principal:
                return halted('invalid', 'undrawn_repayment', kind)
            lines = {'debt': principal, 'cash': -principal}
            nd -= principal
            cash_class, paths = 'financing', ['/loan/principal', '/events']
        elif kind == 'payroll':
            lines = {'payroll': q(cash['payroll']), 'cash': -q(cash['payroll'])}
            cash_class, paths = 'operating', ['/cash/payroll']
        elif kind == 'plant_addition':
            lines = {'plant_cost': q(cash['capex']), 'cash': -q(cash['capex'])}
            na.append({'id': cash['capex_id'], 'cost': cash['capex'], 'life': cash['capex_life'], 'accumulated': '0/1', 'in_service': cash['capex_service']})
            cash_class, paths = 'investing', ['/cash/capex', '/cash/capex_life', '/cash/capex_service']
        elif kind == 'depreciation':
            amount = Q(0)
            for a in na:
                if a['in_service'] <= body['period']['start']:
                    charge = min(q(a['cost']) / q(a['life']), q(a['cost']) - q(a['accumulated']))
                    accumulated = q(a['accumulated']) + charge
                    a['accumulated'] = f'{accumulated.numerator}/{accumulated.denominator}'
                    amount += charge
            lines = {'depreciation': amount, 'accum_depreciation': -amount}
            paths = ['/assets', '/depreciation_method', '/period', '/cash/capex_service']
        elif kind == 'interest':
            share = q(debt['floating_share'])
            amount = q(debt['principal']) * ((1-share) * q(debt['fixed_rate']) + share * q(debt['floating_rate'])) * q(debt['coupon_years'])
            lines = {'interest': amount, 'cash': -amount}
            cash_class, paths = 'operating', ['/debt']
        elif kind == 'tax':
            pbt = -balances['revenue'] - sum(balances[k] for k in TEMPORARY if k not in ['revenue', 'tax'])
            if pbt < 0:
                return halted('unsupported', 'loss_tax_method', kind)
            amount = pbt * q(body['tax']['rate'])
            lines = {'tax': amount, 'cash': -amount}
            cash_class, paths = 'operating', ['/tax', 'state/temporary_accounts']
        elif kind == 'dividend':
            lines = {'retained': q(cash['dividend']), 'cash': -q(cash['dividend'])}
            cash_class, paths = 'financing', ['/cash/dividend']
        else:
            income = {k: -balances[k] if k == 'revenue' else balances[k] for k in TEMPORARY}
            lines = {k: -balances[k] for k in TEMPORARY}
            lines['retained'] = sum(balances[k] for k in TEMPORARY)
            paths = ['state/temporary_accounts', '/period']
        assert sum(lines.values(), Q(0)) == 0
        cash_delta = lines.get('cash', Q(0))
        if balances['cash'] + cash_delta < 0:
            return halted('funding_failure', 'cash_shortfall', kind, shortfall=-(balances['cash']+cash_delta))
        for account, amount in lines.items():
            balances[account] += amount
        claims, assets, units, facility_drawn = nc, na, nu, nd
        if cash_delta:
            flows[cash_class] += cash_delta
        minimum = min(minimum, balances['cash'])
        assert units * q(inv['unit_cost']) == balances['inventory']
        assert sum((q(a['cost']) for a in assets), Q(0)) == balances['plant_cost']
        assert sum((q(a['accumulated']) for a in assets), Q(0)) == -balances['accum_depreciation']
        for ledger, account, sign in [('receivable', 'receivables', 1), ('payable', 'payables', -1)]:
            assert sum((c['outstanding'] for c in claims.values() if c['ledger']==ledger), Q(0)) == sign * balances[account]
        schedule.append({'event': kind, 'date': event['at'][:10], 'at': event['at'], 'journal': lines,
            'cash_class': cash_class, 'cash_after': balances['cash'], 'facility_principal_after': facility_drawn,
            'method': 'northstar.company-input.' + kind + '@draft1', 'input_paths': paths})
    profit = income['revenue'] - sum(income[k] for k in TEMPORARY if k != 'revenue')
    asset_total = sum(balances[k] for k in ASSETS)
    liabilities = -(balances['payables'] + balances['debt'])
    equity = -(balances['capital'] + balances['retained'])
    indirect = profit + income['depreciation'] - (balances['receivables']-initial['receivables']) - (balances['inventory']-initial['inventory']) - (balances['payables']-initial['payables']) - (balances['tax_prepaid']-initial['tax_prepaid'])
    assert asset_total == liabilities + equity
    assert indirect == flows['operating']
    assert initial['cash'] + sum(flows.values(), Q(0)) == balances['cash']
    assert equity == -initial['capital'] - initial['retained'] + profit - q(cash['dividend'])
    assert all(balances[k] == 0 for k in TEMPORARY)
    return result('complete_conditional', closing_balances=balances, claims=claims, assets=assets,
                  inventory_units=units, journals=schedule, income=income, minimum_cash=minimum, facility_drawn=facility_drawn,
                  statements={'assets': asset_total, 'liabilities': liabilities, 'equity': equity, 'profit': profit,
                              'cash': balances['cash'], 'cash_flows': flows}, indirect_cfo=indirect,
                  lineage={'source_sha256': body['source']['sha256'], 'opening_digest': body['opening_digest'],
                           'input_sha256': hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                           'information': body['information'], 'forecast_journals_imported': False})


def input_digest(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def execute(body, source_bytes):
    value = _execute(body, source_bytes)
    value['input_sha256'] = input_digest(body)
    value['source_sha256'] = hashlib.sha256(source_bytes).hexdigest()
    return value
